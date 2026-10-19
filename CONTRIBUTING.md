# Contributing and getting help

This project accepts reproducibility questions, documentation improvements, confirmed replay bugs and separately proposed research extensions. The frozen October 18 original finite-grid semantics are an important baseline. **Do not silently alter them** when adding a new research experiment.

## Issue reporting

Use the question or bug-report issue template. Include Python version, platform, command, date/clock timezone, the full acceptance/rejection reason, sanitized file-name patterns, sample counts, the frozen strategy ID, and whether the issue concerns the original replay or your own modified experiment.

Before filing, review docs/DATA_COLLECTION.md, docs/QUALITY_AND_CAUSALITY.md, docs/REPRODUCTION.md and docs/FAQ.md. Screenshots of profitable results without the losing and rejected populations cannot reproduce a claim.

## Proposed research contributions

- Open a separate named engine variant with explicit input schema, fee/latency change and source code.
- Add deterministic tests and demonstrate non-lookahead behavior.
- Include every market denominator, failed test and changed threshold.
- Explicitly describe whether discovery used train, test, holdout or genuinely future untouched recordings.
- Preserve source filenames/commit ID, hashes and operating system dependencies.

Do not publish user secrets, account records, raw unpublished recordings or full live trading code. Please do not ask maintainers to approve particular funded trades on the basis of these retrospective model returns.

## Maintainer responsiveness

Issues and pull requests may be reviewed and answered as maintainers are available; no continuous response service is guaranteed. Do not rely on an immediate reply for urgent account or market decisions. See SECURITY.md for the secure reporting boundary.
