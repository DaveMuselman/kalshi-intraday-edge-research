# What the original research found — and what it did not

These are historical modeled data, not independently audited realized profits. All examples are drawn from surviving dated local research summaries, and none establishes a live win probability.

## Original October 18 discovery

Original family: 24,570 theoretical configurations; 3,126 produced at least one modeled purchase in the initial broad scan. The initial 140 October 18 raw coin-windows were divided into TRAIN 08:00–09:45 Eastern, TEST 10:00–10:45 and VALIDATION 11:00–12:45. 76/140 windows met the existing >=80% quote-freshness condition, which was **already specified** then; the initial broad scoring was not restricted identically to subsequent strict quality-accepted scans.

The chosen YES55→65 frozen rule had 55 positive outcomes out of 62 modeled entries and +$57.84 over the initial three groups. On the next previously untouched 21 coin-windows it showed 4/4 and +$7.04. That small fresh block made it more interesting than other originally promising candidates which lost in that block. It did **not** make it lossless.

Later independent recordings detected genuine *model* failures of the frozen YES55 entry condition, including a roughly $9 loss on a subsequently finalized NO market. The original strict-quality search discovered NO40, NO35 and YES60 as additional families. These are not paper leaderboard winners.

## October 19 intraday research

A full original-grid compilation for Central-time October 19 midnight through the market opening at 09:00 used 259 recorded coin-windows; 167 accepted by strict QA and 167 officially finalized, with 3,159 of 24,570 configurations ever producing an eligible model entry. (The 10:00 Eastern opening is 09:00 Central; the table excludes Eastern 00:00–00:45 because they belong to the preceding Central calendar day.)

| Existing frozen rule | Positive / modeled buys | Modeled net USD |
| --- | ---: | ---: |
| YES55→65 | 73/88 | +19.4681 |
| NO40→50 | 60/71 | +58.3127 |
| NO35→50 | 37/50 | +42.4119 |
| YES60→75 | 65/81 | +48.8326 |

Two newly noticed families were YES40→55, 73/91 and +$132.19, and YES35→50, 56/72 and +$117.73. However, re-evaluating them against earlier 76 strict-quality October 18 windows produced roughly -$14.89 and -$17.48 under base modeled delay. This is **historical adverse-case evidence**, not proof that today's market advantage was absent. Neither today's data-mined candidate had an independent uninspected next-window confirmation at the time of this note.

## Three evidence systems that MUST stay separate

1. **Native orderbook/benchmark discovery**: actual recorded quotes, quality flags, 24,570 grid rules, hypothetical fills, later finalized market payouts.
2. **Hunter virtual-paper farm**: its own approximately 22-cohort eligible groups and thousands of preexisting simulated strategy accounts, with previous-window winner selection. Those outputs do **not** supply the native grid's rule discoveries.
3. **Funded Kalshi execution**: signed order acknowledgments, confirmed partial/full fills, cash movements, exposure, cancellation/settlement reconciliation. None is part of this public research engine.

Also separate the later STAR_SEARCH causal-pattern research from the original 24,570-rule grammar; different features imply different hypothesis selection and validation.

## Common reporting errors

- Calling profitable simulation rows 'actual trades'.
- Treating official finalized YES/NO payout as a verified buy or sell fill.
- Implying a rule was always quality-screened when its original discovery used a broader raw population.
- Adding mutually exclusive paper portfolios together or summing overlapping candidate trades as an executable portfolio.
- Picking the day's top rule *after* seeing its gains and calling it available earlier.
- Demanding a transient today's pattern must also profit yesterday.
- Ignoring multiple testing, sparse independent 15-minute openings, stale quotes and loss tails.

The code and audit trail are made public so these distinctions can be inspected and challenged.
