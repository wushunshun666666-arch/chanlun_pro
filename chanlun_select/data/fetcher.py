import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv

load_dotenv()

class DataFetcher:
    def __init__(self):
        self.tushare_token = os.getenv('TUSHARE_TOKEN')
        self._ts_pro = None

    def _init_tushare(self):
        if not self._ts_pro:
            try:
                import tushare as ts
                ts.set_token(self.tushare_token)
                self._ts_pro = ts.pro_api()
            except Exception as e:
                raise RuntimeError('tushare init failed: ' + str(e))

    def get_daily(self, ts_code, start_date=None, end_date=None, count=500):
        """
        Return daily K-lines as DataFrame indexed by trade_date asc with columns [open, high, low, close, vol]
        Uses tushare if token available, otherwise attempts akshare.
        """
        if self.tushare_token:
            try:
                self._init_tushare()
                df = self._ts_pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
                if df is None or df.empty:
                    raise ValueError('empty from tushare')
                df = df.rename(columns={'trade_date':'date'})
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')
                df = df.set_index('date')
                return df[['open','high','low','close','vol']].tail(count)
            except Exception:
                # fallback to akshare
                pass
        try:
            import akshare as ak
            df = ak.stock_zh_a_hist(symbol=ts_code.split('.')[0], period='daily', adjust='qfq')
            if df is None or df.empty:
                raise ValueError('empty from akshare')
            df = df.rename(columns={'日期':'date','开盘':'open','最高':'high','最低':'low','收盘':'close','成交量':'vol'})
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            df = df.set_index('date')
            return df[['open','high','low','close','vol']].tail(count)
        except Exception as e:
            raise RuntimeError('no data source available: ' + str(e))

    def get_minute(self, ts_code, freq='1min', start=None, end=None, count=500):
        """Fetch minute-level K-lines. For tushare, use "tick"/intraday if available; otherwise use akshare.
        This implementation requests recent minutes and returns as DataFrame.
        """
        # Tushare pro has an endpoint stktick or intraday not universally available; try akshare first for simplicity
        try:
            import akshare as ak
            symbol = ts_code.split('.')[0]
            if freq == '1min':
                df = ak.stock_zh_a_minute(symbol=symbol, period='1')
            elif freq == '5min':
                df = ak.stock_zh_a_minute(symbol=symbol, period='5')
            else:
                df = ak.stock_zh_a_minute(symbol=symbol, period='1')
            if df is None or df.empty:
                raise ValueError('empty from akshare minute')
            df = df.rename(columns={'时间':'date','开盘':'open','最高':'high','最低':'low','收盘':'close','成交量':'vol'})
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            df = df.set_index('date')
            return df[['open','high','low','close','vol']].tail(count)
        except Exception:
            # attempt tushare (best-effort)
            if self.tushare_token:
                try:
                    self._init_tushare()
                    # tushare pro intraday data not always available; fall back to daily
                    df = self._ts_pro.daily(ts_code=ts_code)
                    df['date'] = pd.to_datetime(df['trade_date'])
                    df = df.set_index('date')
                    return df[['open','high','low','close','vol']].tail(count)
                except Exception as e:
                    raise RuntimeError('minute fetch failed: ' + str(e))
            raise RuntimeError('minute fetch no provider available')
