# Questions and answers

**What is the purpose of this project?** Finding short-lived order-book/underlying-price relationships in 15-minute Kalshi cryptocurrency markets by searching *recorded market data*, not existing paper-account winners.

**Is YES55 'an algorithm' that won 55/62 real orders?** No. It is an exact frozen hypothetical strategy configuration from a 24,570-combination research grid. 55/62 was historical simulated result count under the initial source conditions, not signed exchange-confirmed fills.

**Do I need a Kalshi funded account?** No funded trading account is accessed by this code. For data recording, consult Kalshi's current market-data API access terms and the underlying reference feed's legal availability. Official payout verification uses a public read-only market endpoint.

**Why isn't market-data recording included?** The historical input already existed as proprietary research-specific receipt-time JSONL envelopes, across separate WebSocket and reference-price feeds. Blindly publishing a recorder tied to someone else's credentials or assumptions would give a misleading reproducibility claim. The required adapter format is fully documented; contributions can add optional independently testable read-only recorders.

**What is the 80% gate?** A market needs at least 80% of the 4,500 causal 200ms rows to have fresh reconstructable book and benchmark observations. This gate was already specified in the original research; later analyses applied stricter explicit per-market acceptance before scoring.

**Does 200ms mean a trade every 200ms?** No. It is the research grid's sampling resolution. The original entry signals are in a 40–180-second interval and modeled actions have multi-second latency.

**Why can a profitable rule be bad yesterday?** The point of intraday regime detection is to find time-localized opportunities. An earlier day's loss is valuable downside information, but a rule discovered on today's completed window needs a later same-day prospective challenge rather than universal cross-day profitability.

**How do you prevent overfitting?** You cannot eliminate it merely by running a very large grid. Predeclare grammar, retain all tested configurations, select on a bounded recent block, freeze the exact rule before new markets settle, then inspect strictly subsequent timestamps and stress delays/slippage.

**Can I turn this on for live orders?** No. No order creation, account permission, position reconciliation or funded-controller logic is present. Any separate real-money execution implementation would require substantial independent safety and reliability testing.

**Why might a window fail QA when the file is full of events?** Raw event rate does not guarantee current-market snapshots, strike, fresh both-sided executable depth or a fresh underlying price. The script reports exact rejection reasons.

**Where do I ask questions?** Open a GitHub Issue with steps to reproduce, sanitized dates/tickers and source-hash identifiers. Never include private keys or account data.
