import pandas as pd

from elpris.forecast import forecast_next_week


def make_daily_prices():
    """30 påhittade dagar med olika priser."""
    return pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=30, freq="D"),
            "mean": range(30),
            "max": [v + 1 for v in range(30)],
            "min": [v - 1 for v in range(30)],
        }
    )


def test_forecast_has_seven_rows_and_right_columns():
    result = forecast_next_week(make_daily_prices(), "2026-01-20")

    assert len(result) == 7
    assert list(result.columns) == ["target_date", "horizon", "mean", "max", "min"]


def test_random_forest_forecast_has_seven_rows_and_right_columns():
    result = forecast_next_week(
        make_daily_prices(), "2026-01-30", model="random_forest"
    )

    assert len(result) == 7
    assert list(result.columns) == ["target_date", "horizon", "mean", "max", "min"]
    assert result["target_date"].min() == pd.Timestamp("2026-01-31")
