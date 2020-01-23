import json

from reprocess.settings import REPROCESS_SETTINGS
from platform_sdk.domain.schema.api import SchemaApi
from reprocess.reprocess_queue import ReprocessQueue


class ReprocessExecutor:

    def __init__(self, schema, solution, reprocess_settings):
        self.schema = schema
        self.reprocess_check = ReprocessQueue('reprocess_queue', solution, reprocess_settings)
        self.reprocess_exec = ReprocessQueue('reprocess_queue', solution, reprocess_settings)

    def reprocess(self):
        method_frame, header_frame, body = self.reprocess_check.check_next_message()
        if body:
            print(" [ ] Can it reprocess? %r" % body)
            event = json.loads(body)
            if not self.schema.is_reprocessing(event['solution']):
                self.reprocess_check.close()
                method_frame, header_frame, body = self.reprocess_exec.dequeue()
                print(" [x] Reprocessing %r" % body)
                return False


if __name__ == '__main__':
    schema = SchemaApi({'uri': ''})
    for solution in schema.get_reprocessable_solutions():
        executor = ReprocessExecutor(schema, solution, REPROCESS_SETTINGS)
        executor.reprocess()

