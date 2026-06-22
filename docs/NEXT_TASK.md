# Current Task

## Phase 3B — Split Integrity and Model-Selection Audit

## Why This Phase Exists
Phase 3A is complete. Before any manuscript writing or additional training, audit whether the current random train/validation split contains duplicated, near-duplicated, or likely adjacent-frame samples. The current AP values are very high, so split integrity must be documented before treating them as publication-grade.

Also correct the dropout-ratio interpretation: E2 (`p=0.15`) has the best full-modality AP50/AP75, whereas E4 (`p=0.20`) has the best P@0.50/F1@0.50 and is better in all three tested missing-modality AP50 conditions. Do not state that `p=0.15` is universally best.

## Read First
- `docs/PROJECT_CONTEXT.md`
- `docs/EXPERIMENT_STATUS.md`
- `runs/phase3a_report.md`
- `runs/dropout_ablation_summary.md`
- `runs/handoff_latest.md`
- `D:\download\triair\splits\train.txt`
- `D:\download\triair\splits\val.txt`

## Strict Scope
- Do not train any model.
- Do not alter E0–E6 runs, checkpoints, Dataset code, model code, or training code.
- Do not edit `rarepdet/train_early_fusion.py`, `rarepdet/models/`, or `datasets/triair_dataset.py`.
- Do not add new architecture, loss, or augmentation.
- Only create or modify audit/report scripts under `rarepdet/tools/`, docs, and lightweight files under `runs/`.
- Do not commit source images, npy files, copied data, figure panels, weights, or raw predictions.

## Task 1 — Cross-split integrity audit
Create `rarepdet/tools/audit_split_integrity.py`.

It must read the existing train/validation split lists and produce:
- `runs/split_integrity_summary.md`
- `runs/split_integrity_summary.csv`
- `runs/split_integrity_nearest_pairs.csv`
- `runs/split_integrity_manual_review.csv`
- optional local-only panels under `runs/local_split_audit_panels/` (must be gitignored and never committed)

### Required audit checks
1. Path overlap: number of identical paths listed in both splits.
2. Exact byte duplication: SHA256 of `.npy` bytes across train/validation; report count and all duplicate pairs.
3. Filename/id adjacency when parsable:
   - identify whether filenames contain numeric ids;
   - report the fraction of validation ids with train ids at distance 1, 2, 5, and 10;
   - report `NA` if ids cannot be parsed.
4. Near-duplicate visual audit using the RGB channels only:
   - derive a deterministic compact perceptual signature from each sample without loading all arrays simultaneously;
   - for every validation sample, find its nearest train sample by Hamming distance or equivalent deterministic signature distance;
   - report distribution quantiles and fractions at conservative distance thresholds;
   - write the nearest train partner for every validation sample to CSV.
5. Top-pair review manifest:
   - list the 50 closest cross-split pairs with train path, val path, ids, signature distance, direct RGB MAE, GT-box counts, and an initially blank manual-review field;
   - create local-only image panels for these pairs if possible, but do not commit them.

### Interpretation rules
- Do not claim that a perceptual-signature threshold proves leakage.
- Separate exact duplication from near-duplicate similarity.
- Add an explicit final status using only these labels:
  - `BLOCKED: exact cross-split duplicates found`
  - `CAUTION: near-duplicate or adjacent-frame review required`
  - `NO STRONG AUTOMATIC EVIDENCE OF LEAKAGE`
- Explain that human review of the closest pairs is required when the result is `CAUTION`.

## Task 2 — Correct the dropout-ratio conclusion
Create `runs/dropout_ratio_selection_note.md` and update `runs/phase3a_report.md` plus `runs/dropout_ablation_summary.md` only as needed to avoid an overclaim.

The note must state factually:
- E2 (`p=0.15`) yields the highest full-modality AP50/AP75.
- E4 (`p=0.20`) yields the highest P@0.50/F1@0.50 and the strongest AP50 in `w/o RGB`, `w/o Thermal`, and `w/o Event` conditions.
- Therefore there is no universally dominant ratio in the current single-seed 50-epoch ablation.
- For an accuracy-first main result, retain E2.
- For a robustness-first operating point, report E4 as a separate variant.
- Do not call the arithmetic mean missing-modality AP50 a standard metric.

Do not retrain either model in this phase.

## Task 3 — Phase 3B report and status update
Create `runs/phase3b_report.md` with:
1. split audit outcome and any required manual-review next action;
2. corrected E2/E4 model-positioning statement;
3. explicit recommendation:
   - if `BLOCKED` or `CAUTION`, do not begin manuscript drafting or final 100-epoch runs until the issue is resolved;
   - if `NO STRONG AUTOMATIC EVIDENCE OF LEAKAGE`, next phase may perform a controlled seed-replication of E2 versus E4 before final model selection.

Update:
- `docs/EXPERIMENT_STATUS.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`

## Completion
1. Run all audit scripts without GPU training.
2. Commit only source code, Markdown, CSV, TXT, JSON, and documentation.
3. Commit message: `Phase 3B: audit split integrity and model selection`.
4. Push to `research/ra-repdet-triair`.
5. If blocked, create/update `docs/TASK_BLOCKER.md` with the failed command, final error, attempted fix, and smallest safe next action.