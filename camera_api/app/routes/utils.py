from flask import Blueprint, request, jsonify
from payload_sdk import PayloadSdkInterface, input_mode_t
from threading import Thread, Lock
import logging
import time
import asyncio
from sdk_context import sdk
from payload_define import PAYLOAD_CAMERA_GIMBAL_MODE, PAYLOAD_CAMERA_RC_MODE, payload_camera_rc_mode ,payload_camera_gimbal_mode
from pymavlink import mavutil

utils_routes = Blueprint('utils', __name__)

event_loop = None
scan_task = None

@utils_routes.route("/gimbal/positionMove", methods=["POST"])
def gimbal_position_move():
    yaw = request.json.get("yaw")
    pitch = request.json.get("pitch")
    roll = request.json.get("roll")
    sdk.setGimbalSpeed(float(pitch), float(roll), float(yaw), input_mode_t.INPUT_ANGLE)
    return jsonify({"message": "짐벌 이동이 시작되었습니다."})

@utils_routes.route("/gimbal/continuousMove", methods=["POST"])
def gimbal_continuous_move():
    yaw = float(request.json.get("yaw", 0))
    pitch = float(request.json.get("pitch", 0))
    roll = float(request.json.get("roll", 0))
    logging.info(f"Gimbal continuous move - yaw:{yaw}, pitch:{pitch}, roll:{roll}")
    sdk.setGimbalSpeed(pitch, roll, yaw, input_mode_t.INPUT_SPEED)
    if yaw == 0.0 and pitch == 0.0 and roll == 0.0:
        message = "짐벌 이동이 중지되었습니다."
    else:
        message = "짐벌 이동이 시작되었습니다."
    return jsonify({"message": message})

@utils_routes.route('/gimbal/calib', methods=['POST'])
def set_gimbal_follow_mode():
    sdk.sdk.setPayloadCameraParam(
        PAYLOAD_CAMERA_GIMBAL_MODE,
        payload_camera_gimbal_mode.PAYLOAD_CAMERA_GIMBAL_MODE_RESET, mavutil.mavlink.MAV_PARAM_TYPE_UINT32)
    time.sleep(1.0)
    sdk.sdk.setPayloadCameraParam(
        PAYLOAD_CAMERA_GIMBAL_MODE,
        payload_camera_gimbal_mode.PAYLOAD_CAMERA_GIMBAL_MODE_FOLLOW, mavutil.mavlink.MAV_PARAM_TYPE_UINT32)
    time.sleep(1.0)
    return jsonify({
        'status': 'Gimbal reseted',
        'param_id': PAYLOAD_CAMERA_GIMBAL_MODE,
        'param_value': int(payload_camera_gimbal_mode.PAYLOAD_CAMERA_GIMBAL_MODE_FOLLOW)
    })

# ===============================
# scan-surround 시작
# ===============================

async def async_sleep_interruptible(total_time, check_interval=0.01):
    elapsed = 0.0
    while elapsed < total_time:
        await asyncio.sleep(check_interval)
        elapsed += check_interval

async def scan_surround_worker(yaw_speed, hold, sweep_range, pitch_stages):
    """
    단순 스윕 기반 스캔:
      - 각도 피드백 없음
      - INPUT_SPEED만 사용
    개선점:
      1) 방향 전환 시 짧은 브레이크 + 안정화
      2) 각 회전 끝마다 정지 + 안정화
      3) 루프 끝 0° 정렬 시퀀스 강화 + 로그 출력
      4) 각 회전 후 현재 yaw 로그 출력
    """
    try:
        logging.info("scan_surround_worker 시작됨")

        # ===== 튜닝 포인트 =====
        BRAKE_RATIO = 0.35
        BRAKE_TIME  = 0.08
        SETTLE      = 0.12
        RECENTER_EACH_CYCLE = True  # True로 두면 매 루프 끝 0° 정렬
        # ======================

        # 짐벌 모드 초기화
        sdk.sdk.setPayloadCameraParam(
            PAYLOAD_CAMERA_GIMBAL_MODE,
            payload_camera_gimbal_mode.PAYLOAD_CAMERA_GIMBAL_MODE_RESET,
            mavutil.mavlink.MAV_PARAM_TYPE_UINT32)
        await async_sleep_interruptible(0.5)
        
        sdk.sdk.setPayloadCameraParam(
            PAYLOAD_CAMERA_GIMBAL_MODE,
            payload_camera_gimbal_mode.PAYLOAD_CAMERA_GIMBAL_MODE_FOLLOW,
            mavutil.mavlink.MAV_PARAM_TYPE_UINT32)
        await async_sleep_interruptible(2.0)
        
        with sdk.lock:
            current_yaw = sdk.data.get('attitude', {}).get('yaw', 0.0)
        logging.info(f"[SCAN] 시작 시 현재 Yaw: {current_yaw:.2f}°")

        prev_dir = None
        loop_count = 0

        while True:
            loop_count += 1
            logging.info(f"[SCAN] ===== Loop {loop_count} 시작 =====")

            for pitch in pitch_stages:
                sdk.setGimbalSpeed(pitch, 0, 0, input_mode_t.INPUT_ANGLE)
                await async_sleep_interruptible(1.0)

                for direction in [1, -1, -1, 1]:
                    # (A) 방향 전환 시 브레이크
                    if prev_dir is not None and prev_dir != direction:
                        logging.info(f"[SCAN] 방향 전환: {prev_dir} → {direction}, 브레이크 실행")
                        sdk.setGimbalSpeed(0, 0, -prev_dir * yaw_speed * BRAKE_RATIO, input_mode_t.INPUT_SPEED)
                        await async_sleep_interruptible(BRAKE_TIME)
                        sdk.setGimbalSpeed(0, 0, 0, input_mode_t.INPUT_SPEED)
                        await async_sleep_interruptible(SETTLE)

                    # (B) 스윕
                    sdk.setGimbalSpeed(0, 0, yaw_speed * direction, input_mode_t.INPUT_SPEED)
                    await async_sleep_interruptible(sweep_range / max(yaw_speed, 1e-6))

                    # (C) 정지 + 안정화
                    sdk.setGimbalSpeed(0, 0, 0, input_mode_t.INPUT_SPEED)
                    await async_sleep_interruptible(SETTLE + hold)

                    # 현재 yaw 로그 출력
                    with sdk.lock:
                        cur_yaw = sdk.data.get('attitude', {}).get('yaw', 0.0)
                    logging.info(f"[SCAN] 회전 종료 (dir={direction}), 현재 Yaw: {cur_yaw:.2f}°")

                    prev_dir = direction

            # 루프 끝 0° 정렬
            if RECENTER_EACH_CYCLE:
                logging.info("[SCAN] 루프 종료 → 0° 정렬 시퀀스 시작")
                sdk.setGimbalSpeed(0, 0, 1, input_mode_t.INPUT_ANGLE)
                await async_sleep_interruptible(0.2)
                sdk.setGimbalSpeed(0, 0, 0, input_mode_t.INPUT_ANGLE)
                await async_sleep_interruptible(0.2)
                
                with sdk.lock:
                    cur_yaw = sdk.data.get('attitude', {}).get('yaw', 0.0)
                logging.info(f"[SCAN] 정렬 종료, 현재 Yaw: {cur_yaw:.2f}°")
                
                logging.info("[SCAN] 0° 정렬 완료")

    except asyncio.CancelledError:
        logging.warning("scan_surround_worker 중단됨")
        sdk.setGimbalSpeed(0, 0, 0, input_mode_t.INPUT_SPEED)
        raise

@utils_routes.route("/gimbal/scan-surround", methods=["POST"])
def gimbal_scan_surround():
    global scan_task, event_loop

    if scan_task and not scan_task.done():
        return jsonify({"message": "이미 scan-surround가 실행 중입니다."}), 400

    yaw_speed = float(request.json.get("yaw_speed", 120))
    hold = float(request.json.get("hold", 1.0))
    sweep_range = 1000
    pitch_stages = [0]

    def start_scan():
        global scan_task
        scan_task = asyncio.create_task(
            scan_surround_worker(yaw_speed, hold, sweep_range, pitch_stages)
        )

    event_loop.call_soon_threadsafe(start_scan)
    return jsonify({"message": "scan-surround 시작됨"})

@utils_routes.route("/gimbal/stop-scan", methods=["POST"])
def stop_scan():
    global scan_task
    if scan_task and not scan_task.done():
        scan_task.cancel()
        scan_task = None
        return jsonify({"message": "scan-surround 중단 요청됨"})
    else:
        return jsonify({"message": "scan-surround가 실행 중이 아닙니다."}), 400
