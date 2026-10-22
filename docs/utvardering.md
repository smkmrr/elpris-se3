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



