from flask import Blueprint, request

from reprocess.settings import REPROCESS_SETTINGS
from reprocess.reprocess_queue import ReprocessQueue
from platform_sdk.process_memory import GetWithEntitiesType
from reprocess.entities_to_reprocess import EntitiesToReprocess


def construct_blueprint(process_memory_api, domain_reader):
    discovery_blueprint = Blueprint('discovery', __name__, url_prefix='/discovery')

    @discovery_blueprint.route('/check', methods=['POST'])
    def check():
        solution = request.json['solution']
        app = request.json['app']
        instance_id = request.json['instance_id']
        if instance_id:
            reprocess_queue = ReprocessQueue('reprocess_queue', solution, REPROCESS_SETTINGS)
            process_memory_entities = process_memory_api.get_entities(instance_id)
            entities_to_reprocess = EntitiesToReprocess.get_entities_to_reprocess(process_memory_entities)
            process_memories_to_reprocess = get_process_memories_to_reprocess(app, entities_to_reprocess)
            for process_memory_to_reprocess in [pm for pm in process_memories_to_reprocess if pm != instance_id]:
                event = process_memory_api.get_event(process_memory_to_reprocess)
                event['reprocessing'] = {
                    'instance_id': instance_id
                }
                reprocess_queue.enqueue(process_memory_to_reprocess, {
                    'solution': solution,
                    'app': app,
                    'event': event,
                })

    def get_process_memories_to_reprocess(app, entities):
        if entities:
            '''Process memories that used entity'''
            to_reprocess = process_memory_api.get_using_entities(_get_using_entities_body(entities))

            '''Process memories that would use the entities'''
            process_memories_with_entities_type = process_memory_api.get_with_entities_type(
                _get_with_entities_type(entities))

            for process_memory in process_memories_with_entities_type:
                if process_memory not in to_reprocess:
                    maps = process_memory_api.get_maps(process_memory)
                    for entity in entities:
                        entity_map = maps[entity['__type__']]
                        if entity_map and process_memory_should_use(app, entity_map, entity, process_memory):
                            to_reprocess.append(process_memory)

            return to_reprocess

    def process_memory_should_use(app, map, entity, process_memory):
        persisted_entities = []
        params = get_query_string(process_memory)
        for filter_name in map['filters'].keys():
            entities = domain_reader.get_map_entities(app, entity['__type__'], filter_name, params)
            if entities:
                persisted_entities.append(entities)
        return (e for e in persisted_entities if e['id'] == entity['id']) or (e for e in persisted_entities if
                                                                              e.pop('_metadata') == entity.pop(
                                                                                  '_metadata'))

    def get_query_string(process_memory):
        return process_memory_api.get_payload(process_memory)

    def _get_using_entities_body(entities):
        ret = GetWithEntitiesType()
        [ret.add(id=entity['id'], timestamp=entity['_metadata']['modified_at']) for entity in entities if entity['id']]
        return ret

    def _get_with_entities_type(entities):
        ret = GetWithEntitiesType()
        [ret.add(type=entity['__type__'], timestamp=entity['_metadata']['modified_at']) for entity in entities]
        return ret

    return discovery_blueprint
