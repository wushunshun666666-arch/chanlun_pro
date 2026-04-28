import os
import time
import logging
import argparse
from dotenv import load_dotenv
from .data.fetcher import DataFetcher
from .core.chanlun import analyze_daily_for_signals
from .data.stocks import get_all_a_shares
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--stocks", default="all", help="'all' or path to file with ts_code lines")
    parser.add_argument("--interval", type=int, default=60, help="poll interval seconds")
    parser.add_argument("--freq", default="1min", help="minute frequency: 1min/5min")
    parser.add_argument("--max-per-cycle", type=int, default=200, help="max stocks to check per poll cycle")
    args = parser.parse_args()

    fetcher = DataFetcher()

    if args.stocks == "all":
        try:
            ts_codes = get_all_a_shares(exclude_st=True)
        except Exception:
            ts_codes = []
    else:
        with open(args.stocks, 'r') as f:
            ts_codes = [line.strip() for line in f if line.strip()]

    logger.info(f"Starting realtime agent for {len(ts_codes)} stocks (filtered), interval={args.interval}s, freq={args.freq}")

    while True:
        # limit to a subset per cycle to avoid hitting rate limits
        batch = ts_codes[:args.max_per_cycle]
        with ThreadPoolExecutor(max_workers=10) as ex:
            futures = {ex.submit(fetcher.get_minute, ts, args.freq, None, None, 200): ts for ts in batch}
            for fut in as_completed(futures):
                ts = futures[fut]
                try:
                    df = fut.result()
                    sig = analyze_daily_for_signals(df)
                    if sig:
                        print(f"Signal for {ts}:", sig)
                except Exception as e:
                    logger.debug(f"Error processing {ts}: {e}")
        time.sleep(args.interval)
