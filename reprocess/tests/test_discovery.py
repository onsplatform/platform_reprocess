import json
import unittest

from flask import Flask

from reprocess.settings import *
from reprocess.discovery import construct_blueprint
from platform_sdk.domain.reader import DomainReaderApi
from platform_sdk.process_memory import ProcessMemoryApi
from platform_sdk.domain.schema.api import SchemaApi


class DiscoveryTest(unittest.TestCase):
    _app = Flask(__name__, instance_relative_config=True)
    _app_client = _app.test_client()
    _app.register_blueprint(construct_blueprint(ProcessMemoryApi(PROCESS_MEMORY), DomainReaderApi(DOMAIN_READER), SchemaApi(SCHEMA)))

    def test_discovery_check_200_status_code_SAAT(self):
        # arrange / action
        response = self._app_client.post('/discovery/check',
                                         data=json.dumps(
                                             {
                                                 'solution': 'sager',
                                                 'app': 'ONS.SAGER.Calculo.Taxa.Teip.Mensal',
                                                 'instance_id': 'a22d9e4d-c352-4ac2-8321-2c496fe3a116'
                                             }),
                                         follow_redirects=True,
                                         mimetype='application/json')

        # assert
        assert 200 == response.default_status
