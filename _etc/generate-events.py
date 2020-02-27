import csv
import gzip
import random
import string
import sys
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

SIMPLE_WORDS = """
recovery intern mother lawmaker planner vengeance cartel
middle pace lantern device labor homicide mood tub gratitude kind estimate
clown nitrogen duration tip legacy validity facility victory multimedia
oak release excerpt muslim waste vantage pyramid sort liberal catalogue punch nose
ship carpenter superstar trumpet kindness firing face node
counting galaxy trek link criminal camper average corridor bearing
""".strip().split()

WORDS = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer eu metus lectus. Donec scelerisque vestibulum nibh sit amet interdum. Donec luctus ut neque ultrices elementum. Nam viverra elit vitae mauris hendrerit porta. Morbi posuere posuere urna, vitae sollicitudin sem tempor vitae. Vivamus ornare nunc vitae suscipit tincidunt. Sed mattis faucibus enim a tincidunt. Vivamus ultricies suscipit dui, ac euismod est bibendum id.
Donec vel nisi eu libero pellentesque ultricies. Nunc elit massa, tincidunt ac nunc quis, tempor vestibulum lorem. Cras at quam at eros lacinia sagittis vitae eu ante. Donec ac nunc tincidunt, tempus sapien sed, euismod purus. Nunc sem nisi, accumsan ut neque vitae, scelerisque ornare dui. Suspendisse laoreet pharetra mauris, quis imperdiet orci sodales in. Suspendisse potenti.
Donec at arcu rutrum, elementum odio eget, eleifend eros. Aliquam placerat leo in erat feugiat, id fermentum urna sagittis. Curabitur luctus lectus orci, vitae finibus ex sollicitudin iaculis. Mauris sapien felis, maximus scelerisque fringilla ut, convallis ac ipsum. Proin tempor lorem a mauris tempor, vitae cursus orci accumsan. Pellentesque ultrices metus ac magna volutpat faucibus. Donec molestie augue nec aliquam facilisis. Pellentesque vel orci et eros cursus varius. Sed eu convallis ligula. Pellentesque pulvinar, nisi nec maximus tempus, eros ligula egestas enim, sed tempus urna sapien sit amet nunc. Nullam vehicula magna augue, at dignissim magna egestas quis. Ut id turpis in mauris semper eleifend. Curabitur efficitur, leo at suscipit imperdiet, ligula elit sollicitudin libero, non bibendum ipsum eros in nulla. Mauris eu dui et mauris blandit aliquet vitae eu orci. Phasellus tempor sem ac commodo consectetur. Nulla vitae feugiat elit, ac gravida metus.
Aliquam faucibus id turpis eget malesuada. Donec malesuada mi id ligula euismod dapibus. Praesent leo arcu, sagittis quis volutpat a, rutrum sed eros. Phasellus bibendum erat est, quis elementum lectus elementum sed. Lorem ipsum dolor sit amet, consectetur adipiscing elit. In ut nisi tempor, elementum dolor id, commodo massa. Curabitur nisl elit, pulvinar et odio in, imperdiet consequat arcu.
Pellentesque quis enim id ex suscipit hendrerit quis in sapien. Aliquam consectetur nulla id elit dignissim, non maximus erat ultrices. Sed euismod rhoncus velit, id consequat ex. Cras vel pretium sapien. Fusce tempor arcu risus, vitae dictum metus finibus sed. Morbi blandit, ipsum sit amet iaculis congue, lacus tortor ornare tortor, at maximus tellus nisi vel elit. Pellentesque quis eros metus. Etiam elementum purus in libero luctus facilisis. Donec maximus ultricies molestie. Phasellus elementum orci ut metus convallis ultrices. Aliquam dictum neque tortor, sit amet pretium purus finibus et. Nulla facilisi.
Nulla at pellentesque ligula. Praesent pulvinar libero quis nulla euismod, ac ornare justo sodales. Quisque iaculis finibus felis, non varius magna cursus in. Donec laoreet leo non mauris elementum, a molestie nunc luctus. Maecenas sed turpis et libero viverra cursus eu vitae libero. Aliquam erat volutpat. In congue egestas mi et rutrum. Suspendisse ac fermentum ex, vel elementum lorem. Etiam elementum risus eu lorem tempor, id molestie tellus tempus. Suspendisse mauris justo, pellentesque eu egestas sit amet, fermentum non risus. Ut non augue ipsum. Donec hendrerit in nisi ac eleifend. Sed et sem dictum, venenatis odio non, congue ex.
""".strip().split()


def message():
    return ' '.join(random.choices(WORDS, k=16))


def logger():
    return '.'.join(random.choices(SIMPLE_WORDS, k=8))


def some(size):
    return ''.join(random.choice(string.hexdigits) for _ in range(size))


def logging_event(total):
    levels = ['ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE']
    levels_weights = (2, 1, 10, 30, 5,)
    event_time = (datetime.now() - timedelta(days=196)).timestamp()
    time_delta = timedelta(days=365).total_seconds() / total
    for i in range(total):
        event_time += time_delta
        level, = random.choices(levels, levels_weights)
        time = round(event_time * 1000)
        msg = message()
        logger1 = logger()
        yield (time, msg, logger1, level, some(16), 1, None, None, None, None, f'{some(32)}.java',
               f'{logger1}.{some(32)}', f'{some(32)}', '23', i)


def logging_event_property(total):
    apps = ['app1', 'app2', 'app3', 'app4', 'app5', 'app6', 'app7', 'app8']
    trace = str(uuid4())
    app = random.choice(apps)
    for i in range(total):
        if random.random() > 0.90:
            app = random.choice(apps)
            trace = str(uuid4())

        yield i, 'appName', app,
        yield i, 'trace-id', trace,
        yield i, 'some', some(64),


def main(total):
    Path("tmp").mkdir(exist_ok=True)
    with gzip.open('tmp/logging_event.csv.gz', 'wt', encoding='utf-8') as f:
        writer = csv.writer(f, dialect=csv.unix_dialect)
        for e in logging_event(total):
            writer.writerow(e)

    with gzip.open('tmp/logging_event_property.csv.gz', 'wt', encoding='utf-8') as f:
        writer = csv.writer(f, dialect=csv.unix_dialect)
        for e in logging_event_property(total):
            writer.writerow(e)


if __name__ == '__main__':
    main(int(sys.argv[0]))
