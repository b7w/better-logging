from better_logging.core import parse_query


def test_parse_query_empty():
    trace, messages = parse_query('')

    assert trace == ['%']
    assert messages == ['%']


def test_parse_query_empty_messages():
    trace, messages = parse_query(' trace:id ')

    assert trace == ['id']
    assert messages == ['%']


def test_parse_query_empty_trace():
    trace, messages = parse_query(' some ')

    assert trace == ['%']
    assert messages == ['some']


def test_parse_query_trace():
    trace, _ = parse_query('some trace:id1 some trace:id2')

    assert trace == ['id1', 'id2']


def test_parse_query_messages():
    _, messages = parse_query('trace:id1 client "Find error" BOB "some "')

    assert messages == ['%client%', '%find error%', '%bob%', '%some %']
