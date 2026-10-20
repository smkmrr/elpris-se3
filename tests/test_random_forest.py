import pandas as pd

from elpris.random_forest import run_random_forest_backtest


def make_daily_prices(days=60):
    values = [float(v % 7) for v in range(days)]
    return pd.DataFrame({
        "date": pd.date_range("2026-01-01", periods=days, freq="D"),
        "mean": values,
        "max": [v + 1 for v in values],
        "min": [v - 1 for v in values],
    })


def test_output_has_common_format():
    result = run_random_forest_backtest(
        make_daily_prices(), "2026-02-10", n_estimators=10
    )
    assert list(result.columns) == [
        "forecast_date", "target_date", "horizon",
        "target", "y_pred", "y_true", "model",
    ]
    assert set(result["horizon"]) == set(range(1, 8))
    assert set(result["target"]) == {"mean", "max", "min"}
    assert (result["model"] == "random_forest").all()
    assert result["y_true"].notna().all()


def test_only_forecasts_in_test_period():
    result = run_random_forest_backtest(
        make_daily_prices(), "2026-02-10", n_estimators=10
    )
    assert (result["forecast_date"] >= pd.Timestamp("2026-02-10")).all()


def test_same_seed_gives_same_result():
    daily = make_daily_prices()
    first = run_random_forest_backtest(daily, "2026-02-10", n_estimators=10)
    second = run_random_forest_backtest(daily, "2026-02-10", n_estimators=10)
    assert first["y_pred"].equals(second["y_pred"])