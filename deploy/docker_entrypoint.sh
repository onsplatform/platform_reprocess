#!/usr/bin/env bash

service nginx start

gunicorn wsgi:reprocess_api --name ReprocessAPI --workers 3 --bind=unix:/var/www/reprocess/gunicorn.sock --log-level=debug --log-file=- --timeout $GUNICORN_TIMEOUT
