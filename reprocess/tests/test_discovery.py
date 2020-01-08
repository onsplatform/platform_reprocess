import pytest
import unittest
from flask import Flask

from reprocess.discovery import construct_blueprint
from .mock.process_memory import ProcessMemoryApi


class DiscoveryTest(unittest.TestCase):

    _app = Flask(__name__, instance_relative_config=True)
    _app_client = _app.test_client()
    _app.register_blueprint(construct_blueprint(ProcessMemoryApi()))

    def test_discovery_check_200_status_code(self):
        # arrange / action
        response = self._app_client.post('/discovery/check', data = { 'instance_id': 1 })

        # assert
        assert 200 == response.default_status