# Experiment Status

Generated: 2026-07-09

## Current Status

`V41_SIVP_MANUSCRIPT_ALIGNMENT_COMPLETE_AUTHOR_METADATA_PARTIAL`

The V41 three-seed interim development-validation evidence is consolidated, and the active SIVP LaTeX narrative has been aligned to the validation-only evidence state. The user-provided author names, affiliation, and corresponding-author email have now been inserted into the active SIVP entry files.

No new training, evaluation, guard/test access, checkpoint loading, raw data access, or prediction-cache access was performed. Manuscript edits were limited to SIVP LaTeX metadata/narrative alignment and local preflight/compile recording.

## Evidence Inputs

- V40 seed0/seed2 source: `runs/v40_expanded_adjacency_v2_compute_minimized/v40_four_run_summary.json`.
- V41 fresh seed1 source: `runs/v41_q1_upgrade/seed1/seed1_per_run_summary.csv`.
- V41 seed1 source lock: `runs/v41_q1_upgrade/seed1/source_lock_seed1.md/json`.
- V41 seed1 completion commit: `5d839ae900849919189edff4bdd364f42c043b86`.
- Three-seed package: `runs/v41_q1_upgrade/interim_devval/`.

## Author metadata inserted

- Authors: Nan Xin and Xueting Jin.
- Corresponding author: Nan Xin.
- Affiliation: Anhui Police College, Hefei, Anhui, China.
- Corresponding email: `floomeer83felix@gmail.com`.
- Updated entry files:
  - `submission/sivp/tex/main.tex`
  - root `main.tex`
  - root `main_sivp_snjnl.tex`

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

## SIVP manuscript alignment completed

- Updated `submission/sivp/tex/ra_repdet_sivp.tex` so the active narrative uses reliability-aware `p=0.15` versus matched early fusion across seed0/seed1/seed2 on the frozen V40 component-disjoint development-validation split.
- Updated `submission/sivp/tex/main.tex`, root `main.tex`, and `main_sivp_snjnl.tex` abstracts/keywords so active entry points match the V41 validation-only claim boundary.
- Inserted `submission/sivp/tables/Table_8_three_seed_interim_devval.tex` as the active main results table.
- Recorded pre-edit and post-edit claim scans under `runs/v41_q1_upgrade/sivp_alignment/`.
- Post-edit body scan: `p=0.20`, `R4`, `block64`, `guard16`, and `optimal` are zero; remaining high-risk terms occur only as limitation/claim-boundary wording.
- `python scripts/preflight_submission.py --root . --allow-placeholders`: PASS with expected warnings for placeholders and missing final figure assets.
- Local LaTeX: direct MiKTeX `pdflatex` pass generated an 8-page PDF during checking, confirming TeX/table syntax integration. Build products were removed after logging.
- `latexmk` is unavailable because MiKTeX lacks Perl; full BibTeX multi-pass compile timed out and remains a local toolchain/bibliography closure item.

## Task blocker state

`docs/TASK_BLOCKER.md` records `NO_ACTIVE_BLOCKER`. The older V40 GPU-deferred blocker is historical and no longer represents the active task state.

## Current claim boundary

Allowed wording: three-seed interim development-validation descriptive evidence on the frozen V40 component-disjoint development-validation split.

Disallowed wording: independent test, external generalization, statistical significance, manuscript-final aggregate, optimal dropout, calibrated sensor reliability, or physical sensor-fault robustness.

## Work intentionally left for final submission

- Final artwork for Fig. 1--6.
- Funding, competing interests, author contributions, acknowledgments, and data/code availability.
- Public archive/DOI and release metadata.
- TriAir provider/license/version/redistribution/synchronization details.
- Full BibTeX/cross-reference closure after local toolchain repair.

## Remaining scientific limitations

- Validation-only evidence.
- Three seed pairs only; seed3/seed4 are not planned in the current line.
- No independent test.
- No causal ablations separating stems, dynamic gate, and dropout.
- No COCO mAP@[0.50:0.95] package.
- Dataset provider provenance remains unresolved.
- Label-quality review remains incomplete.
