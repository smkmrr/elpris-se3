"""Hämta SE3-elpriser från elprisetjustnu.se och spara rådata per dag."""

import json
import time
from datetime import date, timedelta
from pathlib import Path

import httpx

START_DATE = date(2021, 11, 1)
RAW_DIR = Path("data/raw")
API_URL = "https://www.elprisetjustnu.se/api/v1/prices/{day.year}/{day:%m-%d}_{area}.json"


def build_url(day, area="SE3"):
    """URL till API:t för en dag och ett elområde."""
    return API_URL.format(day=day, area=area)


def fetch_range(start, end, raw_dir=RAW_DIR, area="SE3"):
    """Hämta varje dag från start till end och spara som JSON i raw_dir.

    Dagar som redan finns sparade hoppas över.
    """
    raw_dir.mkdir(parents=True, exist_ok=True)

    day = start
    while day <= end:
        filename = raw_dir / f"{day}_{area}.json"

        if not filename.exists():
            response = httpx.get(build_url(day, area), timeout=20)

            if response.status_code == 200:
                data = response.json()
                filename.write_text(json.dumps(data))
                print("Sparade", filename, "med", len(data), "priser")
                time.sleep(0.5)
            else:
                print("Misslyckades:", day, "kod", response.status_code)

        day += timedelta(days=1)


def main():
    fetch_range(START_DATE, date.today())


if __name__ == "__main__":
    main()