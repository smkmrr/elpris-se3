import glob
import json
import os

import pandas as pd

# Hittar alla råa datafiler, sorterar
files = sorted(glob.glob("data/raw/*_SE3.json"))
print("Antal filer:", len(files))

# Läs in alla filer till en lång lista
rows = []
for filename in files:
    with open(filename) as file:
        rows.extend(json.load(file))

# Gör om listan till en tabell
prices = pd.DataFrame(rows)

# Gör om texten för "time_start" till riktig tid
prices["time_start"] = pd.to_datetime(prices["time_start"], utc=True)
prices["time_start"] = prices["time_start"].dt.tz_convert("Europe/Stockholm")

# Avrunda varje tid nedåt till hel timme (görs i UTC för att slippa sommartidsproblem)
prices["hour"] = (
    prices["time_start"]
    .dt.tz_convert("UTC")
    .dt.floor("h")
    .dt.tz_convert("Europe/Stockholm")
)

# Räkna medelpriset för varje timme
hourly = prices.groupby("hour")["SEK_per_kWh"].mean().reset_index()

# Alla timmar som borde finnas, från första till sista
expected = pd.date_range(hourly["hour"].min(), hourly["hour"].max(), freq="h")

# Vilka av dem saknas i vår data?
missing = expected.difference(hourly["hour"])

print("Förväntade timmar:", len(expected))
print("Timmar vi har:", len(hourly))
print("Saknade timmar:", len(missing))
print(missing)

columns = ["time_start", "hour", "SEK_per_kWh"]


# Lägg till en kolumn med bara datumet, räknar antal timmar per dag och visar dagarna som inte har 24 timmar
hourly["date"] = hourly["hour"].dt.date
hours_per_day = hourly.groupby("date")["hour"].count()
print(hours_per_day[hours_per_day != 24])

# Räkna medel, högsta och lägsta pris för varje dag
daily = hourly.groupby("date")["SEK_per_kWh"].agg(["mean", "max", "min"]).reset_index()

# Skapar mappen om den inte finns
os.makedirs("data/processed", exist_ok=True)

# Spara tim och dagspriser
hourly.to_csv("data/processed/hourly_prices.csv", index=False)
daily.to_csv("data/processed/daily_prices.csv", index=False)

print("Sparade", len(hourly), "timmar och", len(daily), "dagar")