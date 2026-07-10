# RA-RepDet-TriAir Handoff

Generated: 2026-07-10T22:31:56+08:00

## Current task state

- Task: `V46 COCO metrics and causal fusion ablations`
- Status: `V47_STRUCTURE_LITERATURE_COMPILE_AND_V46_COCO_ABLATION_SEED0_PARTIAL_COMPLETE`
- Blocker: `PARTIAL_GPU_TIME_AND_ALLOWED_SCOPE_BLOCKER`
- Final preflight passed: `True`

## Preserved V47 manuscript state

The remotely completed V47 manuscript restructure, 40-reference literature package, and 10-page Springer compile closure are preserved. V46 did not edit manuscript narrative files, so the new V46 metrics are evidence-package outputs awaiting a separately authorized manuscript-integration task.

- Revision report: `runs/v47_structure_literature/STRUCTURE_AND_REFERENCE_REVISION_REPORT.md`
- Compile report: `runs/v47_structure_literature/V47_COMPILE_AND_CITATION_CLOSURE.md`
- Active cited keys: 40; missing citations: 0; undefined cross-references: 0.

## Completed fixed-checkpoint COCO evaluation

All six fixed matched-early and reliability-aware `p=0.15` seed0/1/2 checkpoints were evaluated on frozen development-validation and locked same-dataset guard manifests with canonical `pycocotools` bbox AP, IoU 0.50:0.05:0.95, 101 recall samples, and maxDets=100.

| Protocol | Metric | Mean paired delta | Sample SD | Min | Max | n |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| development-validation | ap50_95 | 0.035350 | 0.020586 | 0.022666 | 0.059103 | 3 |
| development-validation | ap50 | 0.016167 | 0.005581 | 0.012857 | 0.022610 | 3 |
| development-validation | ap75 | 0.063844 | 0.016352 | 0.053539 | 0.082698 | 3 |
| development-validation | ar100 | 0.024800 | 0.018168 | 0.013653 | 0.045764 | 3 |
| same-dataset guard | ap50_95 | 0.006195 | 0.018737 | -0.012653 | 0.024818 | 3 |
| same-dataset guard | ap50 | 0.008534 | 0.005456 | 0.002728 | 0.013556 | 3 |
| same-dataset guard | ap75 | 0.003258 | 0.017719 | -0.016067 | 0.018742 | 3 |
| same-dataset guard | ar100 | 0.006171 | 0.018647 | -0.012025 | 0.025237 | 3 |

The guard mean AP50:95 delta is positive but smaller than development-validation, and guard seed2 is negative. The guard was not used for tuning, selection, or continuation.

## Seed0 causal ablations

| Contrast | Delta AP50:95 | Delta AP50 | Delta AP75 | Delta F1 |
| --- | ---: | ---: | ---: | ---: |
| ra_full_p015_minus_ra_no_moddrop | 0.016728 | 0.006256 | 0.025162 | 0.010975 |
| ra_no_moddrop_minus_matched_early | 0.005938 | 0.006601 | 0.028377 | 0.001662 |
| early_moddrop_minus_matched_early | -0.032643 | 0.005777 | -0.024206 | 0.004745 |
| ra_full_p015_minus_early_moddrop | 0.055309 | 0.007080 | 0.077745 | 0.007892 |

Fresh `ra_no_moddrop_seed0` and `early_moddrop_seed0` runs used the locked 50-epoch protocol and development-validation AP50 checkpoint selection. No ablation guard evaluation was run.

## Partial blockers

- ra_no_moddrop and early_moddrop seeds 1 and 2 require about 28-34 additional GPU hours.
- ra_static_equal and ra_stems_concat_or_project require protected architecture/training plumbing changes outside the V46 allowed-file list.

## Claim boundary

- Allowed: descriptive three-seed COCO-style within-TriAir fixed-checkpoint comparisons plus seed0-only development-validation causal contrasts.
- Guard: locked same-dataset held-out evidence only; never used for tuning, selection, or ablation continuation.
- Fresh ablation: seed0-only; stems and dynamic gate remain bundled without static controls.

## Primary outputs

- `runs/v46_coco_ablation/source_lock_v46.md/json`
- `runs/v46_coco_ablation/coco_metric_summary.md/json` and four required COCO CSV files
- `runs/v46_coco_ablation/ablation_devval_per_run.csv`
- `runs/v46_coco_ablation/ablation_devval_summary.md/json`
- `runs/v46_coco_ablation/ablation_claim_boundary.md`
- `runs/v46_coco_ablation/v46_claim_scan.txt` and review
- `runs/v46_coco_ablation/preflight_commands.txt` and outputs
