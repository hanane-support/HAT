from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import sys

# 로깅 설정
import logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# 라우터 임포트
from my_data_api import router as data_router
from my_settings_api import router as settings_router

# FastAPI 앱 초기화
app = FastAPI(title="TradingView Webhook Manager")

# 라우터 연결
app.include_router(data_router, tags=["Data & Webhook"])
app.include_router(settings_router, tags=["Settings & Management"])

# HTML 템플릿 로드 (같은 디렉토리에 my_admin_page.html이 있어야 함)
TEMPLATES = Jinja2Templates(directory=".")

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    """
    관리자 웹페이지를 제공합니다. (my_admin_page.html 로드)
    """
    try:
        # my_admin_page.html 파일을 템플릿으로 로드하여 응답
        return TEMPLATES.TemplateResponse("my_admin_page.html", {"request": request})
    except Exception as e:
        # 파일 로드 오류 시 HTML 응답
        return HTMLResponse(f"<h1>Error loading admin page: {e}</h1>", status_code=500)

# 로컬 테스트 시: uvicorn my_server:app --reload
