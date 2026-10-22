"""Enkel baseline för sjudagarsprognoser av elpris i SE3."""

from __future__ import annotations

import pandas as pd

REQUIRED_COLUMNS = {"date", "mean", "max", "min"}


def create_weekday_baseline(
    daily_prices: pd.DataFrame,
    forecast_date: str | pd.Timestamp,
    horizon: int = 7,
) -> pd.DataFrame:
    """Skapa prognoser från samma veckodag en vecka tidigare.

    Prognosen görs klockan 12 dag D för D+1 till D+7.
    Projektets antagande är att priserna till och med dag D är kända.
    """

    missing_columns = REQUIRED_COLUMNS.difference(daily_prices.columns)

    if missing_columns:
        raise ValueError(f"Dagstabellen saknar kolumner: {sorted(missing_columns)}")

    if horizon < 1:
        raise ValueError("horizon måste vara minst 1")

    prices = daily_prices[["date", "mean", "max", "min"]].copy()

    prices["date"] = pd.to_datetime(
        prices["date"],
        errors="raise",
    ).dt.normalize()

    if prices["date"].duplicated().any():
        raise ValueError("Dagstabellen innehåller dubbla datum")

    for column in ["mean", "max", "min"]:
        prices[column] = pd.to_numeric(
            prices[column],
            errors="raise",
        )

    day_d = pd.Timestamp(forecast_date).normalize()

    # Endast information som är känd senast dag D får användas.
    available = prices[prices["date"] <= day_d].set_index("date")

    forecasts = []

    for step in range(1, horizon + 1):
        target_date = day_d + pd.Timedelta(days=step)
        source_date = target_date - pd.Timedelta(days=7)

        if source_date not in available.index:
            raise ValueError(
                "Historik saknas för baseline: "
                f"måldag={target_date.date()}, "
                f"källdag={source_date.date()}"
            )

        source = available.loc[source_date]

        forecasts.append(
            {
                "forecast_date": day_d,
                "target_date": target_date,
                "horizon": step,
                "source_date": source_date,
                "mean": source["mean"],
                "max": source["max"],
                "min": source["min"],
            }
        )

    return pd.DataFrame(forecasts)
