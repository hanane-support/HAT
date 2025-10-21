# my_app/routers/my_webhook.py

from fastapi import APIRouter, Header, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..models.my_database import MyTradeSignal, SessionLocal, my_create_db_tables
import os

router = APIRouter()

# --- 의존성 주입 함수 ---
def get_db():
    """데이터베이스 세션을 제공합니다."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 요청 바디 모델 ---
class MyWebhookMessage(BaseModel):
    """TradingView 웹훅 메시지 구조"""
    symbol: str
    action: str # 예: 'BUY', 'SELL'
    price: float | None = None
    secret: str # 보안 토큰

# --- 웹훅 엔드포인트 ---
@router.post("/webhook/tradingview")
async def receive_tradingview_webhook(
    message: MyWebhookMessage, 
    x_tradingview_token: str | None = Header(None), # 헤더의 보안 토큰 (옵션)
    db: Session = Depends(get_db)
):
    """
    TradingView 웹훅 신호를 수신하고 DB에 저장합니다.
    """
    # 1. 보안 검증 (Header 또는 Body의 secret 필드)
    # 실제 환경에서는 환경 변수에서 시크릿을 로드합니다.
    EXPECTED_SECRET = os.getenv("WEBHOOK_SECRET", "YOUR_DEFAULT_SECRET_TOKEN") 
    
    if message.secret != EXPECTED_SECRET and x_tradingview_token != EXPECTED_SECRET:
        raise HTTPException(status_code=401, detail="Invalid secret token")

    # 2. 신호 저장
    db_signal = MyTradeSignal(
        symbol=message.symbol,
        action=message.action,
        price=message.price
    )
    db.add(db_signal)
    db.commit()
    db.refresh(db_signal)

    print(f"✅ Webhook received and saved: ID {db_signal.id}, Symbol: {message.symbol}, Action: {message.action}")
    
    return {"message": "Webhook signal saved successfully", "signal_id": db_signal.id}