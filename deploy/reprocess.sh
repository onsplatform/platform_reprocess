#!/bin/bash
timestamp=`date +%Y/%m/%d-%H:%M:%S`
echo "System path is $PATH at $timestamp"

python -V
python3 -V
pipenv -h

python /var/cron/reprocess/reprocess/reprocess_executor.py