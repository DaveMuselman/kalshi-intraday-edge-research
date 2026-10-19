# Audited local provenance (October 2026)

The bundled `engine/` files are copies of locally audited October 18 original
research scripts, adapted ONLY to make the directory root configurable and the
OrderBook import local. `tools/discover_new_closed_windows.py` is the October
18 read-only batch runner, changed only to resolve files within this new
repository. Fee model, scoring grammar, strategy decision masks, entry
time limits and default 2-second delay are the original code.

Original sources on the owner's machine (not included in the public repo):
- Kalshi_Independent_API_Lane_20261016/parity_overhaul_STAGED_20261017/research_book_reversion_20261018/systematic_native200_scan.py
- same directory: prepare_native200_grids.py, stress_native200_candidates.py
- AllCoin_FullRoster_20261016/ETH/book_tape.py
- Kalshi_Research_Recovery_20261018/discover_new_closed_windows.py

The source legacy names `ORACLES` and `PROXY_SETTLEMENT` are retained for
calculation parity; the public run driver **overrides the oracle with verified
official final Kalshi market results**, not a 60-second settlement estimate.
Quote-based buy and sell remain hypothetical, never official fills.

The source research descriptions included in `research/examples` are not
recomputed in a new environment and must not be treated as an independent
third-party certification.

Not included: account data; public/raw feed archives; API credentials; any
funded executor or order routing code; shadow/paper-account league; any
private business or personal files.
