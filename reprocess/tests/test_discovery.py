import json
import pytest
import unittest
from flask import Flask

from reprocess.discovery import construct_blueprint
from .mock.process_memory import ProcessMemoryApi
from .mock.domain_reader import DomainReader
from .mock.event_manager import EventManager


class DiscoveryTest(unittest.TestCase):
    _app = Flask(__name__, instance_relative_config=True)
    _app_client = _app.test_client()
    _app.register_blueprint(construct_blueprint(ProcessMemoryApi(), DomainReader(), EventManager()))

    def test_discovery_check_200_status_code(self):
        # arrange / action
        response = self._app_client.post('/discovery/check',
                                         data=json.dumps({'solution': 'SAGER', 'app': 'SAGER_TESTE', 'instance_id': 1}),
                                         follow_redirects=True,
                                         mimetype='application/json')

        # assert
        assert 200 == response.default_status
