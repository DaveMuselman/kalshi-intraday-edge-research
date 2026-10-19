# Exact finite search and what the P&L means

The public engine is a portable copy of the October 18 original read-only research code. It intentionally preserves the historical strategy grammar, signal masks and modeled accounting rather than retrospectively improving them.

## 24,570 rule combinations

~~~text
2 sides × 13 maximum entry limits (20, 25, ..., 80 cents)
        × 3 sale increments (+5, +10, +15 cents)
        × 15 underlying-price trajectory filters
        × 7 contract-book filters
        × 3 opening-entry timing filters
      = 24,570 theoretical combinations.
~~~

Motion filters include: ANY; spot favored/unfavored relative to strike; within ±5 or ±12 basis points of strike; farther than 12 bp; 10/30-second aligned, opposing, quiet or strong movement; persistent alignment and recovery; and favored/aligned combinations. Book filters include no additional filter, five-second contract-bid drops of 3/6c, rises of 3c, small changes, book move with quiet spot, or YES/NO side spread <=2c. Time filters: first 90 seconds, second 90 seconds or first 180 seconds; the base signal window still starts at 40 seconds.

Example immutable ID:

~~~text
YES_55_10_MOVE10_ALIGNED_SPREAD_LE2C_FIRST_180S
~~~

Meaning: YES ask at 48–55c, YES spread <=2c, underlying increased >=1 bp in prior ten seconds, earliest eligible signal T+40–180; buy with a 55c limit and sell at a full-order executable YES bid >=65c. For NO_40_10_MOVE10_OPPOSED..., an underlying price **rise** >=1 bp favors the *opposite* of a NO purchase. This counterintuitive condition is present in the original research.

## Modeled $8–$10 one-buy-per-market structure

- For each entry-limit price, quantity is a fixed whole-share number designed around a $10 limit-inclusive fee budget (e.g. 17 shares at 55c and 23 at 40c). Minimum modeled spend $8.
- A signal can occur when the displayed ask is within seven cents below the rule limit.
- A **2-second delay** is modeled from signal to first eligible full-quantity book purchase, with the order modeled as a limit that can execute before T+180s.
- Buy price comes from sweeping sufficient displayed opposing-side bids (through complement pricing), with a max 2c adverse depth walk. A one-contract top quote alone is insufficient.
- One modeled buy maximum per strategy/coin/15-minute market; each candidate evaluated separately. Simultaneous candidate outcomes must **not** be summed as an executable portfolio.
- Profit exit requires sufficient **whole-order** displayed same-side bid depth >= the goal; a target signal must still be executable after the modeled delay.
- If no target exit, look for recorded executable depth in final ten seconds; otherwise use finalized YES/NO payout as the modeled settlement result.
- Modeled fee uses ceil(0.07 × price × (1 − price) × contracts × 10,000) / 10,000 for the original historical research. It is a **research assumption**, not a promise that any current user's exchange fee tier is identical.

Full formulas live in engine/systematic_native200_scan.py and the alternate delay/slippage evaluator in engine/stress_native200_candidates.py.

## Stress evaluation and failure modes

For frozen candidates, replay alternative delays (2, 4, 8 seconds) and adverse slip (0.5c/leg or 1c/leg when explicitly tested). Longer delay may change which markets receive modeled buys; do not compare headline net alone without counts. Full-spend losses (~$8–$10 for a failed entry) can overwhelm many +10c exits. Some apparent positive results reverse under worse assumptions.

**Displayed depth is NOT authenticated fill evidence.** The model does not simulate queue position, actual order acknowledgment, rejected orders, partial fills, maker competition, unavailable API, cancellations, simultaneous account cash usage, inventory limits or a funded kill switch. It is not a live execution specification.

## Separate research from everything else

The Hunter 22-cohort paper farm selected virtual winners from prior 15-minute windows; it **did not discover** these 24,570 rules. STAR_SEARCH explored a distinct family of causal feature hypotheses; it is likewise a separate experiment, not this exact grid. Do not mix paper account results with native market replay or claim account profit from hypothetical P&L.
