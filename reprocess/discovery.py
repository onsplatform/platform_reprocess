from flask import Blueprint, request

from .entities_to_reprocess import EntitiesToReprocess


def construct_blueprint(process_memory_api, domain_reader, event_manager):
    discovery_blueprint = Blueprint('discovery', __name__, url_prefix='/discovery')

    @discovery_blueprint.route('/check', methods=['POST'])
    def check():
        app = request.json['app']
        instance_id = request.json['instance_id']
        if instance_id:
            process_memory_entities = process_memory_api.get_entities(instance_id)
            entities_to_reprocess = EntitiesToReprocess.get_entities_to_reprocess(process_memory_entities)
            process_memories_to_reprocess = get_process_memories_to_reprocess(app, entities_to_reprocess)
            process_memories_to_reprocess.remove(instance_id)
            for process_memory in process_memories_to_reprocess:
                event = process_memory['event']
                event_manager.emit_event(event)

    def get_process_memories_to_reprocess(app, entities):
        reprocess_after = entities[0]['_metadata']['modified_at']
        '''Process memories that used entity'''
        to_reprocess = process_memory_api.get_using_entities(entities, reprocess_after)

        '''Process memories that would use the entities'''
        process_memories_with_entities_type = \
            process_memory_api.get_with_entities_type(entities, reprocess_after)

        for entity in entities:
            for process_memory in process_memories_with_entities_type:
                if process_memory not in to_reprocess:
                    maps = process_memory_api.get_maps(process_memory)
                    if process_memory_should_use(app, maps[entity['__type__']], entity, process_memory):
                        to_reprocess.append(process_memory)

        return to_reprocess

    def process_memory_should_use(app, map, entity, process_memory):
        params = get_query_string(process_memory)
        persisted_entities = domain_reader.execute_query(app, map, params)
        return (e for e in persisted_entities if e['id'] == entity['id']) or (e for e in persisted_entities if
                                                                              e.pop('_metadata') == entity.pop('_metadata'))

    def get_query_string(process_memory):
        return process_memory_api.get_payload(process_memory)


    return discovery_blueprint
