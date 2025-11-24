# Gremsy Payload Camera API Server

Flask 기반 REST API 서버로, Gremsy Payload SDK를 래핑하여 카메라 및 짐벌 제어를 HTTP API로 제공합니다.

## 개요

### 배경

**Gremsy**는 드론 및 로봇용 고성능 짐벌 시스템을 제조하는 회사입니다. 짐벌은 카메라를 안정적으로 유지하면서 원하는 방향으로 정밀하게 제어할 수 있는 기계 장치입니다. Gremsy의 **페이로드(Payload)** 시스템은 EO(일반 광학) 카메라와 IR(적외선) 카메라, 그리고 LRF(레이저 거리 측정기)가 통합된 짐벌 시스템으로, 주로 드론, 로봇, 감시 시스템 등에 탑재됩니다.

### 문제점

Gremsy는 자체적으로 **Payload SDK**를 제공하지만, 이는 Python 기반의 저수준 라이브러리로 다음과 같은 제약이 있습니다:

- **MAVLink 프로토콜 직접 사용**: 항공/로봇 통신 프로토콜인 MAVLink를 직접 다뤄야 함
- **로컬 환경 제약**: SDK를 사용하려면 Python 환경과 의존성을 직접 설치해야 함
- **통합의 어려움**: 웹 애플리케이션, 모바일 앱, 다른 프로그래밍 언어에서 직접 연동하기 어려움
- **복잡한 인터페이스**: 카메라/짐벌 제어를 위해 SDK의 복잡한 함수들을 직접 호출해야 함

### 해결 방법

이 프로젝트는 **Gremsy Payload SDK를 HTTP REST API로 래핑**하여 위의 문제들을 해결합니다:

1. **간단한 HTTP 인터페이스**: 복잡한 SDK 대신 간단한 HTTP 요청으로 제어
2. **언어 독립적**: 어떤 프로그래밍 언어에서도 HTTP 클라이언트로 접근 가능
3. **네트워크 기반**: 로컬뿐만 아니라 원격에서도 제어 가능
4. **Docker 지원**: 컨테이너로 쉽게 배포 및 실행
5. **RESTful 설계**: 직관적인 엔드포인트로 카메라/짐벌 기능 제공

### 아키텍처

```
┌─────────────────┐      HTTP REST API       ┌──────────────────┐
│   클라이언트    │ ──────────────────────> │  Flask API 서버  │
│  (웹/앱/기타)   │ <────────────────────── │  (이 프로젝트)   │
└─────────────────┘      JSON 응답           └──────────────────┘
                                                      │
                                               PyMAVLink / SDK
                                                      │
                                              MAVLink Protocol
                                                (UDP/UART)
                                                      │
                                                      ▼
                                           ┌──────────────────┐
                                           │ Gremsy Payload   │
                                           │ (짐벌 + 카메라)  │
                                           └──────────────────┘
```

### 사용 사례

- **드론 지상 관제소(GCS)**: 웹 기반 인터페이스에서 카메라 제어
- **로봇 제어 시스템**: ROS 또는 다른 로봇 프레임워크와 통합
- **원격 감시 시스템**: 네트워크를 통한 원격 카메라 모니터링 및 제어
- **자동화 시스템**: 스크립트나 자동화 도구로 카메라 제어 자동화
- **모바일 앱**: 스마트폰에서 카메라/짐벌 제어

### 주요 기능

- **카메라 제어**: 줌, 포커스, 이미지 캡처, 비디오 녹화, IR 팔레트 설정
- **짐벌 제어**: 모드 전환, 캘리브레이션, 자동 튜닝
- **상태 모니터링**: 실시간 자세 정보, LRF 데이터, 파라미터 조회
- **좌표 변환**: LRF 거리 데이터를 로봇 기준 3D 좌표로 변환
- **Docker 지원**: 컨테이너화된 배포

## 지원 하드웨어

- **Payload**: Gremsy VIO, ZIO, GHardron Payload (v2.0.0 이상)
- **플랫폼**: Ubuntu PC, NVIDIA Jetson, Raspberry Pi, Qualcomm RB5165

## 프로젝트 구조

```
Camera_API/
├── app/                      # Flask 애플리케이션
│   ├── app.py                # 메인 애플리케이션 진입점
│   ├── sdk_context.py        # SDK 싱글톤 인스턴스
│   ├── routes/               # API 엔드포인트 라우트
│   │   ├── camera_control.py    # 카메라 제어 API
│   │   ├── gimbal_control.py    # 짐벌 제어 API
│   │   ├── get_status.py        # 상태 조회 API
│   │   ├── param_control.py     # 파라미터 제어 API
│   │   ├── system_control.py    # 시스템 제어 API
│   │   └── utils.py             # 유틸리티 함수
│   └── libs/                 # SDK 라이브러리
│       ├── config.py             # SDK 설정
│       ├── payload_sdk.py        # Payload SDK 인터페이스
│       ├── payload_define.py     # 상수 및 Enum 정의
│       └── ...
├── libs/                     # 추가 라이브러리 (백업)
├── Dockerfile                # Docker 이미지 정의
├── build_docker.sh           # Docker 이미지 빌드 스크립트
├── launch_docker.sh          # Docker 컨테이너 실행 스크립트
├── run_docker.sh             # Docker 실행 스크립트
├── requirements.txt          # Python 의존성
└── README.md                 # 이 문서
```

## 설치 및 실행

### 방법 1: Docker 사용 (권장)

#### 1. Docker 이미지 빌드
```bash
./build_docker.sh
```

#### 2. Docker 컨테이너 실행
```bash
./launch_docker.sh
```

기본 설정:
- 포트: `6783`
- Gremsy IP: `192.168.12.240` (환경변수로 변경 가능)

환경변수를 수정하려면 `launch_docker.sh` 파일을 편집하거나:
```bash
docker run -it --rm --name gremsy_api \
  --network host \
  -e PORT=6783 \
  -e GREMSY_IP="192.168.12.240" \
  docker.argusvision.io/intel/krm-gremsy-api:0.3.0-start
```

### 방법 2: 로컬 환경에서 실행

#### 1. Python 가상 환경 생성
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

#### 3. 설정 변경
`app/libs/config.py` 파일에서 Gremsy 페이로드 IP 주소를 수정:
```python
UDP_IP_TARGET = "192.168.12.240"  # 실제 페이로드 IP로 변경
```

#### 4. 애플리케이션 실행
```bash
cd app
python app.py
```

서버는 기본적으로 `http://0.0.0.0:6783`에서 실행됩니다.

## API 문서

### 기본 엔드포인트

```bash
GET /
# 서버 상태 확인
```

### 카메라 제어 (`/camera`)

#### 줌 제어
```bash
# 스텝 줌
POST /camera/zoom/step
Content-Type: application/json
{"zoomDirection": 1}  # 1: Zoom In, -1: Zoom Out

# 연속 줌
POST /camera/zoom/continuous
Content-Type: application/json
{"zoomDirection": 1.0}

# 레인지 줌 (퍼센트)
POST /camera/zoom/range
Content-Type: application/json
{"zoomPercentage": 50.0}  # 0-100
```

#### 포커스 제어
```bash
# 포커스 모드 설정
POST /camera/focus/set-mode
Content-Type: application/json
{"focusMode": 1}  # 0: Manual, 1: Auto

# 연속 포커스
POST /camera/focus/continuous
Content-Type: application/json
{"focusDirection": 1.0}

# 오토 포커스
POST /camera/focus/auto
```

#### 이미지 캡처 및 녹화
```bash
# 이미지 캡처
POST /camera/capture-image

# 캡처 중지
POST /camera/stop-capture

# 녹화 시작
POST /camera/start-record

# 녹화 중지
POST /camera/stop-record
```

#### 카메라 설정
```bash
# 뷰 소스 변경
POST /camera/change-view-src
Content-Type: application/json
{"viewSrc": 1}  # 0: EO, 1: IR, 2: PIP

# IR 팔레트 설정
POST /camera/set-ir-palette
Content-Type: application/json
{"irPalette": 9}

# OSD 모드 설정
POST /camera/set-osd-mode
Content-Type: application/json
{"osdMode": 1}

# 플립 모드 설정
POST /camera/set-flip-mode
Content-Type: application/json
{"flipMode": 0}  # 0: Normal, 1: Horizontal, 2: Vertical, 3: Both
```

#### ICR (Infrared Cut filter Removal) 제어
```bash
# ICR 모드 설정
POST /camera/icr/set-mode
Content-Type: application/json
{"icrMode": 0}  # 0: AUTO, 1: MANUAL

# 수동 ICR 제어
POST /camera/icr/set-manual-control
Content-Type: application/json
{"manualState": 1}  # 0: OFF, 1: ON

# ICR 임계값 설정
POST /camera/icr/set-threshold
Content-Type: application/json
{"threshold": 128}  # 0-255
```

#### FFC (Flat Field Correction) 제어
```bash
# FFC 모드 설정
POST /camera/set-ffc-mode
Content-Type: application/json
{"ffcMode": 1}

# FFC 트리거
POST /camera/trigger-ffc
```

### 짐벌 제어 (`/gimbal`)

```bash
# Follow 모드로 전환
POST /gimbal/follow

# Reset 모드로 전환
POST /gimbal/reset

# 짐벌 정지
POST /gimbal/stop

# RC 모드 설정
POST /gimbal/set-rc-mode
Content-Type: application/json
{"rcMode": 0}  # 0: Standard, 1: Gremsy

# 자이로 캘리브레이션
POST /gimbal/calib-gyro

# 가속도 캘리브레이션
POST /gimbal/calib-accel

# 모터 캘리브레이션
POST /gimbal/calib-motor

# 홈 위치 탐색
POST /gimbal/search-home

# 오토 튠
POST /gimbal/auto-tune
Content-Type: application/json
{"status": true}
```

### 상태 조회 (`/status`)

```bash
# 모든 상태 조회
GET /status/all

# 특정 파라미터 조회
GET /status/<param_name>
# 예: GET /status/PARAM_EO_ZOOM_LEVEL

# 자세 정보 조회
GET /status/attitude

# LRF 디버그 정보
GET /status/lrf_debug

# Heading Preset 설정
POST /status/heading_preset
Content-Type: application/json
{"degree": 90.0}

# Heading Preset 조회
GET /status/heading_preset

# Ego Pose (로봇 기준 자세) 조회
GET /status/ego_pose
# 응답: {"ego_yaw": -45.2, "ego_pitch": 12.3}

# LRF 3D 좌표 조회
GET /status/lrf_coords
# 응답: {"x": 3.5, "y": 1.2, "z": -0.8, "source_data": {...}}
```

### SDK 디버그

```bash
# SDK 디버깅 정보 조회
GET /debug/sdk_info
```

## 좌표계 및 계산

### 로봇 기준 좌표계 (Right-Handed)

- **X축**: 로봇 정면 방향
- **Y축**: 로봇 왼쪽 방향
- **Z축**: 로봇 아래 방향

### Heading Preset

카메라가 로봇에 장착된 각도를 설정합니다:
- `0°`: 로봇과 같은 방향
- `-90°`: 로봇 기준 왼쪽 90도
- `+90°`: 로봇 기준 오른쪽 90도

### LRF 3D 좌표 변환

LRF 거리 데이터와 카메라 자세(yaw, pitch)를 사용하여 로봇 기준 3D 좌표를 계산:

```
x = distance × cos(pitch) × cos(yaw)
y = distance × cos(pitch) × sin(yaw)
z = distance × sin(pitch)
```

## 설정

### 환경 변수

- `PORT`: Flask 서버 포트 (기본값: `6783`)
- `GREMSY_IP`: Gremsy 페이로드 IP 주소 (기본값: `192.168.12.240`)

### SDK 설정

`app/libs/config.py` 파일에서 다양한 설정을 변경할 수 있습니다:

- 연결 방법 (UDP/UART)
- MAVLink 시스템 ID
- 카메라 및 짐벌 설정
- 타임아웃 및 레이트 설정

## 애플리케이션 동작 방식

1. **백그라운드 SDK 스레드**: 애플리케이션 시작 시 Gremsy Payload SDK 연결 초기화
2. **콜백 등록**: 페이로드로부터 실시간 데이터 수신
3. **짐벌 초기화**: RESET → FOLLOW 모드로 자동 초기화
4. **Flask 서버**: HTTP API 요청을 SDK 명령으로 변환
5. **상태 동기화**: 페이로드 상태를 메모리에 캐시하여 빠른 조회 제공

## 의존성

주요 Python 패키지:
- `flask`: 웹 프레임워크
- `pymavlink`: MAVLink 프로토콜 지원
- `numpy`: 수치 계산
- `pyserial`: 시리얼 통신
- `paho-mqtt`: MQTT 클라이언트
- `requests`: HTTP 클라이언트

전체 의존성은 `requirements.txt` 참조

## 문제 해결

### 연결 실패

1. Gremsy 페이로드 IP가 올바른지 확인:
```bash
ping 192.168.12.240
```

2. 방화벽이 포트 14566(MAVLink)를 허용하는지 확인

3. 로그 확인:
```bash
# Docker 컨테이너 로그
docker logs gremsy_api

# 로컬 실행 시 콘솔 출력 확인
```

### LRF 데이터 수신 안 됨

1. 페이로드가 LRF를 지원하는지 확인 (VIO 페이로드)
2. LRF 디버그 엔드포인트 확인:
```bash
curl http://localhost:6783/status/lrf_debug
```

### SDK 연결 문제

1. SDK 디버그 정보 확인:
```bash
curl http://localhost:6783/debug/sdk_info
```

2. `app/libs/config.py`에서 연결 방법 확인 (UDP/UART)

## 개발 정보

- **SDK 버전**: 3.0.0_build.27052025
- **MAVLink 프로토콜**: 2.0
- **Flask 포트**: 6783 (기본값)
- **Payload 타입**: VIO

## 라이선스

이 프로젝트는 Gremsy Payload SDK를 기반으로 합니다.

## 참고

- Gremsy Payload SDK 상세 문서는 원본 SDK의 `PayloadSDK.md` 참조
- MAVLink 프로토콜: https://mavlink.io/
