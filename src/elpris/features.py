"""Skapa läckagesäkra features för Random Forest."""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd


REQUIRED_COLUMNS = {"date", "mean", "max", "min"}
TARGET_COLUMNS = ["y_mean", "y_max", "y_min"]


def _prepare_daily_prices(
    daily_prices: pd.DataFrame,
) -> pd.DataFrame:
    """Validera och sortera dagstabellen."""

    missing_columns = REQUIRED_COLUMNS.difference(
        daily_prices.columns
    )

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(
            f"Dagstabellen saknar kolumner: {missing}"
        )

    daily = daily_prices[
        ["date", "mean", "max", "min"]
    ].copy()

    daily["date"] = pd.to_datetime(
        daily["date"],
        errors="raise",
    ).dt.normalize()

    for column in ("mean", "max", "min"):
        daily[column] = pd.to_numeric(
            daily[column],
            errors="raise",
        )

    if daily["date"].duplicated().any():
        raise ValueError(
            "Dagstabellen innehåller dubbla datum"
        )

    daily = daily.sort_values(
        "date"
    ).reset_index(drop=True)

    expected_dates = pd.date_range(
        daily["date"].min(),
        daily["date"].max(),
        freq="D",
    )

    if len(expected_dates) != len(daily):
        raise ValueError(
            "Dagstabellen innehåller saknade datum"
        )

    return daily


def build_feature_table(
    daily_prices: pd.DataFrame,
    available_data_fn: Callable[
        [pd.DataFrame, pd.Timestamp],
        pd.DataFrame,
    ]
    | None = None,
) -> pd.DataFrame:
    """Bygg en rad per prognosdatum och prognosdag.

    Features för prognosdatum D skapas endast från priser
    som är kända till och med D. Framtida priser sparas
    enbart i y-kolumnerna.
    """

    daily = _prepare_daily_prices(daily_prices)
    rows: list[dict] = []

    if available_data_fn is None:

        def available_data_fn(
            data: pd.DataFrame,
            origin_date: pd.Timestamp,
        ) -> pd.DataFrame:
            return data[
                data["date"] <= origin_date
            ].copy()

    # Det behövs 14 historiska dagar och
    # 7 framtida måldagar.
    first_origin_position = 13
    last_origin_position = len(daily) - 8

    for origin_position in range(
        first_origin_position,
        last_origin_position + 1,
    ):
        origin_date = daily.loc[
            origin_position,
            "date",
        ]

        available = available_data_fn(
            daily.copy(),
            origin_date,
        )

        available = available.sort_values(
            "date"
        ).reset_index(drop=True)

        if (
            available["date"] > origin_date
        ).any():
            raise ValueError(
                "A1-funktionen returnerade data "
                "efter origin_date"
            )

        if len(available) < 14:
            continue

        history_7 = available.tail(7)
        history_14 = available.tail(14)

        base_features = {
            "origin_date": origin_date,
            "mean_rolling_7": (
                history_7["mean"].mean()
            ),
            "max_rolling_7": (
                history_7["max"].max()
            ),
            "min_rolling_7": (
                history_7["min"].min()
            ),
            "mean_rolling_14": (
                history_14["mean"].mean()
            ),
            "max_rolling_14": (
                history_14["max"].max()
            ),
            "min_rolling_14": (
                history_14["min"].min()
            ),
        }

        for lag in range(7):
            source_row = available.iloc[-1 - lag]

            base_features[
                f"mean_lag_{lag}"
            ] = source_row["mean"]

            base_features[
                f"max_lag_{lag}"
            ] = source_row["max"]

            base_features[
                f"min_lag_{lag}"
            ] = source_row["min"]

        for horizon in range(1, 8):
            target_row = daily.iloc[
                origin_position + horizon
            ]

            target_date = target_row["date"]

            row = base_features.copy()

            row.update(
                {
                    "target_date": target_date,
                    "horizon": horizon,
                    "target_weekday": (
                        target_date.dayofweek
                    ),
                    "target_month": (
                        target_date.month
                    ),
                    "y_mean": target_row["mean"],
                    "y_max": target_row["max"],
                    "y_min": target_row["min"],
                }
            )

            rows.append(row)

    return pd.DataFrame(rows)


def get_model_feature_columns(
    feature_table: pd.DataFrame,
) -> list[str]:
    """Returnera tillåtna modellfeatures."""

    excluded = {
        "origin_date",
        "target_date",
        *TARGET_COLUMNS,
    }

    return [
        column
        for column in feature_table.columns
        if column not in excluded
    ]