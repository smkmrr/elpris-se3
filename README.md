# Elpris SE3 — 7-day spot price forecast

## Problem and purpose
Forecast the daily mean, max and min spot price in SE3 for each of the next seven days.

## Target users
Households with high electricity use, e.g. EV owners planning when to charge.

## Group members
- Bilal Mah
- Hamed Rezaei
- Isac Reger
- Ali Akyel

## Data source
_TBD: source, owner, terms of use, fetch date, limitations._

## Project structure
_TBD_

## Installation
_TBD_

## How to run
_TBD_

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
