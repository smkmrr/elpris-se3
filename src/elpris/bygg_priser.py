"""Bygg tim- och dagspriser från rådatan i data/raw."""

import json
from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")


def load_raw(raw_dir=RAW_DIR, area="SE3"):
    """Läs alla råfiler till en tabell med en rad per pris."""
    files = sorted(raw_dir.glob(f"*_{area}.json"))
    print("Antal filer:", len(files))

    rows = []
    for filename in files:
        rows.extend(json.loads(filename.read_text()))
    return pd.DataFrame(rows)


def to_hourly(prices):
    """Timmedel av priserna. Kvartspriser (från 1 okt 2025) blir ett pris per timme."""
    time_start = pd.to_datetime(prices["time_start"], utc=True)

    # Avrunda nedåt till hel timme i UTC för att slippa sommartidsproblem
    hour = time_start.dt.floor("h").dt.tz_convert("Europe/Stockholm")

    hourly = (
        prices.assign(hour=hour).groupby("hour")["SEK_per_kWh"].mean().reset_index()
    )
    hourly["date"] = hourly["hour"].dt.date
    return hourly


def to_daily(hourly):
    """Medel, högsta och lägsta timpris per dag."""
    return (
        hourly.groupby("date")["SEK_per_kWh"].agg(["mean", "max", "min"]).reset_index()
    )


def report_quality(hourly):
    """Skriv ut saknade timmar och dagar som inte har 24 timmar."""
    expected = pd.date_range(hourly["hour"].min(), hourly["hour"].max(), freq="h")
    missing = expected.difference(hourly["hour"])
    print("Förväntade timmar:", len(expected))
    print("Timmar vi har:", len(hourly))
    print("Saknade timmar:", len(missing))
    print(missing)

    hours_per_day = hourly.groupby("date")["hour"].count()
    print(hours_per_day[hours_per_day != 24])


def main():
    prices = load_raw()
    hourly = to_hourly(prices)
    report_quality(hourly)
    daily = to_daily(hourly)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    hourly.to_csv(PROCESSED_DIR / "hourly_prices.csv", index=False)
    daily.to_csv(PROCESSED_DIR / "se3_daily.csv", index=False)
    print("Sparade", len(hourly), "timmar och", len(daily), "dagar")


if __name__ == "__main__":
    main()
