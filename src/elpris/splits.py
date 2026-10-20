"""Testupplägg och läckageskydd (A1)."""

from datetime import date, timedelta

import pandas as pd

HORIZONS = range(1, 8)


def available_at_noon(daily: pd.DataFrame, forecast_date: date) -> pd.DataFrame:
    """Dagsvärden som var kända kl. 12 på forecast_date."""
    return daily[daily["date"] <= forecast_date ].copy()



def make_targets(daily: pd.DataFrame, forecast_date: date) -> pd.DataFrame:
    """Sju måldagar (D+1 ... D+7) med verkliga dagsvärden. Endast för utvärdering."""
    rows = [
        {"forecast_date": forecast_date, "target_date": forecast_date + timedelta(days=h), "horizon": h}
        for h in HORIZONS
    ]
    targets = pd.DataFrame(rows)
    return targets.merge(daily, left_on="target_date", right_on="date", how="left").drop(columns="date")


def valid_origins(daily: pd.DataFrame, history_days: int = 7) -> list[date]:
    """Alla dagar som kan vara prognostillfälle."""
    first = daily["date"].min() + timedelta(days=history_days - 1)
    last = daily["date"].max() - timedelta(days=7)
    return [d for d in daily["date"] if first <= d <= last]


def split_origins(origins: list[date], test_start: date) -> tuple[list[date], list[date]]:
    """Tidsuppdelning utan läckage: träningens måldagar slutar före testperioden."""
    train = [d for d in origins if d + timedelta(days=7) < test_start]
    test = [d for d in origins if d >= test_start]
    return train, test




