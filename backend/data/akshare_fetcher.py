import os
import pandas as pd
import numpy as np
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def _ak_symbol_from_ts(ts_code: str) -> str:
    # ts_code like 600000.SH or 000001.SZ -> symbol without suffix
    return ts_code.split('.')[0]


def get_kline(ts_code: str, timeframe: str = 'D', count: int = 500):
    """
    timeframe: 'D' daily, 'W' weekly, 'M' monthly, '1m' minute(not for scan)
    returns DataFrame indexed by datetime with columns open, high, low, close, vol
    """
    import akshare as ak
    symbol = _ak_symbol_from_ts(ts_code)
    timeframe = timeframe.upper()
    if timeframe == 'D':
        df = ak.stock_zh_a_hist(symbol=symbol, period='daily', adjust='')
    elif timeframe == 'W':
        df = ak.stock_zh_a_hist(symbol=symbol, period='weekly', adjust='')
    elif timeframe == 'M':
        df = ak.stock_zh_a_hist(symbol=symbol, period='monthly', adjust='')
    else:
        # for minutes or intraday, use minute endpoint
        if timeframe.endswith('M') or timeframe.endswith('m'):
            per = '1' if timeframe in ('1M','1m') else '5' if timeframe in ('5M','5m') else '1'
            df = ak.stock_zh_a_minute(symbol=symbol, period=per)
        else:
            raise ValueError('unsupported timeframe')

    if df is None or df.empty:
        return pd.DataFrame()

    # normalize column names
    # akshare daily returns 日期 开盘 最高 最低 收盘 成交量 ...
    col_map = {}
    for c in df.columns:
        if '日期' in c or '时间' in c:
            col_map[c] = 'date'
        elif '开盘' in c:
            col_map[c] = 'open'
        elif '最高' in c:
            col_map[c] = 'high'
        elif '最低' in c:
            col_map[c] = 'low'
        elif '收盘' in c:
            col_map[c] = 'close'
        elif '成交量' in c or '成交量(手)' in c:
            col_map[c] = 'vol'
    df = df.rename(columns=col_map)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').set_index('date')
    else:
        # some minute endpoints already have datetime index
        try:
            df.index = pd.to_datetime(df.index)
        except Exception:
            pass
    # ensure numeric
    for col in ['open','high','low','close','vol']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df[['open','high','low','close','vol']].tail(count)
