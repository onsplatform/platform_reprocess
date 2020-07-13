debug: export FLASK_ENV=development
debug | run | celery: export CELERY_BROKER=pyamqp://guest@localhost
debug:
	@flask run --port 8099
celery:
	@celery -A reprocess.discovery:app worker --loglevel=info
run:
	@gunicorn wsgi:reprocess_api --bind 0.0.0.0:8099 --log-level debug --log-file - --timeout 30000