# V41 Interim Development-Validation Status

Generated: 2026-07-09

## Status

`V41_INTERIM_DEVVAL_CONSOLIDATION_COMPLETE`

## Scope

This document consolidates existing lightweight evidence only:

- V40 seed0/seed2 matched early and reliability p=0.15 rows from `runs/v40_expanded_adjacency_v2_compute_minimized/v40_four_run_summary.json`.
- V41 fresh seed1 matched early and reliability p=0.15 rows from `runs/v41_q1_upgrade/seed1/seed1_per_run_summary.csv`.

No training, evaluation, checkpoint loading, raw data access, prediction-cache access, guard/test access, or manuscript rewriting was performed by this consolidation task.

## Three-seed interim development-validation descriptive summary

| Metric | Mean paired delta, reliability p=0.15 - early | Sample SD | n seed pairs |
| --- | ---: | ---: | ---: |
| Precision | +0.011629 | 0.016501 | 3 |
| Recall | +0.024487 | 0.026581 | 3 |
| F1 | +0.018524 | 0.006208 | 3 |
| AP50 | +0.016064 | 0.005699 | 3 |
| AP75 | +0.064657 | 0.016415 | 3 |

## Evidence package

- CSV: `runs/v41_q1_upgrade/interim_devval/three_seed_interim_devval_summary.csv`
- Markdown: `runs/v41_q1_upgrade/interim_devval/three_seed_interim_devval_summary.md`
- JSON: `runs/v41_q1_upgrade/interim_devval/three_seed_interim_devval_summary.json`
- Claim boundary: `runs/v41_q1_upgrade/interim_devval/interim_claim_boundary.md`
- Consolidation tool: `rarepdet/tools/v41_interim_devval_consolidate.py`

## Current claim boundary

Allowed: three-seed interim development-validation descriptive evidence on the frozen V40 component-disjoint development-validation split.

Not allowed: independent-test performance, external generalization, statistical significance, final manuscript aggregate, optimal dropout, calibrated sensor-health interpretation, or physical sensor-fault robustness.

## Remaining limitations

- Validation-only evidence.
- Three seed pairs only; seed3/seed4 are not planned in the current work line.
- No independent test.
- No causal mechanism ablations separating stems, dynamic gate, and modality dropout.
- No COCO mAP@[0.50:0.95] package.
- Dataset provider provenance remains unresolved.
- Label-quality review remains incomplete.
