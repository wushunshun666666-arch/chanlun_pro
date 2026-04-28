import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from ..data.akshare_fetcher import get_kline
from ..indicators.cci import compute_cci
from ..cci_trend.cci_trend import detect_cci_trend_break
from ..db.session import SessionLocal
from ..db.models import CciSignal
from ..data.stocks import get_all_a_shares


def _scan_stock(ts_code: str, timeframe: str) -> dict:
    df = get_kline(ts_code, timeframe=timeframe, count=300)
    if df is None or df.empty or len(df) < 30:
        return None
    cci = compute_cci(df, n=14)
    res = detect_cci_trend_break(cci, dates=df.index.to_series())
    return res


def _insert_signal(db, ts_code: str, stock_name: str, timeframe: str, signal_date, meta: dict):
    s = CciSignal(
        stock_code=ts_code,
        stock_name=stock_name,
        signal_type='CCI_BREAK',
        timeframe=timeframe,
        signal_date=signal_date,
        meta=meta
    )
    try:
        db.add(s)
        db.commit()
        return True
    except IntegrityError:
        db.rollback()
        return False


def run_manual_scan(timeframes=['D']):
    # run a single scan across all A shares for given timeframes
    ts_list = get_all_a_shares(exclude_st=True)
    db = SessionLocal()
    results = []
    for tf in timeframes:
        # parallelize
        with ThreadPoolExecutor(max_workers=10) as ex:
            futures = {ex.submit(_scan_stock, ts, tf): ts for ts in ts_list}
            for fut in as_completed(futures):
                ts = futures[fut]
                try:
                    res = fut.result()
                    if res:
                        signal_date = res.get('signal_date')
                        if isinstance(signal_date, pd.Timestamp) or hasattr(signal_date, 'isoformat'):
                            signal_date = pd.to_datetime(signal_date).date()
                        elif isinstance(signal_date, str):
                            from datetime import datetime
                            signal_date = datetime.strptime(signal_date, '%Y-%m-%d').date()
                        # insert to DB with de-duplication
                        ok = _insert_signal(db, ts, '', tf, signal_date, res)
                        if ok:
                            results.append({'ts': ts, 'timeframe': tf, 'signal_date': str(signal_date)})
                except Exception:
                    pass
    db.close()
    return results


# APScheduler job wrapper
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Shanghai'))

# schedule: every trading day at 15:10
scheduler.add_job(lambda: run_manual_scan(['D','W','M']), CronTrigger(hour=15, minute=10))

def start_scheduler():
    scheduler.start()

def run_manual_scan_entry():
    return run_manual_scan(['D','W','M'])

# expose function for API
run_manual_scan = run_manual_scan_entry
