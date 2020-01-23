import os

SCHEMA = {
    'uri': os.environ.get('SCHEMA_URI', 'http://localhost:8002/api/v1/entitymap/'),
}


PROCESS_MEMORY = {
    'api_url': os.environ.get('PROCESS_MEMORY_URI', 'http://10.24.2.146:9091/'),
}

REPROCESS_SETTINGS = {
    'host': 'localhost'
}