# RA-RepDet-TriAir Handoff

Generated: 2026-07-09

## Current Task State

- Task file: `docs/NEXT_TASK.md`
- Current task: V41 SIVP manuscript alignment with three-seed validation-only evidence
- Status: `HANDOFF_TO_CODEX`
- Active blocker: `NO_ACTIVE_BLOCKER`

## What Assistant Completed

Prepared a safe SIVP manuscript-alignment package from existing evidence only. No training, evaluation, guard/test access, checkpoint loading, raw data access, prediction-cache access, or direct LaTeX manuscript rewriting was performed in this assistant step.

Files prepared:

- `submission/sivp/tables/Table_8_three_seed_interim_devval.tex`
- `submission/sivp/review/V41_SIVP_CLAIM_LEDGER.md`
- `submission/sivp/review/V41_SIVP_REPLACEMENT_TEXT.md`
- `submission/sivp/review/V41_SIVP_MANUSCRIPT_ALIGNMENT_PLAN.md`
- `docs/NEXT_TASK.md`
- updated `docs/EXPERIMENT_STATUS.md`

## Codex Next Task

Codex should execute `docs/NEXT_TASK.md`.

Primary target:

- `submission/sivp/tex/ra_repdet_sivp.tex`

Required local work:

1. Replace the active R4 p=0.20 / seed0,2 / block64_guard16 narrative with reliability-aware p=0.15 seed0/1/2 V40 component-disjoint development-validation wording.
2. Insert `Table_8_three_seed_interim_devval.tex` or equivalent values into the active main results table.
3. Apply validation-only claim boundary throughout abstract, contributions, results, discussion, limitations, and conclusion.
4. Run manuscript claim scans and preflight.
5. Compile if local LaTeX is available.
6. Update status and handoff.

## Three-Seed Interim Development-Validation Summary

Reliability p=0.15 minus matched early, paired by seed:

| Metric | Mean delta | Sample SD | n seed pairs |
| --- | ---: | ---: | ---: |
| Precision | +0.011629 | 0.016501 | 3 |
| Recall | +0.024487 | 0.026581 | 3 |
| F1 | +0.018524 | 0.006208 | 3 |
| AP50 | +0.016064 | 0.005699 | 3 |
| AP75 | +0.064657 | 0.016415 | 3 |

## Claim Boundary

Allowed wording: three-seed interim development-validation descriptive evidence on the frozen V40 component-disjoint development-validation split.

Disallowed wording: independent test, external generalization, statistical significance, manuscript-final aggregate, optimal dropout, calibrated sensor reliability, or physical sensor-failure robustness.

## What Assistant Could Not Complete Safely

- Full LaTeX source rewrite, because the local source must be edited and compiled together with the SIVP template and table wiring.
- Springer/SIVP LaTeX compilation.
- Final figure/artwork verification.
- Author metadata, declarations, funding, conflicts, contributions, acknowledgments, or data/code availability finalization.
- TriAir provider URL, version, license, redistribution rights, synchronization details, or official event representation verification.
- New experiments, independent test creation, COCO AP50:95, causal ablations, or label-quality review.
