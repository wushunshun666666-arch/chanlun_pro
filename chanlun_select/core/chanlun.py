import pandas as pd
import numpy as np

# Simplified ChanLun core utilities


def identify_turning_points(df, window=5):
    """
    Identify simple turning points (peaks and troughs) by comparing to neighbors.
    Returns list of tuples (index, 'peak'/'trough', price)
    """
    prices = df['close']
    pts = []
    n = len(prices)
    for i in range(window, n-window):
        left = prices.iloc[i-window:i]
        right = prices.iloc[i+1:i+1+window]
        cur = prices.iloc[i]
        if cur > left.max() and cur > right.max():
            pts.append((prices.index[i], 'peak', cur))
        if cur < left.min() and cur < right.min():
            pts.append((prices.index[i], 'trough', cur))
    return pts


def build_pens_from_turns(turns):
    """Simplified pens: consecutive turns form a pen between their values"""
    pens = []
    for i in range(len(turns)-1):
        t0 = turns[i]
        t1 = turns[i+1]
        pen = {
            'start': t0[0],
            'end': t1[0],
            'high': max(t0[2], t1[2]),
            'low': min(t0[2], t1[2]),
            'dir': 'up' if t1[2] > t0[2] else 'down'
        }
        pens.append(pen)
    return pens


def detect_zs(pens, min_pens=3):
    """
    Detect simple middle zones (中枢) as overlap of consecutive pens ranges of length min_pens
    Returns list of dicts with 'start_idx','end_idx','high','low'
    """
    zs = []
    for i in range(len(pens)-min_pens+1):
        group = pens[i:i+min_pens]
        high = min(p['high'] for p in group)
        low = max(p['low'] for p in group)
        if high > low:
            zs.append({'start_idx': i, 'end_idx': i+min_pens-1, 'high': high, 'low': low})
    return zs


def analyze_daily_for_signals(df):
    """
    Given a DataFrame of OHLCV indexed by date, return simple signals or None.
    Strategy (very simplified):
      - find turning points, build pens
      - detect last middle zone
      - if latest close breaks above last zs.high and last pen is up -> 'buy'
    """
    if df is None or df.empty or len(df) < 30:
        return None
    turns = identify_turning_points(df, window=5)
    if len(turns) < 6:
        return None
    pens = build_pens_from_turns(turns)
    zs = detect_zs(pens, min_pens=3)
    if not zs:
        return None
    last_zs = zs[-1]
    last_pen = pens[-1]
    last_close = df['close'].iloc[-1]
    if last_close > last_zs['high'] and last_pen['dir'] == 'up':
        return {'type': 'break_zs_up', 'price': float(last_close), 'zs_high': float(last_zs['high'])}
    return None
