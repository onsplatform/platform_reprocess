import json
from datetime import datetime
from flask import current_app as current_app
from flask import Blueprint, request, make_response
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
            current_app.logger.debug(f'checking reprocess to instance: {instance_id} app: {app} solution: {solution}')
            current_app.logger.debug(f'getting entities from pm')
            process_memory_entities = process_memory_api.get_entities(instance_id)
            current_app.logger.debug(f'getting entities to reprocess')
            entities_to_reprocess = EntitiesToReprocess.get_entities_to_reprocess(process_memory_entities)
            current_app.logger.debug(f'getting pm to reprocess')
            process_memories_to_reprocess = get_process_memories_to_reprocess(app, entities_to_reprocess)
            queue_process_memories_to_reprocess(app, instance_id, process_memories_to_reprocess, solution)
        return make_response('', 200)

    @discovery_blueprint.route('/force_reprocess', methods=['POST'])
    def force_reprocess():
        app = request.json['app']
        solution = request.json['solution']
        process_id = request.json['process_id']
        date_begin_validity = request.json['date_begin_validity']
        date_end_validity = request.json['date_end_validity']
        current_app.logger.debug(
            f'force reprocess to: {solution} app: {app} process_id: {process_id} dates: {date_begin_validity} - {date_end_validity}')
        instances_to_reprocess = process_memory_api.get_events_between_dates(process_id, date_begin_validity,
                                                                             date_end_validity)
        current_app.logger.debug(f'instances found: {instances_to_reprocess}')
        if solution and app and instances_to_reprocess:
            queue_process_memories_to_reprocess(app, None, instances_to_reprocess, solution)
        return make_response('', 200)

    def queue_process_memories_to_reprocess(app, instance_id, process_memories_to_reprocess, solution):
        if process_memories_to_reprocess:
            reprocess_queue = ReprocessQueue('reprocess_queue', solution, REPROCESS_SETTINGS)
            for process_memory_to_reprocess in [pm for pm in process_memories_to_reprocess if pm != instance_id]:
                current_app.logger.debug(f'reprocessing: ' + json.dumps(process_memory_to_reprocess))
                event = process_memory_api.get_event(process_memory_to_reprocess)
                event['scope'] = 'reprocessing'
                event['reprocessing'] = {
                    'instance_id': instance_id,
                    'from': instance_id
                }
                reprocess_queue.enqueue(process_memory_to_reprocess, {
                    'solution': solution,
                    'app': app,
                    'event': event,
                })

    def get_process_memories_to_reprocess(app, entities):
        if entities:
            current_app.logger.debug(entities)
            current_app.logger.debug(f'getting process memories that used those entities')
            to_reprocess = process_memory_api.get_using_entities(_get_using_entities_body(entities))
            if not to_reprocess: to_reprocess = list()
            current_app.logger.debug(f'process memories to reprocess: {to_reprocess}')

            current_app.logger.debug(f'getting process memories that used those entities types')
            process_memories_with_entities_type = process_memory_api.get_with_entities_type(
                _get_with_entities_type(entities))
            current_app.logger.debug(
                f'process memories could reprocess before filter check: {process_memories_with_entities_type}')

            if process_memories_with_entities_type:
                for process_memory in process_memories_with_entities_type:
                    if process_memory not in to_reprocess:
                        maps = process_memory_api.get_maps(process_memory)
                        for entity in entities:
                            entity_map = maps[entity['__type__']]
                            current_app.logger.debug(f"testing domain reader with {entity['__type__']}")
                            if entity_map and would_instance_use_entity(app, entity_map, entity, process_memory):
                                to_reprocess.append(process_memory)

            return to_reprocess

    def would_instance_use_entity(app, map, entity, process_memory):
        founds_entities = []
        params = get_query_string(process_memory)
        current_app.logger.debug(f'payload {params}')
        for filter_name in map['filters'].keys():
            current_app.logger.debug(f'executing filter {filter_name}')
            entities = domain_reader.get_map_entities(app, entity['__type__'], filter_name, params)
            if entities:
                current_app.logger.debug(f'founds entities: {len(entities)}from filter {filter_name}')
                founds_entities.append(entities)
        current_app.logger.debug(f'founds entities: {founds_entities}')
        entity_is_equal = {e for e in founds_entities if compare_entity(e, entity)}
        return entity_is_equal

    def compare_entity(entity_from, entity_to):
        entity_from.pop('_metadata')
        entity_to.pop('_metadata')
        return entity_from == entity_to

    def get_query_string(process_memory):
        return process_memory_api.get_payload(process_memory)

    # To refactor (dry)
    def _get_using_entities_body(entities):
        ret = GetWithEntitiesType()
        [ret.add(
            id=entity['id'],
            timestamp=entity['_metadata']['modified_at']
            if 'modified_at' in entity['_metadata'].keys()
            else datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')
        ) for entity in entities if 'id' in entity.keys() and entity['id']]
        return ret

    # To refactor (dry)
    def _get_with_entities_type(entities):
        ret = GetWithEntitiesType()
        [ret.add(
            type=entity['__type__'],
            timestamp=entity['_metadata']['modified_at']
            if 'modified_at' in entity['_metadata'].keys()
            else datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')
        ) for entity in entities]
        return ret

    return discovery_blueprint
