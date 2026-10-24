# Elpris SE3 – prognos för spotpriset sju dagar framåt

## Problem och syfte
Prognos för dagens medel, högsta och lägsta spotpris i SE3 för var och en
av de kommande sju dagarna. Prognosen görs varje dag kl. 12.

## Målgrupp
Hushåll med hög elförbrukning, till exempel elbilsägare som vill planera
när de ska ladda.

## Gruppmedlemmar
- Bilal Mah
- Hamed Rezaei
- Isac Reger
- Ali Akyel

## Datakälla
Spotpriser för elområde SE3 hämtas från API:et
[Elpriset just nu](https://www.elprisetjustnu.se/elpris-api), som drivs av
Beneficial Apps AS. Datan kommer ursprungligen från ENTSO-E och är fri att
använda om källan anges. Den finns från 1 november 2021 och fram till idag.
Priserna är i SEK per kWh, utan skatt, moms och nätavgifter.

Datan sparas inte i repot. Den hämtas med skriptet i steg 1 under
"Så här kör du", och hämtningsdatumet är den dag skriptet körs.

Begränsningar och detaljer om bearbetningen finns i
[docs/datakalla.md](docs/datakalla.md).

## Projektstruktur

```
data/raw/          rådata från API:et, en JSON-fil per dag (inte i git)
data/processed/    hourly_prices.csv och se3_daily.csv (inte i git)
docs/              datakälla och utvärdering
notebooks/         utforskning (EDA, testupplägg, Random Forest, felanalys)
results/           MAE-tabeller och grafer (skapas av evaluate)
src/elpris/        all kod i projektet
tests/             tester med pytest
```


## Installation
Requires Python 3.10 or later.

```bash
git clone https://github.com/smkmrr/elpris-se3.git
cd elpris-se3
python -m venv .venv
source .venv/Scripts/activate   # Windows (Git Bash)
# source .venv/bin/activate     # macOS / Linux
pip install -e ".[dev]"
pytest
```

## How to run
Run each step from the project root:

| Step | Command | Output |
|---|---|---|
| 1. Fetch prices | `python -m elpris.hamta_elpris` | `data/raw/` (takes 15–20 min the first time, then only new days) |
| 2. Build hourly and daily prices | `python -m elpris.bygg_priser` | `data/processed/se3_daily.csv` |
| 3. Compare baseline and Random Forest | `python -m elpris.evaluate` | `results/` |
| 4. Forecast the next seven days | `python -m elpris.forecast` | table printed in the terminal |

## Methods
_TBD: baseline and Random Forest._

## Results
_TBD_

## Limitations
_TBD_

## Use of generative AI
_TBD_

## License
_TBD_


## Prognosdefinition och baseline

Prognosen görs varje dag D klockan 12.00 för dag D+1 till D+7.
Detta ger flera historiska testfall och gör att felet senare kan
redovisas separat för prognosdag 1 till 7.

Vid prognostillfället betraktas spotpriserna till och med dag D
som kända. Priserna för D+1 publiceras först omkring klockan 13.

### Baseline 1

För varje måldag används samma veckodag en vecka tidigare.

För måldagen D+h används:

`D+h−7`

Det betyder:

- Prognosdag 1 använder dag D−6.
- Prognosdag 2 använder dag D−5.
- Prognosdag 3 använder dag D−4.
- Prognosdag 4 använder dag D−3.
- Prognosdag 5 använder dag D−2.
- Prognosdag 6 använder dag D−1.
- Prognosdag 7 använder dag D.

Baselinen förutsäger följande tre dagsvärden:

- Dagsmedel
- Högsta dagspris
- Lägsta dagspris

Dagstabellen ska innehålla kolumnerna:

- `date`
- `mean`
- `max`
- `min`

Baseline-funktionen returnerar sju prognosrader med
`forecast_date`, `target_date`, `horizon`, `source_date`,
`mean`, `max` och `min`.

Kolumnen `source_date` visar vilken historisk dag prognosen
hämtades från och kan användas för att kontrollera att ingen
framtida information har använts.

### Baseline 2

En andra baseline där dag D:s värden används för samtliga sju
prognosdagar är valfri och har inte implementerats i den första
versionen.
