# Experiment Status

Generated: 2026-07-09

## Current Status

`V43_SIVP_HELDOUT_GUARD_INTEGRATION_COMPLETE`

The V42 locked held-out guard evaluation has been integrated into the active SIVP manuscript. The paper is no longer described as validation-only. The active claim is now: three-seed component-disjoint development-validation evidence plus a locked same-dataset TriAir held-out guard evaluation using fixed seed0/seed1/seed2 checkpoints.

No new training, hyperparameter tuning, checkpoint selection, split modification, robustness experiment, profiling run, or external-data evaluation was performed during the V43 manuscript integration. The guard results were used only as already-completed V42 evidence for manuscript writing.

## Evidence Inputs

- V42 commit: `187632960a4093778d83c3383e7f5540723a60e1`.
- V42 source lock: `runs/v42_locked_guard_heldout/heldout_guard_source_lock.md/json`.
- V42 summary: `runs/v42_locked_guard_heldout/heldout_guard_summary.md/json`.
- V42 claim boundary: `runs/v42_locked_guard_heldout/heldout_guard_claim_boundary.md`.
- Guard source manifest: `runs/component_disjoint_v40/guard.txt`.
- Guard rows: 837 images.
- Guard GT boxes: 1264.
- Guard normalized LF SHA256: `9f871c16aa60b517ffd8df530782eed1befcd652969a9f94e5cd6af5ac2c8c2e`.
- Guard raw file SHA256 recorded by evaluator: `0cf3270c0a73d03caf8d698bb4e9ddb0adba46e688c52d8589f57ea12488881f`.
- Evaluator: `rarepdet/eval_map.py` SHA256 `94557cb80ae24b8663e9eb31955afe668b994058cd8e3e7618ae33e4c0017715`.
- Metrics helper: `rarepdet/metrics.py` SHA256 `6ffa798647376594befc45f89ebb1aa1a5fbe3b50e5f484e7804c22bac13b081`.

## Manuscript updates

- Updated `submission/sivp/tex/ra_repdet_sivp.tex` to include V42 held-out guard evidence in the Introduction, protocol, Results, Discussion, Limitations, and Conclusion.
- Updated `submission/sivp/tex/main.tex`, root `main.tex`, and `main_sivp_snjnl.tex` title/abstract/keywords to describe component-disjoint development-validation plus locked held-out guard evaluation.
- Created `submission/sivp/tables/Table_9_locked_heldout_guard.tex` as the active held-out guard result table.
- Updated `submission/sivp/tables/Table_1_dataset_and_clean_split.tex` to include held-out guard images and boxes.
- Updated `submission/sivp/tables/Table_2_implementation_and_reproducibility.tex` to include fixed-checkpoint guard evaluation.
- Updated `submission/sivp/review/REVIEWER_REPORT_PRE_SUBMISSION.md` to reflect the stronger V42 evidence state.

## Development-validation descriptive summary

Reliability-aware `p=0.15` minus matched early fusion, paired by seed:

| Metric | Mean delta | Sample SD | n seed pairs |
| --- | ---: | ---: | ---: |
| Precision | +0.011629 | 0.016501 | 3 |
| Recall | +0.024487 | 0.026581 | 3 |
| F1 | +0.018524 | 0.006208 | 3 |
| AP50 | +0.016064 | 0.005699 | 3 |
| AP75 | +0.064657 | 0.016415 | 3 |

## Held-out guard descriptive summary

Reliability-aware `p=0.15` minus matched early fusion, paired by seed:

| Metric | Mean delta | Sample SD | n seed pairs |
| --- | ---: | ---: | ---: |
| Precision | +0.003213 | 0.010920 | 3 |
| Recall | +0.010549 | 0.016220 | 3 |
| F1 | +0.006946 | 0.008943 | 3 |
| AP50 | +0.008562 | 0.006229 | 3 |
| AP75 | +0.002173 | 0.017305 | 3 |

Per-seed held-out guard deltas:

| Seed | Precision | Recall | F1 | AP50 | AP75 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0 | -0.001084 | -0.005538 | -0.003307 | +0.001628 | +0.005322 |
| 1 | +0.015628 | +0.010285 | +0.013129 | +0.010372 | +0.017686 |
| 2 | -0.004904 | +0.026899 | +0.011018 | +0.013685 | -0.016491 |

## Current claim boundary

Allowed wording: component-disjoint development-validation evidence plus locked same-dataset held-out TriAir guard evaluation, using descriptive three-seed paired comparisons between matched early fusion and reliability-aware `p=0.15`.

Disallowed wording: external dataset generalization, independent public benchmark test, training-time model selection or tuning using guard results, statistical significance, optimal dropout, calibrated physical sensor reliability, real sensor-fault robustness, or COCO AP@[0.50:0.95].

## Remaining scientific limitations

- The held-out guard partition is within the TriAir project dataset, not an external dataset.
- The evidence is descriptive with three seed pairs only.
- The guard results must not be used for future model selection without rewriting the claim boundary.
- No causal ablation separates stems, dynamic gate, and modality dropout.
- No COCO mAP@[0.50:0.95] package is available.
- Dataset provider provenance remains only partially resolved by naming TriAir as public.
- Label-quality review remains incomplete.

## Remaining submission-packaging items

- Real Springer `sn-jnl` class build and BibTeX/cross-reference closure.
- Optional replacement of simple text schematics with high-resolution vector artwork.
- Public release/archive DOI and release metadata if required by the submission workflow.
