#!/usr/bin/env bash

# Setup a cron schedule
echo "* * * * * /var/cron/reprocess/deploy/reprocess.sh >> /var/cron/reprocess/log/reprocess_cron.log 2>&1
# This extra line makes it a valid cron" > scheduler.txt