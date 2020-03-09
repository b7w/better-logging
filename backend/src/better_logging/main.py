import asyncio
import json
import logging
import os
import sys
import types
import typing
from logging.config import dictConfig
from pathlib import Path

from aiohttp import web
from aiohttp.web_response import json_response
from asyncpg import create_pool
from asyncpg.pool import Pool

from better_logging.core import find_modules, find_events

LOGGING_CONFIG_DEFAULTS = dict(
    version=1,
    disable_existing_loggers=True,
    loggers={
        "better_logging": {'level': 'INFO', 'handlers': ['console']},
        "aiohttp": {'level': 'INFO', 'handlers': ['console']},
    },
    handlers={
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "stream": sys.stdout,
        }
    },
    formatters={
        "generic": {
            "format": "[%(asctime)s] {%(process)d} [%(levelname)s] %(name)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S %z",
            "class": "logging.Formatter",
        }
    },
)

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
    if app.config.db:
        await app.config.db.close()
        LOG.info('Closed PG pool')


async def update_modules(app: web.Application):
    t = app.config.modules_update_time
    while True:
        res = await find_modules(app.config)
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
    res = request.app.config.modules
    if res:
        return json_response(res)
    res = await find_modules(request.app.config)
    return json_response(res)


async def search(request: web.Request):
    """
    Logging Event search
    """
    params = await request.json()
    events = find_events(request.app.config, params)
    response = web.StreamResponse()
    await response.prepare(request)

    async for event in events:
        record = bytes(json.dumps(event) + '\n', encoding='utf-8')
        await response.write(record)
    await response.write_eof()
    return response


class Config:
    db: Pool = None
    modules: typing.List[str] = None
    tz_info = 'Europe/Moscow'
    db_url: str = None
    modules_update_time: str = 3600
    modules_query_limit: int = 4 * 10 ** 6
    search_query_limit: int = 4096

    def __init__(self):
        filename = os.environ.get('CONFIG_PATH', 'config.py')
        module = types.ModuleType('config')
        module.__file__ = filename
        try:
            with open(filename) as config_file:
                exec(
                    compile(config_file.read(), filename, 'exec'),
                    module.__dict__,
                )
        except IOError as e:
            e.strerror = f'Unable to load config file "{filename}" ({e.strerror})'
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
    app.router.add_static('/', Path(Path(__file__).parent, 'static'))

    web.run_app(app, port=8000, print=LOG.info, access_log=None)


if __name__ == '__main__':
    main()
