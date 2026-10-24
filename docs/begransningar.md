# Resultat, begränsningar och risker

Det här dokumentet bygger på felanalysen i `notebooks/03_a2_hamed.ipynb` och tabellerna i `results/`. Prognosdagarna i testperioden är 2025-10-01 till 2026-10-05.

## Vad resultaten visar

- **Helhet.** Random Forest hade lägre MAE än baseline för alla tre målvärden (dagsmedel, högsta och lägsta pris) och alla sju prognosdagar, räknat över hela testperioden. För dagsmedel dag 1 var felet 0,270 kr/kWh för RF och 0,362 kr/kWh för baseline.

- **Störst skillnad dag 1.** Där hade RF ungefär 25 % lägre fel för dagsmedel och högsta pris. En trolig förklaring är att RF använder dagens priser, vilket baseline inte gör.

- **Mindre skillnad längre fram.** Ju längre fram prognosen gäller, desto mindre blev skillnaden. För lägsta pris dag 7 var RF bara ungefär 6 % bättre (0,254 mot 0,270).

- **Baselinen är platt.** Baselinens fel var nästan lika stort alla dagar (ungefär 0,36 kr/kWh för dagsmedel). Det beror på att baselinens prognos för en viss dag alltid är samma veckodag veckan innan, oavsett när prognosen görs.

## Vad resultaten inte visar

- **Att RF är bättre under alla förhållanden.** Medelvärdet över hela testperioden döljer skillnader mellan årstider. På vintern hade RF större fel än baseline för lägsta pris (se nedan).

- **Hur dyra felen är för ett hushåll.** MAE räknar alla fel lika, men ett fel på en dag med mycket höga priser kostar mer än ett lika stort fel på en billig dag. Utvärderingen mäter alltså inte den ekonomiska konsekvensen av felen.

- **Om hushållet väljer rätt dag.** Användaren vill främst veta vilken dag som är billigast. Vi har inte mätt hur ofta prognosen pekar ut rätt billigaste dag, bara hur stort felet är i kr/kWh.

- **Hur säkra skillnaderna är.** Testperioden är ett år, och vi har inte beräknat osäkerhet eller spridning. Små skillnader, till exempel ca 6 % för lägsta pris dag 7, kan bero på slumpen. Hösten finns dessutom med två gånger i testperioden (2025 och 2026), vilket ger den större vikt.

- **Hur modellerna fungerar i framtiden.** Resultaten gäller testperioden oktober 2025 – oktober 2026. Om prisnivån eller elmarknaden ändras kan felen bli både större och mindre.

## Var modellerna missar

Tabellerna finns i `results/mae_by_season.csv`, `results/bias_by_season.csv` och `results/mae_spike_vs_normal.csv`.

- **Spikdagar.** En spikdag är en dag där det verkliga högsta priset hör till de 10 % högsta i testperioden (38 dagar). På spikdagar är felet för högsta pris ungefär dubbelt så stort som på vanliga dagar för båda modellerna (ca 1,04 kr/kWh mot 0,40–0,52). Random Forest är bättre än baseline på vanliga dagar, men inte på spikdagar. För dagsmedel och lägsta pris är RF till och med sämre än baseline på spikdagar.

- **Vintern och lägsta pris.** Random Forest hade större fel än baseline för lägsta pris på vintern (MAE 0,344 mot 0,270). Bias var −0,265, alltså förutsade RF i genomsnitt för lågt pris. Under övriga årstider var bias nära noll. Grafen i notebooken visar att prisnivån steg kraftigt från mitten av januari 2026 och att RF inte följde med.

- **Hösten.** Hösten hade störst fel för baseline (alla målvärden) och för högsta pris hos RF. En förklaring är att de flesta spikdagarna låg på hösten (16 av 38). En annan är att hösten finns med två gånger i testperioden, från två olika år.

- **Längre prognoser.** Random Forests fel ökar något med antalet dagar framåt, från 0,270 dag 1 till 0,313 dag 7 för dagsmedel. Baselinens fel är ungefär lika stort alla dagar.

## Begränsningar i data

- **Bara spotpris.** Datan är spotpriset för elområde SE3 från Elpriset just nu (som hämtar från ENTSO-E). Skatt, moms, nätavgift och påslag ingår inte.
- **Hela SE3, inte bara Stockholm.** Priset är detsamma i hela elområdet.
- **Timmedel i stället för kvartspriser.** Från 1 oktober 2025 finns priser per kvart. Vi räknade om dem till timmedel så att hela perioden blir jämförbar. Då försvinner korta pristoppar inom en timme, så det verkliga högsta priset kan vara något högre än i vår data.
- **En timme saknas i källan.** 2021-11-04 saknar timmen 23:00. Dagsvärdena för den dagen bygger på 23 timmar.
- **Energikrisen 2022.** Träningsdatan innehåller sensommaren och hösten 2022 med extremt höga priser (som mest 8,56 kr/kWh 2022-08-30). Det kan påverka vad modellen lär sig om normala prisnivåer.
- **Ingen väderdata.** Temperatur, vind och vattennivåer påverkar elpriset men finns inte med. SMHI:s öppna data har inga historiska prognoser från prognostidpunkten, så temperatur togs bort (se issue #18). Uppmätt temperatur kunde inte användas i stället, eftersom den inte är känd kl. 12 för de kommande dagarna och skulle ge dataläckage.

## Begränsningar i metoden

- **Random Forest tränas en gång.** Modellen tränas på data fram till hösten 2025 och tränas inte om under testperioden. Den kan därför inte anpassa sig när prisnivån ändras.
- **Random Forest kan inte extrapolera.** Modellen förutsäger medelvärden av det den har sett i träningen. Den har därför svårt att förutsäga priser som är högre eller lägre än tidigare.
- **Bara prishistorik och kalender som features.** Modellen vet inget om väder, bränslepriser eller produktion, som ofta förklarar stora prisförändringar.
- **Standardinställningar.** Random Forest körs med 200 träd och sklearns standardinställningar, utan hyperparameteroptimering. En modell förutsäger alla tre målvärden och alla sju prognosdagar samtidigt.
- **Baseline använder inte dagens priser.** Baselinen tittar bara på samma veckodag förra veckan. Det gör den enkel och stabil, men långsam när prisnivån ändras.
- **Ett enda mätvärde.** Vi mäter bara MAE. Prognoserna har inga osäkerhetsintervall, så användaren vet inte hur säker en enskild prognos är.
- **Demon och utvärderingen använder olika träning.** I utvärderingen tränas Random Forest en gång på data fram till september 2025. I demon (`forecast.py`) tränas den om på all data fram till prognosdagen. Utvärderingens siffror gäller alltså en modell som inte tränas om. Demomodellen har mer och nyare data och kan därför vara något bättre, men det har vi inte mätt.

## När prognosen inte ska användas

- **På spikdagar.** Felet för högsta pris är ungefär dubbelt så stort som vanliga dagar, och Random Forest är inte bättre än baseline. Ett hushåll kan alltså inte lita på prognosen för att undvika de dyraste dagarna.

- **På vintern, särskilt för lägsta pris.** Random Forest hade större fel än baseline (MAE 0,344 mot 0,270) och förutsade för lågt pris (bias −0,265). Från mitten av januari 2026 steg prisnivån kraftigt och RF följde inte med. Ett hushåll kan då tro att en dag är billigare än den är. På vintern bör man därför jämföra RF med baseline: om modellerna skiljer sig mycket är prognosen osäker.

- **När prisnivån plötsligt ändras.** Random Forest tränades bara en gång, på data fram till hösten 2025, och lär sig inte av nya priser under testperioden. När priserna plötsligt stiger eller sjunker följer RF därför inte med. Baseline följer efter, men först en vecka senare. De första veckorna efter en stor förändring är alltså båda modellerna osäkra.

- **Som en prognos för elräkningen.** Prognosen gäller bara spotpriset i SE3. Skatt, moms, nätavgift och elhandlarens påslag ingår inte. Prognosen visar därför när el är relativt billig eller dyr, men inte vad hushållet faktiskt kommer att betala.

## Förslag på förbättringar

Varje förslag bygger på ett fynd från felanalysen.

- **Träna om modellen regelbundet (expanderande fönster).** RF följde inte prisnivån i januari 2026 eftersom den bara tränades en gång. Om modellen tränas om varje vecka med all data fram till prognosdagen kan den anpassa sig snabbare. Demon i `forecast.py` gör redan detta, men nästa steg är att även utvärdera modellen på samma sätt, så att siffrorna gäller den modell som faktiskt används.
- **Lägg till väderprognoser.** Felen var störst på vintern och hösten, då väder påverkar priset mest. Temperatur- och vindprognoser kan hjälpa modellen att förutse höga priser. Det kräver en källa med historiska prognoser från prognostidpunkten, till exempel Open-Meteos historiska prognoser, så att ingen framtida information läcker in.
- **Korrigera systematiska fel.** RF:s fel på vintern var mest systematiska (bias −0,265 av MAE 0,344). En enkel korrigering baserad på de senaste veckornas fel kan minska dem.
- **Mät det användaren bryr sig om.** Mät hur ofta prognosen pekar ut rätt billigaste dag i veckan, inte bara felet i kr/kWh.
- **Ge osäkerhet i prognosen.** Ett intervall, till exempel "mellan 0,8 och 1,2 kr/kWh", skulle visa när prognosen är osäker, särskilt på vintern och vid spikdagar.