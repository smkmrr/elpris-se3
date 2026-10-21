"""B2: Random Forest som jämförs med baselinen."""

import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from elpris.backtest import to_long_predictions
from elpris.features import build_feature_table, get_model_feature_columns
from elpris.splits import available_at_noon, split_origins

TARGET_COLUMNS = ["y_mean", "y_max", "y_min"]


def run_random_forest_backtest(
    daily_prices, test_start, n_estimators=200, random_state=42
):
    """Träna på dagarna före test_start och gör prognoser för testperioden.

    Returnerar prognoserna i det gemensamma formatet från A2.
    """
    features = build_feature_table(
        daily_prices, available_data_fn=available_at_noon
    )

    origins = list(features["origin_date"].drop_duplicates().sort_values())
    train_origins, test_origins = split_origins(origins, pd.Timestamp(test_start))

    train = features[features["origin_date"].isin(train_origins)]
    test = features[features["origin_date"].isin(test_origins)]

    feature_cols = get_model_feature_columns(features)
    model = RandomForestRegressor(
        n_estimators=n_estimators, random_state=random_state, n_jobs=-1
    )
    model.fit(train[feature_cols], train[TARGET_COLUMNS])
    pred = model.predict(test[feature_cols])

    forecasts = pd.DataFrame({
        "forecast_date": test["origin_date"].values,
        "target_date": test["target_date"].values,
        "horizon": test["horizon"].values,
        "mean": pred[:, 0],
        "max": pred[:, 1],
        "min": pred[:, 2],
    })
    return to_long_predictions(forecasts, daily_prices, "random_forest")