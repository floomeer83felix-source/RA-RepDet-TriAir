# Current Task

## Title
Phase 7G — Submission Ledger Reconciliation and Author Intake Package

## Goal
Correct the submission ledger so it reflects the completed Phase 7C table insertion, then create a fillable author-input package for the remaining external facts and approvals. This is documentation and validation only. Do not modify experiments, manuscript TeX, data, models, figures, or final assets.

## Read First
- `docs/EXPERIMENT_STATUS.md`
- `runs/handoff_latest.md`
- `runs/phase7b_publication_state_reconciliation.md`
- `runs/phase7c_table_insertion_report.md`
- `runs/phase7f_author_review_intake_report.md`
- `docs/TASK_BLOCKER.md`
- `submission/sivp/metadata/FINAL_SUBMISSION_INPUT_LEDGER.md`
- `submission/sivp/review/FINAL_SUBMISSION_INPUT_LEDGER.csv`
- `submission/sivp/review/TABLE_RENDERING_CHECK.md`
- `submission/sivp/review/AUTHOR_FIGURE_REVIEW_PACKET.md`
- `scripts/preflight_submission.py`
- `rarepdet/tools/generate_handoff.py`
- `rarepdet/tools/update_project_status.py`

## Frozen Facts
- The official manuscript headline is R4 Reliability p=0.20 on `block64_guard16_seed0`, seeds 0 and 2.
- Phase 7C inserted evidence-locked Tables 1–7. The SIVP body has zero `TABLE PLACEHOLDER` strings, and source CSVs were unchanged.
- Fig. 3–5 are local, ignored, non-final review candidates only. Fig. 1–2 need author-approved designs; Fig. 6 needs author panel selection.
- Strict preflight must remain FAIL until final figures and author-provided facts are genuinely available.

## Allowed Files To Modify
- `docs/NEXT_TASK.md`
- `docs/EXPERIMENT_STATUS.md`
- `docs/TASK_BLOCKER.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`
- `runs/phase7g_submission_intake_report.md`
- `runs/phase7g_submission_intake_report.json`
- `submission/sivp/metadata/FINAL_SUBMISSION_INPUT_LEDGER.md`
- `submission/sivp/review/FINAL_SUBMISSION_INPUT_LEDGER.csv`
- `submission/sivp/metadata/AUTHOR_SUBMISSION_INPUT_PACKET.md`
- `submission/sivp/metadata/AUTHOR_SUBMISSION_INPUT_RESPONSES.csv`
- `submission/sivp/metadata/ENVIRONMENT_RECORD_TEMPLATE.md`
- `submission/sivp/review/SUBMISSION_INPUT_COMPLETENESS_CHECK.md`
- `submission/sivp/review/SUBMISSION_INPUT_COMPLETENESS_CHECK.csv`
- `rarepdet/tools/generate_handoff.py`
- `rarepdet/tools/update_project_status.py`

## Forbidden Files To Modify
- Manuscript TeX including `main.tex`, `main_sivp_snjnl.tex`, and `submission/sivp/tex/ra_repdet_sivp.tex`.
- All experimental code, model code, data, source CSVs, checkpoints, candidate/final figures, local panels, and final PDFs.
- Do not add or infer author identities, affiliations, emails, ORCIDs, funding, declarations, data licences, citations, release URLs, tags, commit hashes, archive dates, DOIs, hardware facts, or approvals.
- Do not run training, inference, evaluation, source-data mutation, or LaTeX compilation.

## Required Work
1. Reconcile `TAB_001` in the canonical Markdown and CSV ledgers:
   - State: `complete — evidence-locked Tables 1–7 inserted in Phase 7C`.
   - Evidence: `runs/phase7c_table_insertion_report.md`, `submission/sivp/tables/TABLE_SOURCE_TRACEABILITY.md`, and `submission/sivp/review/TABLE_RENDERING_CHECK.md`.
   - Strict-preflight effect: table-placeholder failure is resolved; non-table blockers remain.
   - Closure action: none for table placeholders; final visual compile review remains under `TEX_001`.
2. Update status/handoff generators so the resolved table item is not counted as an open `table_asset` blocker.
3. Create `AUTHOR_SUBMISSION_INPUT_PACKET.md`, organized into: authorship/contact; declarations; TriAir citation/version/licence/access/redistribution; code/archive/release; figure decisions; claim scope; environment; final Springer compile owner. Every unresolved item must say `pending author confirmation`.
4. Create `AUTHOR_SUBMISSION_INPUT_RESPONSES.csv` with one row per unresolved ledger item, excluding resolved `TAB_001`, using columns:
   `item_id,category,exact_required_input,current_status,author_response,confirmed_by,confirmation_date,source_of_confirmation,repository_destination,validation_rule,notes`
   Leave all response and confirmation fields blank.
5. Create `ENVIRONMENT_RECORD_TEMPLATE.md` with fields for hardware, OS, Python, PyTorch/Torchvision, CUDA/cuDNN, package versions, training image size, batch size, seeds, epochs, profiling protocol, confirmer, and date. Only prefill repository-documented experimental facts such as image size 640, seeds 0/2, and 50 epochs where verified; leave system-specific facts blank.
6. Create Markdown and CSV completeness checks showing ledger total, resolved count, unresolved count by category, author-template row count, `TAB_001` resolved, no response fields prefilled, and strict preflight expected to remain FAIL.
7. Create Phase 7G Markdown/JSON report. Update `docs/TASK_BLOCKER.md`, handoff, and status. Remove only the obsolete table-asset blocker; preserve figure, author, data-governance, release, claim-scope, environment, and compile blockers.

## Required Commands
```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git status --short
python scripts/preflight_submission.py --root . --allow-placeholders
python rarepdet/tools/generate_handoff.py
python rarepdet/tools/update_project_status.py
python scripts/preflight_submission.py --root . --allow-placeholders
python scripts/preflight_submission.py --root .
powershell -ExecutionPolicy Bypass -File rarepdet/tools/finish_task.ps1
```

If the fast-forward pull cannot proceed, do not rewrite history or force push. Record the blocker and stop.

## Acceptance Criteria
- `TAB_001` is resolved in both ledger formats and is absent from open table blockers.
- The response CSV includes every unresolved ledger item and contains no fabricated facts.
- The intake packet routes each requested author input to a repository destination.
- The environment template contains only verified experiment settings and blank system-specific fields.
- Strict preflight is recorded truthfully as FAIL on remaining non-table blockers.
- No manuscript TeX, experiment, model, dataset, metric, source CSV, figure, candidate/final asset, or final PDF changes.
- Commit only allowed files and push.

## Commit Message
`docs: reconcile submission ledger and author intake package`

## Completion Rule
Finish the documentation reconciliation and intake package, refresh handoff/status, commit, and push. Do not claim formal submission readiness.