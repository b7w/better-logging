Better Logging
==============

[![License: MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://drone.b7w.me/api/badges/b7w/better-logging/status.svg)](https://drone.b7w.me/b7w/better-logging)


Simple UI for Logback Postgres DBAppender



Generate test events
--------------------

```sh
cd _etc
python generate-events.py
docker-compose up -d;
date;
echo "COPY logging_event FROM PROGRAM 'zcat /data/logging_event.csv.gz' CSV;" | psql "postgres://root:root@127.0.0.1:5432/root"
echo "COPY logging_event_property FROM PROGRAM 'zcat /data/logging_event_property.csv.gz' CSV;" | psql "postgres://root:root@127.0.0.1:5432/root"
date;
```


About
-----

Better Logging is open source project, released by MIT license.


Look, feel, be happy :-)
