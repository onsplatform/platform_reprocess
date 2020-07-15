import os

SCHEMA = {
    'uri': os.environ.get('SCHEMA_URI', 'http://localhost:9092/api/v1/'),
}

CORE_API = {
    'uri': os.environ.get('COREAPI_URL', 'http://localhost'),
    'port': os.environ.get('COREAPI_PORT', '9110'),
}

PROCESS_MEMORY = {
    'api_url': os.environ.get('PROCESS_MEMORY_URI', 'http://localhost:9091/'),
}

EVENT_MANAGER = {
    'api_url': os.environ.get('EVENT_MANAGER_URI', 'http://localhost:8081/'),
}

DOMAIN_READER = {
    'api_url': os.environ.get('DOMAIN_READER_URI', 'http://localhost:9093/reader/api/v1/'),
}

REPROCESS_SETTINGS = {
    'host': os.environ.get('RABBIT_MQ', 'localhost'),
}

CELERY = {
    'broker': os.environ.get('CELERY_BROKER', 'pyamqp://guest@rabbitmq//'),
    'name': 'discovery_worker'
}
