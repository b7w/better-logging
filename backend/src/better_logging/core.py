import logging
import re
import time

import arrow

LOG = logging.getLogger('better_logging.core')


def date_between(dt):
    dt_from = arrow.get(dt[0]).floor('day')
    if len(dt) == 2:
        dt_to = arrow.get(dt[1]).ceil('day')
    else:
        dt_to = dt_from.replace().ceil('day')
    return dt_from.timestamp * 1000, dt_to.timestamp * 1000


def parse_query(query):
    trace = re.findall(r'trace:([\w-]+)', query)
    q = re.sub(r'trace:[\w-]+', '', query).strip()
    messages = re.split(r'(".*?"|\S+)', q)
    messages = ['%' + i.strip('"').lower() + '%' for i in messages if i.strip()]
    return trace or ['%'], messages or ['%']


async def db_fetch(db, sql, *params):
    async with db.acquire() as conn:
        star = time.time_ns()
        rows = await conn.fetch(sql, *params)
        end = round((time.time_ns() - star) / 10 ** 6)
        LOG.info('Found %s rows in %sms for %s parameters', len(rows), end, params)
        return rows
