# my_app/my_core.py

import asyncio
import time
import os
from sqlalchemy.orm import Session
from sqlalchemy import text
from dotenv import load_dotenv
import httpx # 비동기 HTTP 클라이언트

from .models.my_database import MyTradeSignal, MyTradeLog, MySettings, SessionLocal

# .env 파일 로드
load_dotenv()

# --- DB 세션 관리 ---
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

# --- 핵심 로직 ---
async def process_signal(db: Session, signal: MyTradeSignal, settings: MySettings):
    """개별 매매 신호를 처리하고 거래소 API에 주문을 요청합니다."""
    print(f"💡 Processing signal ID: {signal.id} - {signal.symbol} {signal.action}")

    # 1. 거래소 API 통신 (Asyncio 및 httpx 사용)
    # 실제로는 거래소 API 라이브러리를 사용하며, 인증 및 복잡한 주문 로직이 들어갑니다.
    async with httpx.AsyncClient(timeout=10) as client:
        # TODO: 실제 거래소 API 엔드포인트와 인증 키를 사용
        
        # 임시 주문 시뮬레이션
        is_order_success = True
        
        if is_order_success:
            order_id = f"ORDER_{int(time.time() * 1000)}_{signal.id}"
            executed_price = signal.price if signal.price else 100.0 # 예시
            executed_qty = 0.01
            
            # 2. 거래 로그 저장
            trade_log = MyTradeLog(
                signal_id=signal.id,
                order_id=order_id,
                symbol=signal.symbol,
                side=signal.action,
                executed_price=executed_price,
                executed_qty=executed_qty,
                fee=executed_price * executed_qty * 0.0005 # 예시 수수료
            )
            db.add(trade_log)

            # 3. 신호 처리 상태 업데이트
            signal.is_processed = True
            signal.processed_at = datetime.utcnow()
            db.commit()
            
            print(f"✅ Trade executed: {order_id} on {signal.symbol}. Log saved.")
        else:
            print(f"❌ Order failed for signal ID: {signal.id}.")

async def my_trading_core_loop():
    """자동매매 코어의 메인 비동기 루프 (DB Polling)"""
    print("🤖 HATB Core Loop started...")
    
    while True:
        db = get_db()
        try:
            # 1. 설정 확인 (봇이 활성 상태인지)
            settings = db.query(MySettings).filter(MySettings.is_active == True).first()
            if not settings:
                print("⏸️ Bot is not active. Waiting...")
                await asyncio.sleep(5) # 5초 대기
                continue

            # 2. 미처리된 신호 Polling (최신 신호 5개만 가져오기)
            unprocessed_signals = db.query(MyTradeSignal)\
                                    .filter(MyTradeSignal.is_processed == False)\
                                    .order_by(MyTradeSignal.webhook_time.asc())\
                                    .limit(5).all()

            if unprocessed_signals:
                print(f"🔎 Found {len(unprocessed_signals)} new signals to process.")
                
                # 비동기로 신호 처리
                tasks = [process_signal(db, signal, settings) for signal in unprocessed_signals]
                await asyncio.gather(*tasks)
            else:
                # print("💤 No new signals. Polling in 1 second...")
                pass
            
            # DB Polling 간격
            await asyncio.sleep(1) # 1초마다 확인 (요청에 따라 1~5초)

        except Exception as e:
            print(f"🚨 An error occurred in core loop: {e}")
            await asyncio.sleep(5) # 에러 발생 시 5초 대기
        finally:
            db.close()

if __name__ == '__main__':
    from datetime import datetime
    try:
        # DB 테이블이 생성되어 있는지 확인 (개발 편의를 위해)
        print("Starting core. Ensuring database connection.")
        # NOTE: 실제 운영 환경에서는 systemd/supervisor가 DB를 관리
        
        asyncio.run(my_trading_core_loop())
    except KeyboardInterrupt:
        print("\n👋 HATB Core Loop stopped by user.")