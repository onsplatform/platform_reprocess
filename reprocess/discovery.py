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
            current_app.logger.debug(entities_to_reprocess)
            current_app.logger.debug(f'getting pm to reprocess')
            process_memories_to_reprocess = get_process_memories_to_reprocess(instance_id, entities_to_reprocess)
            process_memories_to_reprocess = order_by_reference_date_and_remove_loop(process_memories_to_reprocess, instance_id)
            
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
            queue_process_memories_to_reprocess("deploy", instances_to_reprocess, solution)

        return make_response('', 200)

    def order_by_reference_date_and_remove_loop(process_memories_ids, instance_id):
        # TODO: Melhorar performance
        active_event = process_memory_api.get_event(instance_id)
        if process_memories_ids:
            pms = list()
            for pm_id in process_memories_ids:
                event = process_memory_api.get_event(pm_id)
                if not (event['name'] == active_event['name']\
                    and event['header']['referenceDate'] == active_event['header']['referenceDate'] \
                    and event['payload'] == active_event['payload']\
                    and event['header']['image'] == active_event['header']['image']):
                    pms.append(event)
            pms_sorted = sorted(pms, key=lambda k: k['referenceDate']) 
            return [item['header']['instanceId'] for item in pms_sorted]
        return process_memories_ids

    def queue_process_memories_to_reprocess(instance_id, process_memories_to_reprocess, solution):
        if process_memories_to_reprocess:
            reprocess_queue = ReprocessQueue('reprocess_queue', solution, REPROCESS_SETTINGS)
            for process_memory_to_reprocess in [pm for pm in process_memories_to_reprocess if pm != instance_id]:
                current_app.logger.debug(f'reprocessing: ' + json.dumps(process_memory_to_reprocess))
                event = process_memory_api.get_event(process_memory_to_reprocess)

                originalInstanceId = event['reprocessing'].get('originalInstanceId')
                if not originalInstanceId:
                    originalInstanceId = event['instanceId']

                event['scope'] = 'reprocessing'
                event['reprocessing'] = {
                    'instance_id': instance_id,
                    'originalInstanceId': originalInstanceId,
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

            current_app.logger.debug(f'getting process memories that used those entities')

            to_reprocess = process_memory_api.get_using_entities(
                {'entities': [entity['id'] for entity in entities],
                 'tables_grouped_by_tags': reprocessable_tables_grouped_by_tags})

            if not to_reprocess: to_reprocess = list()

            current_app.logger.debug(f'process memories to reprocess: {to_reprocess}')
            current_app.logger.debug(f'getting process memories that used those entities types')
            
            # encontrar instâncias de processo das seguintes tags que fizeram queries nas tabelas informadas para aquela tag (entidades reprocessáveis)
            process_memories_could_reprocess = process_memory_api.get_by_tags(reprocessable_tables_grouped_by_tags)

            if process_memories_could_reprocess:
                process_memories_could_reprocess = [item for item in process_memories_could_reprocess if item['id'] != instance_id]

            current_app.logger.debug(
                f'process memories could reprocess before filter check: {process_memories_could_reprocess}')
            
            if process_memories_could_reprocess:
                memories_will_have_filters_tested = dict()
                for process_memory in process_memories_could_reprocess:
                    if process_memory['id'] not in to_reprocess:
                        memories_will_have_filters_tested.update({process_memory['id']: set()})

                        # TODO: verificar se funciona essa lógica (melhor performance)
                        # memories_will_have_filters_tested[process_memory['id']].update((entity for entity in entities if entity['_metadata']['table'] in reprocessable_tables_grouped_by_tags[process_memory['tag']]))
                        # { '4a716eb8-12f9-409b-9732-549585090f61': { 'unidadegeradora': 'e_unidadegeradora' }}
                        for entity in entities:
                            if entity['_metadata']['table'] in reprocessable_tables_grouped_by_tags[process_memory['tag']]: 

                                 # entities_in_process_memory = {  'unidadegeradora': 'e_unidadegeradora', 'usina': 'e_usi' }}
                                entities_in_process_memory = memories_will_have_filters_tested[process_memory['id']] 

                                 # entities_in_process_memory = {  'unidadegeradora': 'e_unidadegeradora', 'usina': 'e_usi', 'calculo': 'e-calculo' }}
                                entities_in_process_memory.add(entity['_metadata']['type'])  

                                memories_will_have_filters_tested.update({process_memory['id']: entities_in_process_memory})
                
                # Somente memórias que possuirem entidades/tabelas reprocessáveis serão válidas para reprocessamento
                memories_will_have_filters_tested = {k: list(v) for k, v in memories_will_have_filters_tested.items() if len(v) > 0}        
                
                if len(memories_will_have_filters_tested) > 0:
                    # parametros { instancia: entidade: tabela }
                    # exemplo de parametros { '4a716eb8-12f9-409b-9732-549585090f61': { 'unidadegeradora', 'evento' }, .... }
                    instances_filters = process_memory_api.get_instance_filters_by_instance_ids_and_types(memories_will_have_filters_tested)
                    instances_ids_would_use_reprocessable_entity = would_instances_use_entities(entities, instances_filters)
                    if instances_ids_would_use_reprocessable_entity:
                        to_reprocess.extend(instances_ids_would_use_reprocessable_entity)
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

    def would_instances_use_entities(entities, instance_filters):
        for filter in instance_filters:
            filter['params']['branch'] = filter['branch']

        instances_filters_treated = [   
            {
                'instance_id': filter['header']['instanceId'],
                'app': filter['app'], 
                'version': filter['header']['version'], 
                'type': filter['type'], 
                'filter_name': filter['filter_name'], 
                'params': filter['params']
            } for filter in instance_filters]

        instancesIds = domain_reader.instances_which_queries_would_find_any_touched_entity(entities, instances_filters_treated)
        # Exemplo de retorno esperado: ['4a716eb8-12f9-409b-9732-549585090f61', '4a716eb8-12f9-409b-9732-549585090f62']


        return instancesIds

    def entities_have_same_id(entity_from, entity_to):
        return entity_from['id'] == entity_to['id']

    return discovery_blueprint
