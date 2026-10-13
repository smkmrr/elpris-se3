import pandas as pd

from elpris.baseline import create_weekday_baseline


def evaluate_one(daily, forecast_date):
    forecast = create_weekday_baseline(daily, forecast_date)

    actual = daily.copy()
    actual["date"] = pd.to_datetime(actual["date"])

    merged = forecast.merge(
        actual,
        left_on="target_date",
        right_on="date",
        suffixes=("_pred", "_true"),
    )

    merged["err_mean"] = (merged["mean_pred"] - merged["mean_true"]).abs()

    merged["err_max"] = (merged["max_pred"] - merged["max_true"]).abs()

    merged["err_min"] = (merged["min_pred"] - merged["min_true"]).abs()

    

    return merged[["forecast_date", "horizon", "target_date", "err_mean", "err_max", "err_min"]]


def evaluate_many(daily, forecast_dates):
    results = []
    for d in forecast_dates:
        results.append(evaluate_one(daily, d))
    return pd.concat(results, ignore_index=True)


def mae_table(errors):
    return errors.groupby("horizon")[["err_mean", "err_max", "err_min"]].mean()

if __name__ == "__main__":
    daily =pd.read_csv("data/sample_daily_prices.csv")
    dates = pd.date_range("2026-09-20", "2026-09-23")
    errors = evaluate_many(daily, dates)
    print(mae_table(errors))
