# Correction: October 18 NO40, all vetted data reconciled

The previous chat comparison was misleading: the newly mined YES45 and YES50 strategies were compared against 76 EARLIER October 18 strict-QA markets. They are DIFFERENT rule families from NO40, and their losses do not contradict NO40's profits on those earlier SAME-DAY recordings. The subsequent NO40 losing block is a different nonoverlapping period. No funded orders or live changes.

## October 18 ONLY — original NO40→50 modeled results

| Eastern starts | Central starts | Raw coin-windows | Strict QA | Model profitable / buys | Net model |
|---|---|---:|---:|---:|---:|
| 13:45–19:15 | 12:45–18:15 | 161 | 56 | 27/30 | +$52.6912 |
| 19:30–20:15 | 18:30–19:15 | 28 | 20 | 5/5 | +$12.3761 |
| 20:30–21:00 | 19:30–20:00 | 21 | 3 | 1/1 | +$1.9717 |
| 21:15–21:45 | 20:15–20:45 | 21 | 17 | 7/10 | −$9.6829 |
| **Nonoverlapping October 18 total** | | **231** | **96** | **40/46** | **+$57.3561** |

Every accepted coin-window has a public Kalshi FINALIZED YES/NO outcome. Full per-market prices and statuses verified via frozen original `stress_native200_candidates.eval_one`, independent of the full scanner: results matched exactly on the latest 17 clean markets.

## Same-day strict-quality NO40 results by coin (all four non-overlapping blocks)

| Coin | Profitable/entries | Net modeled |
|---|---:|---:|
| ETH | 4/4 | +$13.0685 |
| HYPE | 10/10 | +$23.1547 |
| BNB | 3/5 | −$6.8062 |
| XRP | 4/4 | +$9.0540 |
| NEAR | 6/8 | −$4.1163 |
| ZEC | 8/8 | +$21.4332 |
| DOGE | 5/7 | +$1.5682 |

Coin-only filtering would be POST-HOC parameter fitting and requires fresh prospective validation; do not activate any subset automatically.

## Precisely why the later new period is negative

- BNB 20:15 Central start: modeled BUY NO, failed 50c exit, Kalshi finalized YES: **−$8.8853** modeled.
- BNB 20:30 Central: similarly Kalshi finalized YES: **−$9.3835**.
- DOGE 20:30 Central: similarly Kalshi finalized YES: **−$9.1396**.
- Those three lost **−$27.4084**, exceeding the seven modeled target-exit gains of **+$17.7255**, for −$9.6829. All three Kalshi official finalized YES outcomes independently rechecked via new public GET requests.
- Original NO40 rule still means NO signal ask 33–40c, underlying index UP ≥1bp over 10 seconds, spread ≤2c, first T+40–180s, modeled limit BUY ≤40c and sell at executable NO bid ≥50c, otherwise preclose or settlement. These are model opportunities, not actual signed fills.
- The same later block under 4s latency +0.5c adverse per-leg slippage lost −$19.5439 modeled. No software discrepancy found in original versus replay evaluator.

## Evidence

`DISCOVERY_RUNS/2026-10-18_2115_2145/NO40_OCT18_NONOVERLAP_FROZEN_REPLAY_AUDIT.json`
`DISCOVERY_RUNS/2026-10-18_2115_2145/no40_oct18_nonoverlap_audit.py`
`DISCOVERY_RUNS/2026-10-18_2115_2145/FROZEN_NEXT_WINDOW_RETROSPECTIVE_CHALLENGE.json`
`replay_verify_readonly.py`

**CAUTIONS**: 46 modeled entries at only 16 distinct market-opening times; correlated coins and 24,570-rule search mean overfitting risk. NO40 was selected using earlier results. Historical L2 simulations are not actual fill executions. Strict vetting screens the input quality, not the reliability of a selected edge. No live trading-system code was changed.
