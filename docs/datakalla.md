## Datakälla: elpriser

**Källa**: Elpriset just nu, API för elområde SE3 (https://www.elprisetjustnu.se/elpris-api) 
**Ägare**: Tjänsten drivs av Beneficial Apps AS. Prisdatan kommer ursprungligen från ENTSO-E (entsoe.eu). 
**Villkor**: Öppet och gratis att använda. Vi anger Elpriset just nu som källa. 
**Period**: 2021-11-01 till pågående 
**Innehåll**: Spotpris i SEK per kWh, exklusive skatt, moms och nätavgifter 

### Begränsningar

- Historik finns bara från 1 november 2021.
- Priserna räknas om från euro till kronor av källan och kan avvika något från officiella priser.
- Före 1 oktober 2025 finns ett pris per timme, därefter ett per kvart. Vi räknar om kvartspriserna till timmedel.
- Priset gäller hela elområde SE3, inte bara Stockholm.
- Sensommaren och hösten 2022 påverkades av energikrisen och har ovanligt höga priser (som högst 8,56 kr/kWh den 30 augusti 2022).
- En timme saknas i källans data (4 november 2021). Dagsvärdena för den dagen är räknade på 23 timmar

### Så här hämtas och bearbetas datan

1. `python -m elpris.hamta_elpris` hämtar rådata till `data/raw/`
2. `python -m elpris.bygg_priser` räknar tim- och dagspriser till `data/processed/`