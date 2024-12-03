import torch
import cv2
from ultralytics import YOLO
import threading # 추론을 비동기적으로 실행하기 위한 쓰레드.

class MultiStreamYOLOInference:
    def __init__(self, model_path, device='cuda' if torch.cuda.is_available() else 'cpu'):
        """
        YOLO 다중 스트림 추론 클래스 초기화.

        Args:
            model_path (str): YOLO 모델 파일의 경로.
            device (str): 추론을 실행할 디바이스 ('cuda' 또는 'cpu').
        """
        self.model = YOLO(model_path).to(device)  # YOLO 모델 로드
        self.device = device  # 디바이스 설정
        self.streams = {}  # 스트림을 관리하는 딕셔너리
        self.confidence_threshold = 0.3

    def process_frame(self, frame):
        """
        단일 프레임을 처리하고 감지 결과를 반환.

        Args:
            frame (numpy.ndarray): 입력 프레임.

        Returns:
            list: 감지된 객체들의 리스트.
        """

        with torch.no_grad():
            results = self.model.predict(
                source=frame, 
                conf=self.confidence_threshold,
                iou = 0.5,
                half=True,
                # classes = [0],
                show=False,
                verbose=True # False
            )  # 오직 detection 만을 진행.

        detections = [] #모델의 추론 결과에서 각 객체 정보 추출
        result = results[0]
        for box in result.boxes:
            conf = box.conf[0]
            xywh = box.xywhn.detach().cpu().numpy().tolist()[0]
            detection = {

                'cls':'class_name', # 클래스 이름
                "conf": round(float(conf),4),  # 물체 신뢰도 
                "xywh": [round(i,6) for i in  xywh] # 물체 좌표값
            }
            detections.append(detection)
        return detections
    
    def _inference_thread(self, stream_url):
        """
        특정 스트림에서 추론을 실행하는 쓰레드.

        Args:
            stream_url (str): RTSP 스트림 또는 비디오 파일 URL.
        """
        cap = cv2.VideoCapture(stream_url)  # 비디오 스트림 열기
        if not cap.isOpened():  # 스트림 열기 실패 시 오류 출력
            print(f'Error: Could not open video stream {stream_url}')
            self.streams[stream_url]["running"] = False
            return

        while self.streams[stream_url]["running"]:  # 스트림 실행 중일 때
            ret, frame = cap.read()  # 프레임 읽기
            if not ret:  # 프레임 읽기 실패 시 종료
                print(f'Failed to grab frame from {stream_url}')
                break

            detections = self.process_frame(frame)  # 프레임에서 객체 감지
            print(f"Stream [{stream_url}] Detections:", detections)  # 감지 결과 출력

        cap.release()  # 비디오 스트림 닫기
        print(f"Stream [{stream_url}] stopped.")  # 스트림 종료 메시지

    def start_stream(self, stream_url):
        """
        특정 스트림에서 추론 시작.

        Args:
            stream_url (str): RTSP 스트림 또는 비디오 파일 URL.
        """
        if stream_url not in self.streams:  # 스트림이 아직 추가되지 않았으면
            self.streams[stream_url] = {
                "running": True,  # 실행 상태 # 추론 실행 여부를 나타내는 플래그 : 이 플래그를 통해서 모델을 처리에 대한 명제임. False 이면 추론을 동작 안하고, True 이면 추론이 동작함.
                "thread": threading.Thread(target=self._inference_thread, args=(stream_url,))  # 쓰레드 생성
            }
            self.streams[stream_url]["thread"].start()  # 쓰레드 실행

    def stop_stream(self, stream_url):
        """
        특정 스트림에서 추론 중지.

        Args:
            stream_url (str): RTSP 스트림 또는 비디오 파일 URL.
        """
        if stream_url in self.streams:  # 해당 스트림이 존재하면
            self.streams[stream_url]["running"] = False  # 실행 상태 해제
            self.streams[stream_url]["thread"].join()  # 쓰레드 종료 대기
            del self.streams[stream_url]  # 스트림 데이터 삭제

    def stop_all_streams(self):
        """
        모든 스트림에서 추론 중지.
        """
        for stream_url in list(self.streams.keys()):  # 모든 스트림 URL에 대해 반복
            self.stop_stream(stream_url)  # 각 스트림 중지

# 사용 예제
if __name__ == "__main__":
    model_path = "best.pt"  # 학습된 모델 파일 경로
    model_path = "yolo11n.pt"
    stream_urls = [
        "rtsp://stream1:port1",  # 스트림 URL 1
        "rtsp://stream2:port2",  # 스트림 URL 2
    ]

    yolo = MultiStreamYOLOInference(model_path)  # YOLO 추론 클래스 인스턴스 생성
    try:
        print("Starting YOLO Inference for multiple streams...")
        for url in stream_urls:
            yolo.start_stream(url)  # 각 스트림에 대해 추론 시작
        input("Press Enter to stop all streams...\n")  # 엔터를 누르면 모든 스트림 종료
    finally:
        yolo.stop_all_streams()  # 모든 스트림 중지
        print("All streams stopped.")  # 종료 메시지 출력
