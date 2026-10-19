# Systematic 200ms opening-entry search — October 18, 2026

Read-only market research. NO changes to the 22 paper cohorts or funded/API execution. NO live orders sent.

## Direct answer and method
There is no proof of a universal lossless one-sided contract trade. We searched a broad, finite family, not literally every conceivable rule.

The 200ms study reconstructed archived actual Kalshi dollar book top 2c depth, YES/NO bid/asks, coin/target distance in bps, 10/30sec momentum, five-second quote changes, and spread.

Combinatorial enumerated parameter grid: two sides × 13 entry levels (20–80c, 5c steps) × three profit targets (5, 10, 15c) × 15 coin-trajectory filters × seven book filters × three entry windows = 24,570 theoretical combinations. 3,126 generated >=1 modeled eligible purchase. Buy <=180 seconds into each 15min market; one fixed ~$10 order per isolated rule/coin-window. Sell target until near expiry, then if book is executable at preclose flatten; if unsold use recorded final-60sec CF Benchmarks average as PROVISIONAL settlement proxy. Whole contracts, top-2c ladder, 2-second simulated latency each leg, modeled fees, no queue/fill confirmation. Higher latencies and 0.5c per-leg adverse slippage separately stressed.

Historical split:
- TRAIN: 56 coin-windows, 08:00–09:45 EDT October 18, eight markets per coin.
- TEST: 28 coin-windows, 10:00–10:45 EDT October 18, four markets per coin.
- VALIDATION: 56 coin-windows, 11:00–12:45 EDT October 18, eight markets per coin.
- FRESH UNTOUCHED BLOCK: 21 coin-windows, 13:00–13:30 EDT October 18, three markets per coin, captured after the earlier research, not used to choose rules.
- An additional 84 distributed market windows from Oct 17 were prepared, but cross-date outcome validation is NOT yet complete. Do not claim otherwise.

## Important source limitations and provenance

- 140/140 October 18 initial archives readable, timestamps extend through window close, 0 explicit SEQUENCE_GAP/DISCONNECT markers, all have their own current-market TARGET_METADATA, BUT metadata always first recorded approximately 30.08–30.43 seconds AFTER opening. Therefore T+0–30 seconds—the user's primary opening interest—was NOT tested. This is a material capture/metadata synchronization gap.
- 62/140 individual archives had no current-market snapshot INSIDE that file; reconstruction requires previous-window archive seeding for full depth, which the native200 preparation used.
- Some windows show long stretches without fresh both-sided executable books, especially near expiration. Strict <=1.8sec book age and <=1.5sec observed coin price age led to >=80% valid quote ticks in only 76/140 windows; six had <60%; three archives had >5-second receive-time gaps detected by strict reconstruction even though recorder emitted no gap marker. This must be qualified, not declared faultless archival coverage.
- ETH/XRP/DOGE underlying price native ~200ms; HYPE/BNB/NEAR/ZEC underlying price native ~1s. Market BOOK sampled causally at 200ms when fresh.
- First valid quote/target observation T+30.2 to T+30.6 sec, not the literal 50c/50c opening.
- 161 October 18 market-window tape files examined for two-sided price-complement safety check: 573,534 valid 200ms samples; 0 snapshots allowed simultaneous BUY YES + BUY NO for < $1 total (minimum best ask sum ~$1.001 before fees). This means no trivial riskless paired-side arbitrage existed at sampled quotes.
- Simulator has no exchange-confirmed orders, maker queue position, partial-fill reconciliation, or official Kalshi settlement verification. Net figures are modeled, not transferable to live execution.

## Main empirical candidates from initial 140 October 18 coin-windows

**NO 80c limit BUY, 95c limit SELL, 2c maximum spread, first 180 seconds, one BUY**:
- Earlier TRAIN 20 buys, 18 profitable, +$24.41.
- TEST 11 buys, 11 profitable, +$22.41.
- VALIDATION 25 buys, 21 profitable, +$13.59.
- All three combined 56 modeled purchases, 50 profitable, +$60.41.
- 6 losses included ~$9 full-entry-loss equivalents. Correlation between coins, sample selection from multiple tested hypotheses, and queue execution risks matter.

**YES 50c limit BUY, 65c limit SELL, 2c maximum spread, during 90–180sec, with prior-30sec coin move OPPOSED to YES**:
- TRAIN 16 buys, 13 profitable, +$14.84.
- TEST 5 buys, 4 profitable, +$2.68.
- VALIDATION 21 buys, 21 profitable, +$68.90.
- Across these 140 windows 42 buys, 38 profitable, +$86.41.
- Three early TRAIN losses and one TEST loss were close to $9–$10.

**YES 55c limit BUY, 65c limit SELL, 2c maximum spread, coin's prior-10sec move favorable to YES, first 180sec**:
- TRAIN 21 buys, 18 profitable, +$9.99.
- TEST 12 buys, 10 profitable, +$4.97.
- VALIDATION 29 buys, 27 profitable, +$42.88.
- 62 modeled buys, 55 profitable, +$57.84.
- Not lossless; seven failures and significant downside tails. Trajectory alignment gave far fewer same-day failures in the later validation group.

These were chosen AFTER looking at a large space of rules; the initial three splits are not fully independent of the final selection.

## Additional 21 markets NEVER USED TO SELECT candidates

Final new-window block 13:00–13:30 EDT on October 18, 7 coins × 3 windows:
| Previously found candidate | Trades | Wins | Modeled net |
|---|---:|---:|---:|
| NO80→95, spread ≤2c | 7 | 5 | **-$9.47** |
| YES50→65, coin prior30sec adverse to YES, spread ≤2c | 4 | 3 | **-$1.54** |
| YES55→65, coin prior10sec favorable to YES, spread ≤2c | 4 | 4 | **+$7.04** |

NO80 also had a negative net under 4s, 8s, and 0.5c adverse slippage sensitivity in the fresh block. YES50's one losing fresh trade cost ~$9.26, offsetting most of three profits. YES55 4/4 is a very small independent sample and NOT proof of reliable profit; across the earlier 140 it had seven losing trades.

## Lesson: directional/target information matters, but no one-sided no-loss truth established

Actual trading opportunity depends on underlying location relative to the target, recent trend/persistence, orderbook movement/imbalance, spread and liquidity. Very high apparent chance to retrace does NOT mean the smallest remaining set of losing contracts will not overwhelm many +10–15c wins.

Another key vulnerability is correlated coins. 56 buys across seven coins and twenty 15-minute clock intervals are NOT 56 statistically independent market regimes.

The three fresh-block results are the closest current confirmation. The only remaining tentative best candidate for strictly further shadow-only research is YES55→65 with favorable recent coin momentum and spread ≤2c; do NOT arm funded trading on this evidence.

## Files

- raw_archive_provenance_audit.py / .json (140 archives)
- prepare_native200_grids.py / prepared_native200/ (140+21+84 separate source-day grids)
- systematic_native200_scan.py / systematic_native200_results.json / systematic_native200_traces.json
- stress_native200_candidates.py / systematic_native200_stress_results.json
- fresh21_untouched_validation_results.json
- validate_oct17_cross_date.py and prepared Oct17 grids; Oct17 evaluation incomplete as of this report

Funding: STAGED_NOT_ARMED, live_orders_enabled=false at last checked.
