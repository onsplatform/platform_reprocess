#!/usr/bin/env bash
timestamp=`date +%Y/%m/%d-%H:%M:%S`
echo "System path is $PATH at $timestamp"

python -V
python3 -V

export SCHEMA_URI=http://schema/api/v1/
export EVENT_MANAGER_URI=http://event_manager:8081/
export RABBIT_MQ=rabbitmq

env

cd /var/cron/reprocess

/usr/local/bin/pipenv run python reprocess/reprocess_executor.py

