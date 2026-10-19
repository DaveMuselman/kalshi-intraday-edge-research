# Full original Kalshi 200ms systematic rule search — NEW October 18 periods
Finished 2026-10-18. **READ-ONLY RESEARCH**, no funded trading changes, no API orders, no modifications to 22 paper cohorts or the initial October 18 training outputs.

## Chronology and data
- Original discovery had selected YES55→65 from 08:00-12:45 EDT and evaluated the additional 13:00-13:30 EDT untouched block.
- NEW subsequent research tape: 13:45-19:15 EDT October 18, **7 coins × 23 15-minute openings = 161 coin-windows**.
- Frozen chronological time groups BEFORE running search: TRAIN 13:45–15:45 EDT (9 windows/coin); TEST 16:00–17:00 (5); later HOLDOUT 17:15–19:15 (9).
- Each raw recording and preceding seed recording verified for presence/uniqueness; gzip and JSON parse, exact ticker and timestamped current-market strike metadata, no declared gaps/clock reversals >250ms/receiver gaps >5s, early valid quote, causal book reconstruction, quote freshness max 1.8s and underlying benchmark age max 1.5s.
- **56/161 windows pass the strict 80%-fresh-book coverage criterion**, 105 rejected. There are **35 missing strike metadata windows**, ALL seven coins at **15:00, 16:00, 18:15, 18:30, 18:45 EDT**; these yield no valid book+target grid. Remaining low-coverage exclusions reflect actual stale/missing usable reconstructed quotes. Raw files can be intact but their derived data are unusable.
- Quality accepted: TRAIN 32 coin-windows, TEST 11, HOLDOUT 13. This is a small, correlated sample; does NOT represent all market opportunities.
- **All 56 included tickers verified FINALIZED with published YES/NO settlement via public Kalshi read-only API**, replacing the original study's provisional final-60s benchmark settlement proxy for outcomes. Quote-depth BUY/SELL are still purely **modeled fills**, NOT exchange-confirmed.
- Original exact systematic_native200_scan.py entry/exit/features/search was reused with a separate driver and separate outputs; only *independent market selection* and official finalized outcomes supplied externally. No original scenario thresholds, delays, fees or execution assumptions were optimized.
- 24,570 theoretical combinations (2 sides × 13 price limits × 3 profit targets × 15 trajectory conditions × 7 book filters × 3 early-entry time filters). **3,006 produced >=1 modeled buy** in quality-accepted windows; **937** passed original TRAIN n>=8, wins>=6, positive net; **139** passed test n>=3 positive and holdout n>=4 positive as well.
- **These 139 ARE NOT 139 independently validated trading strategies.** Multiple rules are nearly identical; the same time series and official later period were used to select them. Look-ahead in outcome selection remains and independent unseen forward testing is necessary.

## Previously frozen strategy: YES55 to YES65
YES_55_10_MOVE10_ALIGNED_SPREAD_LE2C_FIRST_180S, original unchanged.
| Chronological group | Modeled wins/trades | Modeled net |
|---|---:|---:|
| TRAIN | 13/14 | +$21.838 |
| TEST | 5/6 | +$2.018 |
| HOLDOUT | **3/5** | **−$12.619** |
| ALL accepted | 21/25 | +$11.237 |

In clean ETH 19:00 EDT (18:00 CDT) the rule qualified a signal at T+172sec: YES ask 48c, spread 1c, 10-second underlying momentum +6.019bp. One modeled 17-share BUY around T+174 and 55c ceiling would have been a ~-$9.14 losing trade at the market's officially verified NO result, with no confirmed model exit at 65c. This is an **actual failure mode of the frozen rule**, not only manual deviation from the rule. Separately, user's much larger later ETH buys caused greater dollar exposure than the original ~$10-per-window fixed model.

## Highest-interest independent candidate families from this SEARCH (do not deploy yet)

### A: NO40→50, rising underlying, tight spread
Exact original scenario:
NO_40_10_MOVE10_OPPOSED_SPREAD_LE2C_FIRST_180S

Condition: ask for NO 33–40c; NO bid/ask spread <=2c; 10-second underlying benchmark **rises >=1bp** (a move *opposing* NO); first eligible signal T+40–180s, one ~$8–$10 modeled 40c-limit BUY after 2 seconds (23 whole contracts at maximum 40c), sell NO at 50c+ with original target and close/settlement handling. NOT YES55 and NOT an API-configured trading strategy.

| Quality-screened sample | Modeled wins/trades | Net modeled |
|---|---:|---:|
| Oct 18 new TRAIN | 13/15 | +$27.306 |
| Oct 18 new TEST | 7/8 | +$5.615 |
| Oct 18 new HOLDOUT | 7/7 | +$19.771 |
| Oct 18 combined | **27/30** | **+$52.691** |
| Oct 16 earlier date, 53 quality-screened windows | **29/34** | **+$25.245** |
| Oct 17 earlier date, 40 quality-screened windows | **11/12** | **+$20.926** |

- Oct18 30 modeled purchases occur in **only 9 distinct 15-minute market-start times** across seven coins; correlated crypto outcomes greatly reduce statistical independence.
- Of the Oct18 3 modeled losses, two were NEAR and one DOGE. There was no modeled guarantee against ~$9 losses.
- Original stress evaluator on same 56 strict-clean Oct18 windows: 4s delay 24/28 +$48.700; 8s delay 23/27 +$60.737; 0.5c per-leg adverse slippage 24/29 +$33.911; 4s+slippage 23/29 +$34.845.
- Earlier Oct16 and Oct17 tests used the historical archives and official finalized market outcomes, but are **earlier in calendar time**, not prospective market-forward holdouts.

### B: YES60→75, momentum, tight spread
YES_60_15_MOVE10_ALIGNED_SPREAD_LE2C_FIRST_180S

Signal YES ask 53–60c, spread <=2c, prior 10s rising benchmark >=1bp, T+40–180s; modeled 60c BUY ceiling; sell at YES bid>=75c, with original close/expiry.
- Oct18 28/31 positive, +$52.366 modeled; TRAIN 14/15 +$33.513, TEST 8/9 +$11.714, HOLDOUT 6/7 +$7.139.
- Oct16 quality-screened 30/39 positive, +$5.840; Oct17 quality-screened 18/23 positive, +$7.533.
- Original stress: 8s delay 22/26 +$31.222; 0.5c adverse price on each leg 26/29 +$47.987.
- It is NOT validated for live funding or shown safer than the original. ZEC losses were present in this rule.

### C: NO35→50, benchmark rising, tight spread
NO_35_15_MOVE10_OPPOSED_SPREAD_LE2C_FIRST_180S
- Oct18 23/29 profitable, +$59.040; TRAIN 13/18 +$25.988, TEST 5/6 +$9.774, HOLDOUT 5/5 +$23.279.
- Oct16 quality-screened 23/28 +$53.304; Oct17 quality-screened 4/5 +$12.781.
- With 4s delay+0.5c slippage per leg: 21/29 +$45.640; 6 losses in base are significant tail risk.

## Selection warnings / what is NOT proven
- An optimizer searched thousands of conditions, and filtering the later period for positive results **uses up the holdout for the selected candidate**. No untouched *future* block remains in this completed research for a genuinely unbiased rule-selection confirmation.
- Quality selection of just 56/161 windows can also bias sample composition. Weak source windows are NOT counted as losses or wins; neither should they be silently included to boost averages.
- No partial fill, queue depth certainty, real account concurrency, maker competition, intermittent API, or actual limit order resting modeled to production reliability.
- Shared clock times across seven coins are correlated. Multiple modeled funded trades per concurrent market window would need separate authorization, risk limits and server capacity.
- NO live code was changed. No automatic promotion/arming. The original YES55 logic and 22 paper cohorts remain untouched.
- The prior-day October 17 comparison initially omitted 8 public outcomes because of temporary read-read issues, then a second successful public GET and rerun confirmed **40/40** quality-clean market outcomes; report uses the complete v2 rerun. Oct16 **53/53** verified.
- This report is a candidate-screening research artifact, not a claim of future winning probability. Require forward shadow capture, full BUY/SELL execution reconciliation and hard adverse-risk tests before live promotion.

## Source artifacts (in this folder and parent)
full_grid_results.json; quality_decisions.json; official_finalized_verification.json; per_market_scenarios.jsonl; stress_shortlist.json; cross_date_16_official_quality_verified.json; cross_date_v2_17_official_quality_verified.json.
In parent: oct18_postdiscovery_raw_audit_v1.json, oct18_new1730_1915_raw_audit_v2.json, oct18_postdiscovery_prepared_quality_v1.json, oct18_new1730_1915_prepared_quality_v2.json and their frozen source scripts.
