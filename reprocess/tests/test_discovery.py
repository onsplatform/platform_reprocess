import json
import unittest
from flask import Flask

from reprocess.discovery import construct_blueprint
from .mock.process_memory import ProcessMemoryApi
from .mock.domain_reader import DomainReader


class DiscoveryTest(unittest.TestCase):
    _app = Flask(__name__, instance_relative_config=True)
    _app_client = _app.test_client()
    _app.register_blueprint(construct_blueprint(ProcessMemoryApi(), DomainReader()))

    def test_discovery_check_200_status_code_SAAT(self):
        # arrange / action
        response = self._app_client.post('/discovery/check',
                                         data=json.dumps({'solution': 'SAAT', 'app': 'SAAT_TESTE', 'instance_id': 1}),
                                         follow_redirects=True,
                                         mimetype='application/json')

        # assert
        assert 200 == response.default_status

    def test_discovery_check_200_status_code_SAGER(self):
        # arrange / action
        response = self._app_client.post('/discovery/check',
                                         data=json.dumps(
                                             {'solution': 'SAGER', 'app': 'SAGER_TESTE', 'instance_id': 1}),
                                         follow_redirects=True,
                                         mimetype='application/json')

        # assert
        assert 200 == response.default_status
