# Utvärdering och baseline

## Syfte

Koden mäter hur bra en prognosmodell är, på samma sätt för alla modeller,
så att baseline och Random Forest kan jämföras rättvist.

## Filer

| Fil | Funktion | Gör |
|---|---|---|
| `src/elpris/metrics.py` | `mae` | Genomsnittligt absolut fel mellan verkliga och förutsagda värden |
| | `mae_table` | MAE per modell, målvärde och prognosdag |
| `src/elpris/backtest.py` | `to_long_predictions` | Gör om prognoser till gemensamt format och lägger till verkliga priser |
| | `run_baseline_backtest` | Kör baselinen för varje prognosdag i en period |
| `src/elpris/plots.py` | `plot_mae_by_horizon` | Ritar MAE per prognosdag, en linje per målvärde |

## Gemensamt prognosformat

Alla modeller ska lämna sina prognoser i det här formatet, en rad per prognos:

| Kolumn | Innehåll |
|---|---|
| `forecast_date` | Dagen då prognosen görs (kl. 12) |
| `target_date` | Dagen som förutsägs |
| `horizon` | Antal dagar framåt, 1–7 |
| `target` | `mean`, `max` eller `min` |
| `y_pred` | Förutsagt pris, SEK/kWh |
| `y_true` | Verkligt pris, SEK/kWh |
| `model` | Modellens namn |

En modell som ger prognoser i bred form (kolumnerna `mean`, `max`, `min`)
kan göras om med `to_long_predictions(forecasts, daily_prices, "modellnamn")`.

## Så körs utvärderingen

```python
import pandas as pd
from elpris.backtest import run_baseline_backtest
from elpris.metrics import mae_table
from elpris.plots import plot_mae_by_horizon

daily = pd.read_csv("data/processed/se3_daily.csv")

forecast_dates = pd.date_range("STARTDATUM", "SLUTDATUM", freq="D")
result = run_baseline_backtest(daily, forecast_dates)
table = mae_table(result)
fig = plot_mae_by_horizon(table, "baseline")
```

## Beslut

- **Mätvärde: MAE i SEK/kWh.** Visar hur mycket prognosen missar i genomsnitt,
  i samma enhet som priset.
- **MAE per målvärde och per prognosdag.** Projektförslaget kräver att
  dagsmedel, högsta och lägsta pris mäts var för sig och att felet visas för
  dag 1–7. Ett enda MAE-tal skulle dölja om modellen blir sämre längre fram
  i veckan.
- **Samma funktion för alla modeller.** Baseline och Random Forest räknas med
  exakt samma kod, så att ingen modell gynnas av hur felet räknas.
- **Baseline: samma veckodag en vecka tidigare.** Använder bara priser som är
  kända kl. 12 dag D. Fångar skillnaden mellan vardagar och helger, som syns i EDA:n.


## Slutliga resultat

Vi jämförde Random Forest med baselinen på samma testperiod: prognosdatum
från 2025-10-01 till och med 2026-10-15. Datan består av dagspriser för
elområde SE3 från Elpriset just nu. Baselinen använder priset från samma
veckodag en vecka tidigare. MAE redovisas separat för dagsmedel (`mean`),
högsta pris (`max`) och lägsta pris (`min`) för prognosdag 1–7.

Den samlade MAE-tabellen visar att Random Forest hade lägre MAE än baselinen
för samtliga tre mått och alla sju prognosdagar. Tabellen nedan visar
genomsnittet av de sju prognosdagarnas MAE:

| Mått | Baseline | Random Forest | Lägre MAE för Random Forest |
|---|---:|---:|---:|
| Mean | 0,3651 | 0,3067 | 16,0 % |
| Max | 0,5679 | 0,4694 | 17,3 % |
| Min | 0,2683 | 0,2522 | 6,0 % |

Årstidsanalysen visar att Random Forest hade lägre MAE för mean och max under
alla årstider. För min var Random Forest bättre under höst, sommar och vår,
men sämre under vintern: MAE var 0,3453 för Random Forest och 0,2704 för
baselinen. Random Forest hade också negativ bias på vintern: −0,0975 för max,
−0,1905 för mean och −0,2647 för min. Negativ bias betyder att modellen
tenderade att förutsäga för låga priser.

På vanliga dagar hade Random Forest lägre MAE för alla tre mått. På spikdagar
var MAE för max nästan lika för modellerna, och marginellt lägre för Random
Forest (1,0496 jämfört med 1,0539). För mean och min var Random Forest sämre
på spikdagar: 0,6290 jämfört med 0,5837 för mean och 0,5396 jämfört med
0,4177 för min.

Sammantaget hade Random Forest lägre MAE än baselinen under testperioden,
men felanalysen visar att den inte var bättre i alla situationer. Resultaten
gäller den utvärderade perioden och bör tolkas försiktigt, särskilt för
enskilda årstider och spikdagar.

Tabeller och graf från utvärderingen finns i `results/`. Mer om metodens
begränsningar finns i `docs/begransningar.md`.
