import pandas as pd
import pytest

from elpris.baseline import create_weekday_baseline


def make_daily_prices() -> pd.DataFrame:
    dates = pd.date_range(
        "2026-09-01",
        periods=30,
        freq="D",
    )

    return pd.DataFrame(
        {
            "date": dates,
            "mean": range(30),
            "max": [
                value + 10
                for value in range(30)
            ],
            "min": [
                value - 10
                for value in range(30)
            ],
        }
    )


def test_baseline_returns_seven_rows() -> None:
    result = create_weekday_baseline(
        make_daily_prices(),
        forecast_date="2026-09-21",
    )

    assert len(result) == 7

    assert result["horizon"].tolist() == [
        1, 2, 3, 4, 5, 6, 7
    ]

    assert result.iloc[0]["target_date"] == pd.Timestamp(
        "2026-09-22"
    )

    assert result.iloc[0]["source_date"] == pd.Timestamp(
        "2026-09-15"
    )


def test_day_seven_uses_forecast_day() -> None:
    result = create_weekday_baseline(
        make_daily_prices(),
        forecast_date="2026-09-21",
    )

    last = result.iloc[-1]

    assert last["target_date"] == pd.Timestamp(
        "2026-09-28"
    )

    assert last["source_date"] == pd.Timestamp(
        "2026-09-21"
    )

    assert last["mean"] == 20


def test_missing_history_raises_error() -> None:
    prices = make_daily_prices()

    prices = prices[
        prices["date"] != "2026-09-15"
    ]

    with pytest.raises(
        ValueError,
        match="Historik saknas",
    ):
        create_weekday_baseline(
            prices,
            forecast_date="2026-09-21",
        )