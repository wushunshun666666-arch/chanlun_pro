from dotenv import load_dotenv
import os
import time
import logging
from .data.fetcher import DataFetcher
from .core.chanlun import analyze_daily_for_signals

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    import argparse
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--stocks", default="all", help="'all' or path to file with ts_code lines")
    parser.add_argument("--interval", type=int, default=60, help="poll interval seconds")
    parser.add_argument("--freq", default="1min", help="minute frequency: 1min/5min")
    args = parser.parse_args()

    fetcher = DataFetcher()

    if args.stocks == "all":
        # simple: use akshare to get current A-share list
        try:
            from akshare import stock_info_a_shares
            all_stocks = stock_info_a_shares()
            ts_codes = list(all_stocks['代码'].apply(lambda x: f"{x}.SZ" if str(x).startswith('0') or str(x).startswith('3') else f"{x}.SH"))
        except Exception:
            ts_codes = []
    else:
        with open(args.stocks, 'r') as f:
            ts_codes = [line.strip() for line in f if line.strip()]

    logger.info(f"Starting realtime agent for {len(ts_codes)} stocks, interval={args.interval}s, freq={args.freq}")

    while True:
        for ts in ts_codes[:200]:
            try:
                df = fetcher.get_minute(ts, freq=args.freq, count=200)
                sig = analyze_daily_for_signals(df)
                if sig:
                    print(f"Signal for {ts}:", sig)
            except Exception as e:
                logger.exception(e)
        time.sleep(args.interval)
