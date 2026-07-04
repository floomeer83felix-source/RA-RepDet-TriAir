# Current Task

## Title
Phase 7J — Conditional Application of Confirmed Authorship and Declarations

## Goal
Apply only author-confirmed and Phase 7I-eligible `author_metadata` and `declarations` rows to their planned metadata and submission-source destinations. This task is conditional: it must not run beyond the eligibility check until at least one applicable row is marked `eligible_for_future_guarded_application` in `submission/sivp/metadata/CONFIRMED_UPDATE_PLAN.csv`.

## Read First
1. `AGENTS.md` if it exists.
2. `docs/PROJECT_CONTEXT.md`
3. `docs/EXPERIMENT_STATUS.md`
4. `runs/handoff_latest.md`
5. `runs/phase7h_author_response_validation_report.md`
6. `runs/phase7i_update_planning_report.md`
7. `docs/TASK_BLOCKER.md`
8. `docs/UPCOMING_TASKS.md`
9. `submission/sivp/review/FINAL_SUBMISSION_INPUT_LEDGER.csv`
10. `submission/sivp/metadata/AUTHOR_SUBMISSION_INPUT_RESPONSES.csv`
11. `submission/sivp/metadata/AUTHOR_RESPONSE_VALIDATION.csv`
12. `submission/sivp/metadata/CONFIRMED_UPDATE_PLAN.csv`
13. `submission/sivp/metadata/CONFIRMED_UPDATE_PLAN.md`
14. `submission/sivp/review/CONFIRMED_UPDATE_PLAN_CHECK.md`
15. `submission/sivp/metadata/submission_metadata.yaml`
16. `submission/sivp/metadata/submission_metadata.tex`
17. `submission/sivp/metadata/author_information_template.md`
18. `submission/sivp/metadata/submission_form_answers_draft.md`
19. `submission/sivp/metadata/author_contributions_template.md`
20. `submission/sivp/metadata/competing_interests_statement_draft.md`
21. `submission/sivp/metadata/ai_use_disclosure_draft.md`
22. `main.tex`
23. `main_sivp_snjnl.tex`
24. `scripts/preflight_submission.py`
25. `rarepdet/tools/generate_handoff.py`
26. `rarepdet/tools/update_project_status.py`

## Frozen Assets
- Remote branch: `research/ra-repdet-triair`.
- Official manuscript headline: **R4 Reliability p=0.20** on `block64_guard16_seed0`, controlled seeds `0` and `2`.
- Phase 7C Tables 1–7 and `TAB_001` are complete and must remain unchanged.
- Current Phase 7I plan has 29 unresolved rows and zero rows eligible for future guarded application unless authors subsequently provide confirmed input.
- This task concerns only `AUTH_001`–`AUTH_004` and `DECL_001`–`DECL_005`; all data-governance, release/archive, figure, claim-scope, environment, and compile-readiness rows are out of scope.
- A well-formed response is not enough: each applied row must be author-confirmed through nonblank response, confirmer identity, confirmation date, source of confirmation, and Phase 7I eligibility.

## Trigger Gate
Before any source file is edited, run Phase 7H validation and Phase 7I planning.

Proceed only when at least one row in category `author_metadata` or `declarations` has:

```text
validation_state = structurally_ready_for_future_apply
plan_state = eligible_for_future_guarded_application
author_confirmation_complete = yes
```

If no such row exists, do not edit any metadata or TeX. Update only `docs/TASK_BLOCKER.md`, handoff/status, and a short Phase 7J blocked report stating that external author input is still required; then commit and push the safe blocked-state update.

## Allowed Files To Modify
- `docs/NEXT_TASK.md`
- `docs/UPCOMING_TASKS.md`
- `docs/EXPERIMENT_STATUS.md`
- `docs/TASK_BLOCKER.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`
- `runs/phase7j_confirmed_authorship_declarations_report.md`
- `runs/phase7j_confirmed_authorship_declarations_report.json`
- `main.tex`
- `main_sivp_snjnl.tex`
- `submission/sivp/metadata/submission_metadata.yaml`
- `submission/sivp/metadata/submission_metadata.tex`
- `submission/sivp/metadata/author_information_template.md`
- `submission/sivp/metadata/submission_form_answers_draft.md`
- `submission/sivp/metadata/author_contributions_template.md`
- `submission/sivp/metadata/competing_interests_statement_draft.md`
- `submission/sivp/metadata/ai_use_disclosure_draft.md`
- `submission/sivp/review/CONFIRMED_AUTHORS_DECLARATIONS_APPLICATION_CHECK.md`
- `submission/sivp/review/CONFIRMED_AUTHORS_DECLARATIONS_APPLICATION_CHECK.csv`
- `rarepdet/tools/generate_handoff.py`
- `rarepdet/tools/update_project_status.py`

## Forbidden Files To Modify
- `submission/sivp/metadata/AUTHOR_SUBMISSION_INPUT_RESPONSES.csv`, `AUTHOR_RESPONSE_VALIDATION.csv`, and `CONFIRMED_UPDATE_PLAN.*`; these are evidence/plan inputs and must not be overwritten.
- `submission/sivp/review/AUTHOR_FIGURE_REVIEW_DECISIONS.csv` and `FIGURE6_PANEL_REVIEW_TEMPLATE.csv`.
- `submission/sivp/tex/**`, including `ra_repdet_sivp.tex`.
- All reference/BibTeX files, data-governance destinations, release/archive manifests, figures, source CSVs, table fragments, raw data, checkpoints, models, training/evaluation code, and final PDFs.
- Do not apply data-governance, release/archive, figure, claim-scope, environment, or compile-readiness values in this task.
- Do not infer or normalize factual values beyond exact author-confirmed input. Do not invent ORCIDs, affiliations, grants, declarations, contributor roles, disclosure text, or dates.
- Do not run training, inference, evaluation, data mutation, network access, or LaTeX compilation.

## Required Commands

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git status --short
python scripts/preflight_submission.py --root . --allow-placeholders
python submission/sivp/metadata/validate_author_submission_inputs.py --root . --responses submission/sivp/metadata/AUTHOR_SUBMISSION_INPUT_RESPONSES.csv --ledger submission/sivp/review/FINAL_SUBMISSION_INPUT_LEDGER.csv --output-prefix submission/sivp/metadata/author_response_validation
python submission/sivp/metadata/plan_confirmed_submission_updates.py --root . --responses submission/sivp/metadata/AUTHOR_SUBMISSION_INPUT_RESPONSES.csv --validation submission/sivp/metadata/AUTHOR_RESPONSE_VALIDATION.csv --ledger submission/sivp/review/FINAL_SUBMISSION_INPUT_LEDGER.csv --figure-decisions submission/sivp/review/AUTHOR_FIGURE_REVIEW_DECISIONS.csv --figure6-template submission/sivp/review/FIGURE6_PANEL_REVIEW_TEMPLATE.csv --output-prefix submission/sivp/metadata/confirmed_update_plan
```

If `git pull --ff-only` cannot proceed, do not reset, force-push, or rewrite history. Record the exact blocker and stop.

If the trigger gate fails, do not run any source-application step. Create only the blocked report/check, refresh handoff/status, then run:

```powershell
python rarepdet/tools/generate_handoff.py
python rarepdet/tools/update_project_status.py
python scripts/preflight_submission.py --root . --allow-placeholders
python scripts/preflight_submission.py --root .
powershell -ExecutionPolicy Bypass -File rarepdet/tools/finish_task.ps1
```

If the trigger gate passes, apply only eligible `AUTH_*` and `DECL_*` items exactly as confirmed. Then run the same final commands. Strict preflight is still expected to fail on remaining categories and final figures.

## Required Outputs

### 1. Gated application report
Create `runs/phase7j_confirmed_authorship_declarations_report.md` and matching JSON recording:

- Phase 7H and Phase 7I command outcomes;
- all examined `AUTH_*` and `DECL_*` item IDs;
- gate status for every examined item;
- each source destination changed, if any, and exact originating item ID;
- before/after placeholder checks for applied destination files;
- confirmation that no out-of-scope category was applied;
- remaining strict-preflight blockers.

### 2. Application integrity check
Create Markdown and CSV application checks. They must verify:

- every applied value maps to one eligible plan row and its author-response confirmation metadata;
- no pending or externally gated row was applied;
- no duplicate or contradictory author/declaration value was placed across allowed destination files;
- no unconfirmed author/declaration placeholder was silently removed;
- no author identity, affiliation, ORCID, email, funding, acknowledgement, contribution, competing-interest, or AI-use declaration was invented;
- no TeX body, figure, table, data, release/archive, model, metric, or experiment file changed;
- strict preflight does not falsely report formal submission readiness.

### 3. Blocked state rule
With the current known blank response template, the expected result is **BLOCKED — zero eligible author/declaration rows**. Do not treat this as an error in the validator or planner. Do not fabricate an application merely to complete the task.

## Acceptance Criteria
- No application occurs without the Trigger Gate passing for the relevant row.
- With blank current author-response inputs, only safe blocked-state documents/handoff/status are changed.
- With valid confirmed input later, only eligible `AUTH_*`/`DECL_*` values are written to their planned destinations, preserving exact author-confirmed text.
- All applied fields are traceable to response/validation/plan artifacts.
- All out-of-scope categories remain untouched.
- Placeholder-mode preflight is documented; strict preflight remains truthfully FAIL until later phases close all other categories.
- Commit only allowed files and push.

## Commit Message
`docs: apply confirmed authorship and declarations conditionally`

## Completion / Blocker Rule
Run only after the Trigger Gate is met. Otherwise write the blocked-state report and stop. Never use this task to infer missing facts or to close submission blockers without documentary evidence.