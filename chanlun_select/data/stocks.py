import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


def get_all_a_shares(exclude_st=True):
    """
    Return a list of ts_code strings like '600000.SH' or '000001.SZ' for all A shares.
    If exclude_st=True, filter out names containing 'ST' or '*ST' (case-insensitive).
    Tries tushare first (if token provided), otherwise akshare.
    """
    tushare_token = os.getenv('TUSHARE_TOKEN')
    df = None
    if tushare_token:
        try:
            import tushare as ts
            ts.set_token(tushare_token)
            pro = ts.pro_api()
            df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
            if df is not None and not df.empty:
                # ts_code is like 600000.SH already
                if exclude_st:
                    df = df[~df['name'].str.contains('ST|\*ST', na=False, case=False)]
                return df['ts_code'].tolist()
        except Exception:
            df = None
    # fallback to akshare
    try:
        import akshare as ak
        all_stocks = ak.stock_info_a_shares()
        # akshare returns columns '代码' and '名称'
        if '代码' in all_stocks.columns and '名称' in all_stocks.columns:
            if exclude_st:
                filtered = all_stocks[~all_stocks['名称'].str.contains('ST|\*ST', na=False, case=False)]
            else:
                filtered = all_stocks
            def to_ts_code(code):
                s = str(code).zfill(6)
                return f"{s}.SZ" if s.startswith(('0','3')) else f"{s}.SH"
            return [to_ts_code(c) for c in filtered['代码'].tolist()]
    except Exception as e:
        raise RuntimeError('failed to get A share list: ' + str(e))
    raise RuntimeError('no provider available to fetch A share list')
