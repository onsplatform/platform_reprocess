#!/usr/bin/env bash

# Setup a cron schedule
echo "* * * * * /reprocess.sh >> /var/log/reprocess_cron.log 2>&1
# This extra line makes it a valid cron" > scheduler.txt

crontab scheduler.txt
cron -f