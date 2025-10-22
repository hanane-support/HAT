# C:\Python\HATB\my_main.py

from fastapi import FastAPI, Request # Request 추가
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# 템플릿 폴더 지정
my_templates = Jinja2Templates(directory="my_templates")

my_app = FastAPI()

# 임시 관리자 페이지 경로
@my_app.get("/admin", response_class=HTMLResponse)
async def my_admin_page(request: Request):
    # Jinja2Templates를 사용하려면 request 객체가 필요합니다.
    return my_templates.TemplateResponse("my_admin.html", {"request": request, "title": "HATB Admin"})

# 웹훅을 받을 경로 (POST 메서드)
@my_app.post("/webhook")
async def my_tradingview_webhook():
    # 실제 웹훅 로직은 나중에 추가
    return {"status": "ok", "message": "Webhook received successfully (DUMMY)"}

# Vultr IP로 접속 시 초기 페이지
@my_app.get("/")
async def my_index():
    return {"message": "my_HATB Bot Server is Running."}

if __name__ == "__main__":
    import uvicorn
    # 포트를 9000으로 변경
    uvicorn.run("my_main:my_app", host="0.0.0.0", port=9000, reload=True)