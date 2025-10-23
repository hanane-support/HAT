# my_main.py
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette.status import HTTP_302_FOUND
import uvicorn
from starlette.middleware.sessions import SessionMiddleware # 세션 관리를 위한 미들웨어

from my_config import my_settings, MyGlobalSettings 

# 서버 시작 시간 기록
MY_SERVER_START_TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# config.py의 포트를 기본값으로 사용
PORT = my_settings.port 
app = FastAPI()

# 🔑 세션 미들웨어 설정 (실제 환경에서는 더 강력한 암호화 키를 사용해야 합니다)
app.add_middleware(SessionMiddleware, secret_key="a_very_secure_secret_for_session")

# Jinja2 템플릿 설정
templates = Jinja2Templates(directory="my_templates")

# Pydantic 모델: 트레이딩뷰 웹훅 데이터 구조 정의
class MyWebhookPayload(BaseModel):
    action: str
    symbol: str
    price: float = None
    secret: str 

# ===========================
#  의존성 함수 (인증)
# ===========================

# 인증 상태 확인 의존성 함수
def my_get_current_admin(request: Request):
    # 요청 세션에서 사용자 ID를 확인
    if not request.session.get("user_id"):
        # 인증되지 않은 경우 로그인 페이지로 리디렉션
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)
    return True # 인증 성공

# ===========================
#  웹훅 엔드포인트
# ===========================

@app.post("/webhook")
async def my_handle_webhook(payload: MyWebhookPayload):
    # 1. 웹훅 시크릿 키 검증
    if payload.secret != my_settings.webhook_secret:
        raise HTTPException(status_code=401, detail="Unauthorized Webhook Secret")
    
    print(f"✅ Webhook Received: {payload.symbol} - {payload.action}")
    
    # TODO: 여기에 Upbit 주문 로직을 구현합니다.

    return {"message": "Webhook received and verified. Order processing initiated."}

# ===========================
#  관리자 페이지 (Admin)
# ===========================

# 관리자 대시보드
@app.get("/admin", response_class=HTMLResponse)
async def my_admin_dashboard(request: Request, authenticated: bool = Depends(my_get_current_admin)):
    if isinstance(authenticated, RedirectResponse):
        return authenticated
        
    context = {
        "request": request,
        "user": my_settings.admin_user, 
        "port": PORT,
        "start_time": MY_SERVER_START_TIME
    }
    return templates.TemplateResponse("my_admin.html", context)

# 로그인 페이지 (GET)
@app.get("/admin/login", response_class=HTMLResponse)
async def my_login_page(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse(url="/admin", status_code=HTTP_302_FOUND)
        
    return templates.TemplateResponse("my_login.html", {"request": request, "error": None})

# 로그인 처리 (POST)
@app.post("/admin/login")
async def my_process_login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == my_settings.admin_user and password == my_settings.admin_pass: 
        request.session["user_id"] = username # 세션에 사용자 ID 저장
        return RedirectResponse(url="/admin", status_code=HTTP_302_FOUND)
    else:
        return templates.TemplateResponse("my_login.html", {"request": request, "error": "Invalid username or password"})

# 🛠️ 관리자 설정 페이지 (GET)
@app.get("/admin/settings", response_class=HTMLResponse)
async def my_settings_page(request: Request, authenticated: bool = Depends(my_get_current_admin)):
    if isinstance(authenticated, RedirectResponse):
        return authenticated
        
    context = {
        "request": request,
        "settings": my_settings,
        "message": None
    }
    return templates.TemplateResponse("my_settings.html", context)

# 💾 관리자 설정 업데이트 (POST)
@app.post("/admin/settings")
async def my_update_settings(
    request: Request,
    authenticated: bool = Depends(my_get_current_admin),
    webhook_secret: str = Form(...),
    admin_user: str = Form(...),
    admin_pass: str = Form(...)
):
    if isinstance(authenticated, RedirectResponse):
        return authenticated
        
    # 전역 설정 객체 업데이트
    my_settings.webhook_secret = webhook_secret
    my_settings.admin_user = admin_user
    
    if admin_pass: 
        my_settings.admin_pass = admin_pass

    context = {
        "request": request,
        "settings": my_settings,
        "message": "설정이 성공적으로 업데이트되었습니다. (서버 재시작 시 초기화됩니다!)"
    }
    return templates.TemplateResponse("my_settings.html", context)

# 로그아웃 처리
@app.get("/admin/logout")
async def my_admin_logout(request: Request):
    request.session.pop("user_id", None)
    return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)

if __name__ == "__main__":
    uvicorn.run("my_main:app", host="0.0.0.0", port=PORT, reload=True)