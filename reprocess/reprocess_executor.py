import json
from settings import *
from reprocess_queue import ReprocessQueue
from platform_sdk.domain.schema.api import SchemaApi
from platform_sdk.event_manager import EventManager


class ReprocessExecutor:

    def __init__(self, schema, event_manager, solution, reprocess_settings):
        self.solution = solution
        self.reprocess_settings = reprocess_settings
        self.schema = schema
        self.event_manager = event_manager
        self.reprocess_check = ReprocessQueue('reprocess_queue', solution, reprocess_settings)
        self.reprocess_exec = ReprocessQueue('reprocess_queue', solution, reprocess_settings)

    def reprocess2(self):
        method_frame, header_frame, body = self.reprocess_check.check_next_message()
        if body:
            print(" [ ] Can it reprocess? %r" % body)
            event = json.loads(body)
            solution = self.schema.get_solution_by_name(event['solution'])
            if not self.schema.is_reprocessing(solution['id']):
                self.reprocess_check.close()
                method_frame, header_frame, body = self.reprocess_exec.dequeue()
                event = json.loads(body)
                self.event_manager.send_event(event['event'])
                print(" [x] Reprocessing %r" % event)
        else:
            print('Nothing to do...')
    
    def reprocess(self):
        events = self.get_all_messages_without_dequeue()
        self.reprocess_check = ReprocessQueue('reprocess_queue', self.solution, self.reprocess_settings)

        if events:
            event =  events[0]
            solution = self.schema.get_solution_by_name(event['solution'])

            if not self.schema.is_reprocessing(solution['id']):
                self.reprocess_exec.dequeue()
                if not self.message_is_repeated(events, event):
                    self.event_manager.send_event(event['event'])
                    print(" [x] Reprocessing %r" % event)
                else:
                    print(" [x] Discarded - Repeated message in queue: %r" % event)
                    print(" Getting next message..")
                    self.reprocess()
            else:
                print(f' Solution is already being reprocessed, retry will occur soon...')
        else:
            print('Nothing to do...')

    def message_is_repeated(self, messages, message):
        # Verificar se é necessário incluir a tag da process_memory na verificacao
        count_equal = 0
        for messages_item in messages:
            if messages_item['event']['name'] == message['event']['name']\
            and messages_item['event']['header']['referenceDate'] == message['event']['header']['referenceDate'] \
            and messages_item['event']['payload'] == message['event']['payload']\
            and messages_item['event']['header']['image'] == message['event']['header']['image']:
                count_equal = count_equal + 1
                if count_equal > 1:
                    return True

    def get_all_messages_without_dequeue(self):
        messages = list()   
        while True : 
            method_frame, header_frame, body = self.reprocess_check.check_next_message()
            if body:
                event = json.loads(body)
                messages.append(event)
            else :
                break
        self.reprocess_check.close()
        return messages



schema = SchemaApi(SCHEMA)
event_manager = EventManager(EVENT_MANAGER)
print(f'Checkin Reprocessable solutions...')
solutions = schema.get_reprocessable_solutions()
print(f'Reprocessable solutions: {solutions}')
for solution in schema.get_reprocessable_solutions():
    print(f'Checking reprocess to: {solution}')
    executor = ReprocessExecutor(schema, event_manager, solution['name'], REPROCESS_SETTINGS)
    executor.reprocess()
