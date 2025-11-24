from flask import Blueprint, request, jsonify
from payload_sdk import PayloadSdkInterface
from sdk_context import sdk
from pymavlink import mavutil
import logging

from libs.payload_define import (
    PAYLOAD_CAMERA_VIEW_SRC,
    PAYLOAD_CAMERA_IR_PALETTE,
    PAYLOAD_CAMERA_VIDEO_OSD_MODE,
    PAYLOAD_CAMERA_VIDEO_FLIP,
    # ICR 제어를 위한 상수 추가
    PAYLOAD_CAMERA_VIDEO_ICR_MODE,
    PAYLOAD_CAMERA_VIDEO_ICR_MANUAL,
    PAYLOAD_CAMERA_VIDEO_ICR_THRESHOLD
)

camera_routes = Blueprint('camera', __name__)

@camera_routes.route("/zoom/step", methods=["POST"])
def camera_zoom_step():
    direction = request.json.get("zoomDirection")
    logging.info(f"Camera step zoom: {direction}")
    sdk.setCameraZoom(0.0, float(direction))
    return jsonify({"message": "스텝 줌이 설정되었습니다."})

@camera_routes.route("/zoom/continuous", methods=["POST"])
def camera_zoom_continuous():
    direction = request.json.get("zoomDirection")
    logging.info(f"Camera continuous zoom: {direction}")
    sdk.setCameraZoom(1.0, float(direction))
    return jsonify({"message": "연속 줌이 설정되었습니다."})

@camera_routes.route("/zoom/range", methods=["POST"])
def camera_zoom_range():
    zoom_percentage = request.json.get("zoomPercentage")
    logging.info(f"Camera range zoom: {zoom_percentage}")
    sdk.setCameraZoom(2.0, float(zoom_percentage))
    return jsonify({"message": "레인지 줌이 설정되었습니다."})

@camera_routes.route("/change-view-src", methods=["POST"])
def camera_change_view():
    view_src = request.json.get("viewSrc")
    logging.info(f"Change camera view src: {view_src}")
    sdk.setPayloadCameraParam(PAYLOAD_CAMERA_VIEW_SRC, int(view_src), mavutil.mavlink.MAV_PARAM_TYPE_UINT32)
    return jsonify({"message": "뷰 소스가 변경되었습니다."})

@camera_routes.route("/set-ir-palette", methods=["POST"])
def camera_set_ir_palette():
    palette = request.json.get("irPalette")
    logging.info(f"Set IR palette: {palette}")
    sdk.setPayloadCameraParam(PAYLOAD_CAMERA_IR_PALETTE, int(palette), mavutil.mavlink.MAV_PARAM_TYPE_UINT32)
    return jsonify({"message": "IR 팔레트가 설정되었습니다."})

@camera_routes.route("/set-osd-mode", methods=["POST"])
def camera_set_osd_mode():
    osd_mode = request.json.get("osdMode")
    logging.info(f"Set OSD mode: {osd_mode}")
    sdk.setPayloadCameraParam(PAYLOAD_CAMERA_VIDEO_OSD_MODE, int(osd_mode), mavutil.mavlink.MAV_PARAM_TYPE_UINT32)
    return jsonify({"message": "OSD 모드가 설정되었습니다."})

@camera_routes.route("/set-flip-mode", methods=["POST"])
def camera_flip_mode():
    flip = request.json.get("flipMode")
    logging.info(f"Set flip mode: {flip}")
    sdk.setPayloadCameraParam(PAYLOAD_CAMERA_VIDEO_FLIP, int(flip), mavutil.mavlink.MAV_PARAM_TYPE_UINT32)
    return jsonify({"message": "플립 모드가 설정되었습니다."})

@camera_routes.route("/focus/set-mode", methods=["POST"])
def camera_focus_mode():
    mode = request.json.get("focusMode")
    logging.info(f"Set focus mode: {mode}")
    sdk.setPayloadCameraParam("C_V_FM", int(mode), mavutil.mavlink.MAV_PARAM_TYPE_UINT32)
    return jsonify({"message": "포커스 모드가 설정되었습니다."})

@camera_routes.route("/focus/continuous", methods=["POST"])
def camera_focus_continuous():
    direction = request.json.get("focusDirection")
    logging.info(f"Continuous focus: {direction}")
    sdk.setCameraFocus(1.0, float(direction))
    return jsonify({"message": "포커스 값이 설정되었습니다."})

@camera_routes.route("/focus/auto", methods=["POST"])
def camera_focus_auto():
    logging.info("Auto focus requested")
    sdk.setCameraFocus(1.0)
    return jsonify({"message": "AUTO FOCUS"})

@camera_routes.route("/capture-image", methods=["POST"])
def camera_capture_image():
    logging.info("Image capture requested")
    sdk.setPayloadCameraCaptureImage(0)
    return jsonify({"message": "이미지 캡처가 실행되었습니다."})

@camera_routes.route("/stop-capture", methods=["POST"])
def camera_stop_capture():
    logging.info("Stop image capture requested")
    sdk.setPayloadCameraStopImage()
    return jsonify({"message": "이미지 캡처가 중지되었습니다."})

@camera_routes.route("/start-record", methods=["POST"])
def camera_start_record():
    logging.info("Start record requested")
    sdk.setPayloadCameraRecordVideoStart()
    return jsonify({"message": "비디오 녹화가 시작되었습니다."})

@camera_routes.route("/stop-record", methods=["POST"])
def camera_stop_record():
    logging.info("Stop record requested")
    sdk.setPayloadCameraRecordVideoStop()
    return jsonify({"message": "비디오 녹화가 중지되었습니다."})

@camera_routes.route("/set-ffc-mode", methods=["POST"])
def camera_set_ffc_mode():
    mode = request.json.get("ffcMode")
    logging.info(f"Set FFC mode: {mode}")
    sdk.setPayloadCameraFFCMode(int(mode))
    return jsonify({"message": "FFC 모드가 설정되었습니다."})

@camera_routes.route("/trigger-ffc", methods=["POST"])
def camera_trigger_ffc():
    logging.info("FFC trigger requested")
    sdk.setPayloadCameraFFCTrigg()
    return jsonify({"message": "FFC가 트리거되었습니다."})

# ----------------------------------------
# ICR (Infrared Cut filter Removal) Control
# ----------------------------------------

@camera_routes.route("/icr/set-mode", methods=["POST"])
def camera_set_icr_mode():
    """ICR 모드를 설정합니다. (0: AUTO, 1: MANUAL)"""
    mode = request.json.get("icrMode")
    logging.info(f"Set ICR mode: {mode}")
    sdk.setPayloadCameraParam(PAYLOAD_CAMERA_VIDEO_ICR_MODE, int(mode), mavutil.mavlink.MAV_PARAM_TYPE_UINT32)
    return jsonify({"message": f"ICR 모드가 '{'AUTO' if mode == 0 else 'MANUAL'}' (으)로 설정되었습니다."})

@camera_routes.route("/icr/set-manual-control", methods=["POST"])
def camera_set_icr_manual_control():
    """수동 ICR 상태를 설정합니다. (0: OFF, 1: ON) - MANUAL 모드에서만 동작합니다."""
    state = request.json.get("manualState")
    logging.info(f"Set manual ICR control state: {state}")
    sdk.setPayloadCameraParam(PAYLOAD_CAMERA_VIDEO_ICR_MANUAL, int(state), mavutil.mavlink.MAV_PARAM_TYPE_UINT32)
    return jsonify({"message": f"수동 ICR 제어가 '{'ON' if state == 1 else 'OFF'}' 상태로 설정되었습니다."})

@camera_routes.route("/icr/set-threshold", methods=["POST"])
def camera_set_icr_threshold():
    """ICR 임계값을 설정합니다. (0-255) - AUTO 모드에서만 유효합니다."""
    threshold = request.json.get("threshold")
    logging.info(f"Set ICR threshold: {threshold}")
    sdk.setPayloadCameraParam(PAYLOAD_CAMERA_VIDEO_ICR_THRESHOLD, int(threshold), mavutil.mavlink.MAV_PARAM_TYPE_UINT32)
    return jsonify({"message": f"ICR 임계값이 {threshold}(으)로 설정되었습니다."})
