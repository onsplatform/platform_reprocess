import json
import logging

from celery import Celery

from reprocess.settings import *
from reprocess.reprocess_queue import ReprocessQueue
from reprocess.entities_to_reprocess import EntitiesToReprocess

from platform_sdk.domain.reader import DomainReaderApi
from platform_sdk.process_memory import ProcessMemoryApi
from platform_sdk.domain.schema.api import SchemaApi
from platform_sdk.core_api import core_metadata

app = Celery(CELERY['name'], broker=CELERY['broker'])
app.conf.task_default_queue = 'reprocess_discovery'

domain_schema = SchemaApi(SCHEMA)
domain_reader = DomainReaderApi(DOMAIN_READER)
process_memory_api = ProcessMemoryApi(PROCESS_MEMORY)
core_metadata_api = core_metadata.Metadata(CORE_API['uri'])

logger = logging.getLogger('check.tasks')


@app.task
def check(solution, instance_id):
    if instance_id:
        logger.warning(f'checking reprocess to instance: {instance_id} solution: {solution}')
        logger.info(f'getting entities from pm')
        process_memory_entities = process_memory_api.get_entities(instance_id)
        logger.info(f'getting entities to reprocess')
        entities_to_reprocess = EntitiesToReprocess.get_entities_to_reprocess(process_memory_entities)
        logger.info(entities_to_reprocess)
        logger.info(f'getting pm to reprocess')
        process_memories_to_reprocess = get_process_memories_to_reprocess(instance_id, entities_to_reprocess)
        process_memories_to_reprocess = order_by_reference_date_and_remove_loop(process_memories_to_reprocess,
                                                                                instance_id)

        queue_process_memories_to_reprocess(instance_id, process_memories_to_reprocess, solution)

@app.task
def force_reprocess(application, solution, process_id, date_begin_validity, date_end_validity):
    sorted_operations = sorted(core_metadata_api.find_by_process_id(process_id).content, key=lambda k: k['_metadata']['modified_at'],
                               reverse=True)

    current_operations = {}
    for operation in sorted_operations:
        if operation['name'] not in current_operations:
            current_operations[operation['name']] = operation

    reprocessable_operation = []
    for operation_name in current_operations.keys():
        if current_operations[operation_name]['reprocessable']:
            reprocessable_operation.append(current_operations[operation_name]['name'])

    if not reprocessable_operation:
        return

    logger.warning(
        f'force reprocess to: {solution} app: {application} process_id: {process_id} dates: {date_begin_validity} - {date_end_validity}')
    import pdb; pdb.set_trace()
    instances_to_reprocess = [pm['id'] for pm in
                              process_memory_api.get_current_events_between_dates(process_id, date_begin_validity,
                                                                                  date_end_validity) if
                              pm['event'] in reprocessable_operation]

    logger.info(f'instances found: {instances_to_reprocess}')
    if solution and application and instances_to_reprocess:
        queue_process_memories_to_reprocess("deploy", instances_to_reprocess, solution)


def order_by_reference_date_and_remove_loop(process_memories_ids, instance_id):
    # TODO: Melhorar performance
    active_event = process_memory_api.get_event(instance_id)
    if process_memories_ids:
        pms = list()
        for pm_id in process_memories_ids:
            event = process_memory_api.get_event(pm_id)
            if not (event['name'] == active_event['name']
                    and event['header']['referenceDate'] == active_event['header']['referenceDate']
                    and event['payload'] == active_event['payload']
                    and event['header']['image'] == active_event['header']['image']):
                pms.append(event)
        pms_sorted = sorted(pms, key=lambda k: k['referenceDate'])
        return [item['header']['instanceId'] for item in pms_sorted]
    return process_memories_ids

def queue_process_memories_to_reprocess(instance_id, process_memories_to_reprocess, solution):
    if process_memories_to_reprocess:
        reprocess_queue = ReprocessQueue('reprocess_queue', solution, REPROCESS_SETTINGS)
        for process_memory_to_reprocess in [pm for pm in process_memories_to_reprocess if pm != instance_id]:
            logger.info(f'reprocessing: ' + json.dumps(process_memory_to_reprocess))
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
            {'types': [entity['_metadata']['type'] for entity in entities],
             "tag": f"{active_event['header']['image']}"})

        logger.info(f'getting process memories that used those entities')

        to_reprocess = process_memory_api.get_using_entities(
            {'entities': [entity['id'] for entity in entities],
             'tables_grouped_by_tags': reprocessable_tables_grouped_by_tags})

        if not to_reprocess: to_reprocess = list()

        logger.info(f'process memories to reprocess: {to_reprocess}')
        logger.info(f'getting process memories that used those entities types')

        # encontrar instâncias de processo das seguintes tags que fizeram queries nas tabelas informadas para aquela tag (entidades reprocessáveis)
        process_memories_could_reprocess = process_memory_api.get_by_tags(reprocessable_tables_grouped_by_tags)

        if process_memories_could_reprocess:
            process_memories_could_reprocess = [item for item in process_memories_could_reprocess if
                                                item['id'] != instance_id]

        logger.info(
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
                        if entity['_metadata']['table'] in reprocessable_tables_grouped_by_tags[
                            process_memory['tag']]:
                            # entities_in_process_memory = {  'unidadegeradora': 'e_unidadegeradora', 'usina': 'e_usi' }}
                            entities_in_process_memory = memories_will_have_filters_tested[process_memory['id']]

                            # entities_in_process_memory = {  'unidadegeradora': 'e_unidadegeradora', 'usina': 'e_usi', 'calculo': 'e-calculo' }}
                            entities_in_process_memory.add(entity['_metadata']['type'])

                            memories_will_have_filters_tested.update(
                                {process_memory['id']: entities_in_process_memory})

            # Somente memórias que possuirem entidades/tabelas reprocessáveis serão válidas para reprocessamento
            memories_will_have_filters_tested = {k: list(v) for k, v in memories_will_have_filters_tested.items() if
                                                 len(v) > 0}

            if len(memories_will_have_filters_tested) > 0:
                # parametros { instancia: entidade: tabela }
                # exemplo de parametros { '4a716eb8-12f9-409b-9732-549585090f61': { 'unidadegeradora', 'evento' }, .... }
                instances_filters = process_memory_api.get_instance_filters_by_instance_ids_and_types(
                    memories_will_have_filters_tested)
                instances_ids_would_use_reprocessable_entity = would_instances_use_entities(entities,
                                                                                            instances_filters)
                if instances_ids_would_use_reprocessable_entity:
                    to_reprocess.extend(instances_ids_would_use_reprocessable_entity)
        return to_reprocess

def would_instance_use_entity(entity, instance_filters):
    founds_entities = []
    for filter in instance_filters:
        if entity['__type__'] == filter['type']:
            logger.info(f"executing filter {filter['type']} {filter['filter_name']}")
            filter['params']['branch'] = filter['branch']
            entities = domain_reader.get_map_entities(filter['app'],
                                                      filter['header']['version'],
                                                      filter['type'],
                                                      filter['filter_name'],
                                                      filter['params'])
            if entities:
                logger.info(f"entities: {len(entities)} from filter {filter['filter_name']}")
                [founds_entities.append(e) for e in entities]

    same_entities = [e for e in founds_entities if entities_have_same_id(e, entity.copy())]

    logger.info(f'found equals entity: {same_entities}')
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

    instancesIds = domain_reader.instances_which_queries_would_find_any_touched_entity(entities,
                                                                                       instances_filters_treated)
    # Exemplo de retorno esperado: ['4a716eb8-12f9-409b-9732-549585090f61', '4a716eb8-12f9-409b-9732-549585090f62']

    return instancesIds

def entities_have_same_id(entity_from, entity_to):
    return entity_from['id'] == entity_to['id']
