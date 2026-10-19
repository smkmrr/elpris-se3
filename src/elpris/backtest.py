import pandas as pd

from elpris.baseline import create_weekday_baseline

TARGETS = ["mean", "max", "min"]


def to_long_predictions(forecasts, daily_prices, model_name):
    """Gör om prognoser från bred till lång form och lägger till facit.

    forecasts ska ha kolumnerna forecast_date, target_date, horizon,
    mean, max och min. daily_prices är dagstabellen med de verkliga priserna.
    """
    # Bred till lång: en rad per gissning
    predictions = forecasts.melt(
        id_vars=["forecast_date", "target_date", "horizon"],
        value_vars=TARGETS,
        var_name="target",
        value_name="y_pred",
    )

    # Facit i samma långa form
    actuals = daily_prices.melt(
        id_vars=["date"],
        value_vars=TARGETS,
        var_name="target",
        value_name="y_true",
    )
    actuals["date"] = pd.to_datetime(actuals["date"])

    # Para ihop varje gissning med verkligt pris för samma dag och värde
    predictions = predictions.merge(
        actuals,
        left_on=["target_date", "target"],
        right_on=["date", "target"],
        how="left",
    )
    predictions = predictions.drop(columns="date")
    predictions["model"] = model_name

    return predictions


def run_baseline_backtest(daily_prices, forecast_dates):
    """Kör baselinen för varje prognosdag i forecast_dates."""

    all_forecasts = []
    for forecast_date in forecast_dates:
        forecasts = create_weekday_baseline(daily_prices, forecast_date)
        all_forecasts.append(forecasts)

    all_forecasts = pd.concat(all_forecasts, ignore_index=True)

    return to_long_predictions(all_forecasts, daily_prices, "baseline")