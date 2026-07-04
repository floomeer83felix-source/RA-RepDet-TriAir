# Current Task

## Title
Phase 7G — Expanded Submission Ledger, Author Intake, and Static Audit Batch

## Goal
Complete a larger batch of **non-experimental, evidence-preserving submission-readiness tasks** in one pass:

1. reconcile the canonical submission ledger with completed table insertion;
2. create a fillable author-input package for remaining external facts and approvals;
3. audit static SIVP source consistency, citations, labels, table/figure crosswalks, and reproducibility closure requirements;
4. produce a clear dependency-ordered closure roadmap.

This task is documentation and static validation only. It must not alter experiments, metrics, model code, source data, manuscript claims, final TeX content, figure assets, or publication metadata.

## Read First
- `AGENTS.md` if it exists.
- `docs/PROJECT_CONTEXT.md`
- `docs/EXPERIMENT_STATUS.md`
- `runs/handoff_latest.md`
- `runs/phase4b_report.md`
- `runs/phase7b_publication_state_reconciliation.md`
- `runs/phase7c_table_insertion_report.md`
- `runs/phase7d_figure_source_lock_report.md`
- `runs/phase7e_candidate_render_report.md`
- `runs/phase7f_author_review_intake_report.md`
- `docs/TASK_BLOCKER.md`
- `submission/sivp/metadata/FINAL_SUBMISSION_INPUT_LEDGER.md`
- `submission/sivp/review/FINAL_SUBMISSION_INPUT_LEDGER.csv`
- `submission/sivp/review/TABLE_RENDERING_CHECK.md`
- `submission/sivp/tables/TABLE_SOURCE_TRACEABILITY.md`
- `submission/sivp/review/AUTHOR_FIGURE_REVIEW_PACKET.md`
- `submission/sivp/review/AUTHOR_FIGURE_REVIEW_DECISIONS.csv`
- `submission/sivp/review/FIGURE6_PANEL_INVENTORY_CHECK.md`
- `submission/sivp/figures/FIGURE_SOURCE_TRACEABILITY.md`
- `submission/sivp/figures/FINAL_ASSET_INSERTION_MAP.md`
- `submission/sivp/tex/main.tex`
- `submission/sivp/tex/ra_repdet_sivp.tex`
- `submission/sivp/tex/references.bib`
- `main.tex`
- `main_sivp_snjnl.tex`
- `scripts/preflight_submission.py`
- `rarepdet/tools/generate_handoff.py`
- `rarepdet/tools/update_project_status.py`

## Frozen Facts
- The official manuscript headline is **R4 Reliability p=0.20** on `block64_guard16_seed0`, controlled seeds `0` and `2`.
- Publication headline means: F1@0.50 `0.920861`, AP50 `0.962495`, AP75 `0.891266`, w/o RGB AP50 `0.916051`, w/o Thermal AP50 `0.718277`, w/o Event AP50 `0.961577`.
- Phase 4B decision: `SELECT R4 AS CLEAN-SPLIT MAIN VARIANT`.
- Phase 7C completed evidence-locked insertion of Tables 1–7. The SIVP body has zero `TABLE PLACEHOLDER` strings, every table fragment is traceable to an unchanged source CSV, and strict preflight no longer has a table-placeholder failure.
- Phase 7E Fig. 3–5 PDFs are local, ignored, visibly non-final candidates only. Phase 7F confirmed that 20/20 Fig. 6 manifest entries have locally existing panels, but author selection and final composition remain pending.
- Fig. 1–2 remain author-design/Visio dependencies. The six figure placeholders remain intentional until final approved assets exist.
- Any unresolved external field must remain `missing — author confirmation required`, `pending author review`, or another equally explicit pending state.

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
- `submission/sivp/metadata/SUBMISSION_CLOSURE_ROADMAP.md`
- `submission/sivp/review/SUBMISSION_INPUT_COMPLETENESS_CHECK.md`
- `submission/sivp/review/SUBMISSION_INPUT_COMPLETENESS_CHECK.csv`
- `submission/sivp/review/STATIC_SUBMISSION_SOURCE_AUDIT.md`
- `submission/sivp/review/STATIC_SUBMISSION_SOURCE_AUDIT.csv`
- `submission/sivp/review/FIGURE_TABLE_CROSSWALK.md`
- `submission/sivp/review/FIGURE_TABLE_CROSSWALK.csv`
- `submission/sivp/review/REPRODUCIBILITY_CLOSURE_AUDIT.md`
- `submission/sivp/review/REPRODUCIBILITY_CLOSURE_AUDIT.csv`
- `submission/sivp/review/static_submission_audit.py`
- `rarepdet/tools/generate_handoff.py`
- `rarepdet/tools/update_project_status.py`

## Forbidden Files To Modify
- All training, model, dataset, loss, evaluation, data-loading, and split-generation files.
- All source evidence CSVs, raw data, labels, checkpoints, weights, candidate/final figure files, local qualitative panel files, table fragments, manuscript body TeX, final PDFs, and prior experimental outputs.
- Do not modify `submission/sivp/tex/ra_repdet_sivp.tex`, `main.tex`, or `main_sivp_snjnl.tex` in this task.
- Do not add or infer author identities, affiliations, emails, ORCIDs, funding, declarations, data licences, citations, access terms, release URLs, tags, commit hashes, archive dates, DOI values, hardware facts, or approvals.
- Do not approve candidates, choose Fig. 6 panels, remove figure blockers, run training, run inference, recompute metrics, mutate data, or run LaTeX compilation.
- Do not weaken `scripts/preflight_submission.py` or edit strict placeholder rules.

## Required Commands
Start with safe verification:

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git status --short
python scripts/preflight_submission.py --root . --allow-placeholders
```

If `git pull --ff-only` cannot proceed because of genuine local/remote divergence, do not use `--allow-unrelated-histories`, reset, force push, or rewrite history. Record the blocker in `docs/TASK_BLOCKER.md`, commit only safe partial outputs if possible, and stop.

Run the static audit only after implementing it:

```powershell
python submission/sivp/review/static_submission_audit.py --root . --output-prefix submission/sivp/review/static_submission_source_audit
```

Then run:

```powershell
python rarepdet/tools/generate_handoff.py
python rarepdet/tools/update_project_status.py
python scripts/preflight_submission.py --root . --allow-placeholders
python scripts/preflight_submission.py --root .
powershell -ExecutionPolicy Bypass -File rarepdet/tools/finish_task.ps1
```

Strict preflight is expected to remain FAIL. Do not weaken the validator or claim a final-submission PASS.

## Required Work

### A. Canonical submission-ledger reconciliation
Update `FINAL_SUBMISSION_INPUT_LEDGER.md` and its CSV counterpart so `TAB_001` reflects Phase 7C completion:

- Current state: `complete — evidence-locked Tables 1–7 inserted in Phase 7C`.
- Evidence: `runs/phase7c_table_insertion_report.md`, `submission/sivp/tables/TABLE_SOURCE_TRACEABILITY.md`, and `submission/sivp/review/TABLE_RENDERING_CHECK.md`.
- Strict-preflight effect: table-placeholder failure is resolved; only non-table blockers remain.
- Action to close: `none for table placeholders; final visual compile review remains pending under TEX_001`.

Recompute status/handoff open-item counts so tables are not listed as an open `table_asset` blocker. Preserve Phase 7B provenance and add a factual Phase 7G reconciliation note.

### B. Fillable author-submission intake package
Create `submission/sivp/metadata/AUTHOR_SUBMISSION_INPUT_PACKET.md` with a clear opening statement that it is a fillable intake packet, not a completed submission form, and no field may be completed by inference.

Organize remaining unresolved facts and approvals into these sections:

1. Publication authorship and corresponding contact.
2. Funding, acknowledgments, contributions, competing interests, and AI-use disclosure.
3. TriAir citation, version/provider, licence, access terms, and redistribution restrictions.
4. Code/archive/release decision: public URL or explicit no-release policy, release tag, immutable source identifier, archive date, licence, DOI if any.
5. Figure decisions: Fig. 1–2 design decision, Fig. 3–5 candidate approve/revise decision, Fig. 6 panel-selection/composition decision. Reference existing figure-review files; do not repeat panel identifiers or local paths.
6. Claim scope: validation-only wording approval versus a future independent held-out-evidence decision.
7. Final training/evaluation environment record.
8. Final Springer `sn-jnl` compile owner/readiness.

For each item provide: exact response requested, destination files after confirmation, `Current status: pending author confirmation`, and a brief caution where publisher/provider terms must be respected.

Create `AUTHOR_SUBMISSION_INPUT_RESPONSES.csv` with one row per unresolved ledger item, excluding resolved `TAB_001`, using:

```text
item_id,category,exact_required_input,current_status,author_response,confirmed_by,confirmation_date,source_of_confirmation,repository_destination,validation_rule,notes
```

All response and confirmation fields must be blank. Do not prefill factual content.

### C. Environment record template
Create `submission/sivp/metadata/ENVIRONMENT_RECORD_TEMPLATE.md` with fields for:

- training hardware: GPU model/count/memory, CPU, RAM;
- OS;
- Python;
- PyTorch/Torchvision;
- CUDA/cuDNN;
- key package versions;
- training image size, batch size, seed list, epoch count;
- profiling protocol: batch size, warmup, timed iterations, repeats;
- person confirming the record and date.

Only prepopulate values directly documented in repository evidence, including image size `640`, controlled seeds `0, 2`, and 50 epochs where supported by the existing clean-split report. Leave machine-specific facts blank.

### D. Static submission-source audit
Create `submission/sivp/review/static_submission_audit.py`. It must be CPU-only, read-only with respect to source TeX/Bib/CSV files, and must not import model or training code.

It must inspect these static conditions and output matching Markdown and CSV reports:

1. Required source-entry files exist: root `main.tex`, `main_sivp_snjnl.tex`, SIVP main/body TeX, and `references.bib`.
2. All `\input{...}` table references from the SIVP body resolve to existing files; count should be seven.
3. The SIVP body has zero `TABLE PLACEHOLDER` strings and exactly six intentional `Final artwork pending` figure placeholders.
4. All `\label{...}` values in the SIVP body are unique.
5. All `\cite{...}` keys used in the SIVP body exist in `references.bib`; report unused BibTeX keys as warning only.
6. Table labels and figure labels listed in the body have a matching source/status row in the table/figure traceability documentation when applicable.
7. Static checks must not interpret a placeholder-mode preflight PASS as formal submission readiness.
8. Do not modify TeX, BibTeX, tables, figures, or figures placeholders.

The script must accept `--root` and `--output-prefix`, write only the requested Markdown/CSV reports, and exit nonzero for missing required source files, broken table inputs, duplicate labels, or missing cited BibTeX keys. It may emit warnings for intentional figure placeholders, unused BibTeX keys, and unavailable final compile dependencies.

### E. Figure/table crosswalk
Create `FIGURE_TABLE_CROSSWALK.md` and CSV. Include every Table 1–7 and Fig. 1–6 with:

```text
asset_id,asset_type,caption_or_purpose,manuscript_label,source_or_traceability_path,current_state,final_asset_required,author_action_required,strict_preflight_effect,notes
```

Facts required:

- Tables 1–7: evidence-locked and inserted; final visual compile review remains pending.
- Fig. 1–2: author-design required.
- Fig. 3–5: local non-final candidate available; author review required; final PDF absent.
- Fig. 6: local panel inventory complete; author selection/composition required; final PDF absent.

Do not call any asset final or approved.

### F. Reproducibility closure audit
Create `REPRODUCIBILITY_CLOSURE_AUDIT.md` and CSV. Audit only repository-documentable state:

- canonical clean split and R4 headline provenance;
- source locations for the frozen split protocol, controlled-seed report, table traceability, figure traceability, and local candidate rules;
- whether raw data, checkpoints, or local candidate PDFs are tracked in Git according to repository inspection;
- which release/metadata facts remain author-owned;
- whether a final environment record is present or pending;
- whether final compilation is possible now or blocked.

Use statuses `pass`, `warning`, `blocker`, and `pending author confirmation`. Do not claim data/code release readiness or an archive DOI.

### G. Submission-closure roadmap
Create `submission/sivp/metadata/SUBMISSION_CLOSURE_ROADMAP.md` with a dependency-ordered sequence:

1. author responses and metadata confirmation;
2. figure decisions and final approved Fig. 1–6 assets;
3. final release/data-governance decision;
4. environment confirmation;
5. strict preflight;
6. final Springer `sn-jnl` compile;
7. author visual review of tables/final figures;
8. final archive/release tag/immutable source record;
9. formal submission handoff.

For every step include inputs, owner category, verification action, and block-if-missing condition. Do not add dates or promise completion timing.

### H. Completeness check and report
Create `SUBMISSION_INPUT_COMPLETENESS_CHECK.md` and CSV containing:

- canonical ledger total count;
- resolved count and unresolved count by category;
- explicit `TAB_001` resolved state;
- number of response-template rows;
- check that no response-only field was prefilled;
- check that no unresolved item was silently removed;
- static-audit outcome;
- strict-preflight expected outcome and remaining blocker categories;
- status `ready for author intake` unless a consistency error exists.

Create `runs/phase7g_submission_intake_report.md` and matching JSON containing:

- ledger inconsistency corrected;
- counts before/after reconciliation;
- package, template, environment-record, static-audit, crosswalk, reproducibility-audit, and roadmap locations;
- confirmation that no author facts or assets were invented, generated, approved, or inserted;
- remaining strict-preflight blockers.

Update `docs/TASK_BLOCKER.md` to remove only the obsolete table-placeholder/table-asset blocker. Retain all figure, author/metadata, data-governance, release/archive, claim-scope, environment, and compile-readiness blockers.

Refresh `runs/handoff_latest.md` / `.json` and `docs/EXPERIMENT_STATUS.md`. R4 on the frozen blocked split must remain first; E0–E6 remain historical/exploratory. Do not describe the intake package or audit outputs as formal submission readiness.

## Acceptance Criteria
- `TAB_001` is resolved in both ledger formats and no generated status/handoff calls it an open table blocker.
- The author-response CSV includes every unresolved ledger item, excludes resolved `TAB_001`, and contains no fabricated factual response.
- The intake packet routes every item to a destination and defers figure approvals to the existing review files.
- Environment template prepopulates only repository-documented experimental facts; system-specific fields remain blank.
- Static audit passes required structural checks or reports clear blockers without modifying source TeX/Bib files.
- Crosswalk contains all 13 manuscript assets; no figure is mislabeled as final.
- Reproducibility audit distinguishes verified repository facts from author-owned release/environment requirements.
- Completeness check reconciles totals and open categories accurately.
- Placeholder-mode preflight is executed and documented. Strict preflight remains truthfully FAIL because figures and external author-provided facts remain unresolved.
- No manuscript TeX, experiment, model, dataset, metric, source CSV, candidate/final asset, or final PDF changes.
- No training, GPU inference, evaluation, source-data mutation, or LaTeX compilation occurs.
- Commit only allowed files and push.

## Commit Message
`docs: expand submission audit and author intake package`

## Completion Rule
Complete the full documentation/static-audit batch, refresh handoff/status, commit only allowed files, and push. If any audit result cannot be reconciled without guessing, record the discrepancy in `docs/TASK_BLOCKER.md`, commit safe partial outputs, and stop. Do not claim formal submission readiness.