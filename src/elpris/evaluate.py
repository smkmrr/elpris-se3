"""Kör den slutliga jämförelsen mellan baseline och Random Forest."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from elpris.backtest import run_baseline_backtest
from elpris.metrics import bias_by_season, mae_by_season, mae_spike_vs_normal, mae_table
from elpris.plots import plot_model_comparison
from elpris.random_forest import run_random_forest_backtest
from elpris.splits import (
    HISTORY_DAYS,
    TEST_START,
    split_origins,
    valid_origins,
)

DATA_PATH = Path("data/processed/se3_daily.csv")
RESULTS_DIR = Path("results")


def load_daily(path=DATA_PATH):
    daily = pd.read_csv(path, parse_dates=["date"])
    daily["date"] = daily["date"].dt.date
    return daily


def prediction_keys(predictions):
    keys = predictions[["forecast_date", "target_date", "horizon"]].copy()

    keys["forecast_date"] = pd.to_datetime(keys["forecast_date"]).dt.date

    keys["target_date"] = pd.to_datetime(keys["target_date"]).dt.date

    return set(keys.itertuples(index=False, name=None))


def evaluate(daily):
    origins = valid_origins(
        daily,
        history_days=HISTORY_DAYS,
    )

    _, test_origins = split_origins(
        origins,
        TEST_START,
    )

    if not test_origins:
        raise ValueError("Testperioden innehåller inga giltiga prognosdagar")

    baseline_predictions = run_baseline_backtest(
        daily,
        test_origins,
    )

    rf_predictions = run_random_forest_backtest(
        daily,
        TEST_START,
    )

    if prediction_keys(baseline_predictions) != prediction_keys(rf_predictions):
        raise ValueError("Baseline och Random Forest använder olika prognosdagar")

    predictions = pd.concat(
        [
            baseline_predictions,
            rf_predictions,
        ],
        ignore_index=True,
    )

    return predictions, mae_table(predictions)


def main():
    daily = load_daily()
    predictions, table = evaluate(daily)

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    predictions.to_csv(
        RESULTS_DIR / "predictions.csv",
        index=False,
    )

    table.reset_index().to_csv(
        RESULTS_DIR / "mae_table.csv",
        index=False,
    )

    mae_by_season(predictions).reset_index().to_csv(
        RESULTS_DIR / "mae_by_season.csv", index=False
    )
    bias_by_season(predictions).reset_index().to_csv(
        RESULTS_DIR / "bias_by_season.csv", index=False
    )
    mae_spike_vs_normal(predictions).reset_index().to_csv(
        RESULTS_DIR / "mae_spike_vs_normal.csv", index=False
    )

    figure = plot_model_comparison(table)

    figure.savefig(
        RESULTS_DIR / "mae_comparison.png",
        dpi=150,
        bbox_inches="tight",
    )

    plt.close(figure)


if __name__ == "__main__":
    main()
