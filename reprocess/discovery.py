from flask import Blueprint, request


def construct_blueprint(process_memory_api):
    discovery_blueprint = Blueprint('discovery', __name__, url_prefix='/discovery')

    @discovery_blueprint.route('/check', methods=['POST'])
    def check():
        # entities[] = check entities reprocessable updated, inserted or destroyed in the process memory
        # process_memory[] = check all process memory used by entities ordered by execution
        instance_id = request.json['instance_id']
        if instance_id:
            process_memory = process_memory_api.get_process_memory_data(instance_id)
            return process_memory

    return discovery_blueprint
