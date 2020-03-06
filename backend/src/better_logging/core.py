import logging
import re
import time

import arrow
from asyncpg.pool import Pool

LOG = logging.getLogger('better_logging.core')


def date_between(dt, tz_info):
    utc_tz_info = arrow.utcnow().tzinfo
    dt_from = arrow.get(dt[0], tzinfo=tz_info).floor('day')
    if len(dt) == 2:
        dt_to = arrow.get(dt[1], tzinfo=tz_info).ceil('day')
    else:
        dt_to = dt_from.replace().ceil('day')
    return dt_from.astimezone(utc_tz_info).timestamp() * 1000, dt_to.astimezone(utc_tz_info).timestamp() * 1000


def parse_query(query):
    trace = re.findall(r'trace:([\w-]+)', query)
    q = re.sub(r'trace:[\w-]+', '', query).strip()
    messages = re.split(r'(".*?"|\S+)', q)
    messages = ['%' + i.strip('"').lower() + '%' for i in messages if i.strip()]
    return trace or ['%'], messages or ['%']


async def db_fetch(db: Pool, sql, *params):
    async with db.acquire() as conn:
        star = time.time_ns()
        rows = await conn.fetch(sql, *params)
        end = round((time.time_ns() - star) / 10 ** 6)
        LOG.info('Found %s rows in %sms for %s parameters', len(rows), end, params)
        return rows


async def db_cursor(db: Pool, sql, *params):
    async with db.acquire() as conn:
        async with conn.transaction():
            star = time.time_ns()
            count = 0
            async for record in conn.cursor(sql, *params, prefetch=2):
                count += 1
                yield record
            end = round((time.time_ns() - star) / 10 ** 6)
            LOG.info('Found %s rows in %sms for %s parameters', count, end, params)


async def find_modules(config):
    sql = '''
            SELECT distinct mapped_value
            FROM logging_event_property
            WHERE mapped_key = 'appName'
            LIMIT $1;
        '''
    rows = await db_fetch(config.db, sql, config.modules_query_limit)
    return [it[0] for it in rows]


async def find_events(config, params):
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
        LIMIT $7
    '''
    time_from, time_to = date_between(params['datetime'], tz_info=config.tz_info)
    trace_id, messages = parse_query(params['query'])
    cursor = db_cursor(
        config.db, sql,
        time_from, time_to,
        params['levels'],
        params['modules'],
        trace_id,
        messages,
        config.search_query_limit
    )
    async for row in cursor:
        d = arrow.Arrow \
            .fromtimestamp(row['timestmp'] / 1000, config.tz_info) \
            .format('YYYY-MM-DDTHH:mm:ss.SS')
        yield dict(
            id=row['event_id'],
            app=row['app'],
            datetime=d,
            level=row['level_string'],
            logger_name=row['logger_name'],
            message=row['message']
        )
