import pandas as pd
import pytest

from elpris.features import (
    build_feature_table,
    get_model_feature_columns,
)


def make_daily_prices(
    days: int = 30,
) -> pd.DataFrame:
    values = list(range(days))

    return pd.DataFrame(
        {
            "date": pd.date_range(
                "2026-01-01",
                periods=days,
                freq="D",
            ),
            "mean": values,
            "max": [
                value + 2
                for value in values
            ],
            "min": [
                value - 2
                for value in values
            ],
        }
    )


def test_creates_seven_rows_per_origin_date() -> None:
    result = build_feature_table(
        make_daily_prices()
    )

    counts = result.groupby(
        "origin_date"
    ).size()

    assert len(result) == 70
    assert (counts == 7).all()
    assert set(result["horizon"]) == set(
        range(1, 8)
    )


def test_target_date_matches_horizon() -> None:
    result = build_feature_table(
        make_daily_prices()
    )

    expected_target = (
        result["origin_date"]
        + pd.to_timedelta(
            result["horizon"],
            unit="D",
        )
    )

    assert (
        result["target_date"]
        == expected_target
    ).all()


def test_lags_and_rolling_features() -> None:
    result = build_feature_table(
        make_daily_prices()
    )

    first_row = result.iloc[0]

    assert first_row[
        "origin_date"
    ] == pd.Timestamp("2026-01-14")

    assert first_row["mean_lag_0"] == 13
    assert first_row["mean_lag_6"] == 7

    assert first_row[
        "mean_rolling_7"
    ] == pytest.approx(10.0)

    assert first_row[
        "mean_rolling_14"
    ] == pytest.approx(6.5)

    assert first_row[
        "max_rolling_14"
    ] == 15

    assert first_row[
        "min_rolling_14"
    ] == -2


def test_future_does_not_change_features() -> None:
    original = make_daily_prices()
    changed = original.copy()

    # Detta datum ligger efter första origin_date.
    changed.loc[
        14,
        ["mean", "max", "min"],
    ] = 9999

    original_table = build_feature_table(
        original
    )
    changed_table = build_feature_table(
        changed
    )

    original_result = original_table.iloc[0]
    changed_result = changed_table.iloc[0]

    feature_columns = get_model_feature_columns(
        original_table
    )

    pd.testing.assert_series_equal(
        original_result[feature_columns],
        changed_result[feature_columns],
    )


def test_targets_are_not_model_features() -> None:
    result = build_feature_table(
        make_daily_prices()
    )

    feature_columns = get_model_feature_columns(
        result
    )

    assert "y_mean" not in feature_columns
    assert "y_max" not in feature_columns
    assert "y_min" not in feature_columns
    assert "origin_date" not in feature_columns
    assert "target_date" not in feature_columns


def test_rejects_leakage_from_a1() -> None:
    daily = make_daily_prices()

    def leaky_available_data(
        data: pd.DataFrame,
        origin_date: pd.Timestamp,
    ) -> pd.DataFrame:
        return data[
            data["date"]
            <= origin_date + pd.Timedelta(days=1)
        ]

    with pytest.raises(
        ValueError,
        match="data efter origin_date",
    ):
        build_feature_table(
            daily,
            available_data_fn=(
                leaky_available_data
            ),
        )


def test_rejects_missing_dates() -> None:
    daily = make_daily_prices().drop(
        index=10
    )

    with pytest.raises(
        ValueError,
        match="saknade datum",
    ):
        build_feature_table(daily)