import logging

from flask import Flask
from datetime import date
from flask.json import JSONEncoder

from reprocess.settings import *
from reprocess.discovery_api import construct_blueprint


def create_app(test_config=None):
    """
    Application Factory. Register new modules below.
    :param test_config:
    :return:
    """

    class CustomJSONEncoder(JSONEncoder):
        def default(self, obj):
            try:
                if isinstance(obj, date):
                    return obj.isoformat()
                iterable = iter(obj)
            except TypeError:
                pass
            else:
                return list(iterable)
            return JSONEncoder.default(self, obj)

    app = Flask(__name__, instance_relative_config=True)
    app.config["JSON_SORT_KEYS"] = False
    app.json_encoder = CustomJSONEncoder
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

    @app.route('/')
    def hello():
        return 'Hello, World! The application is running.'

    app.register_blueprint(construct_blueprint())

    return app
