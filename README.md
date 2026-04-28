# Simple README for chanlun_select

chanlun_select
===============

A minimal MVP implementation for ChanLun-based stock selection (A-share). This branch provides:

- data fetcher (Tushare primary, akshare fallback)
- simplified ChanLun core (pen / simple middle-zone detection)
- scanner for batch scanning
- realtime polling agent (minute-level, polling)
- CLI entrypoints

Setup
-----

1. Create a Python virtual environment and install dependencies:

   pip install -r chanlun_select/requirements.txt

2. Provide your Tushare token as an environment variable:

   export TUSHARE_TOKEN=your_token_here

   or create a .env file with TUSHARE_TOKEN=your_token_here (do NOT commit it)

Usage
-----

- Scan a list of stocks (CSV or "all"):

  python -m chanlun_select.cli scan --stocks all

- Run realtime polling agent (will poll minute data and print signals):

  python -m chanlun_select.realtime_agent --stocks all --interval 60

Notes
-----
- This is an initial MVP. The ChanLun implementation is simplified and intended for research only.
- Do NOT commit API tokens into the repository. Use environment variables or CI secrets.
