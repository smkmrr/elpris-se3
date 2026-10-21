import json
from datetime import date, timedelta
import os
import time

import httpx

start = date(2021, 11, 1)
end = date.today()

# Skapar mapp för rådata
os.makedirs("data/raw", exist_ok=True)

# Skapar en loop som hämtar data dag för dag, sparar i jsonfiler och hanterar eventuella fel när datan laddas in
day = start
while day <= end:
    url = f"https://www.elprisetjustnu.se/api/v1/prices/{day.year}/{day:%m-%d}_SE3.json"
    filename = f"data/raw/{day}_SE3.json"

    if os.path.exists(filename):
        day = day + timedelta(days=1)
        continue

    response = httpx.get(url)

    if response.status_code != 200:
        print("Misslyckades:", day, "kod", response.status_code)
        day = day + timedelta(days=1)
        continue

    data = response.json()

    with open(filename, "w") as file:
        json.dump(data, file)

    print("Sparade", filename, "med", len(data), "priser")

    time.sleep(0.5)

    day = day + timedelta(days=1)