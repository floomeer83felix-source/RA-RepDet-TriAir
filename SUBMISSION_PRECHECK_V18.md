# Submission Precheck V18

## Status

NOT READY FOR FORMAL SIVP SUBMISSION.

## What Is Verified

- The clean blocked split is documented in `runs/clean_block64g16_protocol.md`.
- Main clean-split validation evidence is documented in `runs/phase4b_report.md`.
- Paper-readiness evidence is documented in `runs/phase5a_report.md`.
- The SIVP source skeleton uses Springer `sn-jnl` with two-column `[iicol]` formatting.
- R4 remains the clean-split main variant by Phase 4B decision.
- The manuscript keeps validation-only wording and does not introduce independent test claims.

## Blocking Missing Inputs

- Author names, affiliations, corresponding email, funding, competing interests, acknowledgments, and author contributions are not provided.
- TriAir source citation, version, licence, access terms, and redistribution permission are not provided.
- Public release URL, release tag, immutable commit hash, Zenodo DOI, and archive date are not provided.
- Final Fig. 1--6 publication assets are not present. In particular, final Visio-derived Fig. 1 and Fig. 2 are not present.
- Hardware/software version record for the final reported runs is incomplete.

## Preflight Interpretation

`python scripts/preflight_submission.py --root . --allow-placeholders` may be used as a draft readiness check.

`python scripts/preflight_submission.py --root .` must fail until the blocking inputs above are replaced with real author-provided or release-verified information.

## Command Results on 2026-06-30

```text
python scripts/preflight_submission.py --root . --allow-placeholders
RESULT: PASS
```

```text
python scripts/preflight_submission.py --root .
RESULT: FAIL
```

The final PDF build was not executed because the requested strict preflight did not return PASS.
