from flask import Blueprint, request, jsonify
from payload_sdk import PayloadSdkInterface
import time
import ctypes

from sdk_context import sdk

system_routes = Blueprint('system', __name__)

@system_routes.route('/connect', methods=['POST'])
def connect():
    result = sdk.sdkInitConnection()
    return jsonify({'status': 'connected' if result else 'failed'}), 200 if result else 500

@system_routes.route('/disconnect', methods=['POST'])
def disconnect():
    sdk.sdkQuit()
    return jsonify({'status': 'disconnected'}), 200

@system_routes.route('/send_time', methods=['POST'])
def send_time():
    unix_time_us = int(time.time() * 1e6)
    boot_time_ms = int(time.time() * 1e3)

    sys_time = ctypes.Structure()
    sys_time.time_unix_usec = ctypes.c_uint64(unix_time_us)
    sys_time.time_boot_ms = ctypes.c_uint32(boot_time_ms)

    sdk.sendPayloadSystemTime(sys_time)
    return jsonify({'status': 'system time sent'})