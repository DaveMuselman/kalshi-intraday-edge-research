# Reproduce a closed-market experiment

## System requirements

Python 3.10+, numpy and requests, sufficient local storage/RAM for compressed archives and per-window 4,500-row arrays. macOS/Linux are the primary tested research environments. A Python virtual environment is recommended. Internet access is needed for the public finalized-outcome lookup; recording is performed separately.

~~~bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
~~~

No auth token is read by the research runner. Do not place your Kalshi signing key in this repository.

## Inputs

Place archives under data/COIN/live_stream/ with filenames and exact JSONL envelope described in [DATA_COLLECTION.md](DATA_COLLECTION.md), including the preceding 15-minute window's file for each researched coin.

~~~bash
export KALSHI_ARCHIVE_ROOT="$PWD/data"
ls "$KALSHI_ARCHIVE_ROOT/ETH/live_stream/"
~~~

The current runner evaluates **all seven** configured coins; missing archives are reported and rejected individually. For meaningful comparisons, publish the predeclared coin roster and all excluded windows.

## Single historical run

Example using four completely closed market openings, in **Eastern** clock time:

~~~bash
python -B tools/discover_new_closed_windows.py \
  --date 2026-10-19 --start 0915 --end 1000
~~~

The last selected opening must already have completed its 15-minute duration. The script prevents overwriting an existing date/start/end run. If you need a different experiment, use a different non-overlapping batch selection; do not delete adverse results to rerun a cherry-picked sample.

Outputs live under:

~~~text
DISCOVERY_RUNS/2026-10-19_0915_1000/
  quality_report.json
  grids/
  scenarios_by_market.jsonl
  research_summary.json
~~~

Everything under DISCOVERY_RUNS/ is ignored by Git. The runner checks official finalized results for quality-passing tickers, and runs the unchanged engine against verified markets only. If outcomes are not final or endpoint access fails, those markets are **not** scored.

## Read the output

quality_report.json tells you exactly why each market was accepted or rejected. research_summary.json includes theoretical combinations, actual rules with at least one candidate buy, four original fixed benchmarks, per-coin results, stress results and exploratory training/test/holdout rankings.

The run's frozen baselines are identified by full rule IDs. Positive model P&L is the sum of separate one-window hypothetical strategy outcomes, **not** one feasible multi-market account P&L. The report does not make a prospective deployment claim.

## Repeating today's work without cheating

Run consecutive **completed** blocks and write down which earlier block was used for selection. Only look at the subsequent batch's outcome after the candidate is frozen. Cross-day evidence can inform downside risk, not invalidate an otherwise genuine intraday effect. See [INTRADAY_DISCOVERY.md](INTRADAY_DISCOVERY.md).

## Source fidelity and known constraints

The October 2026 public code preserves an older research naming convention. For example PROXY_SETTLEMENT can appear in an outcome status, but the included *runner* installs an oracle backed by officially finalized Kalshi market results. A direct standalone execution of engine/systematic_native200_scan.py has a different historical setup and is **not** the recommended public workflow.

The original preparer was explicitly adapted by the runner to handle arbitrary October 2026 days through two runtime substitutions. Other year/month values use the same verified version-guarded runtime transformation. If those source signatures drift, it fails rather than guess. The public preparer uses configurable data roots instead of the original owner's machine layout.

For exact historical numerical reproduction, you need **the same contemporaneous recorded feeds and official outcomes**; code alone cannot recreate unpublished raw market events.
