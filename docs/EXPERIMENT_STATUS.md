# Experiment Status

Generated: 2026-07-09

## Current Status

`V41_INTERIM_DEVVAL_CONSOLIDATION_COMPLETE`

Current active evidence package: `runs/v41_q1_upgrade/interim_devval/`.

This repository state consolidates V40 seed0/seed2 and V41 fresh seed1 evidence into a three-seed interim development-validation descriptive summary. No new training, evaluation, guard/test access, checkpoint loading, raw data access, prediction-cache access, or manuscript rewriting was performed by the consolidation task.

## Inputs

- V40 seed0/seed2 source: `runs/v40_expanded_adjacency_v2_compute_minimized/v40_four_run_summary.json`.
- V41 fresh seed1 source: `runs/v41_q1_upgrade/seed1/seed1_per_run_summary.csv`.
- V41 seed1 source lock: `runs/v41_q1_upgrade/seed1/source_lock_seed1.md/json`.
- V41 seed1 completion commit: `5d839ae900849919189edff4bdd364f42c043b86`.

## Three-seed interim development-validation descriptive summary

Reliability p=0.15 minus matched early, paired by seed:

| Metric | Mean delta | Sample SD | n seed pairs |
| --- | ---: | ---: | ---: |
| Precision | +0.011629 | 0.016501 | 3 |
| Recall | +0.024487 | 0.026581 | 3 |
| F1 | +0.018524 | 0.006208 | 3 |
| AP50 | +0.016064 | 0.005699 | 3 |
| AP75 | +0.064657 | 0.016415 | 3 |

Per-seed paired deltas:

| Seed | Precision | Recall | F1 | AP50 | AP75 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0 | +0.024180 | +0.001704 | +0.012637 | +0.012812 | +0.054121 |
| 1 | +0.017770 | +0.018067 | +0.017925 | +0.012734 | +0.083570 |
| 2 | -0.007062 | +0.053690 | +0.025010 | +0.022645 | +0.056280 |

## Evidence files

- `runs/v41_q1_upgrade/interim_devval/three_seed_interim_devval_summary.csv`
- `runs/v41_q1_upgrade/interim_devval/three_seed_interim_devval_summary.md`
- `runs/v41_q1_upgrade/interim_devval/three_seed_interim_devval_summary.json`
- `runs/v41_q1_upgrade/interim_devval/interim_claim_boundary.md`
- `docs/V41_INTERIM_DEVVAL_STATUS.md`
- `rarepdet/tools/v41_interim_devval_consolidate.py`

## Task blocker state

`docs/TASK_BLOCKER.md` now records `NO_ACTIVE_BLOCKER`. The older V40 GPU-deferred blocker is historical and no longer represents the active task state.

## Current claim boundary

Allowed wording: three-seed interim development-validation descriptive evidence on the frozen V40 component-disjoint development-validation split.

Disallowed wording: independent test, external generalization, statistical significance, manuscript-final aggregate, optimal dropout, calibrated sensor reliability, or physical sensor-fault robustness.

## Remaining limitations

- Validation-only evidence.
- Three seed pairs only; seed3/seed4 are not planned in the current line.
- No independent test.
- No causal ablations separating stems, dynamic gate, and dropout.
- No COCO mAP@[0.50:0.95] package.
- Dataset provider provenance remains unresolved.
- Label-quality review remains incomplete.
