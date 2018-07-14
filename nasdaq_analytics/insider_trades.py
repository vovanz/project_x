#!/usr/bin/env python
import json
from io import FileIO
from tempfile import NamedTemporaryFile
from typing import Set, Dict
from uuid import UUID

from more_itertools import chunked
from scrapy.crawler import CrawlerProcess

from common import load_tickers_file
from config import Config
from db import session, Insider, InsiderTuple, Ticker, InsiderTrade
from spiders import InsiderTradesSpider


def get_insider_trades(tmp_file: FileIO):
    process = CrawlerProcess({
        'CONCURRENT_REQUESTS': Config.CONCURRENT_REQUESTS,
        'FEED_FORMAT': 'jsonlines',
        'FEED_URI': f'file://{tmp_file.name}',
    })

    process.crawl(InsiderTradesSpider, load_tickers_file())
    process.start()


def save_insider_trades(tmp_file: FileIO):
    for chunk in chunked(tmp_file.readlines(), Config.CHUNK_SIZE):
        insider_trades = [json.loads(line) for line in chunk]

        insiders: Set[InsiderTuple] = set(
            InsiderTuple(
                id=insider_trade['insider_id'],
                name=insider_trade['insider_name'],
            )
            for insider_trade in insider_trades
        )
        Insider.insert_insiders(insiders)

        symbols: Set[str] = set(insider_trade['symbol'] for insider_trade in insider_trades)
        Ticker.insert_tickers(symbols)
        symbol_to_uuid: Dict[str, UUID] = Ticker.get_uuids_by_symbol()

        InsiderTrade.bulk_insert(
            [
                dict(
                    ticker_id=symbol_to_uuid[insider_trade['symbol']],
                    **{
                        k: v
                        for k, v in insider_trade.items() if k != 'symbol' and k != 'insider_name'
                    }
                )
                for insider_trade in insider_trades
            ]
        )

        session.commit()

if __name__ == '__main__':
    with NamedTemporaryFile() as insider_trades_file:
        get_insider_trades(insider_trades_file)
        save_insider_trades(insider_trades_file)