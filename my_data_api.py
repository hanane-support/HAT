from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Any
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# 데이터 저장소 (인메모리)
webhook_data: List[Dict[str, Any]] = []
MAX_LOGS = 100

class WebhookPayload(BaseModel):
    # TradingView에서 전송되는 기본 JSON 메시지를 수신합니다.
    message: str

@router.post("/webhook")
async def receive_webhook(payload: WebhookPayload):
    """TradingView 웹훅을 수신하는 엔드포인트입니다."""
    now = datetime.now()
    timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")

    new_entry = {
        "timestamp": timestamp_str,
        "message": payload.message,
        "raw_data": payload.model_dump_json(indent=2)
    }

    # 최신 로그를 리스트 앞에 추가하고 최대 길이를 유지합니다.
    webhook_data.insert(0, new_entry)
    if len(webhook_data) > MAX_LOGS:
        webhook_data.pop()

    logger.info(f"[{timestamp_str}] Webhook Received: {payload.message[:50]}...")

    return {"status": "success", "timestamp": timestamp_str}

@router.get("/data")
async def get_webhook_data():
    """관리자 페이지용 웹훅 수신 데이터 제공."""
    # JSONResponse를 사용하여 리스트를 JSON 형식으로 반환합니다.
    return JSONResponse(content=webhook_data)
