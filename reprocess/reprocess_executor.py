import json
from settings import *
from reprocess_queue import ReprocessQueue
from platform_sdk.domain.schema.api import SchemaApi
from platform_sdk.event_manager import EventManager


class ReprocessExecutor:

    def __init__(self, schema, event_manager, solution, reprocess_settings):
        self.schema = schema
        self.event_manager = event_manager
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
                event = json.loads(body)
                self.event_manager.send_event(event['event'])
                #self.schema.set_reprocessing(event['solution'])
                print(" [x] Reprocessing %r" % event)
        else:
            print('Nothing to do...')



schema = SchemaApi(SCHEMA)
event_manager = EventManager(EVENT_MANAGER)
for solution in schema.get_reprocessable_solutions():
    executor = ReprocessExecutor(schema, event_manager, solution['name'], REPROCESS_SETTINGS)
    executor.reprocess()
