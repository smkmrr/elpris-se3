import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from elpris.baseline import create_weekday_baseline
from elpris.features import TARGET_COLUMNS, build_feature_table, get_model_feature_columns
from elpris.splits import available_at_noon

OUTPUT_COLUMNS = ["target_date", "horizon", "mean", "max", "min"]

def _forecast_random_forest(daily_prices, forecast_date):
    """Träna Random Forest på all historik och gissa D+1 till D+7."""
    forecast_date = pd.Timestamp(forecast_date)

    # Sju tomma framtida dagar, så att build_feature_table gör rader för dag D
    future = pd.DataFrame(
        {"date": pd.date_range(forecast_date + pd.Timedelta(days=1), periods=7, freq="D")}
    )

    daily = daily_prices.assign(date=pd.to_datetime(daily_prices["date"]))
    extended = pd.concat([daily, future], ignore_index=True)

    features = build_feature_table(extended, available_data_fn=available_at_noon)

    # Träna på rader där facit finns, gissa på raderna för dag D
    train = features[features[TARGET_COLUMNS].notna().all(axis=1)]
    today = features[features["origin_date"] == forecast_date]

    feature_cols = get_model_feature_columns(features)
    model = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
    model.fit(train[feature_cols], train[TARGET_COLUMNS])
    pred = model.predict(today[feature_cols])

    return pd.DataFrame(
        {
            "target_date": today["target_date"].values,
            "horizon": today["horizon"].values,
            "mean": pred[:, 0],
            "max": pred[:, 1],
            "min": pred[:, 2],
        }
    )

def forecast_next_week(daily_prices, forecast_date, model="baseline"):
    """Prognos för dag D+1 till D+7, gjord klockan 12 dag D.

    Returnerar en tabell med sju rader: måldag, dag framåt och de tre
    prognostalen (dagsmedel, högsta och lägsta pris) i SEK/kWh.
    """
    if model == "baseline":
        forecasts = create_weekday_baseline(daily_prices, forecast_date)
    elif model == "random_forest":
        forecasts = _forecast_random_forest(daily_prices, forecast_date)
    else:
        raise ValueError(f"Okänd modell: {model}")

    return forecasts[OUTPUT_COLUMNS]


def main():
    """Visa prognosen för de sju dagarna efter den senaste dagen i datan."""

    daily = pd.read_csv("data/processed/se3_daily.csv")
    forecast_date = daily["date"].max()

    model = "baseline"
    forecast = forecast_next_week(daily, forecast_date, model=model)

    print(f"Prognos för SE3 med {model}, gjord {forecast_date} kl. 12 (SEK/kWh):")
    print(forecast.round({"mean": 2, "max": 2, "min": 2}).to_string(index=False))


if __name__ == "__main__":
    main()
