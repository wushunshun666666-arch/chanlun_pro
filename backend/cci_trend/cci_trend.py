import pandas as pd
import numpy as np
from typing import Optional, Dict


def _is_local_high(cci: pd.Series, i: int) -> bool:
    if i <= 0 or i >= len(cci) - 1:
        return False
    return (cci.iloc[i] > cci.iloc[i-1]) and (cci.iloc[i] > cci.iloc[i+1])


def find_local_highs(cci: pd.Series) -> pd.Series:
    idxs = [i for i in range(1, len(cci)-1) if _is_local_high(cci, i) and cci.iloc[i] > 0]
    return pd.Series(idxs)


def detect_cci_trend_break(cci: pd.Series, dates: pd.Series = None) -> Optional[Dict]:
    """
    Implements PRD CCI trend algorithm (main high + secondary high) and checks if the latest bar
    is a breakthrough where previous bar was below trendline and current bar strictly > trendline.

    Returns dict with signal info if breakthrough detected, otherwise None.
    """
    if cci is None or len(cci) < 10:
        return None

    # ensure index positions
    pos = np.arange(len(cci))

    # find local highs (indices)
    local_high_idxs = [i for i in range(1, len(cci)-1) if _is_local_high(cci, i) and cci.iloc[i] > 0]
    if not local_high_idxs:
        return None

    # try each candidate main high
    for main_idx in local_high_idxs:
        main_val = cci.iloc[main_idx]
        # find first local high to the right as initial secondary
        right_highs = [i for i in local_high_idxs if i > main_idx]
        if not right_highs:
            continue
        sec_idx = right_highs[0]
        sec_val = cci.iloc[sec_idx]
        valid = True
        # scan subsequent highs to possibly replace sec or invalidate trend
        for k in right_highs[1:]:
            k_val = cci.iloc[k]
            if k_val > sec_val and k_val < main_val:
                sec_idx = k
                sec_val = k_val
            elif k_val > main_val:
                valid = False
                break
        if not valid:
            continue

        # have main and sec; build trendline mapping position -> value
        x1, y1 = main_idx, main_val
        x2, y2 = sec_idx, sec_val
        if x2 == x1:
            continue
        slope = (y2 - y1) / (x2 - x1)
        intercept = y1 - slope * x1

        # compute trendline value for last two bars
        last_pos = len(cci) - 1
        prev_pos = len(cci) - 2
        trend_prev = slope * prev_pos + intercept
        trend_last = slope * last_pos + intercept
        cci_prev = cci.iloc[prev_pos]
        cci_last = cci.iloc[last_pos]

        # breakthrough: prev < trend_prev and last > trend_last (strict)
        if (cci_prev < trend_prev) and (cci_last > trend_last):
            # ensure yesterday (prev) was not already a breakthrough (we already check prev < trend_prev)
            # prepare dates if given
            signal_date = None
            prev_date = None
            main_date = None
            sec_date = None
            if dates is not None:
                prev_date = pd.to_datetime(dates.iloc[prev_pos]).date()
                signal_date = pd.to_datetime(dates.iloc[last_pos]).date()
                main_date = pd.to_datetime(dates.iloc[main_idx]).date()
                sec_date = pd.to_datetime(dates.iloc[sec_idx]).date()
            return {
                'type': 'CCI_BREAK',
                'signal_date': signal_date,
                'prev_date': prev_date,
                'main_index': int(main_idx),
                'main_date': str(main_date) if main_date is not None else None,
                'sec_index': int(sec_idx),
                'sec_date': str(sec_date) if sec_date is not None else None,
                'trend_slope': float(slope),
                'trend_intercept': float(intercept),
                'cci_prev': float(cci_prev),
                'cci_last': float(cci_last),
                'trend_prev': float(trend_prev),
                'trend_last': float(trend_last)
            }
    return None
