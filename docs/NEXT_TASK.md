# Current Task

## Title
Phase 7F — Author Figure Review Intake and Fig. 6 Panel Inventory

## Goal
Prepare a clear author-review packet for the three local, non-final Fig. 3–5 candidates; make the Fig. 1–2 schematic decisions explicit; and perform a local-only inventory of real Fig. 6 validation panels referenced by the existing qualitative manifest. This task organizes review evidence and decisions. It must not approve assets on the authors’ behalf, generate final figures, insert figures into LaTeX, or change research evidence.

## Read First
1. `AGENTS.md` if it exists.
2. `docs/PROJECT_CONTEXT.md`
3. `docs/EXPERIMENT_STATUS.md`
4. `runs/handoff_latest.md`
5. `runs/phase4b_report.md`
6. `runs/phase7b_publication_state_reconciliation.md`
7. `runs/phase7c_table_insertion_report.md`
8. `runs/phase7d_figure_source_lock_report.md`
9. `runs/phase7e_candidate_render_report.md`
10. `docs/TASK_BLOCKER.md`
11. `submission/sivp/README.md`
12. `submission/sivp/tex/ra_repdet_sivp.tex`
13. `submission/sivp/figures/FINAL_ASSET_INSERTION_MAP.md`
14. `submission/sivp/figures/FIGURE_SOURCE_TRACEABILITY.md`
15. `submission/sivp/figures/FIGURE_BUILD_SPEC.md`
16. `submission/sivp/figures/FIGURE_CANDIDATE_RENDER_MANIFEST.md`
17. `submission/sivp/review/FIGURE_CANDIDATE_CHECK.md`
18. `submission/sivp/review/FIGURE_CANDIDATE_RENDER_CHECK.md`
19. `submission/sivp/metadata/FINAL_SUBMISSION_INPUT_LEDGER.md`
20. `runs/clean_qualitative_manifest.csv`
21. `submission/sivp/figures/figure_candidate_build.py`
22. `scripts/preflight_submission.py`
23. `rarepdet/tools/generate_handoff.py`
24. `rarepdet/tools/update_project_status.py`

## Frozen Assets
- Remote branch: `research/ra-repdet-triair`.
- Official manuscript headline: **R4 Reliability p=0.20** on `block64_guard16_seed0`, controlled seeds `0` and `2`.
- Publication headline means: F1@0.50 `0.920861`, AP50 `0.962495`, AP75 `0.891266`, w/o RGB AP50 `0.916051`, w/o Thermal AP50 `0.718277`, and w/o Event AP50 `0.961577`.
- Phase 4B decision: `SELECT R4 AS CLEAN-SPLIT MAIN VARIANT`.
- Fig. 3–5 local candidates exist only under `runs/local_candidate_figures/phase7e/`, are Git-ignored, visibly marked `CANDIDATE — NOT FINAL`, and are not publication assets.
- Fig. 3–5 source hashes remain those validated in Phase 7D and Phase 7E.
- Fig. 1–2 require author-approved schematic/Visio design sources. Fig. 6 requires verified local real validation panels and author-approved panel selection.
- The six figure placeholders in `submission/sivp/tex/ra_repdet_sivp.tex` remain intentional until final approved assets exist.
- Strict V18 preflight remains blocked by final figures and author-provided metadata/governance/release/environment information.

## Allowed Files To Modify
- `docs/NEXT_TASK.md`
- `docs/EXPERIMENT_STATUS.md`
- `docs/TASK_BLOCKER.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`
- `runs/phase7f_author_review_intake_report.md`
- `runs/phase7f_author_review_intake_report.json`
- `submission/sivp/review/AUTHOR_FIGURE_REVIEW_PACKET.md`
- `submission/sivp/review/AUTHOR_FIGURE_REVIEW_DECISIONS.csv`
- `submission/sivp/review/FIGURE6_PANEL_REVIEW_TEMPLATE.md`
- `submission/sivp/review/FIGURE6_PANEL_REVIEW_TEMPLATE.csv`
- `submission/sivp/review/FIGURE6_PANEL_INVENTORY_CHECK.md`
- `submission/sivp/review/FIGURE6_PANEL_INVENTORY_CHECK.csv`
- `submission/sivp/figures/qualitative_panel_inventory.py`
- `rarepdet/tools/generate_handoff.py`
- `rarepdet/tools/update_project_status.py`

## Local Outputs Required but Never Committed
Create only under:

```text
runs/local_candidate_figures/phase7f/
```

Required local-only output:

```text
fig6_panel_inventory.json
```

This local JSON may include absolute panel paths needed for local verification. It must remain ignored and untracked. Do not copy local absolute paths or local panel filenames into public committed reports.

## Forbidden Files To Modify
- All training, model, dataset, loss, evaluation, data-loading, and split-generation files.
- All raw `.npy` data, labels, checkpoints, weights, source evidence CSVs, source figure CSVs, local qualitative panels, rendered candidate PDFs, final figure assets, and final PDFs.
- `.gitignore`, unless an existing ignore rule does not already cover `runs/local_candidate_figures/`; do not weaken any ignore rule.
- `submission/sivp/tex/ra_repdet_sivp.tex`; do not replace figure placeholders or add `\includegraphics` calls.
- `submission/sivp/figures/FINAL_ASSET_INSERTION_MAP.md` and `submission/sivp/figures/FIGURE_SOURCE_TRACEABILITY.*`; no figure readiness status becomes final in this task.
- Do not generate, alter, copy, rename, or commit any candidate or final Fig. 1–6 PDF/image.
- Do not fabricate author approval, local-panel verification, captions, author information, citations, data terms, release details, or numerical evidence.
- Do not run training, GPU inference, metric recomputation, split mutation, source-data mutation, or LaTeX compilation.

## Required Commands
Start with safe context and source checks:

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git status --short
python scripts/preflight_submission.py --root . --allow-placeholders
python submission/sivp/figures/figure_candidate_build.py --dry-run --root .
```

If `git pull --ff-only` cannot proceed because of genuine local/remote divergence, do not use `--allow-unrelated-histories`, reset, force push, or rewrite history. Record the blocker in `docs/TASK_BLOCKER.md`, commit only safe partial outputs if possible, and stop.

Then run only a local inventory:

```powershell
python submission/sivp/figures/qualitative_panel_inventory.py --dry-run --root . --output runs/local_candidate_figures/phase7f/fig6_panel_inventory.json
```

After producing committed review templates and local inventory, run:

```powershell
git check-ignore -v runs/local_candidate_figures/phase7f/fig6_panel_inventory.json
python rarepdet/tools/generate_handoff.py
python rarepdet/tools/update_project_status.py
python scripts/preflight_submission.py --root . --allow-placeholders
python scripts/preflight_submission.py --root .
powershell -ExecutionPolicy Bypass -File rarepdet/tools/finish_task.ps1
```

The strict preflight is expected to remain FAIL. Do not run a PDF compilation.

## Required Outputs

### 1. Author figure review packet
Create `submission/sivp/review/AUTHOR_FIGURE_REVIEW_PACKET.md`. It must be concise, author-facing, and use only verified repository facts.

It must include:

- A one-paragraph scope statement: this is a review packet, not final approval and not a formal submission package.
- For **Fig. 3**, **Fig. 4**, and **Fig. 5**:
  - the exact local candidate filename/path relative to project root;
  - source CSV path and SHA256;
  - the locked caption and what is shown;
  - reviewer checklist items: correctness, legibility at full width, axis/legend clarity, no unintended implication of significance, and approve/revise decision;
  - a clear statement that candidates are marked `CANDIDATE — NOT FINAL` and must not be copied into final asset paths before written approval.
- For **Fig. 1** and **Fig. 2**:
  - exact schematic content checklist from `FIGURE_BUILD_SPEC.md`;
  - decision options limited to: `provide external source`, `approve a future implementation from checklist`, `revise checklist`, or `defer`.
- For **Fig. 6**:
  - explain that only real local validation panels from the manifest are eligible;
  - state that panel selection, cropping/redaction, and final composition require author review;
  - include no raw local path, image preview, or fabricated panel selection.
- A direct link/reference to `submission/sivp/metadata/FINAL_SUBMISSION_INPUT_LEDGER.md` for non-figure remaining inputs.

### 2. Author decision templates
Create `submission/sivp/review/AUTHOR_FIGURE_REVIEW_DECISIONS.csv` and an accompanying readable Markdown table in the packet. Each figure must have one row with these fields:

```text
figure_id, current_state, candidate_or_source_location, author_decision, author_comments, approval_date, approver_identity, final_asset_authorized, notes
```

Default values must be empty or explicitly `pending author review`. Do not prefill any approval, identity, date, or final authorization.

Create `submission/sivp/review/FIGURE6_PANEL_REVIEW_TEMPLATE.md` and `.csv` with fields:

```text
review_slot, manifest_row_id, sample_identifier, panel_category, local_panel_verified, crop_or_redaction_needed, author_decision, comments, approval_date, approver_identity
```

Populate only the safe metadata already contained in the qualitative manifest, such as a row ID, sample identifier, category, and rank when present. Do not write local absolute paths, raw image file names, or image contents into committed files. Every approval/decision-related field must be `pending author review` or empty.

### 3. Local Fig. 6 inventory tool
Create `submission/sivp/figures/qualitative_panel_inventory.py`.

Requirements:

- Accept exactly `--dry-run`, `--root`, and `--output`.
- Read the existing qualitative manifest; discover the actual manifest schema instead of hard-coding unverified column names.
- Resolve local panel paths only for local verification. Never print full absolute paths to stdout, committed markdown, or committed CSV files.
- Verify, without modifying or rendering, how many manifest rows have an addressable local panel path and how many existing files are present. Do not open images, regenerate detections, or write image files.
- Write exactly one local JSON file to the user-supplied output path. The JSON may contain local absolute paths, existence booleans, and per-row diagnostics because it is ignored/untracked.
- Print a privacy-safe summary only: manifest row count, count with candidate path metadata, count of existing panel files, count missing/unverifiable, and output file location relative to project root.
- Reject output paths outside `runs/local_candidate_figures/` and reject output paths not ignored by Git.
- Do not import model/training code or open a GPU context.

### 4. Committed Fig. 6 inventory summary
Create `submission/sivp/review/FIGURE6_PANEL_INVENTORY_CHECK.md` and `.csv` containing only aggregate, non-sensitive results:

- manifest path and SHA256;
- manifest row count;
- identified safe metadata columns used for review template;
- count of rows with path metadata;
- count of locally existing panels;
- count missing/unverifiable;
- whether any image content was opened (`must be no`);
- whether any local path or panel filename was committed (`must be no`);
- status: `ready for author selection`, `partial local inventory`, or `blocked`.

Do not mark Fig. 6 final or selected. Do not choose panels automatically.

### 5. Report, status, and blocker
Create `runs/phase7f_author_review_intake_report.md` and matching JSON containing:

- local candidate Fig. 3–5 review readiness;
- figure-review packet and decision-template locations;
- Fig. 6 aggregate local-inventory result;
- author decisions required for Fig. 1–6;
- remaining ledger categories outside figures;
- explicit confirmation that no figure asset, candidate PDF, final PDF, source CSV, model, metric, dataset, split, panel image, or LaTeX body changed.

Update `docs/TASK_BLOCKER.md` to reflect that the review packet exists but author decisions and final approved Fig. 1–6 assets are still required. Do not remove any final-figure or metadata blocker.

Refresh `runs/handoff_latest.md` and `.json` and `docs/EXPERIMENT_STATUS.md`. The clean blocked-split R4 headline remains first; E0–E6 remain historical/exploratory. Do not present a review packet, candidate PDF, or panel inventory as a final publication asset.

## Acceptance Criteria
- The author review packet and all four review template/check files exist with no fabricated approvals.
- Fig. 3–5 local candidates remain only local, ignored, untracked, and explicitly non-final.
- `qualitative_panel_inventory.py --dry-run` produces exactly one ignored local JSON inventory and no image/PDF output.
- Committed Fig. 6 inventory files contain no local absolute paths, raw panel filenames, or image contents.
- Fig. 1–2 remain author-design dependencies; Fig. 6 remains pending author selection; no figure placeholder is replaced.
- Placeholder-mode preflight is executed and documented. Strict preflight remains truthfully FAIL because author decisions, final figure assets, and external metadata remain unresolved.
- No training, GPU inference, numerical evaluation, split mutation, source-data mutation, source CSV modification, candidate/final figure generation, or LaTeX compilation occurs.
- `runs/handoff_latest.md` records the final commit SHA, changed files, command outcomes, review-intake state, and residual blockers.
- Commit only allowed code/documentation files and push the branch.

## Commit Message
`docs: add author figure review intake and panel inventory`

## Completion / Blocker Rule
Complete the review-intake and inventory task, refresh handoff/status, commit only the allowed code and documents, and push. If the manifest does not expose a safe way to perform local path verification, document the aggregate limitation in the committed inventory check and keep Fig. 6 blocked. Do not fabricate panel availability, approve candidate figures, insert assets, or claim submission readiness.