# Current Task

## Title
Phase 7C — Evidence-Locked SIVP Table Insertion

## Goal
Replace the seven SIVP manuscript table placeholders with publication-ready LaTeX tables generated exclusively from the existing frozen CSV evidence. This task advances submission assets without changing any experiment, metric, model, split, dataset, or claim scope.

## Read First
1. `AGENTS.md` if it exists.
2. `docs/PROJECT_CONTEXT.md`
3. `docs/EXPERIMENT_STATUS.md`
4. `runs/handoff_latest.md`
5. `runs/phase4b_report.md`
6. `runs/phase7b_publication_state_reconciliation.md`
7. `docs/TASK_BLOCKER.md`
8. `submission/sivp/README.md`
9. `submission/sivp/tex/main.tex`
10. `submission/sivp/tex/ra_repdet_sivp.tex`
11. `submission/sivp/tables/FINAL_TABLE_INSERTION_MAP.md`
12. `manuscript/tables/Table_1_dataset_and_clean_split.csv`
13. `manuscript/tables/Table_2_implementation_and_reproducibility.csv`
14. `manuscript/tables/Table_3_controlled_ablation.csv`
15. `manuscript/tables/Table_4_missing_modality_robustness.csv`
16. `manuscript/tables/Table_5_rgb_only_external_baseline.csv`
17. `manuscript/tables/Table_6_efficiency_and_convergence.csv`
18. `manuscript/tables/Table_7_reliability_weight_audit.csv`
19. `scripts/preflight_submission.py`
20. `rarepdet/tools/generate_handoff.py`
21. `rarepdet/tools/update_project_status.py`

## Frozen Assets
- Remote branch: `research/ra-repdet-triair`.
- Official manuscript headline: **R4 Reliability p=0.20** on `block64_guard16_seed0`, controlled seeds `0` and `2`.
- Publication headline means: F1@0.50 `0.920861`, AP50 `0.962495`, AP75 `0.891266`, w/o RGB AP50 `0.916051`, w/o Thermal AP50 `0.718277`, w/o Event AP50 `0.961577`.
- Phase 4B decision: `SELECT R4 AS CLEAN-SPLIT MAIN VARIANT`.
- The seven CSV files under `manuscript/tables/` are the sole numerical sources for this task.
- Former E0–E6 random-split results are historical/exploratory only and must not be promoted in any generated table or caption.
- Strict V18 preflight remains blocked by author-supplied metadata, TriAir governance facts, final figures, release metadata, final environment record, and final compile readiness.

## Allowed Files To Modify
- `docs/NEXT_TASK.md`
- `docs/EXPERIMENT_STATUS.md`
- `docs/TASK_BLOCKER.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`
- `runs/phase7c_table_insertion_report.md`
- `runs/phase7c_table_insertion_report.json`
- `submission/sivp/tex/ra_repdet_sivp.tex`
- `submission/sivp/tables/Table_1_dataset_and_clean_split.tex`
- `submission/sivp/tables/Table_2_implementation_and_reproducibility.tex`
- `submission/sivp/tables/Table_3_controlled_ablation.tex`
- `submission/sivp/tables/Table_4_missing_modality_robustness.tex`
- `submission/sivp/tables/Table_5_rgb_only_external_baseline.tex`
- `submission/sivp/tables/Table_6_efficiency_and_convergence.tex`
- `submission/sivp/tables/Table_7_reliability_weight_audit.tex`
- `submission/sivp/tables/TABLE_SOURCE_TRACEABILITY.md`
- `submission/sivp/tables/TABLE_SOURCE_TRACEABILITY.csv`
- `submission/sivp/review/TABLE_RENDERING_CHECK.md`
- `submission/sivp/review/TABLE_RENDERING_CHECK.csv`
- `rarepdet/tools/generate_handoff.py`
- `rarepdet/tools/update_project_status.py`

## Forbidden Files To Modify
- All training, model, dataset, loss, primary AP-evaluation, and split-generation source files.
- `manuscript/tables/*.csv` and all other source-evidence CSV files.
- All raw `.npy` data, labels, checkpoints, weights, images, rendered final figure assets, final PDFs, and existing experimental outputs.
- Do not modify numerical experiment values, calculate replacement metrics, regenerate model outputs, run training, run inference sweeps, or mutate split manifests.
- Do not insert fake author information, citations, DOIs, licence terms, release URLs, or final-asset approvals.

## Required Commands
Run only documentation/table-generation checks. Start with:

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git status --short
python scripts/preflight_submission.py --root . --allow-placeholders
```

If `git pull --ff-only` cannot proceed because of local/remote divergence, do not use `--allow-unrelated-histories`, reset, force push, or rewrite history. Record a blocker, commit only safe partial documents if possible, and stop.

After inserting tables, run:

```powershell
python rarepdet/tools/generate_handoff.py
python rarepdet/tools/update_project_status.py
python scripts/preflight_submission.py --root . --allow-placeholders
python scripts/preflight_submission.py --root .
powershell -ExecutionPolicy Bypass -File rarepdet/tools/finish_task.ps1
```

A local PDF compile is optional only if the complete Springer `sn-jnl` environment is available. Do not install packages, fabricate a PDF, or claim visual compilation success when dependencies are missing.

## Required Outputs

### 1. Seven evidence-locked table assets
Create one standalone LaTeX fragment per source CSV, using the exact table numbering and captions already present in `submission/sivp/tex/ra_repdet_sivp.tex`:

| Table | Required fragment | Sole source |
| --- | --- | --- |
| 1 | `submission/sivp/tables/Table_1_dataset_and_clean_split.tex` | `manuscript/tables/Table_1_dataset_and_clean_split.csv` |
| 2 | `submission/sivp/tables/Table_2_implementation_and_reproducibility.tex` | `manuscript/tables/Table_2_implementation_and_reproducibility.csv` |
| 3 | `submission/sivp/tables/Table_3_controlled_ablation.tex` | `manuscript/tables/Table_3_controlled_ablation.csv` |
| 4 | `submission/sivp/tables/Table_4_missing_modality_robustness.tex` | `manuscript/tables/Table_4_missing_modality_robustness.csv` |
| 5 | `submission/sivp/tables/Table_5_rgb_only_external_baseline.tex` | `manuscript/tables/Table_5_rgb_only_external_baseline.csv` |
| 6 | `submission/sivp/tables/Table_6_efficiency_and_convergence.tex` | `manuscript/tables/Table_6_efficiency_and_convergence.csv` |
| 7 | `submission/sivp/tables/Table_7_reliability_weight_audit.tex` | `manuscript/tables/Table_7_reliability_weight_audit.csv` |

Requirements for every fragment:

- Use LaTeX-safe escaping for `%`, `_`, `&`, `#`, and other special characters.
- Preserve every source row, header, numeric value, missing value marker, model name, seed label, threshold, and unit exactly as represented in the source CSV. Do not silently round, recompute, sort, filter, average, or reformat a number.
- Use a readable SIVP-compatible layout that fits a two-column journal paper. Use `\resizebox{\textwidth}{!}{...}` or an equivalent only when necessary; do not change source values to fit the page.
- Use `booktabs`-style rules only when packages already supplied by the source template make them available. Do not add undeclared packages without verifying the main template supports them.
- Keep captions and labels in `ra_repdet_sivp.tex`; fragments should contain only the tabular content, or clearly documented table wrappers if the current LaTeX structure requires it.
- Add concise, factual notes inside the relevant table environment only when they clarify an existing source fact (for example, two seed means or synthetic modality removal). Do not introduce new scientific claims.

### 2. Replace every table placeholder
In `submission/sivp/tex/ra_repdet_sivp.tex`, replace all seven strings containing `TABLE PLACEHOLDER - FINAL VERSION PENDING` with `\input{...}` references to the matching fragment. Preserve all existing captions and labels. Do not modify figure placeholders in this task.

### 3. Source traceability and validation
Create both Markdown and CSV traceability files mapping each table fragment to:

- source CSV path and Git blob/commit provenance if available;
- source row count and rendered row count;
- source header and rendered header;
- exact numerical-token comparison result;
- any LaTeX escaping transformations;
- reviewer status: `pass`, `warning`, or `blocker`.

Create `submission/sivp/review/TABLE_RENDERING_CHECK.md` and `.csv` that records:

- whether all 7 input fragments exist;
- whether the manuscript body contains zero remaining table placeholder strings;
- whether all 7 source CSVs are unchanged by this task;
- whether every source row is represented exactly once in its corresponding fragment;
- whether Table 3 and Table 4 use clean blocked-split R0/R1/R2/R4 evidence rather than legacy E0–E6 headline wording;
- potential width/layout warnings;
- expected strict-preflight result after table insertion.

### 4. Report and status
Create `runs/phase7c_table_insertion_report.md` and matching JSON that includes:

- the seven source-to-fragment mappings;
- verification outcomes and row counts;
- remaining strict-preflight blockers after removing table placeholders;
- a confirmation that no metric, source evidence CSV, model, dataset, split, weights, checkpoint, figure, or final PDF changed;
- any compile limitation.

Update `docs/TASK_BLOCKER.md` to remove table placeholders only if they are actually gone and validated. Keep every unresolved author/metadata/figure/release/environment/compiler blocker.

Refresh `runs/handoff_latest.md` and `.json` and `docs/EXPERIMENT_STATUS.md`. Their publication headline must remain R4 on the frozen blocked split; legacy E0–E6 wording must remain historical/exploratory.

## Acceptance Criteria
- Seven `.tex` table fragments exist and are linked from the SIVP manuscript body.
- The SIVP body contains zero `TABLE PLACEHOLDER` strings.
- Each fragment is demonstrably traceable to exactly one unchanged source CSV, without numeric modification.
- Tables 3 and 4 preserve the clean blocked-split R0/R1/R2/R4 evidence and do not elevate legacy random-split E2 as the manuscript headline.
- Placeholder-mode preflight is executed and documented. Strict preflight must still be reported truthfully; it is expected to remain FAIL until author metadata, data/release facts, final figures, environment record, and final compile readiness are closed.
- No training, GPU inference, numerical evaluation, split mutation, source-data mutation, or core model/dataset/evaluation change occurs.
- No final PDF is generated or labeled submission-ready.
- `runs/handoff_latest.md` records the final commit SHA, changed files, command outcomes, table-validation outcome, and residual blockers.
- Commit all permitted outputs and push the branch.

## Commit Message
docs: insert evidence-locked SIVP tables

## Completion / Blocker Rule
Complete the table-only asset task, refresh handoff/status, commit, and push. If source CSV structure cannot be rendered safely without changing values or if a template dependency is ambiguous, write the issue in `docs/TASK_BLOCKER.md`, commit the traceability findings, and stop. Do not alter experimental evidence or lower strict-preflight standards.
