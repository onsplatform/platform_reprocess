#!/usr/bin/env bash

service nginx start

# Setup a cron schedule
echo "* * * * * /reprocess.sh >> /var/log/reprocess_cron.log 2>&1
# This extra line makes it a valid cron" > scheduler.txt

crontab scheduler.txt
cron -f

gunicorn wsgi:reprocess_api --name ReprocessAPI --workers 3 --bind=unix:/var/www/reprocess/gunicorn.sock --log-level=debug --log-file=- --timeout $GUNICORN_TIMEOUT
