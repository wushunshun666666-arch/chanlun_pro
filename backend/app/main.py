from fastapi import FastAPI
from .api import kline, signals, admin
from .db import base, engine, init_db

app = FastAPI(title='Chanlun CCI Scanner API')

# create DB tables on startup (sqlite default)
@app.on_event('startup')
def startup():
    init_db()

app.include_router(kline.router, prefix='/api/kline', tags=['kline'])
app.include_router(signals.router, prefix='/api/signals', tags=['signals'])
app.include_router(admin.router, prefix='/api/admin', tags=['admin'])
