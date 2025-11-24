# # get_status.py
# from flask import Blueprint, request, jsonify
# from payload_sdk import PayloadSdkInterface, payload_status_event_t, payload_param_t, PAYLOAD_TYPE
# import logging
# import time

# # sdk_context.py에서 공유 인스턴스를 가져옵니다.
# from sdk_context import sdk
# from payload_define import *

# # Flask Blueprint 이어주기.
# status_routes = Blueprint('status', __name__)

# # Callback function for payload status changes
# def onPayloadStatusChanged(event: int, param: list):
#     """
#     SDK로부터 상태 변경 이벤트를 수신하여 공유 데이터 객체(sdk.data)를 업데이트합니다.
#     """
#     with sdk.lock:
#         sdk.data['last_update'] = time.time()
#         event_enum = payload_status_event_t(event)

#         if event_enum == payload_status_event_t.PAYLOAD_GB_ATTITUDE:
#             sdk.data['attitude'] = {'pitch': param[0], 'roll': param[1], 'yaw': param[2]}
        
#         elif event_enum == payload_status_event_t.PAYLOAD_PARAMS:
#             try:
#                 param_enum = payload_param_t(param[0])
#                 sdk.data[param_enum.name] = param[1]
#             except ValueError:
#                 logging.warning(f"Unknown param index received: {param[0]}")

# # --- API 엔드포인트 ---
# @status_routes.route("/all", methods=["GET"])
# def get_all_status():
#     """모든 현재 페이로드 상태를 JSON 형식으로 반환합니다."""
#     with sdk.lock:
#         return jsonify(sdk.data.copy())

# @status_routes.route("/<param_name>", methods=["GET"])
# def get_specific_status(param_name):
#     """특정 파라미터 값을 반환합니다."""
#     with sdk.lock:
#         value = sdk.data.get(param_name.upper()) # URL 파라미터를 대문자로 변환하여 조회
#         if value is not None:
#             return jsonify({param_name: value})
#         else:
#             # 'attitude'와 같은 특수 키도 확인
#             if param_name == 'attitude' and 'attitude' in sdk.data:
#                 return jsonify(sdk.data['attitude'])
#             return jsonify({"error": f"Parameter '{param_name}' not found"}), 404

# # 이 함수는 메인 app.py에서 SDK 초기화 후 호출됩니다.
# def register_sdk_callback_and_set_rates():
#     """
#     SDK에 콜백 함수를 등록하고, 필요한 데이터의 수신 주기를 설정합니다.
#     """
#     sdk.sdk.regPayloadStatusChanged(onPayloadStatusChanged)
#     logging.info("Payload status callback registered.")

#     # dev/payload_get_status.py를 참고하여 필요한 모든 파라미터의 수신 주기를 설정합니다.
#     sdk.sdk.setParamRate(payload_param_t.PARAM_EO_ZOOM_LEVEL, 1000)
#     sdk.sdk.setParamRate(payload_param_t.PARAM_IR_ZOOM_LEVEL, 1000)

#     if PAYLOAD_TYPE == "VIO":
#         sdk.sdk.setParamRate(payload_param_t.PARAM_LRF_RANGE, 100)
#         sdk.sdk.setParamRate(payload_param_t.PARAM_LRF_OFSET_X, 100)
#         sdk.sdk.setParamRate(payload_param_t.PARAM_LRF_OFSET_Y, 100)
#         sdk.sdk.setParamRate(payload_param_t.PARAM_TARGET_COOR_LON, 1000)
#         sdk.sdk.setParamRate(payload_param_t.PARAM_TARGET_COOR_LAT, 1000)
#         sdk.sdk.setParamRate(payload_param_t.PARAM_TARGET_COOR_ALT, 1000)
#         sdk.sdk.setParamRate(payload_param_t.PARAM_CAM_VIEW_MODE, 1000)
#         sdk.sdk.setParamRate(payload_param_t.PARAM_CAM_REC_SOURCE, 1000)
#         sdk.sdk.setParamRate(payload_param_t.PARAM_CAM_IR_TYPE, 1000)
#         sdk.sdk.setParamRate(payload_param_t.PARAM_CAM_IR_PALETTE_ID, 1000)
#         sdk.sdk.setParamRate(payload_param_t.PARAM_GIMBAL_MODE, 1000)
#         sdk.sdk.setParamRate(payload_param_t.PARAM_PAYLOAD_GPS_LON, 1000)
#         sdk.sdk.setParamRate(payload_param_t.PARAM_PAYLOAD_GPS_LAT, 1000)
#         sdk.sdk.setParamRate(payload_param_t.PARAM_PAYLOAD_GPS_ALT, 1000)
#         sdk.sdk.setParamRate(payload_param_t.PARAM_CAM_IR_FFC_MODE, 1000)
#     logging.info("Finished setting parameter rates.")

# # Right-Handed Coordinate System를 기준으로 생각해보자. 
# # 오른손 좌표계에서 Z축을 아래로 정의하면, Yaw(Z축 회전)는 시계 방향이 +, Pitch(Y축 회전)는 기수가 올라가는 것이 +가 된다

# """
# curl -X GET http://localhost:8008/status/all

# {
#   "PARAM_CAM_IR_FFC_MODE": 1.0,
#   "PARAM_CAM_IR_PALETTE_ID": 9.0,
#   "PARAM_CAM_IR_TYPE": 2.0,
#   "PARAM_CAM_REC_SOURCE": 2.0,
#   "PARAM_CAM_VIEW_MODE": 1.0,
#   "PARAM_EO_ZOOM_LEVEL": 1.0,
#   "PARAM_GIMBAL_MODE": 2.0,
#   "PARAM_IR_ZOOM_LEVEL": 1.0,
#   "PARAM_LRF_OFSET_X": 0.0,
#   "PARAM_LRF_OFSET_Y": 0.0,
#   "PARAM_LRF_RANGE": 3.920105457305908,
#   "PARAM_PAYLOAD_GPS_ALT": 0.0,
#   "PARAM_PAYLOAD_GPS_LAT": 0.0,
#   "PARAM_PAYLOAD_GPS_LON": 0.0,
#   "PARAM_TARGET_COOR_ALT": 0.0,
#   "PARAM_TARGET_COOR_LAT": 0.0,
#   "PARAM_TARGET_COOR_LON": 0.0,
#   "attitude": {
#     "pitch": -0.0233154296875,
#     "roll": 0.024075191468000412,
#     "yaw": -2.900390625
#   },
#   "last_update": 1753681842.7586315
# }
# """

# # robot 어떤 preset degree(yaw)를 기준으로 camera가 설치되어있는가? 
# # 로봇 헤딩 방향에서 같은 방향이면 preset은 0도, 왼쪽 90를 바라보고 있으면 -90도 오른쪽을 바라보고 있으면 +90도

# # 여기에 위에 적용된 반대로 된 yaw를 적용해주면 된다. 
# # 즉 preset_degree +yaw(읽은 값) 하면 heading 기준으로 yaw가 나온다. 


# # 내가 추가로 만들고 싶은 get api는 다음과 같다. 
# # heading 기준 yaw, pitch (right-handed coordinates) => -180 ~ + 180도 사이로 조정 
# # 또한 heading 기준 LRF를 yaw,pitch 값을 곱해서 카메라가 바라보고 있는 물체의 거리를 
# # x,y,z로 표현

# # 따라서 ego_yaw, ego_pitch
# # lrf_x , lrf_y, lrf_z 


###############################################################################################################
#############################################################################################################################



# # get_status.py
# from flask import Blueprint, request, jsonify
# from payload_sdk import payload_status_event_t, payload_param_t, PAYLOAD_TYPE
# import logging
# import time
# import math # 삼각함수 계산을 위해 math 라이브러리 추가

# # sdk_context.py에서 공유 인스턴스를 가져옵니다.
# from sdk_context import sdk
# from payload_define import *

# # Flask Blueprint 이어주기.
# status_routes = Blueprint('status', __name__)

# # --- Helper Functions ---
# def normalize_angle(degrees):
#     """각도를 -180 ~ +180 범위로 정규화합니다."""
#     return (degrees + 180) % 360 - 180

# # --- SDK Callback ---
# def onPayloadStatusChanged(event: int, param: list):
#     """
#     SDK로부터 상태 변경 이벤트를 수신하여 공유 데이터 객체(sdk.data)를 업데이트합니다.
#     """
#     with sdk.lock:
#         sdk.data['last_update'] = time.time()
#         try:
#             event_enum = payload_status_event_t(event)

#             if event_enum == payload_status_event_t.PAYLOAD_GB_ATTITUDE:
#                 # 오른손 좌표계, Z축이 아래 방향 기준
#                 # Pitch: 기수 상승이 +
#                 # Yaw: 시계 방향 회전이 +
#                 sdk.data['attitude'] = {'pitch': param[0], 'roll': param[1], 'yaw': param[2]}
            
#             elif event_enum == payload_status_event_t.PAYLOAD_PARAMS:
#                 try:
#                     param_enum = payload_param_t(param[0])
#                     sdk.data[param_enum.name] = param[1]
#                 except ValueError:
#                     logging.warning(f"Unknown param index received: {param[0]}")
#         except ValueError:
#             logging.warning(f"Unknown event index received: {event}")


# # --- API 엔드포인트 ---
# @status_routes.route("/all", methods=["GET"])
# def get_all_status():
#     """모든 현재 페이로드 상태를 JSON 형식으로 반환합니다."""
#     with sdk.lock:
#         # preset_degree도 함께 보여주기 위해 추가
#         response_data = sdk.data.copy()
#         response_data['heading_preset_degree'] = sdk.preset_degree
#         return jsonify(response_data)

# @status_routes.route("/<param_name>", methods=["GET"])
# def get_specific_status(param_name):
#     """특정 파라미터 값을 반환합니다."""
#     with sdk.lock:
#         # 'attitude'와 같은 특수 키도 확인
#         if param_name == 'attitude' and 'attitude' in sdk.data:
#             return jsonify(sdk.data['attitude'])

#         value = sdk.data.get(param_name.upper()) # URL 파라미터를 대문자로 변환하여 조회
#         if value is not None:
#             return jsonify({param_name: value})
#         else:
#             return jsonify({"error": f"Parameter '{param_name}' not found"}), 404

# # --- 신규 추가된 API 엔드포인트 ---

# @status_routes.route("/heading_preset", methods=["POST"])
# def set_heading_preset():
#     """
#     로봇 헤딩 기준 카메라 장착 각도(preset)를 설정하고 저장합니다.
#     Request Body: {"degree": float}
#     """
#     if not request.json or 'degree' not in request.json:
#         return jsonify({"error": "Missing 'degree' in request body"}), 400
    
#     try:
#         degree = float(request.json['degree'])
#         with sdk.lock:
#             sdk.preset_degree = degree
#         logging.info(f"Heading preset degree updated to: {degree}")
#         return jsonify({"message": "Heading preset updated successfully", "new_preset_degree": degree})
#     except (ValueError, TypeError):
#         return jsonify({"error": "'degree' must be a number"}), 400

# @status_routes.route("/ego_pose", methods=["GET"])
# def get_ego_pose():
#     """
#     로봇 헤딩을 기준으로 한 페이로드의 Yaw와 Pitch를 계산하여 반환합니다.
#     Yaw는 -180 ~ +180 범위로 정규화됩니다.
#     """
#     with sdk.lock:
#         if 'attitude' not in sdk.data:
#             return jsonify({"error": "Attitude data not available yet"}), 404
        
#         raw_attitude = sdk.data['attitude']
#         raw_yaw = raw_attitude.get('yaw', 0.0)
        
#         # 헤딩 기준 Yaw 계산: preset 각도 + 현재 페이로드의 yaw
#         ego_yaw = sdk.preset_degree + raw_yaw
        
#         # -180 ~ +180 범위로 정규화
#         normalized_ego_yaw = normalize_angle(ego_yaw)
        
#         response = {
#             "ego_yaw": normalized_ego_yaw,
#             "ego_pitch": raw_attitude.get('pitch', 0.0)
#         }
#         return jsonify(response)

# @status_routes.route("/lrf_coords", methods=["GET"])
# def get_lrf_coordinates():
#     """
#     LRF 거리와 헤딩 기준 자세(ego_yaw, pitch)를 사용하여
#     카메라가 바라보는 지점의 로봇 기준 3D 좌표(x, y, z)를 계산합니다.
#     - x: 정면 방향
#     - y: 왼쪽 방향
#     - z: 아래쪽 방향
#     """
#     with sdk.lock:
#         if 'attitude' not in sdk.data or 'PARAM_LRF_RANGE' not in sdk.data:
#             return jsonify({"error": "Attitude or LRF data not available yet"}), 404
            
#         raw_attitude = sdk.data['attitude']
#         raw_yaw = raw_attitude.get('yaw', 0.0)
#         pitch = raw_attitude.get('pitch', 0.0)
#         distance = sdk.data.get('PARAM_LRF_RANGE', 0.0)

#         # 헤딩 기준 Yaw 계산 및 정규화
#         ego_yaw = sdk.preset_degree + raw_yaw
        
#         # 계산을 위해 각도를 라디안으로 변환
#         pitch_rad = math.radians(pitch)
#         yaw_rad = math.radians(ego_yaw) # 헤딩 기준 yaw 사용

#         # 오른손 좌표계 (X: 정면, Y: 왼쪽, Z: 아래) 기준 좌표 변환
#         # Z축이 아래를 향하므로 pitch가 양수(기수 상승)일 때 z는 음수가 됨
#         x = distance * math.cos(pitch_rad) * math.cos(yaw_rad)
#         y = distance * math.cos(pitch_rad) * math.sin(yaw_rad)
#         # z = -distance * math.sin(pitch_rad)

#         z = distance * math.sin(pitch_rad)
        
#         response = {
#             "x": x,
#             "y": y,
#             "z": z,
#             "source_data": {
#                 "lrf_range": distance,
#                 "ego_yaw": normalize_angle(ego_yaw),
#                 "pitch": pitch,
#                 "preset_degree": sdk.preset_degree
#             }
#         }
#         return jsonify(response)

# # --- SDK 초기화 함수 ---
# def register_sdk_callback_and_set_rates():
#     """
#     SDK에 콜백 함수를 등록하고, 필요한 데이터의 수신 주기를 설정합니다.
#     """
#     sdk.sdk.regPayloadStatusChanged(onPayloadStatusChanged)
#     logging.info("Payload status callback registered.")

#     # dev/payload_get_status.py를 참고하여 필요한 모든 파라미터의 수신 주기를 설정합니다.
#     sdk.sdk.setParamRate(payload_param_t.PARAM_EO_ZOOM_LEVEL, 1000)
#     sdk.sdk.setParamRate(payload_param_t.PARAM_IR_ZOOM_LEVEL, 1000)

#     logging.info("payload type.",PAYLOAD_TYPE)

#     # if PAYLOAD_TYPE == "VIO":
#     # LRF와 자세 데이터는 더 자주 수신하도록 설정 (예: 100ms = 10Hz)
#     sdk.sdk.setParamRate(payload_param_t.PARAM_LRF_RANGE, 100)
#     sdk.sdk.setParamRate(payload_param_t.PARAM_LRF_OFSET_X, 100)
#     sdk.sdk.setParamRate(payload_param_t.PARAM_LRF_OFSET_Y, 100)
#     sdk.sdk.setParamRate(payload_param_t.PARAM_TARGET_COOR_LON, 1000)
#     sdk.sdk.setParamRate(payload_param_t.PARAM_TARGET_COOR_LAT, 1000)
#     sdk.sdk.setParamRate(payload_param_t.PARAM_TARGET_COOR_ALT, 1000)
#     sdk.sdk.setParamRate(payload_param_t.PARAM_CAM_VIEW_MODE, 1000)
#     sdk.sdk.setParamRate(payload_param_t.PARAM_CAM_REC_SOURCE, 1000)
#     sdk.sdk.setParamRate(payload_param_t.PARAM_CAM_IR_TYPE, 1000)
#     sdk.sdk.setParamRate(payload_param_t.PARAM_CAM_IR_PALETTE_ID, 1000)
#     sdk.sdk.setParamRate(payload_param_t.PARAM_GIMBAL_MODE, 1000)
#     sdk.sdk.setParamRate(payload_param_t.PARAM_PAYLOAD_GPS_LON, 1000)
#     sdk.sdk.setParamRate(payload_param_t.PARAM_PAYLOAD_GPS_LAT, 1000)
#     sdk.sdk.setParamRate(payload_param_t.PARAM_PAYLOAD_GPS_ALT, 1000)
#     sdk.sdk.setParamRate(payload_param_t.PARAM_CAM_IR_FFC_MODE, 1000)
#     logging.info("Finished setting parameter rates.")



###############################################################################################################
#############################################################################################################################


# get_status.py
from flask import Blueprint, request, jsonify
from payload_sdk import payload_status_event_t, payload_param_t, PAYLOAD_TYPE
import logging
import time
import math

# sdk_context.py에서 공유 인스턴스를 가져옵니다.
from sdk_context import sdk
from payload_define import *

# Flask Blueprint 이어주기.
status_routes = Blueprint('status', __name__)

# --- Helper Functions ---
def normalize_angle(degrees):
    """각도를 -180 ~ +180 범위로 정규화합니다."""
    return (degrees + 180) % 360 - 180

# --- SDK Callback ---
def onPayloadStatusChanged(event: int, param: list):
    """
    SDK로부터 상태 변경 이벤트를 수신하여 공유 데이터 객체(sdk.data)를 업데이트합니다.
    """
    with sdk.lock:
        sdk.data['last_update'] = time.time()
        try:
            event_enum = payload_status_event_t(event)

            if event_enum == payload_status_event_t.PAYLOAD_GB_ATTITUDE:
                # 오른손 좌표계, Z축이 아래 방향 기준
                # Pitch: 기수 상승이 +
                # Yaw: 시계 방향 회전이 +
                sdk.data['attitude'] = {'pitch': param[0], 'roll': param[1], 'yaw': param[2]}
                logging.debug(f"Attitude updated: pitch={param[0]}, roll={param[1]}, yaw={param[2]}")
            
            elif event_enum == payload_status_event_t.PAYLOAD_PARAMS:
                try:
                    param_enum = payload_param_t(param[0])
                    sdk.data[param_enum.name] = param[1]
                    
                    # LRF 데이터가 업데이트되면 로그 출력
                    if param_enum.name == 'PARAM_LRF_RANGE':
                        logging.info(f"LRF Range updated: {param[1]}")
                    elif param_enum.name in ['PARAM_LRF_OFSET_X', 'PARAM_LRF_OFSET_Y']:
                        logging.debug(f"{param_enum.name} updated: {param[1]}")
                        
                except ValueError:
                    logging.warning(f"Unknown param index received: {param[0]}")
        except ValueError:
            logging.warning(f"Unknown event index received: {event}")

# --- API 엔드포인트 ---
@status_routes.route("/all", methods=["GET"])
def get_all_status():
    """모든 현재 페이로드 상태를 JSON 형식으로 반환합니다."""
    with sdk.lock:
        # preset_degree도 함께 보여주기 위해 추가
        response_data = sdk.data.copy()
        response_data['heading_preset_degree'] = sdk.preset_degree
        return jsonify(response_data)

@status_routes.route("/<param_name>", methods=["GET"])
def get_specific_status(param_name):
    """특정 파라미터 값을 반환합니다."""
    with sdk.lock:
        # 'attitude'와 같은 특수 키도 확인
        if param_name == 'attitude' and 'attitude' in sdk.data:
            return jsonify(sdk.data['attitude'])

        value = sdk.data.get(param_name.upper()) # URL 파라미터를 대문자로 변환하여 조회
        if value is not None:
            return jsonify({param_name: value})
        else:
            return jsonify({"error": f"Parameter '{param_name}' not found"}), 404

# --- LRF 디버깅용 엔드포인트 ---
@status_routes.route("/lrf_debug", methods=["GET"])
def get_lrf_debug():
    """LRF 관련 데이터의 디버깅 정보를 반환합니다."""
    with sdk.lock:
        lrf_data = {
            'PARAM_LRF_RANGE': sdk.data.get('PARAM_LRF_RANGE', 'Not Available'),
            'PARAM_LRF_OFSET_X': sdk.data.get('PARAM_LRF_OFSET_X', 'Not Available'),
            'PARAM_LRF_OFSET_Y': sdk.data.get('PARAM_LRF_OFSET_Y', 'Not Available'),
            'last_update': sdk.data.get('last_update', 'No updates'),
            'payload_type': PAYLOAD_TYPE,
            'all_available_keys': list(sdk.data.keys())
        }
        return jsonify(lrf_data)

# --- 신규 추가된 API 엔드포인트 ---
@status_routes.route("/heading_preset", methods=["POST"])
def set_heading_preset():
    """
    로봇 헤딩 기준 카메라 장착 각도(preset)를 설정하고 저장합니다.
    Request Body: {"degree": float}
    """
    if not request.json or 'degree' not in request.json:
        return jsonify({"error": "Missing 'degree' in request body"}), 400
    
    try:
        degree = float(request.json['degree'])
        with sdk.lock:
            sdk.preset_degree = degree
        logging.info(f"Heading preset degree updated to: {degree}")
        return jsonify({"message": "Heading preset updated successfully", "new_preset_degree": degree})
    except (ValueError, TypeError):
        return jsonify({"error": "'degree' must be a number"}), 400

@status_routes.route("/heading_preset", methods=["GET"])
def get_heading_preset():
    """현재 설정된 헤딩 프리셋 각도를 반환합니다."""
    with sdk.lock:
        return jsonify({"heading_preset_degree": sdk.preset_degree})

@status_routes.route("/ego_pose", methods=["GET"])
def get_ego_pose():
    """
    로봇 헤딩을 기준으로 한 페이로드의 Yaw와 Pitch를 계산하여 반환합니다.
    Yaw는 -180 ~ +180 범위로 정규화됩니다.
    """
    with sdk.lock:
        if 'attitude' not in sdk.data:
            return jsonify({"error": "Attitude data not available yet"}), 404
        
        raw_attitude = sdk.data['attitude']
        raw_yaw = raw_attitude.get('yaw', 0.0)
        
        # 헤딩 기준 Yaw 계산: preset 각도 + 현재 페이로드의 yaw
        ego_yaw = sdk.preset_degree + raw_yaw
        
        # -180 ~ +180 범위로 정규화
        normalized_ego_yaw = normalize_angle(ego_yaw)
        
        response = {
            "ego_yaw": normalized_ego_yaw,
            "ego_pitch": raw_attitude.get('pitch', 0.0)
        }
        return jsonify(response)

@status_routes.route("/lrf_coords", methods=["GET"])
def get_lrf_coordinates():
    """
    LRF 거리와 헤딩 기준 자세(ego_yaw, pitch)를 사용하여
    카메라가 바라보는 지점의 로봇 기준 3D 좌표(x, y, z)를 계산합니다.
    - x: 정면 방향
    - y: 왼쪽 방향
    - z: 아래쪽 방향
    """
    with sdk.lock:
        if 'attitude' not in sdk.data:
            return jsonify({"error": "Attitude data not available yet"}), 404
            
        # LRF 데이터 확인 - 여러 가지 경우를 체크
        lrf_range = sdk.data.get('PARAM_LRF_RANGE')
        if lrf_range is None:
            return jsonify({
                "error": "LRF range data not available", 
                "available_params": [key for key in sdk.data.keys() if 'LRF' in key],
                "all_keys": list(sdk.data.keys())
            }), 404
            
        raw_attitude = sdk.data['attitude']
        raw_yaw = raw_attitude.get('yaw', 0.0)
        pitch = raw_attitude.get('pitch', 0.0)
        distance = float(lrf_range)  # 명시적으로 float 변환

        # 유효한 거리 값인지 확인
        if distance <= 0:
            return jsonify({
                "error": "Invalid LRF range value",
                "lrf_range": distance
            }), 400

        # 헤딩 기준 Yaw 계산 및 정규화
        ego_yaw = sdk.preset_degree + raw_yaw
        
        # 계산을 위해 각도를 라디안으로 변환
        pitch_rad = math.radians(pitch)
        yaw_rad = math.radians(ego_yaw)

        # 오른손 좌표계 (X: 정면, Y: 왼쪽, Z: 아래) 기준 좌표 변환
        x = distance * math.cos(pitch_rad) * math.cos(yaw_rad)
        y = distance * math.cos(pitch_rad) * math.sin(yaw_rad)
        z = distance * math.sin(pitch_rad)
        
        response = {
            "x": x,
            "y": y,
            "z": z,
            "source_data": {
                "lrf_range": distance,
                "ego_yaw": normalize_angle(ego_yaw),
                "pitch": pitch,
                "preset_degree": sdk.preset_degree
            }
        }
        return jsonify(response)

# --- SDK 초기화 함수 ---
def register_sdk_callback_and_set_rates():
    """
    SDK에 콜백 함수를 등록하고, 필요한 데이터의 수신 주기를 설정합니다.
    """
    try:
        sdk.sdk.regPayloadStatusChanged(onPayloadStatusChanged)
        logging.info("Payload status callback registered successfully.")
        
        logging.info(f"Current PAYLOAD_TYPE: {PAYLOAD_TYPE}")
        
        # 먼저 모든 가능한 파라미터를 시도해보고 어떤 것이 지원되는지 확인
        param_list = [
            # 기본 파라미터
            (payload_param_t.PARAM_EO_ZOOM_LEVEL, 1000),
            (payload_param_t.PARAM_IR_ZOOM_LEVEL, 1000),
            # LRF 파라미터
            (payload_param_t.PARAM_LRF_RANGE, 100),
            (payload_param_t.PARAM_LRF_OFSET_X, 100),
            (payload_param_t.PARAM_LRF_OFSET_Y, 100),
            # 기타 파라미터
            (payload_param_t.PARAM_TARGET_COOR_LON, 1000),
            (payload_param_t.PARAM_TARGET_COOR_LAT, 1000),
            (payload_param_t.PARAM_TARGET_COOR_ALT, 1000),
            (payload_param_t.PARAM_CAM_VIEW_MODE, 1000),
            (payload_param_t.PARAM_CAM_REC_SOURCE, 1000),
            (payload_param_t.PARAM_CAM_IR_TYPE, 1000),
            (payload_param_t.PARAM_CAM_IR_PALETTE_ID, 1000),
            (payload_param_t.PARAM_GIMBAL_MODE, 1000),
            (payload_param_t.PARAM_PAYLOAD_GPS_LON, 1000),
            (payload_param_t.PARAM_PAYLOAD_GPS_LAT, 1000),
            (payload_param_t.PARAM_PAYLOAD_GPS_ALT, 1000),
            (payload_param_t.PARAM_CAM_IR_FFC_MODE, 1000)
        ]
        
        successful_params = []
        failed_params = []
        
        for param, rate in param_list:
            try:
                result = sdk.sdk.setParamRate(param, rate)
                param_name = param.name if hasattr(param, 'name') else str(param)
                
                if result == 0 or result is True:  # 성공 조건 (SDK마다 다를 수 있음)
                    successful_params.append(param_name)
                    logging.info(f"✓ Successfully set rate for {param_name}: {rate}ms")
                else:
                    failed_params.append(param_name)
                    logging.warning(f"✗ Failed to set rate for {param_name}: result={result}")
                    
            except Exception as e:
                param_name = param.name if hasattr(param, 'name') else str(param)
                failed_params.append(param_name)
                logging.error(f"✗ Exception setting rate for {param_name}: {e}")
        
        logging.info(f"Parameter rate setting summary:")
        logging.info(f"  - Successful: {successful_params}")
        logging.info(f"  - Failed: {failed_params}")
        
        # LRF 파라미터가 실패했다면 직접 값 요청 시도
        if any("LRF" in param for param in failed_params):
            logging.info("LRF parameters failed, trying direct parameter requests...")
            
            # 직접 파라미터 값 요청 시도 (여러 가지 방법)
            try_direct_param_request()
        
        # 일정 시간 후 파라미터 상태 재확인
        import threading
        def delayed_param_check():
            time.sleep(5)  # 5초 후
            logging.info("=== 5초 후 파라미터 상태 확인 ===")
            with sdk.lock:
                available_params = [key for key in sdk.data.keys() if key.startswith('PARAM_')]
                logging.info(f"현재 수신된 파라미터: {available_params}")
                
                if not any("LRF" in key for key in available_params):
                    logging.warning("⚠️  LRF 파라미터가 여전히 수신되지 않음!")
                    logging.info("페이로드가 LRF를 지원하지 않거나 다른 방법이 필요할 수 있습니다.")
        
        threading.Thread(target=delayed_param_check, daemon=True).start()
            
    except Exception as e:
        logging.error(f"Error during SDK initialization: {e}")
        raise

def try_direct_param_request():
    """직접 파라미터 값 요청을 시도하는 함수"""
    try:
        # 방법 1: getPayloadCameraParam 시도
        if hasattr(sdk.sdk, 'getPayloadCameraParam'):
            logging.info("시도: getPayloadCameraParam으로 LRF 값 직접 요청")
            try:
                lrf_range = sdk.sdk.getPayloadCameraParam(payload_param_t.PARAM_LRF_RANGE)
                if lrf_range is not None:
                    with sdk.lock:
                        sdk.data['PARAM_LRF_RANGE'] = lrf_range
                    logging.info(f"✓ 직접 요청으로 LRF Range 획득: {lrf_range}")
            except Exception as e:
                logging.warning(f"getPayloadCameraParam 실패: {e}")
        
        # 방법 2: requestParam 같은 함수가 있다면 시도
        if hasattr(sdk.sdk, 'requestParam'):
            logging.info("시도: requestParam으로 LRF 값 요청")
            try:
                sdk.sdk.requestParam(payload_param_t.PARAM_LRF_RANGE)
                sdk.sdk.requestParam(payload_param_t.PARAM_LRF_OFSET_X)
                sdk.sdk.requestParam(payload_param_t.PARAM_LRF_OFSET_Y)
                logging.info("✓ requestParam 호출 완료")
            except Exception as e:
                logging.warning(f"requestParam 실패: {e}")
                
        # 방법 3: SDK 객체의 모든 메서드 출력 (디버깅용)
        logging.info("=== SDK 사용 가능한 메서드들 ===")
        methods = [method for method in dir(sdk.sdk) if not method.startswith('_') and callable(getattr(sdk.sdk, method))]
        logging.info(f"SDK methods: {methods}")
        
    except Exception as e:
        logging.error(f"직접 파라미터 요청 중 에러: {e}")