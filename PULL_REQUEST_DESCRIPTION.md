# Pull Request: Add backend FastAPI CCI scanner

This PR adds a FastAPI backend implementing the PRD-specified CCI trendline scanner and automatic scanning job.

Summary of changes
- backend/ - new FastAPI backend with akshare fetcher, CCI indicator, CCI trendline algorithm, scheduler, DB models and APIs
- chanlun_select/ - earlier MVP modules (data fetcher, core, scanner, realtime agent)

Features
- AKShare-based K-line retrieval (D/W/M/min)
- CCI computation and PRD-accurate trendline detection (main high + secondary high)
- APScheduler job that runs daily at 15:10 Asia/Shanghai for D/W/M scans
- SQLite DB (default) with cci_signals table; uniqueness enforced by (stock_code, timeframe, signal_date)
- API endpoints for kline retrieval, listing signals, and manual scan trigger

Run instructions
1. Create venv and install: pip install -r backend/requirements.txt
2. Start API: uvicorn backend.app.main:app --reload --port 8000
3. Manual scan: POST /api/admin/scan

Notes
- AKShare is required. No tokens needed.
- This is a first implementation; further hardening (error handling, retries, logging, Docker, CI) is recommended.
