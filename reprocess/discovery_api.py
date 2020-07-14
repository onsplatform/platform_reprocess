from flask import Blueprint, request, make_response
from reprocess.discovery import check, force_reprocess


def construct_blueprint():
    discovery_blueprint = Blueprint('discovery', __name__, url_prefix='/discovery')

    @discovery_blueprint.route('/check', methods=['POST'])
    def check_reprocess_api():
        solution = request.json['solution']
        instance_id = request.json['instance_id']
        check.delay(solution, instance_id)
        return make_response('', 202)

    @discovery_blueprint.route('/force_reprocess', methods=['POST'])
    def force_reprocess_api():
        app = request.json['app']
        solution = request.json['solution']
        process_id = request.json['process_id']
        date_begin_validity = request.json['date_begin_validity']
        date_end_validity = request.json['date_end_validity']
        force_reprocess.delay(app, solution, process_id, date_begin_validity, date_end_validity)
        return make_response('', 202)

    return discovery_blueprint
