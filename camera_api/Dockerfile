# Dockerfile
FROM docker.argusvision.io/intel/krm-gremsy-api:0.3.0-dev AS gremsy_api

# 작업 디렉토리 설정
WORKDIR /app

# 환경변수 기본값 설정

# Python 애플리케이션 실행
CMD ["sh", "-c", "cd /app/app && python app.py"] 
