Better Logging
==============

[![License: MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://drone.b7w.me/api/badges/b7w/better-logging/status.svg)](https://drone.b7w.me/b7w/better-logging)
[![Wheel Support](https://img.shields.io/pypi/wheel/better-logging)](https://pypi.org/project/better-logging/)
[![Wheel Support](https://img.shields.io/pypi/pyversions/better-logging)](https://pypi.org/project/better-logging/)


Simple UI for Logback Postgres DBAppender



Generate test events
--------------------

```sh
cd _etc

python generate-events.py 100000
docker-compose up -d;

echo "COPY logging_event FROM PROGRAM 'zcat /data/logging_event.csv.gz' CSV;" | psql "postgres://root:root@127.0.0.1:5432/root"
echo "COPY logging_event_property FROM PROGRAM 'zcat /data/logging_event_property.csv.gz' CSV;" | psql "postgres://root:root@127.0.0.1:5432/root"
```


Run Backend
-----------

```sh
cd backend

pip3 install poetry
poetry install

export CONFIG_PATH=../_etc/sample-config.py
poetry run python src/better_logging/main.py
```


Run Frontend
-----------

```sh
cd frontend

npm install
npm run serve
```


About
-----

Better Logging is open source project, released by MIT license.


Look, feel, be happy :-)
