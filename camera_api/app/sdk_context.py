# sdk_context.py
from payload_sdk import PayloadSdkInterface
import threading 

class SDK_Data:
    def __init__(self):
        """
        애플리케이션 전체에서 공유될 SDK 인스턴스, 데이터 저장소, 스레드 Lock을
        싱글톤으로 관리하는 클래스.
        """
        self.sdk =  PayloadSdkInterface()
        self.data = {} # 페이로드 데이터를 저장할 중앙 저장소 
        self.lock = threading.Lock() # 스레드 동기화를 위한 Lock 

        # 로봇 헤딩 기준 카메라의 장착 각도 (기본값: 0도)
        # 이 값은 POST /status/heading_preset API를 통해 업데이트됩니다.
        self.preset_degree = 0.0
    
    # sdk.sdk로 접근하지않고 slef.sdk객체에서 그속성을 찾아서 반환.
    def __getattr__(self, name):
        """
        만약 SDK_Data 객체 자체에 없는 속성(name)을 호출하려고 하면,
        대신 내부의 self.sdk 객체에서 그 속성을 찾아 반환해줍니다.
        """
        return getattr(self.sdk, name)
        
# singletone instance로 만들어 어플리케이션 전체에 공유 
sdk = SDK_Data()
