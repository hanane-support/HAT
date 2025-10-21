# my_app/models/my_database.py

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, func
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

# --- 설정 (환경 변수 또는 .env 파일에서 로드) ---
DATABASE_URL = "postgresql://hatb_user:your_secure_password@localhost/hatb_db"

# --- 데이터베이스 연결 및 세션 ---
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- 모델 정의 ---

class MySettings(Base):
    """봇 설정 (API 키, 전략 파라미터 등)"""
    __tablename__ = "my_settings"

    id = Column(Integer, primary_key=True, index=True)
    exchange_api_key = Column(String, nullable=False)
    exchange_secret_key = Column(String, nullable=False)
    strategy_name = Column(String, default="default_strategy")
    risk_per_trade = Column(Float, default=0.01)  # 거래당 위험 비율
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MyTradeSignal(Base):
    """TradingView 웹훅 신호"""
    __tablename__ = "my_trade_signals"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    action = Column(String, nullable=False) # 'BUY' or 'SELL'
    price = Column(Float)
    webhook_time = Column(DateTime, default=datetime.utcnow)
    is_processed = Column(Boolean, default=False)
    processed_at = Column(DateTime, nullable=True)

class MyTradeLog(Base):
    """실제 매매 체결 기록"""
    __tablename__ = "my_trade_logs"

    id = Column(Integer, primary_key=True, index=True)
    signal_id = Column(Integer, nullable=True) # 어떤 신호로 발생했는지
    order_id = Column(String, index=True, nullable=False) # 거래소 주문 ID
    symbol = Column(String, index=True, nullable=False)
    side = Column(String, nullable=False) # 'BUY' or 'SELL'
    executed_price = Column(Float)
    executed_qty = Column(Float)
    fee = Column(Float)
    log_time = Column(DateTime, default=datetime.utcnow)

# --- 테이블 생성 함수 ---
def my_create_db_tables():
    """DB에 모든 테이블을 생성합니다."""
    # NOTE: Vultr User Data 스크립트에서 호출됩니다.
    Base.metadata.create_all(bind=engine)

if __name__ == '__main__':
    my_create_db_tables()
    print("Database tables created successfully!")