"""Testupplägg och läckageskydd (A1)."""

from datetime import date, timedelta

import pandas as pd

HORIZONS = range(1, 8)

# Gruppens beslut (2026-10-19): låst innan någon modell tränas
TEST_START = date(2025, 10, 1)
HISTORY_DAYS = 14

# Beslutat inför kodfrysen: sista prognosdag i testperioden
TEST_END = date(2026, 10, 15)


def limit_to_test_end(daily: pd.DataFrame, test_end: date = TEST_END) -> pd.DataFrame:
    """Behåll bara data fram till test_end + 7 dagar.
      då blir test_end den  sista prognosdagen."""
    dates = pd.to_datetime(daily["date"])
    return daily[dates <= pd.Timestamp(test_end) + pd.Timedelta(days=7)].copy()


def available_at_noon(daily: pd.DataFrame, forecast_date: date) -> pd.DataFrame:
    """Dagsvärden som var kända kl. 12 på forecast_date."""
    return daily[daily["date"] <= forecast_date].copy()


def make_targets(daily: pd.DataFrame, forecast_date: date) -> pd.DataFrame:
    """Sju måldagar (D+1 ... D+7) med verkliga dagsvärden. Endast för utvärdering."""
    rows = [
        {
            "forecast_date": forecast_date,
            "target_date": forecast_date + timedelta(days=h),
            "horizon": h,
        }
        for h in HORIZONS
    ]
    targets = pd.DataFrame(rows)
    return targets.merge(
        daily, left_on="target_date", right_on="date", how="left"
    ).drop(columns="date")


def valid_origins(daily: pd.DataFrame, history_days: int = HISTORY_DAYS) -> list[date]:
    """Alla dagar som kan vara prognostillfälle."""
    first = daily["date"].min() + timedelta(days=history_days - 1)
    last = daily["date"].max() - timedelta(days=7)
    return [d for d in daily["date"] if first <= d <= last]


def split_origins(
    origins: list[date], test_start: date
) -> tuple[list[date], list[date]]:
    """Tidsuppdelning utan läckage: träningens måldagar slutar före testperioden."""
    train = [d for d in origins if d + timedelta(days=7) < test_start]
    test = [d for d in origins if d >= test_start]
    return train, test