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
    docs_url="/my_admin/docs"  # API 문서 URL
)

# 템플릿 설정 (경로 이름은 my_templates)
my_templates = Jinja2Templates(directory="my_templates")

# --- 1. 웹훅 수신 엔드포인트 (POST) ---

@my_app.post("/my_webhook") 
async def receive_my_webhook(request: Request):
    """
    트레이딩뷰 웹훅 데이터를 수신하는 엔드포인트입니다.
    """
    try:
        data = await request.json()
        print(f"웹훅 수신 데이터: {json.dumps(data, indent=4)}")
        
        # TODO: 여기에 실제 자동 매매 실행 로직을 추가합니다.
        
        return {"status": "success", "message": "Webhook processed successfully", "data": data}
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        print(f"웹훅 처리 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


# --- 2. 관리자/대시보드 엔드포인트 (GET) ---

@my_app.get("/")
async def my_home(request: Request):
    """
    봇의 상태를 보여주는 간단한 HTML 대시보드입니다.
    """
    context = {
        "request": request,
        "title": "my_AutoBot Dashboard",
        "api_doc_url": my_app.docs_url
    }
    # 템플릿 파일 이름은 my_index.html
    return my_templates.TemplateResponse("my_index.html", context) 

# --- 3. 애플리케이션 실행 (로컬 테스트용) ---

if __name__ == "__main__":
    # 실행 시 my_main.py의 my_app 인스턴스를 9000 포트로 실행
    uvicorn.run("my_main:my_app", host="0.0.0.0", port=9000, reload=True)