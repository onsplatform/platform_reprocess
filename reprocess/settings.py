import os

SCHEMA = {
    'uri': os.environ.get('SCHEMA_URI', 'http://schema:9092/api/v1/'),
}

PROCESS_MEMORY = {
    'api_url': os.environ.get('PROCESS_MEMORY_URI', 'http://process_memory:9091/'),
}

EVENT_MANAGER = {
    'api_url': os.environ.get('EVENT_MANAGER_URI', 'http://event_manager:8081/'),
}

DOMAIN_READER = {
    'api_url': os.environ.get('DOMAIN_READER_URI', 'http://domain_reader:9093/reader/api/v1/'),
}

REPROCESS_SETTINGS = {
    'host': os.environ.get('RABBIT_MQ', 'rabbitmq'),
}
