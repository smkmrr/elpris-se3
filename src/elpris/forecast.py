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


def main():
    """Visa prognosen för de sju dagarna efter den senaste dagen i datan."""

    daily = pd.read_csv("data/processed/se3_daily.csv")
    forecast_date = daily["date"].max()

    model = "baseline"
    forecast = forecast_next_week(daily, forecast_date,  model=model)

    print(f"Prognos för SE3 med {model}, gjord {forecast_date} kl. 12 (SEK/kWh):")
    print(forecast.round({"mean": 2, "max": 2, "min": 2}).to_string(index=False))


if __name__ == "__main__":
    main()