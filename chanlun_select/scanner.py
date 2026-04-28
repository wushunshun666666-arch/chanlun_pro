import os
import time
import logging
import argparse
from dotenv import load_dotenv
from .data.fetcher import DataFetcher
from .core.chanlun import analyze_daily_for_signals
from .data.stocks import get_all_a_shares
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def scan_stocks(stock_list, out_csv=None, batch_size=100, max_workers=10, pause_between_batches=1):
    fetcher = DataFetcher()
    results = []

    def worker(ts_code):
        df = fetcher.get_daily(ts_code, count=500)
        sig = analyze_daily_for_signals(df)
        return ts_code, sig

    total = len(stock_list)
    i = 0
    while i < total:
        batch = stock_list[i:i+batch_size]
        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            futures = {ex.submit(worker, ts): ts for ts in batch}
            for fut in as_completed(futures):
                ts = futures[fut]
                try:
                    ts_code, sig = fut.result()
                    if sig:
                        results.append({'ts_code': ts_code, 'signal': sig})
                except Exception as e:
                    logger.exception(f"Error scanning {ts}: {e}")
        i += batch_size
        if i < total:
            time.sleep(pause_between_batches)
    if out_csv:
        import pandas as pd
        pd.DataFrame(results).to_csv(out_csv, index=False)
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('scan', nargs='?', help='scan command', default='scan')
    parser.add_argument('--stocks', default='all', help="'all' or path to file with ts_code lines")
    parser.add_argument('--out', default=None)
    parser.add_argument('--batch-size', type=int, default=100)
    parser.add_argument('--max-workers', type=int, default=10)
    parser.add_argument('--pause', type=float, default=1.0, help='seconds to pause between batches')
    args = parser.parse_args()

    if args.stocks == 'all':
        try:
            stock_list = get_all_a_shares(exclude_st=True)
        except Exception:
            stock_list = []
    else:
        with open(args.stocks, 'r') as f:
            stock_list = [line.strip() for line in f if line.strip()]

    res = scan_stocks(stock_list, out_csv=args.out, batch_size=args.batch_size, max_workers=args.max_workers, pause_between_batches=args.pause)
    print(res)
