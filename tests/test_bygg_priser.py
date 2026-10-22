from datetime import date

import pandas as pd

from elpris.bygg_priser import to_daily, to_hourly


def test_quarter_prices_become_hourly_mean():
    prices = pd.DataFrame({
        "time_start": [
            "2025-10-01T00:00:00+02:00", "2025-10-01T00:15:00+02:00",
            "2025-10-01T00:30:00+02:00", "2025-10-01T00:45:00+02:00",
        ],
        "SEK_per_kWh": [1.0, 2.0, 3.0, 4.0],
    })
    hourly = to_hourly(prices)
    assert len(hourly) == 1
    assert hourly["SEK_per_kWh"].iloc[0] == 2.5


def test_spring_dst_day_has_23_hours():
    # 2025-03-30 ställs klockan fram, dagen har bara 23 timmar
    hours = pd.date_range("2025-03-30", periods=23, freq="h", tz="Europe/Stockholm")
    prices = pd.DataFrame({
        "time_start": hours,
        "SEK_per_kWh": [float(i) for i in range(23)],
    })
    daily = to_daily(to_hourly(prices))
    assert len(daily) == 1
    assert daily["date"].iloc[0] == date(2025, 3, 30)
    assert daily["mean"].iloc[0] == 11.0
    assert daily["max"].iloc[0] == 22.0
    assert daily["min"].iloc[0] == 0.0