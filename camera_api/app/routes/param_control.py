from flask import Blueprint, request, jsonify
from payload_sdk import PayloadSdkInterface

from sdk_context import sdk

param_routes = Blueprint('param', __name__)

@param_routes.route('/request', methods=['POST'])
def request_param():
    sdk.requestParamValue(request.json['index'])
    return jsonify({'status': 'param request sent'})

@param_routes.route('/stream_rate', methods=['POST'])
def set_stream_rate():
    sdk.sendPayloadRequestStreamRate(request.json['index'], request.json['time_ms'])
    return jsonify({'status': 'stream rate set'})

@param_routes.route('/request_all', methods=['POST'])
def request_all_streams():
    sdk.requestMessageStreamInterval()
    return jsonify({'status': 'all param stream requests sent'})
