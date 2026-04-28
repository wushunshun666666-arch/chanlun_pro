from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db.session import SessionLocal
from ..db.models import CciSignal
from typing import List

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get('/')
def list_signals(date: str = None, timeframe: str = None, db: Session = Depends(get_db)) -> List[dict]:
    q = db.query(CciSignal)
    if date:
        from datetime import datetime
        d = datetime.strptime(date, '%Y-%m-%d').date()
        q = q.filter(CciSignal.signal_date == d)
    if timeframe:
        q = q.filter(CciSignal.timeframe == timeframe.upper())
    rows = q.order_by(CciSignal.created_at.desc()).limit(1000).all()
    return [
        {
            'id': r.id,
            'stock_code': r.stock_code,
            'stock_name': r.stock_name,
            'signal_type': r.signal_type,
            'timeframe': r.timeframe,
            'signal_date': str(r.signal_date),
            'created_at': str(r.created_at),
            'meta': r.meta
        } for r in rows
    ]

@router.get('/{signal_id}')
def get_signal(signal_id: int, db: Session = Depends(get_db)):
    row = db.query(CciSignal).filter(CciSignal.id == signal_id).first()
    if not row:
        raise HTTPException(status_code=404, detail='not found')
    return {
        'id': row.id,
        'stock_code': row.stock_code,
        'stock_name': row.stock_name,
        'signal_type': row.signal_type,
        'timeframe': row.timeframe,
        'signal_date': str(row.signal_date),
        'created_at': str(row.created_at),
        'meta': row.meta
    }
