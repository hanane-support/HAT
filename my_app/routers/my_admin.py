# my_app/routers/my_admin.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..models.my_database import MySettings, MyTradeLog, SessionLocal
from typing import List, Optional

router = APIRouter()

# --- 의존성 주입 함수 ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Pydantic 스키마 정의 ---
class SettingsBase(BaseModel):
    exchange_api_key: str
    exchange_secret_key: str
    strategy_name: str
    risk_per_trade: float
    is_active: bool

class TradeLogResponse(BaseModel):
    order_id: str
    symbol: str
    side: str
    executed_price: float
    executed_qty: float
    log_time: str # JSON 직렬화를 위해 문자열로 처리

# --- 설정 API ---
@router.post("/settings")
def update_settings(settings: SettingsBase, db: Session = Depends(get_db)):
    """봇 작동 설정을 업데이트하거나 새로 생성합니다."""
    db_settings = db.query(MySettings).first()
    
    if db_settings:
        # 설정 업데이트
        for key, value in settings.dict(exclude_unset=True).items():
            setattr(db_settings, key, value)
    else:
        # 설정 생성
        db_settings = MySettings(**settings.dict())
        db.add(db_settings)
        
    db.commit()
    db.refresh(db_settings)
    return {"message": "Settings updated successfully", "data": db_settings}

@router.get("/settings")
def get_settings(db: Session = Depends(get_db)):
    """현재 봇 설정을 조회합니다."""
    settings = db.query(MySettings).first()
    if settings is None:
        raise HTTPException(status_code=404, detail="Settings not found. Please initialize settings.")
    return settings

# --- 상태 API (간단 버전) ---
# NOTE: 실제 코어 상태는 trade_core.py에서 상태 파일을 주기적으로 업데이트하거나, Redis를 통해 관리하는 것이 좋습니다.
@router.get("/status")
def get_bot_status():
    """봇의 현재 작동 상태를 조회합니다."""
    # my_core.py가 살아있는지 확인하는 로직 (systemd/Supervisor 상태 확인)이 필요함
    # 여기서는 임시 상태를 반환합니다.
    return {
        "is_core_running": True, 
        "last_trade_time": "2025-10-21T18:00:00Z", 
        "current_balance": 10000.00,
        "message": "Core process is running and monitoring trade signals."
    }

# --- 로그 API ---
@router.get("/logs", response_model=List[TradeLogResponse])
def get_trade_logs(
    limit: int = 10, 
    offset: int = 0, 
    db: Session = Depends(get_db)
):
    """매매 기록을 페이징하여 반환합니다."""
    logs = db.query(MyTradeLog)\
             .order_by(desc(MyTradeLog.log_time))\
             .offset(offset)\
             .limit(limit)\
             .all()
             
    # Pydantic 모델에 맞게 데이터 변환 (날짜 처리)
    response_logs = [
        TradeLogResponse(
            order_id=log.order_id,
            symbol=log.symbol,
            side=log.side,
            executed_price=log.executed_price,
            executed_qty=log.executed_qty,
            # 날짜를 ISO 8601 문자열로 변환
            log_time=log.log_time.isoformat() if log.log_time else ""
        ) for log in logs
    ]

    return response_logs