# Data collection: what must be recorded

This is a **replay/discovery** repository, not a market-data capture service. To reproduce studies, acquire your own recordings through permitted Kalshi interfaces and an appropriate source of underlying benchmark observations. The original researcher used the Kalshi order-book WebSocket and CF Benchmarks reference-price events.

## Raw archive layout

Set the variable KALSHI_ARCHIVE_ROOT to a directory containing one folder per coin:

~~~text
data/
  ETH/live_stream/eth_20261019_0915_EDT_....jsonl.gz
  HYPE/live_stream/hype_20261019_0915_EDT_....jsonl.gz
  BNB/live_stream/bnb_20261019_0915_EDT_....jsonl.gz
  XRP/live_stream/xrp_20261019_0915_EDT_....jsonl.gz
  NEAR/live_stream/near_20261019_0915_EDT_....jsonl.gz
  ZEC/live_stream/zec_20261019_0915_EDT_....jsonl.gz
  DOGE/live_stream/doge_20261019_0915_EDT_....jsonl.gz
~~~

For **each** requested window, also supply the **previous 15-minute window** archive, exactly one file matching each timestamp/coin. In the original capture, a snapshot for the upcoming market may appear in the preceding archive. A current-window stream of deltas without the preceding snapshot cannot safely reconstruct a full book.

Archive names must follow:

~~~text
{coin_lower}_{YYYYMMDD}_{HHMM}_{EDT|EST}_{recorder_suffix}.jsonl.gz
~~~

The HHMM is the market's **opening** local time in America/New_York, not your computer's clock or the close time. The suffix is arbitrary, but exactly one file must match for each coin and opening.

## JSONL envelope expected by the original preparer

Each gzip file contains timestamped JSON objects, one per line. These examples illustrate shape only; they are NOT actual historical quotes.

~~~json
{"kind":"TARGET_METADATA","received_ms":1792415700080,"ticker":"KXETH15M-...","floor_strike":2400.0}
{"kind":"RECEIVED","received_ms":1792415700200,"payload":{"type":"orderbook_snapshot","msg":{"market_ticker":"KXETH15M-...","yes_dollars_fp":[["0.4500","100"]],"no_dollars_fp":[["0.5400","100"]]}}}
{"kind":"RECEIVED","received_ms":1792415700400,"payload":{"type":"orderbook_delta","msg":{"market_ticker":"KXETH15M-...","side":"yes","price_dollars":"0.4500","delta_fp":"2"}}}
{"kind":"RECEIVED","received_ms":1792415700500,"payload":{"type":"cfbenchmarks_value_5hz","msg":{"index_id":"ETHUSD_RTI","value_usd":"2400.80"}}}
~~~

The market ticker in actual data **must exactly equal the contract ticker constructed from its 15-minute close** (see engine/prepare_native200_grids.py). Do not literally reuse the placeholder ticker above. Observed timestamps must reflect **local receipt time in milliseconds since Unix epoch** and be ordered enough to pass continuity checks. No rule may use a quote or benchmark event before it was received.

A valid stream also preserves session/error events and should explicitly record:

- CONNECTED, SOCKET_CONNECT_ATTEMPT, DISCONNECT_OR_FAILURE, STREAM_ERROR, SEQUENCE_GAP as appropriate.
- Current-market TARGET_METADATA with its actual floor_strike and observed timestamp.
- Both-sided orderbook snapshots and every subsequent delta in causal receive order.
- The associated coin's reference index data, with its own receipt timestamps.
- Lossless archive rotations, timestamp integrity and finalization information obtained separately by read-only GET.

The original data included high-rate underlying observations for ETH/XRP/DOGE (around 200 ms) and slower observations for HYPE/BNB/NEAR/ZEC (around 1 second). The research **samples all reconstructed books at 200 ms**, but that does **not** make all underlying reference values native 5 Hz.

## Market details and official outcome

Each YES/NO 15-minute market requires contemporaneous current-market strike and ticker, not strike information learned after the signal. After its close/finalization, the researcher looks up that exact ticker using Kalshi's public market endpoint and requires a finalized YES or NO result. That official payout direction is an outcome label, not confirmation that the hypothetical earlier orders filled.

Reference: [Kalshi API documentation](https://docs.kalshi.com/) and [WebSockets](https://docs.kalshi.com/websockets). Check the current provider rules and availability before implementing a recorder.

## What is intentionally not included

No private recordings, API token, credential, order-routing engine, account balance, wallet state or authenticated user trade ledger is part of this repository. If a third-party feed cannot supply equivalent timestamped CF benchmark values, the original research cannot be reproduced unchanged. Do not silently substitute another price index: record and disclose an explicit methodological variation instead.
