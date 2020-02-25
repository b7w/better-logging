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
echo "COPY logging_event FROM '/data/logging_event.csv' CSV;" | psql {{ PG_URL }}
echo "COPY logging_event_property FROM '/data/logging_event_property.csv' CSV;" | psql {{ PG_URL }}
```


About
-----

Better Logging is open source project, released by MIT license.


Look, feel, be happy :-)
