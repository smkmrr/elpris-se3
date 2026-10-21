import pandas as pd

from elpris.baseline import create_weekday_baseline

OUTPUT_COLUMNS = ["target_date", "horizon", "mean", "max", "min"]


def forecast_next_week(daily_prices, forecast_date, model="baseline"):
    """Prognos för dag D+1 till D+7, gjord klockan 12 dag D.

    Returnerar en tabell med sju rader: måldag, dag framåt och de tre
    prognostalen (dagsmedel, högsta och lägsta pris) i SEK/kWh.
    """
    if model == "baseline":
        forecasts = create_weekday_baseline(daily_prices, forecast_date)
    else:
        raise ValueError(f"Okänd modell: {model}")

    return forecasts[OUTPUT_COLUMNS]