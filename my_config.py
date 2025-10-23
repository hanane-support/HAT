# my_config.py
from pydantic import BaseModel

# 서버 설정 값을 담을 Pydantic 모델
class MyGlobalSettings(BaseModel):
    # 초기 설정 값
    webhook_secret: str = "DEFAULT_SECRET_KEY" 
    admin_user: str = "admin"
    admin_pass: str = "your_secure_password_1234"
    port: int = 8000

# 서버 메모리에 저장될 전역 설정 객체
my_settings = MyGlobalSettings()