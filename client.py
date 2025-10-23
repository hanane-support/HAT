# client.py 파일 내용
import requests

BASE_URL = "http://127.0.0.1:8000"

def access_endpoint(path):
    url = f"{BASE_URL}{path}"
    try:
        response = requests.get(url)
        print(f"\n--- 접속 경로: {path} ---")
        print(f"HTTP 상태 코드: {response.status_code}")
        if response.status_code == 200:
            print("응답 데이터:", response.json())
        else:
            print("접속 실패: 서버 오류 발생")

    except requests.exceptions.RequestException:
        print(f"\n[오류] 서버에 연결할 수 없습니다. 서버가 8000번 포트에서 실행 중인지 확인하세요.")

access_endpoint("/")
access_endpoint("/admin")