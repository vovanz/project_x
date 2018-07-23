# NASDAQ Analytics

Скрапер и веб-интерфейс для получения и анализа некоторых данных с NASDAQ в соответствии с [ТЗ](https://github.com/Life1over/test-task/blob/master/python.md).


## Запуск в docker

Докер-контейнер ожидает, что ему будут переданные следующие переменные окружения:

- `POSTGRES_HOST` - хост, на котором запущен постгрес
- `POSTGRES_PORT` - порт, на котором запушен постгрес, по умолчанию - 5432
- `POSTGRES_DB` - название базы данных
- `POSTGRES_USER` - пользователь, для подключения к БД
- `POSTGRES_PASSWORD` - пароль, для подключения к БД
- `CONCURRENT_REQUESTS` - максимальное количество параллельных запросов, по умолчанию - 16
- `TICKERS_FILE` - путь к файлу `tickers.txt`, по умолчанию - `/var/input/tickers.txt`.

### С помощью docker-compose

В корне есть файл `docker-compose.yml`, который уже содержит все нужные параметры для запуска,
так что можно запустить всё одной командой `docker-compose up -d`.

Чтобы применить миграции нужно вызвать `docker-compose run --rm scraper ./migrations/apply.sh`, после того, как поднимется постгрес.
После того, как постгрес запущен и миграции применены, нужно запустить скрапер командой `docker-compose run --rm scraper`.

В корне есть скрипт `run.sh`, который делает всё вышеперечисленное.

После запуска веб-интерфейс будет доступен на порту `8080`.

## Запуск без docker

Чтобы запустить проект без докера, нужно окружение, в котором есть Python 3.6+ с установленными зависимостями из `requirements.txt`.

Для запуска миграций нужно вызвать скрипт `./migrations/apply.sh`, который ожидает переменные окружения
`POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_USER`, и `POSTGRES_PASSWORD` с данными для доступа к постгресу.

Для запуска скрапера нужно вызвать скрипт `./nasdaq_analytics/scraper.sh` со всеми нужными конфигурационными параметрами (перечисленными выше).

Для запуска веб-приложения можно использовать любой сервер с поддержкой WSGI (например gunicorn, uwsgi, etc...).
WSGI-интерфейс называется `app` и объявлен в файле `./nasdaq_analytics/web.py`.

## Линтинг и документация

## Комментарии к некоторым техническим решениям