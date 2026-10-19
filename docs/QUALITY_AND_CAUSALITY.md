# Original data-quality and causality contract

**Data-quality acceptance precedes strategy ranking.** Do not discard a loss because the rule lost, selectively admit winning markets, or lower coverage criteria to increase modeled profit.

## Strict window acceptance used by the closed-market runner

A requested coin-window is accepted only when:

1. Exactly one corresponding raw archive and one previous-window seed archive are present and readable gzip/JSONL.
2. The current ticker's floor strike is received no later than T+40 seconds and is not contradictory across repeated metadata.
3. The reconstructed two-sided YES/NO book plus fresh benchmark has a causal valid quote by T+50 seconds.
4. At least **80% of all 4,500 200ms rows** over a 15-minute market are valid, fresh reconstructed observations.
5. The market book has a usable current/seed snapshot and subsequent deltas, rather than constructing a fictitious top of book.
6. Book last-update age is **<=1,800 ms**; underlying benchmark last-observed age is **<=1,500 ms**.
7. No clock backstep exceeds 250 ms, receive-time gap exceeds 5 seconds, or disconnection/sequence/error markers invalidate its integrity.
8. The exact market receives a **public, finalized YES/NO result** before being admitted into scored outcomes.

Book prices are from actual YES and NO displayed bids. The complementary asks are:

~~~text
YES_ask = 1 - NO_best_bid
NO_ask  = 1 - YES_best_bid
~~~

A snapshot with impossible prices, absent both-side depth, missing reference price, unknown strike or stale inputs contributes **invalid rows**, never invented quotes. A complete gzip file is not necessarily a complete *usable* market.

## How original recordings differ from full coverage

The October 18 original initial search inspected 140 complete raw coin-window archives, but only 76 would meet the study's >=80% coverage criterion. Some original first-stage aggregate scores were computed over a broader raw sample; later strict-accepted reports explicitly screen **before** ranking. This is not a newly invented screen. Label source populations separately.

In several windows, the earliest observed floor strike was around T+30s. T+0–30s was **not directly tested**, regardless of the theoretical 200ms grid. In some periods 0% of the last three minutes had adequate executable observations despite a file receiving plenty of events. Event volume does not equal valid quote coverage.

## Causal time rules

- Signal features use only prior and current **received** events (no settlement, next-tick or unseen future data).
- For 200ms row t: ten-second momentum uses row t-50; 30-second uses t-150; a five-second quote change uses t-25.
- The original first entry signal is restricted to **T+40 through T+180s**; 90-second filters narrow that window.
- The model applies execution lag, does not use later bid to claim an earlier fill.
- If a book is invalidated after disconnect, it cannot be declared valid until an appropriate new snapshot.
- Do not select candidates based on their later test outcome and then call that same test unseen.

## Auditing every run

The runner writes an immutable per-run folder containing:

- quality_report.json: all attempted markets, archive hashes, metadata timing, quote coverage, rejection flags and official result;
- grids/: reconstructed arrays (local, gitignored);
- scenarios_by_market.jsonl: evaluated rule-trades tied to specific accepted markets;
- research_summary.json: fixed-rule aggregates, exploratory rankings, chronological splits and warnings.

Always publish denominators: **raw / accepted / finalized / modeled entries / positive entries / losses**. Cross-coin outcomes sharing the same quarter-hour are correlated; 70 coin trades are not 70 independent market regimes.
