import os

SCHEMA = {
    'uri': os.environ.get('SCHEMA_URI', 'http://localhost:8002/api/v1/entitymap/'),
}

PROCESS_MEMORY = {
    'api_url': os.environ.get('PROCESS_MEMORY_URI', 'http://localhost:8009/'),
}

DOMAIN_READER = {
    'api_url': os.environ.get('DOMAIN_READER_URI', 'http://localhost:9093/reader/api/v1/'),
}

REPROCESS_SETTINGS = {
    'host': 'localhost'
}
