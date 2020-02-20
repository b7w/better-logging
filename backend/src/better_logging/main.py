import asyncio
import logging

import arrow
from asyncpg import create_pool
from sanic import Sanic
from sanic.log import LOGGING_CONFIG_DEFAULTS
from sanic.response import json
from sanic_openapi import swagger_blueprint

LOGGING_CONFIG_DEFAULTS['loggers']['better_logging'] = {'level': 'INFO', 'handlers': ['console']}
MSK_TZ = 'Europe/Moscow'
LOG = logging.getLogger('better_logging')

app = Sanic(name='better-logging', log_config=LOGGING_CONFIG_DEFAULTS)
app.blueprint(swagger_blueprint)

app.config.setdefault('API_LICENSE_NAME', 'MIT')
app.config.setdefault('API_VERSION', '0.1')
app.config.setdefault('MODULES_UPDATE_TIME', '60')
app.config.from_envvar('CONFIG_PATH')


async def register_db(app, loop):
    app.db = await create_pool(
        dsn=app.config.DB_URL,
        min_size=2,
        max_size=8,
        max_queries=48,
        max_inactive_connection_lifetime=640,
        loop=loop
    )
    LOG.info('Create PG pool')


async def close_connection(app, loop):
    await app.db.close()
    LOG.info('Closed PG pool')


async def find_modules(db):
    async with db.acquire() as conn:
        sql = '''
            SELECT distinct mapped_value
            FROM logging_event_property
            WHERE mapped_key = 'appName'
            ORDER BY mapped_value;
        '''
        rows = await conn.fetch(sql)
        return [it[0] for it in rows]


async def update_modules(app):
    t = int(app.config.get('MODULES_UPDATE_TIME'))
    while True:
        res = await find_modules(app.db)
        if app.config.get('modules') != res:
            app.config.modules = res
            LOG.info('Update modules: %s', app.config.modules)
        try:
            await asyncio.sleep(t)
        except asyncio.TimeoutError as e:
            LOG.info(e)


app.register_listener(register_db, 'before_server_start')
app.register_listener(close_connection, 'after_server_stop')
app.add_task(update_modules)


@app.route('/api/modules')
async def modules(request):
    """
    From logging properties find all `appName`s
    """
    res = request.app.config.get('modules', [])
    if res:
        return json(res)
    return json(await find_modules(request.app.db))


@app.route('/api/search', methods={'POST'})
async def search(request):
    """
    Logging Event search
    """

    def date_between(dt):
        dt_from = arrow.get(dt[0]).floor('day')
        if len(dt) == 2:
            dt_to = arrow.get(dt[1]).ceil('day')
        else:
            dt_to = dt_from.replace().ceil('day')
        return dt_from.timestamp * 1000, dt_to.timestamp * 1000

    params = request.json
    async with request.app.db.acquire() as conn:
        sql = '''
            SELECT event_id, timestmp, level_string, logger_name, formatted_message
            FROM logging_event
            WHERE level_string = any($1::varchar[]) AND timestmp between $2 AND $3
            ORDER BY event_id DESC
            LIMIT 1001
        '''
        levels = params['levels']
        time_from, time_to = date_between(params['datetime'])
        rows = await conn.fetch(sql, levels, time_from, time_to)
        res = []
        for row in rows:
            event_id, timestmp, level_string, logger_name, message = row
            d = arrow.Arrow \
                .fromtimestamp(timestmp / 1000, 'Europe/Moscow') \
                .format('YYYY-MM-DDTHH:mm:ss.SS')
            rec = dict(id=event_id, app='some', datetime=d,
                       level=level_string, logger_name=logger_name[:48], message=message)
            res.append(rec)
    return json(res)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, access_log=False)