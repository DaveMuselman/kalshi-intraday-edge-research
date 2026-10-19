# Discovering the advantage in today's regime

**An intraday advantage does not need to carry across calendar days.** The research goal is to find patterns in recently completed markets, then test whether those patterns remain predictive *after* they are discovered. Yesterday can be an adverse-case reference, not a mandatory same-day opportunity filter.

## Practical chronological protocol

1. **Record continuously** across the seven coins. Include preceding-window book snapshots, contemporaneous strikes, benchmark prices, event timestamps and reconnection markers.
2. **Stop at completed markets only.** Verify official settlements through read-only market GET. Do not incorporate partial/future outcome data as historical truth.
3. **Run the fixed original quality gate first.** Keep all rejected market identifiers and exclusion flags, not just winners.
4. **Discover on a recent block.** Apply the entire fixed 24,570-rule grammar to the QA-accepted window set; rank by **net modeled dollars and downside**, not win rate alone. Use explicit minimum distinct clock-time observations.
5. **Freeze the exact candidate key and assumptions.** Record an immutable research timestamp and the data-hash census used to select it; no threshold change afterward.
6. **Challenge on later, newly completed same-day openings**. Recompute entries from the new tapes using the frozen ID, and report net, losses, duration, coin breakdown, quote freshness and lag/slippage stress.
7. **Track rolling evidence.** A rule may improve, weaken or reverse as regime changes. Distinguish regime-specific observation from genuinely prospective evidence.
8. **Retire research confidence if the rolling challenge deteriorates.** This is a report-level judgment only. This repository does not automate funded arm/disarm or send orders.

## Keep the evidence labels straight

**In-sample**: the observed markets used to choose the rule. Optimistic because thousands were considered.

**Within-day subsequent window**: a later market period after rule selection was frozen. Closer to genuine intraday prospective verification if it was truly uninspected.

**Earlier-day challenge**: useful warning about failure modes, but not a logical disproof of today's transient opportunity.

**Historical holdout used while selecting among survivors**: once you choose the winning rules from its outcomes, that block is no longer an untouched confirmation.

**Signed exchange order fills**: absent. Do not label any historical model entry/exit as actual account profit.

## Suggested operator worksheet

~~~text
Date / timezone / coin universe:
Selected discovery window:
QA raw / admitted / finalized:
Number of rule combinations attempted:
Frozen rule ID and decision cutoff:
Distinct 15-minute clock opens in selection:
Modeled training trades / wins / P&L / worst loss:
Next uninspected same-day challenge market openings:
Next challenge modeled trades / wins / P&L / worst loss:
2s, 4s+0.5c, 8s+1c sensitivity with separate trade counts:
Book/spot freshness and risk flags:
Decision: EXPLORATORY / NEED MORE DATA / REJECTED
~~~

Do not retroactively move the selection cutoff, change the coin universe or silently discard an adverse quote. The original batch runner scans recent markets; it does **not** claim to be an autonomous causal-feature-invention AI, continuously scheduled monitor, or validated funded order executor.
