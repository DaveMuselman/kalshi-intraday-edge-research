# October 19, 2026 — original systematic Kalshi discovery, through 10:00 Eastern market open
READ-ONLY RESEARCH. All values are modeled exchange-orderbook replay P&L after modeled fees, NOT authenticated orders or funded profit. No paper league selection was used.

## Provenance / methodology
The original frozen 24,570 theoretical-rule grammar from systematic_native200_scan.py was evaluated in seven nonoverlapping completed-market batches. The latest batch 09:15–10:00 EDT was rerun today via the original read-only discover_new_closed_windows.py, using original prepare_native200_grids.py causal 200ms reconstructions and same original strict QA. Earlier 00:00–09:00 EDT results already existed and were consolidated, NOT reexecuted during this session. Exact 7 folders under DISCOVERY_RUNS:
- 2026-10-19_0000_0030
- 2026-10-19_0045_0130
- 2026-10-19_0145_0215
- 2026-10-19_0230_0315
- 2026-10-19_0330_0700
- 2026-10-19_0715_0900
- 2026-10-19_0915_1000
Each has quality_report.json, research_summary.json, scenarios_by_market.jsonl, and versioned reconstructed grids; 09:15–10:00 raw/seed hashes and all 16 accepted official final results saved in its quality_report. No overlap in coin+Eastern opening.

## Strict quality and effective sample
41 distinct 15-minute openings, seven coins each: 287 recorded coin-windows, 183 strict-QA accepted with 183/183 verified official finalized Kalshi results; 104 excluded. Of original 24,570 configurations, 3,162 unique variants produced at least one modeled buy across the accepted windows. Same >=80% reconstructed causal 200ms quote+underlier coverage gate, early contemporaneous target and first valid quote, clock/sequence/gap checks; DO NOT change quality policy to raise apparent win rates.
The latest independent 09:15–10:00 EDT run: 28 recorded, 16 accepted and officially finalized, 12 excluded.

## All October 19 to date: four preexisting frozen rule baselines
| Immutable rule | Profitable / modeled buys | Modeled net USD | Worst one loss USD |
|---|---:|---:|---:|
| YES_55_10_MOVE10_ALIGNED_SPREAD_LE2C_FIRST_180S | 85/102 | +27.5405 | -9.4756 |
| NO_40_10_MOVE10_OPPOSED_SPREAD_LE2C_FIRST_180S | 64/76 | +57.0691 | -9.5864 |
| NO_35_15_MOVE10_OPPOSED_SPREAD_LE2C_FIRST_180S | 38/52 | +37.3643 | -9.8800 |
| YES_60_15_MOVE10_ALIGNED_SPREAD_LE2C_FIRST_180S | 71/88 | +56.0375 | -9.8688 |

Latest four openings alone: YES55 12/13 +16.6108; NO40 5/7 -5.6742; NO35 2/3 -0.3152; YES60 8/12 -12.2254.

## Full-grid research candidates: positive TODAY, contradicted on older strict-quality Oct18 replay
Exploratory candidate A: YES_40_15_ANY_SPREAD_LE2C_FIRST_180S. T+40..180 sec, YES ask 33–40c, YES spread <=2c, NO underlying move filter; model 40c limit BUY and 55c full-inventory target sale. On today's 183 QA-clean: 83/103 +151.2823 base 2s, 77/97 +141.7098 at 4s+0.5c each leg, 71/90 +134.4180 at 8s+1c each leg. Yet on independently older Oct18 later/evening clean 56+20 markets: 30/44 -14.8856 base; 29/43 -7.4190 at 4s+0.5c; 25/39 -23.4695 at 8s+1c. Do not promote.
Exploratory candidate B: YES_35_15_ANY_SPREAD_LE2C_FIRST_180S. T+40..180 sec, YES ask 28–35c, YES spread <=2c, NO underlying move filter; model 35c BUY and 50c full-inventory target sale. Today's 183 clean: 63/79 +144.9820 base, 57/74 +125.1713 at 4s+0.5c, 49/67 +88.6819 at 8s+1c. Older Oct18 76 strict-clean: 23/35 -17.4765 base, 23/35 -1.0327 at 4s+0.5c, 18/30 -33.0498 at 8s+1c. Do not promote.
Note: These are distinct from earlier YES40 SECOND_90S rejected configurations. Older Oct18 is retrospective falsification, NOT independent future prospective validation. The market-open times and seven coins are correlated, and 24,570-way selection induces multiple-comparison bias.

## Chronological research insight (exploratory, not pristine unseen validation)
When today's openings are divided TRAIN 00:00–04:45 EDT, TEST 05:00–07:15 EDT, HOLDOUT 07:30–10:00 EDT, 1,069 variants passed initial train criteria and 233 appeared positive in all three partitions. Many are near duplicates and the windows had been inspected in earlier research runs. The top TRAIN candidate YES_60_10_ANY_SPREAD_LE2C_SECOND_90S did +74.2234 in TRAIN but -16.2238 in TEST (then +32.7151 in later group), so it does not survive all three. No independent new rule validated by this procedure.

## Exact cautions
- Initial October 18 broad study's quality notes already defined the 80% coverage threshold; later strict-quality studies consistently excluded insufficient-coverage cases *before scoring*. Do not describe the threshold itself as newly invented. Initial 140 raw windows included 76 meeting >=80% coverage; the original 55/62 YES55 tally was computed in the broad initial 140-window research, not restricted to only those 76.
- Historical BUY/SELL fills are simulated from displayed signed L2 orderbook and specified 2s modeled delays/fee. A PROXY_SETTLEMENT model-status label can use separately verified Kalshi finalized YES/NO payout direction; official settlement does not prove any earlier BUY/SELL actually filled.
- Today's candidate P&Ls are not additive portfolios: candidate signals overlap each other and frozen baselines; size and concurrent exposure need separate enforcement.
- No funded controller, original paper cohort, recorder, or trading account was modified or armed in this research. Do NOT call these rules live-approved.


## User-local Central day interpretation (important)
The primary analysis above uses October 19 EASTERN market-opening date because source filenames are Eastern. Eastern 00:00–00:45 corresponds to October 18 23:00–23:45 CENTRAL. Excluding those four openings, the user-local October 19 CENTRAL 00:00–09:00 market openings (01:00–10:00 EDT) total 259 raw coin-windows, 167 strict QA accepted, 167 verified official settlements and 3,159 active rules.
- Frozen YES55: 73/88, modeled +$19.4681
- Frozen NO40: 60/71, modeled +$58.3127
- Frozen NO35: 37/50, modeled +$42.4119
- Frozen YES60: 65/81, modeled +$48.8326
- Exploratory YES40->55: 73/91, modeled +$132.1884
- Exploratory YES35->50: 56/72, modeled +$117.7253
The older Oct18 retrospective counterevidence still applies. Neither apparent candidate is validated for live execution.
