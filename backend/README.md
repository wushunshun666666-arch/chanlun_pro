# README for backend

This directory provides the FastAPI backend for the Chanlun CCI automatic scanner.

Requirements: see backend/requirements.txt

Run locally:

1. Create virtualenv and install dependencies
   python -m venv venv
   source venv/bin/activate
   pip install -r backend/requirements.txt

2. Start the API:
   uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

API endpoints:
- GET /api/kline/{ts_code}?timeframe=D&count=200
- GET /api/signals?date=YYYY-MM-DD&timeframe=D
- POST /api/admin/scan  (manual scan)

Background job: APScheduler job configured to run daily at 15:10 Asia/Shanghai to perform CCI scans for D/W/M and persist into SQLite database './chanlun.db'
