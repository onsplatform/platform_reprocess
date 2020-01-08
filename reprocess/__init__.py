from flask import Flask

from . import settings
from platform_sdk.process_memory import ProcessMemoryApi

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    from . import discovery
    process_memory = ProcessMemoryApi(settings.PROCESS_MEMORY)
    app.register_blueprint(discovery.construct_blueprint(process_memory))

    return app