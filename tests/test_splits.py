from datetime import date, timedelta

import pandas as pd
import pytest

from elpris.splits import (
    HISTORY_DAYS,
    TEST_START,
    available_at_noon,
    make_targets,
    split_origins,
    valid_origins,
)


@pytest.fixture
def daily():
    """30 påhittade dagar: 2026-01-01 till 2026-01-30."""
    days = [date(2026, 1, 1) + timedelta(days=i) for i in range(30)]
    return pd.DataFrame({"date": days, "mean": 1.0, "max": 2.0, "min": 0.5})


def test_available_at_noon_has_no_future_days(daily):
    origin = date(2026, 1, 15)
    known = available_at_noon(daily, origin)
    assert known["date"].max() == origin


def test_make_targets_horizon_matches_dates(daily):
    origin = date(2026, 1, 10)
    targets = make_targets(daily, origin)
    assert list(targets["horizon"]) == [1, 2, 3, 4, 5, 6, 7]
    assert all(
        targets["target_date"] - targets["forecast_date"]
        == pd.to_timedelta(targets["horizon"], unit="D")
    )


def test_split_has_gap_and_no_overlap(daily):
    test_start = date(2026, 1, 20)
    train, test = split_origins(valid_origins(daily, history_days=7), test_start)

    # 0. Båda delarna måste innehålla dagar, annars testar vi ingenting
    assert train and test

    # 1. Sista träningsoriginens måldagar slutar före testperioden (gap)
    assert train[-1] + timedelta(days=7) < test_start

    # 2. Testet börjar inte före test_start
    assert test[0] >= test_start

    # 3. Ingen dag finns i både train och test
    assert len(set(train) & set(test)) == 0


def test_valid_origins_have_all_seven_targets(daily):
    for origin in valid_origins(daily):
        targets = make_targets(daily, origin)
        assert targets["mean"].notna().all()


def test_group_decisions_are_locked():
    assert TEST_START == date(2025, 10, 1)
    assert HISTORY_DAYS == 14
