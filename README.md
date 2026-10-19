# Kalshi Intraday Edge Research

**A reproducible, research-only framework for identifying short-lived intraday patterns in Kalshi's 15-minute cryptocurrency prediction markets.**

**This is not an official Kalshi product, an automated trading bot, or a claim of profitable live execution.** It does not place orders, handle funded accounts, or use a paper-trading leaderboard to discover its rules.

## What it actually does

The research reconstructs real historical Kalshi YES/NO order books from timestamped WebSocket snapshots and deltas, aligns them to contemporaneous CF Benchmarks cryptocurrency reference prices and market strikes, applies a strict data-quality gate, and evaluates a predeclared, finite family of hypothetical entry/exit conditions. Its original rule grammar contains **24,570 combinations**: two sides, 13 buy limits, three profit targets, 15 coin-motion filters, seven book filters, and three entry-time filters.

The practical objective is **intraday regime discovery**: search a recent block of completed markets for a temporary advantage, freeze candidate rules, then determine whether they continue to work in the *next* completed windows of the same day. A rule is not required to have worked on every previous day. Nor does today's retrospective profit prove it could have been selected before that profit occurred.

The engine can evaluate YES55→65, NO40→50, YES60→75 and many other candidates directly from observed markets. It **does not** infer those opportunities from the existing Hunter virtual-account farm.

## Research pipeline

~~~text
Recorded market-data WebSocket envelopes  +  contemporaneous benchmark/strike data
                         |
       prior-window snapshot + ordered delta replay
                         |
       causal 200 ms YES/NO book / benchmark grids
                         |
      per-market raw integrity and strict 80% quote-quality screen
                         |
        public Kalshi finalized YES/NO market outcome lookup
                         |
          ORIGINAL 24,570-combination systematic search
                         |
      modeled depth-aware entry, exit, fees, delays and losses
                         |
      chronological discovery --> rule freeze --> next-window challenge
                         |
               exploratory report + risks + source hashes
~~~

## Contents

| Location | Purpose |
| --- | --- |
| [engine/](engine/) | Preserved original book reconstruction, finite grid, fee/exit and delay-stress evaluation logic (portable path adjustments only) |
| [tools/discover_new_closed_windows.py](tools/discover_new_closed_windows.py) | Read-only batch runner on completed market windows, with official final outcomes and QA before selection |
| [docs/DATA_COLLECTION.md](docs/DATA_COLLECTION.md) | Required raw source events, exact envelope shape and missing-data handling |
| [docs/QUALITY_AND_CAUSALITY.md](docs/QUALITY_AND_CAUSALITY.md) | Precise eligibility gates, timing, freshness, and provenance |
| [docs/SEARCH_AND_EXECUTION.md](docs/SEARCH_AND_EXECUTION.md) | Original search grammar, buy/sell simulation and non-guarantees |
| [docs/INTRADAY_DISCOVERY.md](docs/INTRADAY_DISCOVERY.md) | How to discover an advantage *for this day* without post-selection claims |
| [docs/REPRODUCTION.md](docs/REPRODUCTION.md) | Setup, commands, output interpretation and tests |
| [docs/INTERPRETING_RESULTS.md](docs/INTERPRETING_RESULTS.md) | Historical examples and the distinctions among research, paper and funded trade evidence |
| [docs/FAQ.md](docs/FAQ.md) | Answers to common questions |
| [research/examples/](research/examples/) | Contemporaneous October 18–19 research summaries; evidence, not an independent certification |
| [tests/](tests/) | Deterministic unit tests, including no-lookahead and trade-fee accounting checks |

## Quick start (Python 3.10+)

~~~bash
git clone https://github.com/DaveMuselman/kalshi-intraday-edge-research.git
cd kalshi-intraday-edge-research
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
~~~

To run real research, **you supply your own legal, timestamped recordings** in the documented per-coin directory structure. No real market archives or credentials are bundled.

~~~bash
export KALSHI_ARCHIVE_ROOT="$PWD/data"
python -B tools/discover_new_closed_windows.py --date 2026-10-19 --start 0915 --end 1000
~~~

The date and clocks above demonstrate the command interface; use actual completed Eastern-time market openings with complete raw source recordings and verified final outcomes. The runner rejects unclosed windows, refuses to overwrite previous runs, and writes a uniquely named audit folder under the gitignored DISCOVERY_RUNS directory. Its completed-market result verification requires access to Kalshi's public HTTPS market endpoint.

## Important limits

- **No orders.** No account authentication, wallet, funding, or live broker state in this repository.
- **No market recorder included.** This package starts from recorded data; see [required inputs](docs/DATA_COLLECTION.md). The archive envelope is a research-specific adapter format, not the raw API schema.
- **No guaranteed fills.** Quotes and displayed depth make trades *modelable*, not executed. Delay, queue priority, partial fills, adverse selection and cancellation behavior are not known.
- **No risk-free inference.** A 24,570-way search on the same data can overfit. Several attractive candidates failed later or other-day blocks.
- **Official settlement is not a fill.** The read-only public-market lookup determines final YES/NO payout direction only.
- **Incomplete openings.** Original strike metadata often arrived around T+30s; the first 30 seconds were not evaluated in the original study.
- **Paper-farm and funded executor separate.** Past virtual-account rankings are not input to this rule discovery.

## October 19 example: why intraday evidence needs chronology

In the owner's October 19 Central-time research through the 9:00 AM market opening, 259 coin-windows were recorded, 167 passed strict QA and 167 finalized outcomes were verified. YES40→55 showed 73 positive results out of 91 modeled entries, but an October 18 clean archival challenge was net negative. That does *not* mean today's regime cannot differ; it means the rule is a **today-selected exploratory candidate** that still requires *future within-day* evaluation after freezing. Read [the dated summary](research/examples/today_20261019_cumulative.md).

## Participation, help and licensing

Open a GitHub Issue using the [question template](.github/ISSUE_TEMPLATE/question.md) to ask about data format, methodology, reproducibility or unexpected results. Do **not** post private keys, account data, raw proprietary feeds or personal information. See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and [LICENSE](LICENSE).

Independent open research. Not affiliated with, endorsed by or sponsored by Kalshi or CF Benchmarks. No financial advice, no assurances of live profitability.
