# Current Task

## Title
Phase 7H — Author-Response Validation Gate and Application Readiness

## Goal
Build a safe, report-only validation gate for the 29 unresolved author-input rows created in Phase 7G. The gate must identify which supplied responses are structurally ready to apply, which are incomplete, and which require external verification. It must not write author facts, figures, release values, or metadata into any manuscript or submission source file.

## Why This Task Exists
Phase 7G reconciled the table ledger and created blank response templates. The next reliable step is to validate incoming author responses before any future task applies them to TeX, metadata, references, archive manifests, or final assets. This prevents an accidental conversion of partial or unverified information into publication facts.

## Read First
- `AGENTS.md` if it exists.
- `docs/PROJECT_CONTEXT.md`
- `docs/EXPERIMENT_STATUS.md`
- `runs/handoff_latest.md`
- `runs/phase7g_submission_intake_report.md`
- `docs/TASK_BLOCKER.md`
- `docs/UPCOMING_TASKS.md`
- `submission/sivp/metadata/FINAL_SUBMISSION_INPUT_LEDGER.md`
- `submission/sivp/review/FINAL_SUBMISSION_INPUT_LEDGER.csv`
- `submission/sivp/metadata/AUTHOR_SUBMISSION_INPUT_PACKET.md`
- `submission/sivp/metadata/AUTHOR_SUBMISSION_INPUT_RESPONSES.csv`
- `submission/sivp/metadata/ENVIRONMENT_RECORD_TEMPLATE.md`
- `submission/sivp/review/SUBMISSION_INPUT_COMPLETENESS_CHECK.md`
- `submission/sivp/review/AUTHOR_FIGURE_REVIEW_DECISIONS.csv`
- `submission/sivp/review/FIGURE6_PANEL_REVIEW_TEMPLATE.csv`
- `submission/sivp/metadata/SUBMISSION_CLOSURE_ROADMAP.md`
- `scripts/preflight_submission.py`
- `rarepdet/tools/generate_handoff.py`
- `rarepdet/tools/update_project_status.py`

## Frozen Facts
- Official manuscript headline: **R4 Reliability p=0.20** on `block64_guard16_seed0`, controlled seeds `0` and `2`.
- Phase 7C Tables 1–7 are complete and evidence-locked. `TAB_001` is resolved and must not reappear as an open table blocker.
- Phase 7G has 30 canonical ledger items: 1 resolved and 29 unresolved author/external-input items.
- The response template contains blank author-response/confirmation fields by design. Blank rows are pending, not confirmed.
- Fig. 3–5 candidates are local, ignored, and non-final. Fig. 1–2 require author-design decisions; Fig. 6 needs author panel selection. No figure decision is presumed approved.
- Strict preflight must remain FAIL until every required external fact and final approved asset is genuinely available.

## Allowed Files To Modify
- `docs/NEXT_TASK.md`
- `docs/UPCOMING_TASKS.md`
- `docs/EXPERIMENT_STATUS.md`
- `docs/TASK_BLOCKER.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`
- `runs/phase7h_author_response_validation_report.md`
- `runs/phase7h_author_response_validation_report.json`
- `submission/sivp/metadata/validate_author_submission_inputs.py`
- `submission/sivp/metadata/AUTHOR_RESPONSE_VALIDATION.md`
- `submission/sivp/metadata/AUTHOR_RESPONSE_VALIDATION.csv`
- `submission/sivp/metadata/METADATA_APPLICATION_READINESS_MAP.md`
- `submission/sivp/metadata/METADATA_APPLICATION_READINESS_MAP.csv`
- `submission/sivp/review/AUTHOR_RESPONSE_GATE_CHECK.md`
- `submission/sivp/review/AUTHOR_RESPONSE_GATE_CHECK.csv`
- `rarepdet/tools/generate_handoff.py`
- `rarepdet/tools/update_project_status.py`

## Forbidden Files To Modify
- `submission/sivp/metadata/AUTHOR_SUBMISSION_INPUT_RESPONSES.csv`: do not populate or alter author responses in this task.
- `submission/sivp/review/AUTHOR_FIGURE_REVIEW_DECISIONS.csv` and `FIGURE6_PANEL_REVIEW_TEMPLATE.csv`: do not populate approvals or selections.
- All manuscript TeX (`main.tex`, `main_sivp_snjnl.tex`, `submission/sivp/tex/**`).
- All model, training, dataset, evaluation, loss, split, or data-loading files.
- All source evidence CSVs, raw data, labels, weights, checkpoints, candidate/final figures, local panels, release/archive manifests, references, and final PDFs.
- Do not create or infer author identities, affiliations, emails, ORCIDs, funding, declarations, dataset citations, licences, release URLs, tags, commit hashes, archive dates, DOIs, hardware information, approvals, or figure selections.
- Do not modify strict preflight rules, run training/inference/evaluation, mutate data, or run LaTeX compilation.

## Required Commands
Start with repository and template verification:

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git status --short
python scripts/preflight_submission.py --root . --allow-placeholders
```

If the fast-forward pull cannot proceed, do not rewrite history, force push, reset, or merge unrelated histories. Record the blocker and stop.

Then run the new validator in report-only mode:

```powershell
python submission/sivp/metadata/validate_author_submission_inputs.py --root . --responses submission/sivp/metadata/AUTHOR_SUBMISSION_INPUT_RESPONSES.csv --ledger submission/sivp/review/FINAL_SUBMISSION_INPUT_LEDGER.csv --output-prefix submission/sivp/metadata/author_response_validation
```

Then run:

```powershell
python rarepdet/tools/generate_handoff.py
python rarepdet/tools/update_project_status.py
python scripts/preflight_submission.py --root . --allow-placeholders
python scripts/preflight_submission.py --root .
powershell -ExecutionPolicy Bypass -File rarepdet/tools/finish_task.ps1
```

Strict preflight is expected to remain FAIL. Do not claim that a structural validation PASS is a formal submission PASS.

## Required Work

### 1. Report-only response validator
Create `submission/sivp/metadata/validate_author_submission_inputs.py`.

It must:

- Accept `--root`, `--responses`, `--ledger`, and `--output-prefix`.
- Read the Phase 7G response CSV and canonical ledger CSV without modifying either.
- Validate that every unresolved ledger `item_id` appears exactly once in the response CSV, while resolved `TAB_001` does not appear as a response requirement.
- Classify every row into one of: `pending_author_response`, `response_present_needs_confirmation`, `structurally_ready_for_future_apply`, `invalid_or_incomplete`, or `external_verification_required`.
- Treat blank `author_response`, `confirmed_by`, `confirmation_date`, or `source_of_confirmation` fields as pending/incomplete—not confirmed.
- Perform only conservative structural checks. Examples:
  - date field, when present, must use `YYYY-MM-DD`;
  - email field, when present, must have a basic email shape;
  - ORCID, when supplied, must have a basic ORCID-style shape;
  - DOI, URL, release tag, and citation fields may be checked for nonblank/format shape only, never independently asserted true;
  - approval fields require a nonblank confirmer, confirmation date, and source-of-confirmation before being classified ready.
- Never download external resources, query release services, inspect private data, or validate facts against the internet.
- Never write to the response CSV, ledger, TeX, reference files, metadata manifests, or figure-decision files.
- Write only its requested Markdown/CSV report outputs plus an optional JSON summary next to the output prefix.
- Exit nonzero only on structural integrity errors such as missing required columns, duplicate item IDs, response items absent from ledger, or ledger unresolved items missing from the response template. It must exit zero when all entries are simply blank/pending.

### 2. Validation report and readiness map
Create:

- `submission/sivp/metadata/AUTHOR_RESPONSE_VALIDATION.md`
- `submission/sivp/metadata/AUTHOR_RESPONSE_VALIDATION.csv`
- `submission/sivp/metadata/METADATA_APPLICATION_READINESS_MAP.md`
- `submission/sivp/metadata/METADATA_APPLICATION_READINESS_MAP.csv`

These must include:

- ledger total, resolved count, unresolved count, template response-row count;
- classification counts by category and readiness state;
- every unresolved item ID with status and the minimum missing fields needed for advancement;
- the exact repository destinations that a future *application task* may update only after the row is structurally ready and author-confirmed;
- a distinction between structurally ready and externally verified: e.g., a well-formed TriAir licence response still may need provider verification, and a well-formed release URL still may need release-owner confirmation;
- a clear statement that the report does not modify or confirm any factual submission value.

### 3. Gate review check
Create:

- `submission/sivp/review/AUTHOR_RESPONSE_GATE_CHECK.md`
- `submission/sivp/review/AUTHOR_RESPONSE_GATE_CHECK.csv`

Include checks for:

- canonical ledger has 30 rows, with `TAB_001` resolved;
- response template has exactly 29 rows and excludes `TAB_001`;
- no unknown or duplicate response item ID;
- no response-only field was auto-filled by this task;
- no author fact, approval, asset, source CSV, TeX file, figure file, or manifest changed;
- validator execution outcome;
- expected strict-preflight state.

### 4. Queue and workflow update
Update `docs/UPCOMING_TASKS.md` so the next stages after this validation gate are explicit:

- Phase 7I — Conditional Application of Confirmed Author Metadata and Declarations.
- Phase 7J — Conditional Application of Confirmed Data Governance and Release/Archive Facts.
- Phase 7K — Conditional Final Figure Asset Workflow after author decisions.
- Phase 7L — Environment Record and Reproducibility Metadata Closure.
- Phase 7M — Strict Preflight Closure Check.
- Phase 7N — Springer `sn-jnl` Compile Dry Run.
- Phase 7O — Final Submission Bundle Assembly.
- Phase 8A — Optional post-submission research continuation.

For each queued stage, include trigger, allowed scope, and a statement that it cannot run until the preceding external confirmations/approvals are available.

### 5. Report, blocker, and handoff
Create `runs/phase7h_author_response_validation_report.md` and matching JSON containing:

- validator behavior and command outcome;
- ledger/template counts and response readiness counts;
- any structural integrity error;
- no-application/no-inference confirmation;
- remaining strict-preflight blockers;
- a concise list of what authors must provide next.

Update `docs/TASK_BLOCKER.md` to say that the response-validation gate exists but no unresolved author fact or final figure blocker is closed until confirmed values and approvals are supplied.

Refresh handoff/status. Maintain the R4 clean blocked-split headline first and historical-only E0–E6 language.

## Acceptance Criteria
- Validator is CPU-only, report-only, and does not edit the response template or any submission/manuscript source.
- With the current blank template, validator exits successfully, reports 29 pending items, and does not classify any factual item as author-confirmed.
- All template/ledger linkage checks pass; `TAB_001` remains resolved and absent from unresolved-response requirements.
- The readiness map identifies destinations without copying any facts into those destinations.
- Queue is updated with dependency-ordered conditional tasks.
- Placeholder-mode preflight is recorded; strict preflight remains truthfully FAIL on external facts/final assets.
- No training, inference, evaluation, data mutation, metric change, source CSV change, figure generation, asset insertion, TeX update, or final PDF compile occurs.
- Commit only allowed code/documentation files and push.

## Commit Message
`docs: add author response validation gate`

## Completion Rule
Complete the report-only validation gate, refresh handoff/status, commit, and push. Stop after reporting readiness. Do not apply any response or claim formal submission readiness.