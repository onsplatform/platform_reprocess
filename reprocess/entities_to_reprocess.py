class EntitiesToReprocess():

    @staticmethod
    def get_entities_to_reprocess(entities):
        entities_to_reprocess = []
        for key in entities.keys():
            for entity in entities[key]:
                if EntitiesToReprocess._need_to_reprocess(entity):
                    entity['__type__'] = key
                    entities_to_reprocess.append(entity)

        return entities_to_reprocess

    @staticmethod
    def _need_to_reprocess(entity):
        metadata = entity['_metadata']
        return ('changeTrack' in metadata and
                'reprocessable' in metadata and
                metadata['reprocessable'] and
                metadata['changeTrack'] in ['create', 'destroy', 'update'])
