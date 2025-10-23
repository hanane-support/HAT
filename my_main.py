from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import json

# FastAPI 애플리케이션 인스턴스 생성
my_app = FastAPI(
    title="my_AutoBot API Admin",
    description="TradingView Webhook Receiver and AutoTrader Backend.",
    version="1.0.0",
    # ⭐ 수정 1: API 문서(Swagger UI) 비활성화
    docs_url=None, 
    # ⭐ 수정 2: 레드oc UI도 비활성화 (문서 관련 기능 모두 제거)
    redoc_url=None
)

my_templates = Jinja2Templates(directory="my_templates")

# --- 1. 웹훅 수신 엔드포인트 (POST) ---
# ... (이 부분은 이전과 동일합니다) ...

@my_app.post("/my_webhook") 
async def receive_my_webhook(request: Request):
    """
    트레이딩뷰 웹훅 데이터를 수신하는 엔드포인트입니다.
    """
    try:
        data = await request.json()
        print(f"웹훅 수신 데이터: {json.dumps(data, indent=4)}")
        return {"status": "success", "message": "Webhook processed successfully", "data": data}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        print(f"웹훅 처리 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


# --- 2. 관리자/대시보드 엔드포인트 (GET) ---

# ⭐ 수정 3: 기본 경로 '/' 대신 '/admin' 경로로 변경
@my_app.get("/admin")
async def my_home(request: Request):
    """
    봇의 상태를 보여주는 간단한 HTML 대시보드입니다.
    """
    context = {
        "request": request,
        "title": "my_AutoBot Dashboard",
        # 문서 URL이 비활성화되었으므로 이 변수는 이제 사용되지 않습니다.
        "api_doc_url": None 
    }
    return my_templates.TemplateResponse("my_index.html", context) 

# --- 3. 애플리케이션 실행 (로컬 테스트용) ---

if __name__ == "__main__":
    uvicorn.run("my_main:my_app", host="0.0.0.0", port=9000, reload=True)