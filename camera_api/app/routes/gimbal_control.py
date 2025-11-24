from flask import Blueprint, request, jsonify
from payload_sdk import PayloadSdkInterface, input_mode_t
import logging
from pymavlink import mavutil
from payload_define import PAYLOAD_CAMERA_GIMBAL_MODE, PAYLOAD_CAMERA_RC_MODE, payload_camera_rc_mode ,payload_camera_gimbal_mode
from sdk_context import sdk

gimbal_routes = Blueprint('gimbal', __name__)

@gimbal_routes.route("/follow", methods=["POST"])
def gimbal_follow():
    logging.info(f"Force set gimbal mode to RESET")
    sdk.sdk.setPayloadCameraParam(
        PAYLOAD_CAMERA_GIMBAL_MODE,
        payload_camera_gimbal_mode.PAYLOAD_CAMERA_GIMBAL_MODE_FOLLOW, mavutil.mavlink.MAV_PARAM_TYPE_UINT32)
    return jsonify({"message": "짐벌 모드가 RESET"})

@gimbal_routes.route("/reset", methods=["POST"])
def gimbal_reset():
    logging.info(f"Force set gimbal mode to RESET")
    sdk.sdk.setPayloadCameraParam(
        PAYLOAD_CAMERA_GIMBAL_MODE,
        payload_camera_gimbal_mode.PAYLOAD_CAMERA_GIMBAL_MODE_RESET, mavutil.mavlink.MAV_PARAM_TYPE_UINT32)
    return jsonify({"message": "짐벌 모드가 RESET"})

@gimbal_routes.route("/stop", methods=["POST"])
def gimbal_stop():
    sdk.setGimbalSpeed(0, 0, 0, input_mode_t.INPUT_SPEED)
    return jsonify({"message": "Gimbal movement stopped"})

@gimbal_routes.route("/set-rc-mode", methods=["POST"])
def gimbal_set_rc_mode():
    mode = request.json.get("rcMode")
    if mode not in [payload_camera_rc_mode.PAYLOAD_CAMERA_RC_MODE_STANDARD, payload_camera_rc_mode.PAYLOAD_CAMERA_RC_MODE_GREMSY]:
        return jsonify({"error": "Invalid RC mode"}), 400
    sdk.setPayloadCameraParam(PAYLOAD_CAMERA_RC_MODE, int(mode), mavutil.mavlink.MAV_PARAM_TYPE_UINT32)
    return jsonify({"message": f"Gimbal RC 모드({mode})가 설정되었습니다."})

@gimbal_routes.route("/calib-gyro", methods=["POST"])
def gimbal_calib_gyro():
    logging.info("Gimbal gyro calibration requested")
    sdk.sendPayloadGimbalCalibGyro()
    return jsonify({"message": "자이로 캘리브레이션이 시작되었습니다."})

@gimbal_routes.route("/calib-accel", methods=["POST"])
def gimbal_calib_accel():
    logging.info("Gimbal accel calibration requested")
    sdk.sendPayloadGimbalCalibAccel()
    return jsonify({"message": "가속도 캘리브레이션이 시작되었습니다."})

@gimbal_routes.route("/calib-motor", methods=["POST"])
def gimbal_calib_motor():
    logging.info("Gimbal motor calibration requested")
    sdk.sendPayloadGimbalCalibMotor()
    return jsonify({"message": "모터 캘리브레이션이 시작되었습니다."})

@gimbal_routes.route("/search-home", methods=["POST"])
def gimbal_search_home():
    logging.info("Gimbal home search requested")
    sdk.sendPayloadGimbalSearchHome()
    return jsonify({"message": "홈 위치 탐색이 시작되었습니다."})

@gimbal_routes.route("/auto-tune", methods=["POST"])
def gimbal_auto_tune():
    status = request.json.get("status")
    logging.info(f"Gimbal auto tune: {status}")
    sdk.sendPayloadGimbalAutoTune(bool(status))
    return jsonify({"message": "오토 튠이 실행되었습니다."})

