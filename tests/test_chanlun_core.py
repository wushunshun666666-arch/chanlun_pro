import pandas as pd
from chanlun_select.core.chanlun import identify_turning_points, build_pens_from_turns, detect_zs, analyze_daily_for_signals


def test_identify_turns():
    # build synthetic up-down series
    dates = pd.date_range('2022-01-01', periods=30, freq='D')
    prices = [i + (i%5 - 2) * 0.5 for i in range(30)]
    df = pd.DataFrame({'close': prices}, index=dates)
    turns = identify_turning_points(df, window=2)
    assert isinstance(turns, list)

