# Current Task

## Title
Phase 7I — Confirmation-Gated Submission Update Planning

## Goal
Create a CPU-only, report-only planner that converts the Phase 7H validation results into an auditable *future update plan*. The planner must state which confirmed inputs could eventually be applied, which destination files would be affected, and which external checks still block application. It must never edit manuscript TeX, metadata destinations, references, release manifests, figure assets, or the author-response template.

## Read First
1. `AGENTS.md` if it exists.
2. `docs/PROJECT_CONTEXT.md`
3. `docs/EXPERIMENT_STATUS.md`
4. `runs/handoff_latest.md`
5. `runs/phase7g_submission_intake_report.md`
6. `runs/phase7h_author_response_validation_report.md`
7. `docs/TASK_BLOCKER.md`
8. `docs/UPCOMING_TASKS.md`
9. `submission/sivp/metadata/FINAL_SUBMISSION_INPUT_LEDGER.md`
10. `submission/sivp/review/FINAL_SUBMISSION_INPUT_LEDGER.csv`
11. `submission/sivp/metadata/AUTHOR_SUBMISSION_INPUT_RESPONSES.csv`
12. `submission/sivp/metadata/AUTHOR_RESPONSE_VALIDATION.md`
13. `submission/sivp/metadata/AUTHOR_RESPONSE_VALIDATION.csv`
14. `submission/sivp/metadata/METADATA_APPLICATION_READINESS_MAP.md`
15. `submission/sivp/review/AUTHOR_RESPONSE_GATE_CHECK.md`
16. `submission/sivp/review/AUTHOR_FIGURE_REVIEW_DECISIONS.csv`
17. `submission/sivp/review/FIGURE6_PANEL_REVIEW_TEMPLATE.csv`
18. `submission/sivp/metadata/SUBMISSION_CLOSURE_ROADMAP.md`
19. `scripts/preflight_submission.py`
20. `rarepdet/tools/generate_handoff.py`
21. `rarepdet/tools/update_project_status.py`

## Frozen Assets
- Remote branch: `research/ra-repdet-triair`.
- Official manuscript headline: **R4 Reliability p=0.20** on `block64_guard16_seed0`, controlled seeds `0` and `2`.
- Phase 7C Tables 1–7 are complete and evidence-locked. `TAB_001` is resolved and excluded from author-response requirements.
- Phase 7H validates 29 unresolved response rows. In the current template all 29 are `pending_author_response`; zero rows are structurally ready.
- Fig. 3–5 candidates remain local, ignored, and non-final. Fig. 1–2 need author design decisions; Fig. 6 needs author panel selection/composition approval.
- Strict preflight remains blocked until all real author/external facts and final approved figure assets are available.

## Allowed Files To Modify
- `docs/NEXT_TASK.md`
- `docs/UPCOMING_TASKS.md`
- `docs/EXPERIMENT_STATUS.md`
- `docs/TASK_BLOCKER.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`
- `runs/phase7i_update_planning_report.md`
- `runs/phase7i_update_planning_report.json`
- `submission/sivp/metadata/plan_confirmed_submission_updates.py`
- `submission/sivp/metadata/CONFIRMED_UPDATE_PLAN.md`
- `submission/sivp/metadata/CONFIRMED_UPDATE_PLAN.csv`
- `submission/sivp/metadata/CONFIRMED_UPDATE_PLAN.json`
- `submission/sivp/review/CONFIRMED_UPDATE_PLAN_CHECK.md`
- `submission/sivp/review/CONFIRMED_UPDATE_PLAN_CHECK.csv`
- `rarepdet/tools/generate_handoff.py`
- `rarepdet/tools/update_project_status.py`

## Forbidden Files To Modify
- `submission/sivp/metadata/AUTHOR_SUBMISSION_INPUT_RESPONSES.csv`.
- `submission/sivp/review/AUTHOR_FIGURE_REVIEW_DECISIONS.csv` and `submission/sivp/review/FIGURE6_PANEL_REVIEW_TEMPLATE.csv`.
- All manuscript TeX including `main.tex`, `main_sivp_snjnl.tex`, and `submission/sivp/tex/**`.
- All references/BibTeX files, metadata destination files, release/archive manifests, figure files, local panels, table fragments, source CSVs, raw data, checkpoints, and final PDFs.
- All model, training, dataset, loss, evaluation, and split-generation files.
- Do not add or infer author names, affiliations, email addresses, ORCIDs, declarations, data citations, licences, URLs, tags, archive dates, DOI values, environment details, approval states, or figure selections.
- Do not create an `--apply`, `--write`, or any automatic source-modification mode in the planner.
- Do not run training, inference, evaluation, data mutation, metric recomputation, network access, or LaTeX compilation.

## Required Commands
Start with safe checks:

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git status --short
python scripts/preflight_submission.py --root . --allow-placeholders
python submission/sivp/metadata/validate_author_submission_inputs.py --root . --responses submission/sivp/metadata/AUTHOR_SUBMISSION_INPUT_RESPONSES.csv --ledger submission/sivp/review/FINAL_SUBMISSION_INPUT_LEDGER.csv --output-prefix submission/sivp/metadata/author_response_validation
```

If `git pull --ff-only` cannot proceed because of genuine local/remote divergence, do not reset, force push, rewrite history, or merge unrelated histories. Document the blocker in `docs/TASK_BLOCKER.md`, commit only safe partial diagnostics if possible, and stop.

Run the new planner:

```powershell
python submission/sivp/metadata/plan_confirmed_submission_updates.py --root . --responses submission/sivp/metadata/AUTHOR_SUBMISSION_INPUT_RESPONSES.csv --validation submission/sivp/metadata/AUTHOR_RESPONSE_VALIDATION.csv --ledger submission/sivp/review/FINAL_SUBMISSION_INPUT_LEDGER.csv --figure-decisions submission/sivp/review/AUTHOR_FIGURE_REVIEW_DECISIONS.csv --figure6-template submission/sivp/review/FIGURE6_PANEL_REVIEW_TEMPLATE.csv --output-prefix submission/sivp/metadata/confirmed_update_plan
```

Then run:

```powershell
python rarepdet/tools/generate_handoff.py
python rarepdet/tools/update_project_status.py
python scripts/preflight_submission.py --root . --allow-placeholders
python scripts/preflight_submission.py --root .
powershell -ExecutionPolicy Bypass -File rarepdet/tools/finish_task.ps1
```

Strict preflight is expected to remain FAIL. Never equate a successful plan report with confirmed metadata, final figures, or submission readiness.

## Required Outputs

### 1. Report-only update planner
Create `submission/sivp/metadata/plan_confirmed_submission_updates.py`.

It must accept exactly:

```text
--root
--responses
--validation
--ledger
--figure-decisions
--figure6-template
--output-prefix
```

It must:

- Read all listed inputs without modifying them.
- Link each unresolved ledger item to exactly one response row and one Phase 7H validation row.
- Emit one plan row per unresolved item with these fields:

```text
item_id,category,validation_state,plan_state,author_confirmation_complete,external_verification_required,future_destination_files,future_application_scope,blocking_conditions,required_evidence,next_safe_action,notes
```

- Use only these plan states:
  - `pending_author_response`
  - `awaiting_confirmation_metadata`
  - `awaiting_external_verification`
  - `awaiting_figure_decision`
  - `eligible_for_future_guarded_application`
  - `not_applicable_in_current_phase`

- Determine `author_confirmation_complete=yes` only when the response has nonblank `author_response`, `confirmed_by`, `confirmation_date`, and `source_of_confirmation`, and the validation row is `structurally_ready_for_future_apply`.
- Preserve a stricter second gate for data governance, release/archive, figure assets, environment, and compile readiness: regardless of response format, those items must be `awaiting_external_verification` unless their required external confirmation/asset evidence is recorded in the response and validation data. Do not independently assert that any evidence is genuine.
- Treat Fig. 1–6 rows as `awaiting_figure_decision` unless their corresponding figure-decision data is explicitly nonblank, author-confirmed, and contains no pending state. For Fig. 6, do not inspect or expose local panel paths; only use decision-template completion state.
- Never produce `eligible_for_future_guarded_application` for the current blank template.
- Write only the requested Markdown/CSV/JSON plan outputs.
- Exit nonzero only on structural linkage errors: missing required columns, duplicate item IDs, unknown IDs, unresolved ledger items absent from validation/response data, or count mismatches. All-pending current input must exit zero.

### 2. Plan reports
Create:

- `submission/sivp/metadata/CONFIRMED_UPDATE_PLAN.md`
- `submission/sivp/metadata/CONFIRMED_UPDATE_PLAN.csv`
- `submission/sivp/metadata/CONFIRMED_UPDATE_PLAN.json`

They must report:

- canonical ledger total/resolved/unresolved counts;
- plan-state counts by category;
- zero eligible-for-application rows for the current blank template;
- destination-file groups without copying any author response into those destinations;
- explicit separation between a future application plan and actual application;
- a category-level sequence for future application: authorship/declarations, data/release facts, figure workflow, claim scope, environment, strict preflight, compile.

### 3. Plan gate review check
Create:

- `submission/sivp/review/CONFIRMED_UPDATE_PLAN_CHECK.md`
- `submission/sivp/review/CONFIRMED_UPDATE_PLAN_CHECK.csv`

Check and report:

- 30 ledger rows, with `TAB_001` resolved;
- 29 response/validation/plan rows with one-to-one linkage;
- no unknown IDs or duplicates;
- zero eligible rows for the current blank template;
- zero response-template edits;
- zero TeX/metadata-destination/figure/release-manifest edits;
- no figure decision or Fig. 6 selection inferred;
- expected strict-preflight result remains FAIL.

### 4. Update the forward queue
Update `docs/UPCOMING_TASKS.md` so the conditional stages after Phase 7I are clear and non-overlapping:

- **Phase 7J — Apply Confirmed Authorship and Declarations**: only after validation and planning identify eligible author/declaration rows.
- **Phase 7K — Apply Confirmed Data Governance and Release Facts**: only after rows are author-confirmed and externally verified.
- **Phase 7L — Final Figure Workflow**: only after author decisions and approved final Fig. 1–6 assets are available.
- **Phase 7M — Environment and Reproducibility Closure**: only after a confirmed environment record is supplied.
- **Phase 7N — Strict Preflight Closure Check**: only after all external blockers are closed.
- **Phase 7O — Springer `sn-jnl` Compile Dry Run**: only after strict preflight passes.
- **Phase 7P — Final Submission Bundle Assembly**: only after compile review and author final approval.
- **Phase 8A — Optional Post-Submission Research Continuation**: isolated from submitted evidence.

### 5. Report, blocker, and handoff
Create `runs/phase7i_update_planning_report.md` and matching JSON with:

- planner command outcome;
- counts by plan state and category;
- confirmation that current blank responses produce zero eligible rows;
- confirmation that no source destination was edited;
- remaining strict-preflight blockers;
- exact next author action: complete the response template plus figure decision files, with confirmation metadata and external evidence where required.

Update `docs/TASK_BLOCKER.md` to state that a dry-run application plan exists but no unresolved category is closed until confirmed values, approvals, and external evidence are present.

Refresh handoff/status. Keep R4 clean blocked-split evidence first and old E0–E6 language historical/exploratory only.

## Acceptance Criteria
- Planner is report-only and does not expose an apply/write mode.
- Planner passes on current blank inputs with 29 plan rows and zero eligible-for-application rows.
- `TAB_001` remains resolved and absent from the plan’s unresolved work.
- Every plan row has a valid ledger/response/validation link and lists future destinations without modifying them.
- Figure rows retain author-decision gates; Fig. 6 exposes no local panel paths or filenames.
- No response, decision, TeX, metadata destination, figure asset, release/archive manifest, source CSV, raw data, model, metric, or final PDF is modified.
- Placeholder-mode preflight is documented. Strict preflight remains truthfully FAIL on external facts/final assets.
- Commit only allowed code/documentation files and push.

## Commit Message
docs: add confirmation-gated update planner

## Completion / Blocker Rule
Complete the report-only planner, refresh handoff/status, commit, and push. Stop after planning. Do not apply responses, final assets, or publication metadata and do not claim submission readiness.
