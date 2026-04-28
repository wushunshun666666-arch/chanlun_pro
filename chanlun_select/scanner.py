import os
import time
import logging
import argparse
from dotenv import load_dotenv
from .data.fetcher import DataFetcher
from .core.chanlun import analyze_daily_for_signals

load_dotenv()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def scan_stocks(stock_list, out_csv=None):
    fetcher = DataFetcher()
    results = []
    for ts_code in stock_list:
        try:
            df = fetcher.get_daily(ts_code, count=500)
            sig = analyze_daily_for_signals(df)
            if sig:
                results.append({'ts_code': ts_code, 'signal': sig})
        except Exception as e:
            logger.exception(f"Error scanning {ts_code}: {e}")
    if out_csv:
        import pandas as pd
        pd.DataFrame(results).to_csv(out_csv, index=False)
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('scan', nargs='?', help='scan command', default='scan')
    parser.add_argument('--stocks', default='all', help="'all' or path to file with ts_code lines")
    parser.add_argument('--out', default=None)
    args = parser.parse_args()

    if args.stocks == 'all':
        try:
            from akshare import stock_info_a_shares
            all_stocks = stock_info_a_shares()
            stock_list = list(all_stocks['代码'].apply(lambda x: f"{x}.SZ" if str(x).startswith('0') or str(x).startswith('3') else f"{x}.SH"))
        except Exception:
            stock_list = []
    else:
        with open(args.stocks, 'r') as f:
            stock_list = [line.strip() for line in f if line.strip()]

    res = scan_stocks(stock_list, out_csv=args.out)
    print(res)
