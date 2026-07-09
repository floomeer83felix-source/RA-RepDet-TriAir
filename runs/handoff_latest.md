# RA-RepDet-TriAir Handoff

Generated: 2026-07-09

## Current Task State

- Task file: `docs/NEXT_TASK.md`
- User-explicit task: V43 SIVP integration of V42 locked held-out guard evidence
- Status: `V43_SIVP_HELDOUT_GUARD_INTEGRATION_COMPLETE`
- Active blocker: `NO_ACTIVE_BLOCKER`

## What Assistant Completed

Integrated the completed V42 locked held-out guard evaluation into the active SIVP manuscript. No new training, tuning, checkpoint selection, split modification, robustness, profiling, external-data work, or additional evaluation was performed.

## Manuscript Files Updated

- `submission/sivp/tex/ra_repdet_sivp.tex`
- `submission/sivp/tex/main.tex`
- `main.tex`
- `main_sivp_snjnl.tex`
- `submission/sivp/tables/Table_1_dataset_and_clean_split.tex`
- `submission/sivp/tables/Table_2_implementation_and_reproducibility.tex`
- `submission/sivp/tables/Table_9_locked_heldout_guard.tex`
- `submission/sivp/review/REVIEWER_REPORT_PRE_SUBMISSION.md`
- `docs/EXPERIMENT_STATUS.md`
- `runs/handoff_latest.md/json`

## Evidence State After V43

The paper is no longer described as validation-only. The active evidence is:

1. Three-seed component-disjoint development-validation evidence.
2. Locked same-dataset TriAir held-out guard evaluation using six fixed checkpoints.

## V42 Guard Source Lock

- Source manifest: `runs/component_disjoint_v40/guard.txt`
- Rows: 837 images
- GT boxes: 1264
- Normalized LF SHA256: `9f871c16aa60b517ffd8df530782eed1befcd652969a9f94e5cd6af5ac2c8c2e`
- Raw file SHA256: `0cf3270c0a73d03caf8d698bb4e9ddb0adba46e688c52d8589f57ea12488881f`
- Evaluator: `rarepdet/eval_map.py` SHA256 `94557cb80ae24b8663e9eb31955afe668b994058cd8e3e7618ae33e4c0017715`
- Metrics helper: `rarepdet/metrics.py` SHA256 `6ffa798647376594befc45f89ebb1aa1a5fbe3b50e5f484e7804c22bac13b081`

## Development-validation Summary

Reliability-aware `p=0.15` minus matched early fusion, paired by seed:

| Metric | Mean delta | Sample SD | n seed pairs |
| --- | ---: | ---: | ---: |
| Precision | +0.011629 | 0.016501 | 3 |
| Recall | +0.024487 | 0.026581 | 3 |
| F1 | +0.018524 | 0.006208 | 3 |
| AP50 | +0.016064 | 0.005699 | 3 |
| AP75 | +0.064657 | 0.016415 | 3 |

## Held-out Guard Summary

Reliability-aware `p=0.15` minus matched early fusion, paired by seed:

| Metric | Mean delta | Sample SD | n seed pairs |
| --- | ---: | ---: | ---: |
| Precision | +0.003213 | 0.010920 | 3 |
| Recall | +0.010549 | 0.016220 | 3 |
| F1 | +0.006946 | 0.008943 | 3 |
| AP50 | +0.008562 | 0.006229 | 3 |
| AP75 | +0.002173 | 0.017305 | 3 |

Per-seed guard deltas:

| Seed | Precision | Recall | F1 | AP50 | AP75 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0 | -0.001084 | -0.005538 | -0.003307 | +0.001628 | +0.005322 |
| 1 | +0.015628 | +0.010285 | +0.013129 | +0.010372 | +0.017686 |
| 2 | -0.004904 | +0.026899 | +0.011018 | +0.013685 | -0.016491 |

## Claim Boundary

Allowed wording: component-disjoint development-validation evidence plus locked same-dataset held-out TriAir guard evaluation, using descriptive three-seed paired comparisons between matched early fusion and reliability-aware `p=0.15`.

Disallowed wording: external dataset generalization, independent public benchmark test, training-time model selection or tuning using guard results, statistical significance, optimal dropout, calibrated physical sensor reliability, real sensor-fault robustness, or COCO AP@[0.50:0.95].

## Remaining Submission Items

- Real Springer `sn-jnl` class build and BibTeX/cross-reference closure.
- Optional replacement of simple text schematics with high-resolution vector artwork.
- Public release/archive DOI and release metadata if required by the submission workflow.
- TriAir provider URL, version, license, redistribution rights, synchronization details, or official event representation verification.
- No external-data generalization, COCO AP50:95, or causal ablation has been added.
