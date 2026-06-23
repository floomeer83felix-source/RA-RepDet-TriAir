# Current Task

## Phase 3C — RGB Duplicate Audit and Leakage-Aware Split Proposal

## Why This Phase Exists
Phase 3B found no identical `.npy` files across train/validation, but the nearest-pair manifest contains many cross-split adjacent `nframe_XXXXX` files with zero RGB signature distance and, for many pairs, zero direct RGB MAE. This is strong evidence of repeated RGB visual content across the random split even though the full 5-channel `.npy` byte streams differ.

Do not start manuscript writing, final 100-epoch training, or new architecture experiments. First determine the scale of cross-split RGB duplication and produce a leakage-aware blocked-split proposal.

## Read First
- `docs/PROJECT_CONTEXT.md`
- `docs/EXPERIMENT_STATUS.md`
- `runs/split_integrity_summary.md`
- `runs/split_integrity_manual_review.csv`
- `runs/phase3b_report.md`
- `runs/dropout_ratio_selection_note.md`
- `runs/handoff_latest.md`
- `D:\download\triair\splits\train.txt`
- `D:\download\triair\splits\val.txt`

## Strict Scope
- Do not train any model.
- Do not modify or overwrite E0–E6 runs, checkpoints, dataset files, model files, or training files.
- Do not modify `rarepdet/train_early_fusion.py`, any file under `rarepdet/models/`, or `datasets/triair_dataset.py`.
- Do not add a new architecture, loss, or augmentation.
- Only create/modify scripts under `rarepdet/tools/`, documentation, and lightweight reports/manifests under `runs/`.
- Do not commit `.npy`, source images, panels, weights, raw predictions, or copied data.

## Task 1 — Exact RGB-content cross-split audit
Create `rarepdet/tools/audit_rgb_cross_split_duplicates.py`.

For every `.npy` referenced by the existing train and validation lists:
1. load only the RGB channels `[0:3]`;
2. create an exact RGB-content SHA256 from contiguous RGB bytes, preserving dtype and shape;
3. report cross-split exact RGB-content matches even when the whole 5-channel `.npy` SHA256 differs;
4. retain the existing 256-bit signature and direct RGB MAE checks for closest pairs.

Generate:
- `runs/rgb_cross_split_duplicate_summary.md`
- `runs/rgb_cross_split_duplicate_summary.csv`
- `runs/rgb_cross_split_exact_pairs.csv`
- `runs/rgb_cross_split_group_stats.csv`

Required metrics:
- exact RGB-content matched validation samples and fraction;
- exact RGB-content matched train samples and fraction;
- number and size distribution of cross-split RGB-content groups;
- how many matching groups have identical GT-box counts and how many differ;
- relationship between exact RGB groups and parsed numeric-id distance;
- at least 30 representative pairs, with val/train path, id distance, RGB SHA256 equality, direct RGB MAE, and GT-box counts.

Interpretation labels in the report must be exactly one of:
- `CONFIRMED RGB-CONTENT CROSS-SPLIT DUPLICATION`
- `NO EXACT RGB-CONTENT CROSS-SPLIT DUPLICATION`

Do not call the result full multimodal byte duplication unless all five channels are byte-identical.

## Task 2 — Build a leakage-aware blocked split proposal
Create `rarepdet/tools/propose_blocked_split.py`.

The proposal is diagnostic only. Do not replace the existing split files and do not train yet.

Use parsed numeric ids separately for `frame_` and `nframe_` filename families. Build deterministic contiguous temporal/id blocks, then assign whole blocks to approximate 80% train and 20% validation while preserving both filename families where possible.

Run at least these candidate settings:
- block size 64, guard band 16;
- block size 128, guard band 32;
- block size 256, guard band 64.

For each candidate:
1. assign full blocks rather than random individual samples;
2. exclude guard-band samples around validation blocks from training rather than allowing them across the boundary;
3. report final train/val/guard image counts and GT-box counts;
4. report exact RGB-content matches across the proposed train/val partitions;
5. report remaining nearest-signature and id-adjacency diagnostics;
6. maintain deterministic seed 0 for block selection;
7. write local proposal lists under `runs/blocked_split_candidates/`, but do not overwrite `D:\download\triair\splits\train.txt` or `val.txt`.

Generate:
- `runs/blocked_split_proposal_summary.md`
- `runs/blocked_split_proposal_summary.csv`
- local candidate list files under `runs/blocked_split_candidates/`

Selection criteria for a recommended candidate:
- zero exact RGB-content train/val matches;
- no train id within the guard band of a validation id for the same filename family;
- validation share as close to 20% as practicable;
- enough validation GT boxes for stable evaluation;
- report any trade-off caused by guard exclusion.

If no candidate meets zero exact RGB-content matches, state this clearly and propose the smallest safe grouping rule needed to satisfy it. Do not silently relax the criterion.

## Task 3 — Existing-model diagnostic evaluation on RGB-separation strata
Create `rarepdet/tools/build_rgb_separation_subsets.py` and lightweight wrappers as needed.

From the *current validation split only*, create two diagnostic subsets without changing training data:
- `near_rgb_match_or_near_neighbor`: exact RGB-content match to training OR signature distance <=4;
- `higher_rgb_separation`: signature distance >16 and no exact RGB-content match.

For each subset, report image count, GT boxes, and the distribution of id distances. These are diagnostic strata only; do not call the higher-separation subset a clean independent test set.

Evaluate the existing E2 and E4 checkpoints on both strata with the established protocol:
- P/R/F1 at `score_thr=0.50`;
- AP50/AP75 from score-ranked evaluation;
- same model, image size, and batch convention as prior evaluation.

Generate:
- `runs/rgb_separation_strata_summary.md`
- `runs/rgb_separation_strata_summary.csv`

Do not use results from the diagnostic strata as final paper headline results. Their purpose is to assess sensitivity of the current random-split metrics to cross-split RGB similarity.

## Task 4 — Phase 3C conclusion
Create `runs/phase3c_report.md` that answers:
1. Are there exact RGB-content cross-split duplicates? Quantify them.
2. Does the current random split remain usable as a publication-grade independent benchmark? Use conservative wording.
3. Which blocked-split candidate is recommended for future retraining and why?
4. Do E2/E4 rankings materially differ between near-RGB and higher-RGB-separation validation strata?
5. What is the next safe action?

Required conclusion policy:
- If exact RGB-content train/val matches exist, do not begin manuscript drafting or final 100-epoch runs on the current random split.
- If a blocked candidate passes the selection criteria, recommend retraining only the two final variants E2 (`p=0.15`) and E4 (`p=0.20`) on that candidate in the next phase.
- Keep E2 accuracy-first and E4 robustness-first positioning until a clean-split comparison is available.

Update:
- `docs/EXPERIMENT_STATUS.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`

## Completion
1. Complete all tasks without GPU training except existing-model evaluation.
2. Commit only source code, Markdown, CSV, TXT, JSON, and documentation.
3. Commit message: `Phase 3C: audit RGB duplication and propose blocked split`.
4. Push to `research/ra-repdet-triair`.
5. If blocked, create/update `docs/TASK_BLOCKER.md` with the exact failed command, final error, attempted fix, and smallest safe next action.