import asyncio
import logging

import arrow
from asyncpg import create_pool
from sanic import Sanic
from sanic.log import LOGGING_CONFIG_DEFAULTS
from sanic.response import json
from sanic_openapi import swagger_blueprint

from better_logging.core import date_between, parse_query, db_fetch

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
    sql = '''
            SELECT distinct mapped_value
            FROM logging_event_property
            WHERE mapped_key = 'appName'
            ORDER BY mapped_value
            LIMIT 1000000;
        '''
    rows = await db_fetch(db, sql)
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
            LOG.warning(e)


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
    params = request.json
    time_from, time_to = date_between(params['datetime'])
    trace_id, messages = parse_query(params['query'])
    rows = await db_fetch(
        request.app.db, sql,
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
    return json(res)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, access_log=False)
