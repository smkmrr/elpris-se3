import pandas as pd
import pytest

from elpris.metrics import bias_by_season, mae_by_season, mae_spike_vs_normal


@pytest.fixture
def predictions():
    """EN vinterdag (fel -1.0) och en sommardag (fel +0.5)."""
    return pd.DataFrame(
        {
            "model": ["m", "m"],
            "target": ["mean", "mean"],
            "target_date": pd.to_datetime(["2026-01-15", "2026-07-15"]),
            "y_true": [2.0, 1.0],
            "y_pred": [1.0, 1.5],
        }
    )


def test_mae_season(predictions):
    table = mae_by_season(predictions)
    assert table.loc[("m", "mean"), "vinter"] == pytest.approx(1.0)
    assert table.loc[("m", "mean"), "sommar"] == pytest.approx(0.5)


def test_bias_by_season_keeps_sign(predictions):
    table = bias_by_season(predictions)
    assert table.loc[("m", "mean"), "vinter"] == pytest.approx(-1.0)
    assert table.loc[("m", "mean"), "sommar"] == pytest.approx(0.5)


def test_mae_spike_vs_normal():
    dates = pd.date_range("2026-01-01", periods=10, freq="D")
    y_true = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    y_pred = [0, 1, 2, 3, 4, 5, 6, 7, 8, 8]
    predictions = pd.DataFrame(
        {
            "model": "m",
            "target": "max",
            "target_date": dates,
            "y_true": y_true,
            "y_pred": y_pred,
        }
    )

    table = mae_spike_vs_normal(predictions)
    assert table.loc[("m", "max"), "spik"] == pytest.approx(2.0)
    assert table.loc[("m", "max"), "normal"] == pytest.approx(1.0)
