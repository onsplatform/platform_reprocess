import unittest

from .mock.process_memory import ProcessMemoryApi
from reprocess.entities_to_reprocess import EntitiesToReprocess


class ReprocessableEntitiesTest(unittest.TestCase):
    def test_get_reprocessable_entities(self):
        # arrange
        entities = ProcessMemoryApi.get_entities(1)

        # action
        entities_to_reprocess = EntitiesToReprocess().get_entities_to_reprocess(entities)

        # assert
        assert len(entities_to_reprocess) == 3
