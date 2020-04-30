import json
from flask import current_app as current_app
from flask import Blueprint, request, make_response
from reprocess.settings import REPROCESS_SETTINGS
from reprocess.reprocess_queue import ReprocessQueue
from reprocess.entities_to_reprocess import EntitiesToReprocess


def construct_blueprint(process_memory_api, domain_reader, domain_schema):
    discovery_blueprint = Blueprint('discovery', __name__, url_prefix='/discovery')

    @discovery_blueprint.route('/check', methods=['POST'])
    def check():
        solution = request.json['solution']
        instance_id = request.json['instance_id']
        if instance_id:
            current_app.logger.debug(f'checking reprocess to instance: {instance_id} solution: {solution}')
            current_app.logger.debug(f'getting entities from pm')
            process_memory_entities = process_memory_api.get_entities(instance_id)
            current_app.logger.debug(f'getting entities to reprocess')
            entities_to_reprocess = EntitiesToReprocess.get_entities_to_reprocess(process_memory_entities)
            current_app.logger.debug(f'getting pm to reprocess')
            process_memories_to_reprocess = get_process_memories_to_reprocess(instance_id, entities_to_reprocess)
            queue_process_memories_to_reprocess(instance_id, process_memories_to_reprocess, solution)
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
            queue_process_memories_to_reprocess(None, instances_to_reprocess, solution)

        return make_response('', 200)

    def queue_process_memories_to_reprocess(instance_id, process_memories_to_reprocess, solution):
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
                    'event': event,
                })

    def get_process_memories_to_reprocess(instance_id, entities):
        if entities:
            active_event = process_memory_api.get_event(instance_id)
            reprocessable_tables_grouped_by_tags = domain_schema.get_reprocessable_tables_grouped_by_tags(
                {'types': [entity['_metadata']['type'] for entity in entities], "tag": f"{active_event['header']['image']}"})

            current_app.logger.debug(f'getting process memories that used those entities count: {len(entities)}')

            to_reprocess = process_memory_api.get_using_entities(
                {'entities': (entity['id'] for entity in entities),
                 'tables_grouped_by_tags': reprocessable_tables_grouped_by_tags})
            if not to_reprocess: to_reprocess = list()

            current_app.logger.debug(f'process memories to reprocess: {to_reprocess}')
            current_app.logger.debug(f'getting process memories that used those entities types')

            process_memories_could_reprocess = process_memory_api.get_by_tags(
                reprocessable_tables_grouped_by_tags)

            current_app.logger.debug(
                f'process memories could reprocess before filter check: {process_memories_could_reprocess}')

            if process_memories_could_reprocess:
                for process_memory in process_memories_could_reprocess:
                    if process_memory['id'] not in to_reprocess:
                        instance_filters = process_memory_api.get_instance_filter(process_memory['id'])
                        for entity in entities:
                            if entity['__table__'] in reprocessable_tables_grouped_by_tags[
                                process_memory['tag']].values():
                                current_app.logger.debug(f"testing domain reader with {entity['__type__']}")
                                if would_instance_use_entity(entity, instance_filters):
                                    to_reprocess.append(process_memory['id'])
            return to_reprocess

    def would_instance_use_entity(entity, instance_filters):
        founds_entities = []
        for filter in instance_filters:
            if entity['__type__'] == filter['type']:
                current_app.logger.debug(f"executing filter {filter['type']} {filter['filter_name']}")
                filter['params']['branch'] = filter['branch']
                entities = domain_reader.get_map_entities(filter['app'],
                                                          filter['header']['version'],
                                                          filter['type'],
                                                          filter['filter_name'],
                                                          filter['params'])
                if entities:
                    current_app.logger.debug(f"entities: {len(entities)} from filter {filter['filter_name']}")
                    [founds_entities.append(e) for e in entities]

        same_entities = [e for e in founds_entities if entities_have_same_id(e, entity.copy())]

        current_app.logger.debug(f'found equals entity: {same_entities}')
        return len(same_entities) > 0

    def entities_have_same_id(entity_from, entity_to):
        return entity_from['id'] == entity_to['id']

    return discovery_blueprint
