"""Модуль, содержащий "паука" для сбора исторических цен."""
import logging
from datetime import datetime
from typing import NamedTuple, Dict

from scrapy.http.request import Request
from scrapy.http.response import Response
from scrapy.selector import Selector

from .base import BaseSpider
from .common import only_numbers


class RawRow(NamedTuple):
    date: str
    open: str
    high: str
    low: str
    close: str
    volume: str

    @staticmethod
    def from_selector(selector: Selector) -> 'RawRow':
        return RawRow(*selector.xpath('./td/text()').extract())


class ParsedRow(NamedTuple):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    symbol: str

    @staticmethod
    def from_raw(raw_row: RawRow, symbol: str) -> 'ParsedRow':
        return ParsedRow(
            date=datetime.strptime(raw_row.date.strip(), '%m/%d/%Y').strftime('%Y-%m-%d'),
            open=float(raw_row.open.strip()),
            high=float(raw_row.high.strip()),
            low=float(raw_row.low.strip()),
            close=float(raw_row.close.strip()),
            volume=int(only_numbers.sub('', raw_row.volume)),
            symbol=symbol,
        )

    def as_dict(self) -> Dict:
        return self._asdict()


class HistoricalPricesSpider(BaseSpider):
    """"""
    name = 'historical_prices'

    def start_requests(self):
        for symbol in self.symbols:
            yield Request(f'https://www.nasdaq.com/symbol/{symbol.lower()}/historical', meta={'symbol': symbol})

    def parse(self, response: Response):
        symbol = response.meta['symbol']
        for row in response.xpath('//div[@id="historicalContainer"]//table/tbody/tr'):
            raw_row = RawRow.from_selector(row)
            try:
                yield ParsedRow.from_raw(raw_row, symbol).as_dict()
            except ValueError:
                logging.exception('Ошибка при парсинге строки таблицы с историческими данными.')
