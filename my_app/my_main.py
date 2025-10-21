# my_app/my_main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os

from .routers import my_webhook, my_admin

# .env 파일 로드 (로컬 개발 환경용)
load_dotenv() 

# --- FastAPI 애플리케이션 인스턴스 ---
app = FastAPI(title="HATB Auto Trading Bot System")

# --- CORS 설정 ---
origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    # 배포 환경에서 관리자 페이지 접속 주소를 추가합니다 (예: 서버 IP)
    "*" 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 정적 파일 및 템플릿 설정 (관리자 페이지) ---
# NOTE: Nginx가 서빙할 예정이지만, 개발 편의상 FastAPI에 등록합니다.
app.mount("/static", StaticFiles(directory="my_admin_page/static"), name="static")
templates = Jinja2Templates(directory="my_admin_page/templates")

# --- 라우터 포함 ---
app.include_router(my_webhook.router, tags=["Webhook"])
app.include_router(my_admin.router, prefix="/api/v1", tags=["Admin API"])

# --- 관리자 페이지 라우트 ---
@app.get("/admin", name="admin_page")
async def my_admin_webpage(request: Request):
    """관리자 페이지 HTML을 반환합니다."""
    # Vultr User Data 스크립트를 통해 Nginx에서 /admin 으로 리버스 프록시 될 예정
    return templates.TemplateResponse(
        "my_admin.html", 
        {"request": request, "server_ip": request.client.host} # 서버 IP는 프록시 설정에 따라 변경될 수 있음
    )

@app.get("/")
async def my_root():
    return {"message": "HATB Auto Trading Bot is running. Access /admin for the management console."}