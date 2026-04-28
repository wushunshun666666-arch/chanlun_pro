from sqlalchemy import Column, Integer, String, Date, DateTime, func, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import JSON
from sqlalchemy.sql import expression

Base = declarative_base()

class CciSignal(Base):
    __tablename__ = 'cci_signals'
    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String, index=True, nullable=False)
    stock_name = Column(String, nullable=True)
    signal_type = Column(String, nullable=False)  # e.g., CCI_BREAK
    timeframe = Column(String, nullable=False)  # 'D'/'W'/'M'
    signal_date = Column(Date, nullable=False, index=True)
    meta = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('stock_code', 'timeframe', 'signal_date', name='uix_stock_timeframe_date'),
    )
