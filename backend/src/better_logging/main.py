import asyncio
import logging
import os
import sys
import types
import typing
from logging.config import dictConfig

import arrow
from aiohttp import web
from aiohttp.web_response import json_response
from asyncpg import create_pool
from asyncpg.pool import Pool

from better_logging.core import date_between, parse_query, db_fetch

LOGGING_CONFIG_DEFAULTS = dict(
    version=1,
    disable_existing_loggers=False,
    loggers={
        "better_logging": {'level': 'INFO', 'handlers': ['console']},
        "aiohttp.web": {'level': 'DEBUG', 'handlers': ['console']},
        "aiohttp.access": {'level': 'DEBUG', 'handlers': ['console']},
        "aiohttp": {'level': 'DEBUG', 'handlers': ['console']},
    },
    handlers={
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "stream": sys.stdout,
        },
        "error_console": {
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "stream": sys.stderr,
        },
        "access_console": {
            "class": "logging.StreamHandler",
            "formatter": "access",
            "stream": sys.stdout,
        },
    },
    formatters={
        "generic": {
            "format": "%(asctime)s [%(process)d] [%(levelname)s] %(message)s",
            "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
            "class": "logging.Formatter",
        },
        "access": {
            "format": "%(asctime)s - (%(name)s)[%(levelname)s][%(host)s]: "
                      + "%(request)s %(message)s %(status)d %(byte)d",
            "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
            "class": "logging.Formatter",
        },
    },
)

MSK_TZ = 'Europe/Moscow'
LOG = logging.getLogger('better_logging')


async def register_db(app: web.Application):
    app.config.db = await create_pool(
        dsn=app.config.db_url,
        min_size=2,
        max_size=8,
        max_queries=48,
        max_inactive_connection_lifetime=640,
    )
    LOG.info('Create PG pool')


async def close_connection(app: web.Application):
    await app.db.close()
    LOG.info('Closed PG pool')


async def find_modules(db):
    sql = '''
            SELECT distinct mapped_value
            FROM logging_event_property
            WHERE mapped_key = 'appName'
            ORDER BY mapped_value
            LIMIT 1000000;
        '''
    rows = await db_fetch(db, sql)
    return [it[0] for it in rows]


async def update_modules(app: web.Application):
    t = app.config.modules_update_time
    while True:
        res = await find_modules(app.config.db)
        if app.config.modules != res:
            app.config.modules = res
            LOG.info('Update modules: %s', res)
        try:
            await asyncio.sleep(t)
        except asyncio.TimeoutError as e:
            LOG.warning(e)


async def update_modules_nowait(app: web.Application):
    asyncio.create_task(update_modules(app))


async def modules(request):
    """
    From logging properties find all `appName`s
    """
    res = request.app.get('modules', [])
    if res:
        return json_response(res)
    res = await find_modules(request.app.db)
    return json_response(res)


async def search(request: web.Request):
    """
    Logging Event search
    """
    sql = '''
        SELECT e.event_id,
               e.timestmp,
               e.level_string,
               e.logger_name,
               e.formatted_message as message,
               p1.mapped_value     as app,
               p2.mapped_value     as traceId
        FROM logging_event e
            LEFT JOIN logging_event_property p1 on e.event_id = p1.event_id AND p1.mapped_key = 'appName'
            LEFT JOIN logging_event_property p2 on e.event_id = p2.event_id AND p2.mapped_key = 'trace-id'
        WHERE e.timestmp between $1 AND $2
            AND e.level_string = any($3::varchar[])
            AND (p1.mapped_value = any($4::varchar[])
                OR p1.mapped_value is null)
            AND (p2.mapped_value LIKE any($5::varchar[])
                OR p2.mapped_value is null)
            AND lower(e.formatted_message) LIKE any($6::varchar[])
        ORDER BY e.timestmp DESC
        LIMIT 1000
    '''
    params = await request.json()
    time_from, time_to = date_between(params['datetime'])
    trace_id, messages = parse_query(params['query'])
    rows = await db_fetch(
        request.app.config.db, sql,
        time_from, time_to,
        params['levels'],
        params['modules'],
        trace_id,
        messages
    )
    res = []
    for row in rows:
        d = arrow.Arrow \
            .fromtimestamp(row['timestmp'] / 1000, 'Europe/Moscow') \
            .format('YYYY-MM-DDTHH:mm:ss.SS')
        res.append(dict(
            id=row['event_id'],
            app=row['app'],
            datetime=d,
            level=row['level_string'],
            logger_name=row['logger_name'],
            message=row['message']
        ))
    return json_response(res)


class Config:
    db: Pool = None
    modules: typing.List[str] = None
    db_url: str = None
    modules_update_time: str = 60

    def __init__(self):
        filename = os.environ.get('CONFIG_PATH', 'config.py')
        module = types.ModuleType("config")
        module.__file__ = filename
        try:
            with open(filename) as config_file:
                exec(
                    compile(config_file.read(), filename, "exec"),
                    module.__dict__,
                )
        except IOError as e:
            e.strerror = f"Unable to load config file ({e.strerror})"
            raise

        for key in dir(module):
            if key.isupper():
                setattr(self, key.lower(), getattr(module, key))


def main():
    dictConfig(LOGGING_CONFIG_DEFAULTS)
    app = web.Application()
    app.config = Config()

    app.on_startup.append(register_db)
    app.on_startup.append(update_modules_nowait)
    app.on_cleanup.append(close_connection)
    app.router.add_route('GET', '/api/modules', modules)
    app.router.add_route('POST', '/api/search', search)

    web.run_app(app, port=8000, print=LOG.info)


if __name__ == '__main__':
    main()
