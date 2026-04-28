import pandas as pd
import numpy as np


def compute_cci(df: pd.DataFrame, n: int = 14, price_col: str = 'close') -> pd.Series:
    """
    Compute CCI as typical implementation.
    CCI = (TP - SMA(TP, n)) / (0.015 * mean_dev)
    where TP = (high+low+close)/3
    """
    if df is None or df.empty:
        return pd.Series(dtype=float)
    tp = (df['high'] + df['low'] + df['close']) / 3.0
    sma = tp.rolling(window=n, min_periods=1).mean()
    mean_dev = tp.rolling(window=n, min_periods=1).apply(lambda x: np.mean(np.abs(x - np.mean(x))), raw=True)
    cci = (tp - sma) / (0.015 * mean_dev.replace(0, np.nan))
    cci = cci.replace([np.inf, -np.inf], np.nan).fillna(0)
    cci.name = 'cci'
    return cci
