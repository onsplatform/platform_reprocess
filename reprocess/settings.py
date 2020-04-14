import os

SCHEMA = {
    'uri': os.environ.get('SCHEMA_URI', 'http://localhost:9092/api/v1/'),
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
