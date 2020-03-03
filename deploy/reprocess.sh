#!/bin/bash
timestamp=`date +%Y/%m/%d-%H:%M:%S`
echo "System path is $PATH at $timestamp"

python -V
python3 -V

cd /var/cron/reprocess

/usr/local/bin/pipenv run python reprocess/reprocess_executor.py