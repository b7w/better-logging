import re

import arrow


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
