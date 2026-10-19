# Security boundary

This project is **research-only** and never submits orders. No keys, API IDs,
signed account calls, wallet addresses, PII, funded trade ledgers, broker
credentials, position state, customer files or private market recordings belong
in public commits. Private API keys may still be required for authenticated
WebSocket market-data collection. Only load them at runtime from environment
variables; never display or export key contents.

Do not copy the author's existing Hunter live executor or paper-farm processes
into this package. This package does not reconcile fills, cancellations, open
positions, trading permissions or account balances. It must not be described as
a deployable funded trading bot.

Do not publish the generated `data/` or `runs/` directories. Historical
examples here are high-level aggregate summaries, not proprietary feeds. The
MIT license only covers material owned by contributors; it does not relicense
Kalshi or CF Benchmarks data.
