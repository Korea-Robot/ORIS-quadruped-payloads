# /workspace/tracker/libs/pid.py

import time
import numpy as np

class PIDController:
    """
    PID(Proportional-Integral-Derivative) 제어기를 구현하는 클래스.
    목표값(setpoint)에 도달하기 위해 제어 출력을 계산합니다.
    """
    def __init__(self, kp, ki, kd, setpoint=0):
        """
        PID 제어기를 초기화합니다.
        :param kp: 비례(Proportional) 게인. 현재 오차에 비례하여 반응합니다.
        :param ki: 적분(Integral) 게인. 과거 오차의 누적값에 반응하여 정상상태 오차를 없앱니다.
        :param kd: 미분(Derivative) 게인. 오차의 변화율에 반응하여 오버슈트를 줄이고 안정성을 높입니다.
        :param setpoint: 제어기가 도달하고자 하는 목표값입니다.
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint

        # 내부 상태 변수 초기화
        self._prev_error = 0
        self._integral = 0
        self._last_time = time.time()

    def update(self, current_value):
        """
        현재 값을 입력받아 PID 제어 계산을 수행하고 제어 출력값을 반환합니다.
        :param current_value: 시스템의 현재 측정값입니다.
        :return: 제어 출력값 (조정량)
        """
        # 1. 시간 경과 (dt) 계산
        current_time = time.time()
        dt = current_time - self._last_time
        if dt <= 0:  # 매우 짧은 시간 동안의 호출은 무시
            return 0

        # 2. 오차(error) 계산: 목표값과 현재값의 차이
        error = self.setpoint - current_value
        
        # 3. 적분항(Integral) 계산: 오차를 시간에 따라 누적
        self._integral += error * dt
        
        # 4. 미분항(Derivative) 계산: 오차의 변화율
        derivative = (error - self._prev_error) / dt
        
        # 5. PID 최종 출력 계산
        output = (self.kp * error) + (self.ki * self._integral) + (self.kd * derivative)
        
        # 6. 다음 계산을 위해 현재 상태 저장
        self._prev_error = error
        self._last_time = current_time
        
        return output

    def reset(self):
        """PID 제어기의 누적된 오차(integral)와 이전 오차 상태를 초기화합니다."""
        self._integral = 0
        self._prev_error = 0
        self._last_time = time.time()


def get_pan_tilt_scale(current_zoom):
    """
    현재 줌 레벨에 따라 Pan/Tilt 속도의 스케일을 동적으로 조절합니다.
    줌이 많이 될수록, 카메라를 조금만 움직여도 화면이 크게 변하므로 속도를 줄여 정밀 제어를 돕습니다.
    """
    # 간단한 역함수 모델을 사용하여 줌이 커질수록 스케일이 작아지도록 함
    scale = 1.0 / (1 + 0.1 * current_zoom)
    # 스케일 값이 너무 작거나 크지 않도록 범위를 0.1 ~ 1.0으로 제한
    return max(0.1, min(1.0, scale))


def compute_control_errors(detections, frame_shape):
    """
    탐지된 객체 정보를 바탕으로 Pan, Tilt, Zoom 제어에 필요한 오차를 계산합니다.
    :param detections: 탐지된 객체 정보 리스트.
    :param frame_shape: 비디오 프레임의 형태 (높이, 너비, 채널).
    :return: (pan 오차, tilt 오차, zoom 현재값, 베스트 타겟) 튜플.
    """
    if not detections:
        return None

    # 일반적으로 하나의 타겟만 들어오지만, 여러 개일 경우를 대비해 신뢰도가 가장 높은 타겟을 선택
    best_detection = max(detections, key=lambda x: x.get('conf', 0))
    
    # 화면의 중심은 정규화 좌표계에서 (0.5, 0.5)
    center_x, center_y = 0.5, 0.5
    
    # 타겟의 정규화된 좌표 (x중심, y중심, 너비, 높이)
    x, y, w, h = best_detection['xywhn']
    
    # Pan/Tilt 오차: 화면 중심과 타겟 중심의 차이. 이 값이 0이 되는 것이 목표.
    # Pan (좌우) 오차는 x좌표, Tilt (상하) 오차는 y좌표와 관련됨.
    error_pan  = x - center_x
    error_tilt = y - center_y
    
    # Zoom 값: 타겟의 현재 높이(h)를 그대로 사용.
    # Zoom PID 컨트롤러는 이 값을 입력받아 자신의 목표값(setpoint)과 비교하여 오차를 계산함.
    current_zoom_value = h 

    return error_pan, error_tilt, current_zoom_value, best_detection
