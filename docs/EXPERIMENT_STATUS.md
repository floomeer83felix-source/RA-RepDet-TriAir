# Experiment Status

Generated: 2026-07-10T22:31:59+08:00

## Current status

`V47_STRUCTURE_LITERATURE_COMPILE_AND_V46_COCO_ABLATION_SEED0_PARTIAL_COMPLETE`

The remotely completed V47 manuscript restructure, 40-reference literature package, and compile closure are preserved. V46 completed canonical COCO-style evaluation for all six fixed baseline/main checkpoints on frozen development-validation and locked same-dataset guard manifests, plus the two feasible fresh seed0 ablations under the locked 50-epoch protocol. Seeds 1 and 2 for fresh variants and architecture-changing static controls remain explicitly deferred.

## V47 manuscript and compile state

- Manuscript structure and recent-journal literature revision: complete.
- Active cited keys: 40; missing citations: 0; undefined cross-references: 0.
- Springer-style compile: 10 pages, no obvious page-level clipping reported.
- V46 did not edit manuscript narrative files; evidence integration remains a future explicitly authorized task.

## COCO-style evidence

| Protocol | Mean delta AP50:95 | SD | Mean delta AP50 | Mean delta AP75 | n |
| --- | ---: | ---: | ---: | ---: | ---: |
| Development-validation | 0.035350 | 0.020586 | 0.016167 | 0.063844 | 3 |
| Same-dataset guard | 0.006195 | 0.018737 | 0.008534 | 0.003258 | 3 |

The project-local AP50/AP75 values were reproduced to floating-point tolerance before the canonical COCO summaries were accepted. Guard results remained evaluation-only.

## Fresh seed0 ablations

| Run | AP50:95 | AP50 | AP75 | F1 | Training seconds |
| --- | ---: | ---: | ---: | ---: | ---: |
| ra_no_moddrop_seed0 | 0.711245 | 0.947747 | 0.866164 | 0.903946 | 44398.4 |
| early_moddrop_seed0 | 0.672664 | 0.946924 | 0.813581 | 0.907029 | 44074.8 |

## Verification

- COCO metric tiny-input smoke test: `True`.
- Existing project metric reproduction: `True`.
- Claim scan passed: `True`.
- Final V46 preflight passed: `True`.

## Active partial blocker

- ra_no_moddrop and early_moddrop seeds 1 and 2 require about 28-34 additional GPU hours.
- ra_static_equal and ra_stems_concat_or_project require protected architecture/training plumbing changes outside the V46 allowed-file list.

## Current claim boundary

Allowed wording: descriptive three-seed COCO-style within-TriAir fixed-checkpoint evidence plus seed0-only development-validation ablation contrasts.

Required cautions: same-dataset guard only; no guard-based tuning or selection; one-seed fresh ablations; stems and dynamic gating remain bundled; no external-data, significance, optimality, calibration, or real-fault claims.
