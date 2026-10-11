"""Hämta ett mindre SE3-utdrag för Grupp B."""

from __future__ import annotations

import argparse
from datetime import date, timedelta
from pathlib import Path

import httpx
import pandas as pd


API_URL = (
    "https://www.elprisetjustnu.se/api/v1/prices/"
    "{year}/{month_day}_{area}.json"
)


def fetch_daily_prices(
    start_date: str | date,
    end_date: str | date,
    area: str = "SE3",
) -> pd.DataFrame:
    """Hämta priser och skapa date, mean, max och min i SEK/kWh."""

    start = pd.Timestamp(start_date).date()
    end = pd.Timestamp(end_date).date()

    if end < start:
        raise ValueError(
            "end_date måste vara samma dag som eller efter start_date"
        )

    rows = []

    with httpx.Client(
        timeout=20.0,
        follow_redirects=True,
    ) as client:
        current = start

        while current <= end:
            url = API_URL.format(
                year=current.year,
                month_day=current.strftime("%m-%d"),
                area=area,
            )

            response = client.get(url)
            response.raise_for_status()

            observations = response.json()

            prices = pd.Series(
                [
                    item["SEK_per_kWh"]
                    for item in observations
                ],
                dtype="float64",
            )

            if prices.empty:
                raise ValueError(
                    f"Inga priser returnerades för {current}"
                )

            rows.append(
                {
                    "date": current.isoformat(),
                    "mean": prices.mean(),
                    "max": prices.max(),
                    "min": prices.min(),
                }
            )

            current += timedelta(days=1)

    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--end-date",
        required=True,
        help="Sista datum, YYYY-MM-DD",
    )

    parser.add_argument(
        "--days",
        type=int,
        default=28,
    )

    parser.add_argument(
        "--area",
        default="SE3",
        choices=("SE1", "SE2", "SE3", "SE4"),
    )

    parser.add_argument(
        "--output",
        default="data/sample_daily_prices.csv",
        type=Path,
    )

    args = parser.parse_args()

    end = pd.Timestamp(args.end_date).date()
    start = end - timedelta(days=args.days - 1)

    daily = fetch_daily_prices(
        start_date=start,
        end_date=end,
        area=args.area,
    )

    args.output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    daily.to_csv(
        args.output,
        index=False,
    )

    print(
        f"Sparade {len(daily)} dagar i {args.output}"
    )


if __name__ == "__main__":
    main()