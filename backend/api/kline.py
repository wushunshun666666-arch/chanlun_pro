from fastapi import APIRouter, HTTPException
from ..data.akshare_fetcher import get_kline
import pandas as pd

router = APIRouter()

@router.get('/{ts_code}')
def get_kline_endpoint(ts_code: str, timeframe: str = 'D', count: int = 500):
    df = get_kline(ts_code, timeframe=timeframe, count=count)
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail='no data')
    # return json-friendly format
    df2 = df.reset_index()
    df2['date'] = df2['date'].astype(str)
    return {'ts_code': ts_code, 'timeframe': timeframe, 'data': df2.to_dict(orient='records')}
