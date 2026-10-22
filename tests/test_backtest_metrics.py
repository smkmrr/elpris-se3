import pandas as pd
import pytest

from elpris.backtest import to_long_predictions
from elpris.metrics import mae, mae_table


def test_mae_known_values():
    y_true = pd.Series([1.0, 2.0, 3.0])
    y_pred = pd.Series([2.0, 2.0, 1.0])
    assert mae(y_true, y_pred) == pytest.approx(1.0)


def test_to_long_predictions_matches_actuals():
    forecasts = pd.DataFrame({
        "forecast_date": pd.to_datetime(["2026-01-01"]),
        "target_date": pd.to_datetime(["2026-01-02"]),
        "horizon": [1],
        "mean": [1.5],
        "max": [3.0],
        "min": [0.5],
    })
    daily = pd.DataFrame({
        "date": ["2026-01-02"],
        "mean": [1.0],
        "max": [2.0],
        "min": [0.0],
    })
    long = to_long_predictions(forecasts, daily, "test_model")

    assert len(long) == 3
    assert set(long["target"]) == {"mean", "max", "min"}
    assert (long["model"] == "test_model").all()

    by_target = long.set_index("target")
    assert by_target.loc["max", "y_pred"] == 3.0
    assert by_target.loc["max", "y_true"] == 2.0


def test_mae_table_per_model_target_and_horizon():
    predictions = pd.DataFrame({
        "model": ["a", "a", "a", "b"],
        "target": ["mean", "mean", "mean", "mean"],
        "horizon": [1, 1, 2, 1],
        "y_true": [1.0, 1.0, 1.0, 1.0],
        "y_pred": [2.0, 4.0, 1.5, 1.0],
    })
    table = mae_table(predictions)

    assert table.loc[("a", "mean"), 1] == pytest.approx(2.0)
    assert table.loc[("a", "mean"), 2] == pytest.approx(0.5)
    assert table.loc[("b", "mean"), 1] == pytest.approx(0.0)