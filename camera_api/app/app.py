# # app.py
# import os
# import signal
# import sys
# import time
# import logging
# import asyncio
# import threading

# # Add libs to path

# sys.path.append(os.path.join(os.path.dirname(__file__), 'libs'))
# sys.path.append(os.path.join(os.path.dirname(__file__), 'dev_ai/tracker'))
# sys.path.append(os.path.dirname(__file__))
# from flask import Flask, jsonify
# from pymavlink import mavutil
# # Import shared SDK context and routes/callbacks
# from sdk_context import sdk
# from routes.get_status import status_routes, register_sdk_callback_and_set_rates
# from routes.camera_control import camera_routes
# from routes.gimbal_control import gimbal_routes
# from routes.system_control import system_routes
# from routes.param_control import param_routes


# # default routes 
# # from routes.tracking_routes import tracking_routes

# # MQTT routes 
# from routes.tracking_routes_mqtt import tracking_routes
# from routes import utils

# from payload_define import PAYLOAD_CAMERA_GIMBAL_MODE, payload_camera_gimbal_mode


# # --- Global Variables ---
# time_to_exit = False

# # --- Flask & SDK Initialization ---
# # === 로깅 설정 ===
# for h in logging.root.handlers[:]:
#     logging.root.removeHandler(h)

# logging.basicConfig(
#     level=logging.INFO,
#     format='[%(asctime)s] %(levelname)s: %(message)s'
# )

# # === Flask & SDK 초기화 ===
# app = Flask(__name__)

# def quit_handler(sig, frame):
#     """Handles termination signal for graceful shutdown."""
#     global time_to_exit
#     print("\nTERMINATING AT USER REQUEST")
#     time_to_exit = True
#     try:
#         sdk.sdk.sdkQuit()
#     except Exception as e:
#         logging.error(f"Error while quitting payload: {e}")
#     sys.exit(0)

# signal.signal(signal.SIGINT, quit_handler)

# # --- Background Payload SDK Logic ---
# def run_payload_sdk():
#     """Initializes and runs the payload SDK in a background thread."""
#     global time_to_exit
#     # try:
#     logging.info("SDK Thread: Initializing connection...")
#     sdk.sdk.sdkInitConnection()

#     if sdk.sdk.checkPayloadConnection():
#         logging.info("SDK Thread: Payload connected successfully.")
        
#         # 1. Register callback and set data rates
#         register_sdk_callback_and_set_rates()

#         # 2. Initialize Gimbal to FOLLOW mode
#         logging.info("SDK Thread: Initializing Gimbal to RESET mode...")
#         sdk.sdk.setPayloadCameraParam(
#             PAYLOAD_CAMERA_GIMBAL_MODE,
#             payload_camera_gimbal_mode.PAYLOAD_CAMERA_GIMBAL_MODE_RESET, mavutil.mavlink.MAV_PARAM_TYPE_UINT32)
#         time.sleep(2.0)
        
#         logging.info("SDK Thread: Initializing Gimbal to FOLLOW mode...")
#         sdk.sdk.setPayloadCameraParam(
#             PAYLOAD_CAMERA_GIMBAL_MODE,
#             payload_camera_gimbal_mode.PAYLOAD_CAMERA_GIMBAL_MODE_FOLLOW, mavutil.mavlink.MAV_PARAM_TYPE_UINT32)
#         time.sleep(2.0)

#         logging.info("SDK Thread: Gimbal initialized.")
#     else:
#         logging.error("SDK Thread: Payload connection failed. Shutting down application.")
#         os.kill(os.getpid(), signal.SIGINT)
#         return

#     # except Exception as e:
#     #     logging.error(f"SDK Thread: A critical error occurred during initialization: {e}")
#     #     os.kill(os.getpid(), signal.SIGINT)
#     #     return

#     while not time_to_exit:
#         time.sleep(1)
#     logging.info("SDK Thread: Shutting down.")


# # --- Register Flask Blueprints ---
# app.register_blueprint(status_routes, url_prefix='/status')
# app.register_blueprint(camera_routes, url_prefix='/camera')
# app.register_blueprint(gimbal_routes, url_prefix='/gimbal')
# app.register_blueprint(system_routes, url_prefix='/system')
# app.register_blueprint(param_routes, url_prefix='/param')
# app.register_blueprint(utils.utils_routes)
# app.register_blueprint(tracking_routes)  


# @app.route('/')
# def index():
#     return jsonify({"message": "Payload SDK Server is running."})

# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 6783))
#     logging.info(f"Main: Starting Flask app on port {port}")

#     # Start the background thread for the payload SDK
#     logging.info("Main: Starting Payload SDK background thread...")
#     payload_thread = threading.Thread(target=run_payload_sdk, daemon=True)
#     payload_thread.start()

#     # asyncio 루프 생성 및 utils_new에 주입
#     loop = asyncio.new_event_loop()
#     utils.event_loop = loop

#     def run_asyncio_loop(loop):
#         asyncio.set_event_loop(loop)
#         loop.run_forever()

#     asyncio_thread = threading.Thread(
#         target=run_asyncio_loop, args=(loop,), daemon=True)
#     asyncio_thread.start()

#     # Start the Flask server
#     app.run(host='0.0.0.0', port=port, debug=True)


import os
import signal
import sys
import time
import logging
import asyncio
import threading

# Add libs to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'libs'))
sys.path.append(os.path.dirname(__file__))

from flask import Flask, jsonify
from pymavlink import mavutil
# Import shared SDK context and routes/callbacks
from sdk_context import sdk
from routes.get_status import status_routes, register_sdk_callback_and_set_rates
from routes.camera_control import camera_routes
from routes.gimbal_control import gimbal_routes
from routes.system_control import system_routes
from routes.param_control import param_routes

# MQTT routes 
from routes import utils

from payload_define import PAYLOAD_CAMERA_GIMBAL_MODE, payload_camera_gimbal_mode

# --- Global Variables ---
time_to_exit = False

# --- Flask & SDK Initialization ---
# === 로깅 설정 ===
for h in logging.root.handlers[:]:
    logging.root.removeHandler(h)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)

# === Flask & SDK 초기화 ===
app = Flask(__name__)

def quit_handler(sig, frame):
    """Handles termination signal for graceful shutdown."""
    global time_to_exit
    print("\nTERMINATING AT USER REQUEST")
    time_to_exit = True
    try:
        sdk.sdk.sdkQuit()
    except Exception as e:
        logging.error(f"Error while quitting payload: {e}")
    sys.exit(0)

signal.signal(signal.SIGINT, quit_handler)

# --- Background Payload SDK Logic ---
def run_payload_sdk():
    """Initializes and runs the payload SDK in a background thread."""
    global time_to_exit
    
    logging.info("SDK Thread: Initializing connection...")
    
    try:
        # SDK 연결 초기화
        sdk_result = sdk.sdk.sdkInitConnection()
        logging.info(f"SDK 연결 초기화 결과: {sdk_result}")
        
        # 연결 상태 확인
        connection_status = sdk.sdk.checkPayloadConnection()
        logging.info(f"페이로드 연결 상태: {connection_status}")

        if connection_status:
            logging.info("SDK Thread: Payload connected successfully.")
            
            # 1. 콜백 등록 및 데이터 수신 주기 설정
            logging.info("SDK Thread: Registering callback and setting rates...")
            register_sdk_callback_and_set_rates()

            # 2. Gimbal 초기화 (RESET -> FOLLOW)
            logging.info("SDK Thread: Initializing Gimbal to RESET mode...")
            try:
                reset_result = sdk.sdk.setPayloadCameraParam(
                    PAYLOAD_CAMERA_GIMBAL_MODE,
                    payload_camera_gimbal_mode.PAYLOAD_CAMERA_GIMBAL_MODE_RESET, 
                    mavutil.mavlink.MAV_PARAM_TYPE_UINT32
                )
                logging.info(f"Gimbal RESET 결과: {reset_result}")
                time.sleep(2.0)
                
                logging.info("SDK Thread: Initializing Gimbal to FOLLOW mode...")
                follow_result = sdk.sdk.setPayloadCameraParam(
                    PAYLOAD_CAMERA_GIMBAL_MODE,
                    payload_camera_gimbal_mode.PAYLOAD_CAMERA_GIMBAL_MODE_FOLLOW, 
                    mavutil.mavlink.MAV_PARAM_TYPE_UINT32
                )
                logging.info(f"Gimbal FOLLOW 결과: {follow_result}")
                time.sleep(2.0)

                logging.info("SDK Thread: Gimbal initialized.")
            except Exception as e:
                logging.error(f"Gimbal 초기화 중 에러: {e}")
                
            # 3. SDK 상태 모니터링 시작
            start_sdk_monitoring()
            
        else:
            logging.error("SDK Thread: Payload connection failed. Shutting down application.")
            os.kill(os.getpid(), signal.SIGINT)
            return

    except Exception as e:
        logging.error(f"SDK Thread: Critical error during initialization: {e}")
        logging.error(f"Exception type: {type(e)}")
        import traceback
        logging.error(f"Traceback: {traceback.format_exc()}")
        os.kill(os.getpid(), signal.SIGINT)
        return

    # 메인 루프
    while not time_to_exit:
        time.sleep(1)
        
    logging.info("SDK Thread: Shutting down.")

def start_sdk_monitoring():
    """SDK 상태를 주기적으로 모니터링하는 간단한 스레드"""
    def monitor_sdk():
        monitor_count = 0
        while not time_to_exit:
            monitor_count += 1
            time.sleep(15)  # 15초마다 체크 (원본 예제는 지속적으로 실행되므로 적당한 간격으로)
            
            with sdk.lock:
                current_params = list(sdk.data.keys())
                param_count = len([k for k in current_params if k.startswith('PARAM_')])
                
            logging.info(f"=== SDK 모니터링 #{monitor_count} ===")
            logging.info(f"현재 수신된 파라미터 수: {param_count}")
            
            with sdk.lock:
                lrf_range = sdk.data.get('PARAM_LRF_RANGE', 'Not Available')
                lrf_x = sdk.data.get('PARAM_LRF_OFSET_X', 'Not Available')
                lrf_y = sdk.data.get('PARAM_LRF_OFSET_Y', 'Not Available')
                
            if lrf_range != 'Not Available':
                logging.info(f"✓ LRF 데이터 수신 중 - Range: {lrf_range}")
    
            monitoring_thread = threading.Thread(target=monitor_sdk, daemon=True)
            monitoring_thread.start()
            logging.info("SDK 모니터링 스레드 시작됨")('PARAM_LRF_OFSET_X', 'Not Available')
            lrf_y = sdk.data.get('PARAM_LRF_OFSET_Y', 'Not Available')
                
            logging.info(f"  - LRF_RANGE: {lrf_range}")
            logging.info(f"  - LRF_OFSET_X: {lrf_x}")
            logging.info(f"  - LRF_OFSET_Y: {lrf_y}")
            
            # 10번째 체크에서 여전히 LRF가 안 된다면 추가 시도
            if monitor_count == 10 and lrf_range == 'Not Available':
                logging.warning("10번째 체크에서도 LRF 데이터 없음. 추가 디버깅 시도...")
                debug_sdk_methods()
    
    monitoring_thread = threading.Thread(target=monitor_sdk, daemon=True)
    monitoring_thread.start()
    logging.info("SDK 모니터링 스레드 시작됨")

def debug_sdk_methods():
    """SDK 객체의 사용 가능한 메서드들을 디버깅"""
    try:
        logging.info("=== SDK 디버깅 정보 ===")
        
        # SDK 객체의 모든 메서드 확인
        sdk_methods = []
        for attr_name in dir(sdk.sdk):
            if not attr_name.startswith('_'):
                attr = getattr(sdk.sdk, attr_name)
                if callable(attr):
                    sdk_methods.append(attr_name)
        
        logging.info(f"SDK 사용 가능한 메서드들: {sdk_methods}")
        
        # LRF 관련 메서드가 있는지 확인
        lrf_methods = [method for method in sdk_methods if 'lrf' in method.lower() or 'range' in method.lower()]
        if lrf_methods:
            logging.info(f"LRF 관련 가능성 있는 메서드들: {lrf_methods}")
        
        # 파라미터 관련 메서드들
        param_methods = [method for method in sdk_methods if 'param' in method.lower()]
        logging.info(f"파라미터 관련 메서드들: {param_methods}")
        
        # 실제 시도할 수 있는 메서드들 테스트
        test_methods = ['getPayloadCameraParam', 'requestParam', 'getAllParams', 'getParamList']
        for method_name in test_methods:
            if hasattr(sdk.sdk, method_name):
                logging.info(f"✓ {method_name} 메서드 사용 가능")
                try:
                    method = getattr(sdk.sdk, method_name)
                    # 안전하게 호출 시도 (인자가 필요 없는 경우)
                    if method_name in ['getAllParams', 'getParamList']:
                        result = method()
                        logging.info(f"{method_name} 결과: {result}")
                except Exception as e:
                    logging.info(f"{method_name} 호출 실패: {e}")
            else:
                logging.info(f"✗ {method_name} 메서드 없음")
                
    except Exception as e:
        logging.error(f"SDK 디버깅 중 에러: {e}")

# --- Register Flask Blueprints ---
app.register_blueprint(status_routes, url_prefix='/status')
app.register_blueprint(camera_routes, url_prefix='/camera')
app.register_blueprint(gimbal_routes, url_prefix='/gimbal')
app.register_blueprint(system_routes, url_prefix='/system')
app.register_blueprint(param_routes, url_prefix='/param')
app.register_blueprint(utils.utils_routes)

@app.route('/')
def index():
    return jsonify({"message": "Payload SDK Server is running."})

@app.route('/debug/sdk_info')
def sdk_debug_info():
    """SDK 디버깅 정보를 반환하는 엔드포인트"""
    try:
        with sdk.lock:
            info = {
                "connection_status": sdk.sdk.checkPayloadConnection() if hasattr(sdk.sdk, 'checkPayloadConnection') else "Unknown",
                "available_data_keys": list(sdk.data.keys()),
                "data_count": len(sdk.data),
                "last_update": sdk.data.get('last_update', 'Never'),
                "sdk_methods": [method for method in dir(sdk.sdk) if not method.startswith('_') and callable(getattr(sdk.sdk, method))]
            }
        return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 6783))
    logging.info(f"Main: Starting Flask app on port {port}")

    # Start the background thread for the payload SDK
    logging.info("Main: Starting Payload SDK background thread...")
    payload_thread = threading.Thread(target=run_payload_sdk, daemon=True)
    payload_thread.start()

    # asyncio 루프 생성 및 utils_new에 주입
    loop = asyncio.new_event_loop()
    utils.event_loop = loop

    def run_asyncio_loop(loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    asyncio_thread = threading.Thread(
        target=run_asyncio_loop, args=(loop,), daemon=True)
    asyncio_thread.start()

    # Start the Flask server
    app.run(host='0.0.0.0', port=port, debug=True)
