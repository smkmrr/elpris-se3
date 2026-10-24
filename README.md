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
Kräver Python 3.10 eller senare.

```bash
git clone https://github.com/smkmrr/elpris-se3.git
cd elpris-se3
python -m venv .venv
source .venv/Scripts/activate   # Windows (Git Bash)
# source .venv/bin/activate     # macOS / Linux
pip install -e ".[dev]"
pytest
```

## Så här kör du
Kör varje steg från projektets rotmapp, i den här ordningen:

| Steg | Kommando | Resultat |
|---|---|---|
| 1. Hämta priser | `python -m elpris.hamta_elpris` | `data/raw/` (tar 15–20 min första gången, sedan hämtas bara nya dagar) |
| 2. Räkna tim- och dagspriser | `python -m elpris.bygg_priser` | `data/processed/se3_daily.csv` |
| 3. Jämför baseline och Random Forest | `python -m elpris.evaluate` | `results/` |
| 4. Prognos för kommande sju dagar | `python -m elpris.forecast` | tabell i terminalen |

## Metod
Varje dag D kl. 12 görs en prognos för dag D+1 till D+7. Då räknas bara
priser till och med dag D som kända, eftersom morgondagens priser
publiceras först omkring kl. 13. Prognosen gäller tre värden per dag:
medelpris, högsta pris och lägsta pris.

**Baseline:** priset för en måldag gissas vara detsamma som samma veckodag
en vecka tidigare. Den är enkel och fungerar som jämförelse.

**Random Forest:** en modell som lär sig av historiken. Den använder
priserna de senaste sju dagarna, medel, högsta och lägsta pris över de
senaste 7 och 14 dagarna, samt veckodag och månad för måldagen och hur
många dagar fram prognosen gäller.

**Utvärdering:** modellen tränas på data före 1 oktober 2025 och testas
på perioden därefter. Mellan träning och test finns en veckas mellanrum
så att ingen framtida information läcker in. Modellerna jämförs med MAE
(genomsnittligt absolut fel i SEK/kWh), separat för varje prognosdag 1–7.

## Results
_TBD_

## Begränsningar
Vad resultaten visar och inte visar, var modellerna missar, begränsningar
i data och metod och när prognosen inte ska användas finns samlat i
[docs/begransningar.md](docs/begransningar.md).

## Use of generative AI
_TBD_

## License
_TBD_


