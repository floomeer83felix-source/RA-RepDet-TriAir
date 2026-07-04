# Current Task

## Title
Phase 7D — Candidate Figure Source Lock and Build Specification

## Goal
Prepare a reproducible, evidence-locked build specification for the six SIVP figures without generating, committing, or inserting final figure files. The task must distinguish figures that can be built from frozen project evidence (Fig. 3–5), the qualitative-panel dependency (Fig. 6), and figures that require author-approved visual design or Visio source (Fig. 1–2).

## Read First
1. `AGENTS.md` if it exists.
2. `docs/PROJECT_CONTEXT.md`
3. `docs/EXPERIMENT_STATUS.md`
4. `runs/handoff_latest.md`
5. `runs/phase4b_report.md`
6. `runs/phase7b_publication_state_reconciliation.md`
7. `runs/phase7c_table_insertion_report.md`
8. `docs/TASK_BLOCKER.md`
9. `submission/sivp/README.md`
10. `submission/sivp/tex/main.tex`
11. `submission/sivp/tex/ra_repdet_sivp.tex`
12. `submission/sivp/figures/FINAL_ASSET_INSERTION_MAP.md`
13. `manuscript/figures/fig3_controlled_ablation_source.csv`
14. `manuscript/figures/fig4_missing_modality_source.csv`
15. `manuscript/figures/fig5_reliability_weight_source.csv`
16. `runs/clean_qualitative_manifest.csv` if present, otherwise the manifest path documented by the repository.
17. `runs/phase3c_report.md`
18. `runs/clean_block64g16_protocol.md`
19. `rarepdet/models/reliability_fusion_fcos.py`
20. `scripts/preflight_submission.py`
21. `rarepdet/tools/generate_handoff.py`
22. `rarepdet/tools/update_project_status.py`

## Frozen Assets
- Remote branch: `research/ra-repdet-triair`.
- Official manuscript headline: **R4 Reliability p=0.20** on `block64_guard16_seed0`, controlled seeds `0` and `2`.
- Publication headline means: F1@0.50 `0.920861`, AP50 `0.962495`, AP75 `0.891266`, w/o RGB AP50 `0.916051`, w/o Thermal AP50 `0.718277`, w/o Event AP50 `0.961577`.
- Phase 4B decision: `SELECT R4 AS CLEAN-SPLIT MAIN VARIANT`.
- Fig. 3, Fig. 4, and Fig. 5 use only the three named frozen CSV sources.
- Fig. 6 requires the existing local real validation panels described by the qualitative manifest; no synthetic or regenerated detections may be substituted.
- Fig. 1 and Fig. 2 remain author-design / Visio-dependent assets and cannot be presented as final without author approval.
- Phase 7C table assets are complete and evidence-locked; table evidence must not be modified in this task.
- Strict V18 preflight remains blocked by author metadata, TriAir governance facts, release metadata, final figures, environment record, and final compile readiness.

## Allowed Files To Modify
- `docs/NEXT_TASK.md`
- `docs/EXPERIMENT_STATUS.md`
- `docs/TASK_BLOCKER.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`
- `runs/phase7d_figure_source_lock_report.md`
- `runs/phase7d_figure_source_lock_report.json`
- `submission/sivp/figures/FINAL_ASSET_INSERTION_MAP.md`
- `submission/sivp/figures/FIGURE_SOURCE_TRACEABILITY.md`
- `submission/sivp/figures/FIGURE_SOURCE_TRACEABILITY.csv`
- `submission/sivp/figures/FIGURE_BUILD_SPEC.md`
- `submission/sivp/figures/figure_candidate_build.py`
- `submission/sivp/review/FIGURE_CANDIDATE_CHECK.md`
- `submission/sivp/review/FIGURE_CANDIDATE_CHECK.csv`
- `rarepdet/tools/generate_handoff.py`
- `rarepdet/tools/update_project_status.py`

## Forbidden Files To Modify
- All training, model, dataset, loss, primary AP-evaluation, data-loading, and split-generation source files.
- All raw `.npy` data, labels, checkpoints, weights, source evidence CSV files, qualitative source images, rendered final figures, final PDFs, and prior experimental outputs.
- `submission/sivp/tex/ra_repdet_sivp.tex` and all figure placeholder text: do not insert any figure asset in this task.
- Do not generate or commit `Fig1_overall_architecture.pdf`, `Fig2_leakage_aware_protocol.pdf`, `Fig3_controlled_ablation.pdf`, `Fig4_missing_modality_robustness.pdf`, `Fig5_reliability_weight_audit.pdf`, `Fig6_qualitative_results.pdf`, or any image/PDF candidate output.
- Do not fabricate author approval, architecture artwork, data terms, figure panels, detections, citations, DOIs, or numerical evidence.
- Do not run training, model inference, GPU evaluation, metric computation, split mutation, or source-data mutation.

## Required Commands
Run only safe inspection and source-lock checks. Start with:

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git status --short
python scripts/preflight_submission.py --root . --allow-placeholders
```

If `git pull --ff-only` cannot proceed because of local/remote divergence, do not use `--allow-unrelated-histories`, reset, force push, or rewrite history. Record the blocker in `docs/TASK_BLOCKER.md`, commit only safe partial outputs if possible, and stop.

After creating the specification and script, run only a CPU-safe dry run:

```powershell
python submission/sivp/figures/figure_candidate_build.py --dry-run --root .
python rarepdet/tools/generate_handoff.py
python rarepdet/tools/update_project_status.py
python scripts/preflight_submission.py --root . --allow-placeholders
python scripts/preflight_submission.py --root .
powershell -ExecutionPolicy Bypass -File rarepdet/tools/finish_task.ps1
```

The figure script must not write any PDF, PNG, SVG, JPG, or other rendered artwork in `--dry-run` mode. Do not run it without `--dry-run` during this task.

## Required Outputs

### 1. Figure traceability ledger
Create:

- `submission/sivp/figures/FIGURE_SOURCE_TRACEABILITY.md`
- `submission/sivp/figures/FIGURE_SOURCE_TRACEABILITY.csv`

Each figure (1–6) must have these fields:

```text
figure_id, target_filename, intended_caption, source_type, frozen_source_paths, source_commit_or_hash, source_row_or_asset_count, allowed_build_method, author_approval_required, current_state, strict_preflight_effect, closure_action, notes
```

Required classifications:

- Fig. 1: architecture schematic; source is the reliability-fusion model and method text; `author_approval_required=yes`; `current_state=author-design required`.
- Fig. 2: leakage-aware protocol schematic; source is Phase 3C and clean split protocol; `author_approval_required=yes`; `current_state=author-design required`.
- Fig. 3: controlled clean-split ablation; source is exactly `manuscript/figures/fig3_controlled_ablation_source.csv`; `author_approval_required=yes` before it is called final; `current_state=candidate build spec ready`.
- Fig. 4: missing-modality robustness; source is exactly `manuscript/figures/fig4_missing_modality_source.csv`; `author_approval_required=yes` before it is called final; `current_state=candidate build spec ready`.
- Fig. 5: reliability-weight audit; source is exactly `manuscript/figures/fig5_reliability_weight_source.csv`; `author_approval_required=yes` before it is called final; `current_state=candidate build spec ready`.
- Fig. 6: qualitative panels; source is the existing qualitative manifest and local real validation panels; `author_approval_required=yes`; `current_state=local-panel inventory required`.

Do not describe candidate readiness as final artwork or final asset approval.

### 2. Reproducible candidate-build script
Create `submission/sivp/figures/figure_candidate_build.py` with the following behavior:

- It has a mandatory `--dry-run` option and a `--root` option.
- Under `--dry-run`, it must read and validate only the three frozen Fig. 3–5 CSV sources, report their exact headers, row counts, numerical-token counts, and target candidate filenames, then exit without rendering or writing image/PDF/SVG files.
- It must include three documented future build plans, one each for Fig. 3–5, using only those CSVs. State plot type, x-axis/grouping, y-axis/units, legend entries, error-bar policy, required caption text, and source-to-panel mapping.
- It must state that a future non-dry run may only write local, untracked candidate files named `*_candidate.*` into a user-provided output directory outside the Git-tracked final asset path. Do not implement final asset generation in this task.
- It must not import project training modules or open a GPU context.
- It must fail clearly if a source CSV is missing, unreadable, or changes expected structure.
- It must write no files during dry run.

### 3. Figure build specification
Create `submission/sivp/figures/FIGURE_BUILD_SPEC.md` specifying, for each figure:

- exact target dimensions: full-width, 174 mm, as reserved in the insertion map;
- caption and manuscript label to preserve;
- source provenance;
- what may be automated versus what requires author approval;
- visual integrity rules: no data interpolation, no redrawing detection outputs, no synthetic qualitative panels, no unstated statistical error bars, no visual manipulation that changes interpretation;
- Fig. 3–5 specific candidate plot plans based only on their source CSVs;
- Fig. 6 local panel selection and redaction/integrity requirements;
- Fig. 1–2 author-provided schematic checklist;
- explicit non-final watermark/filename policy for any future local candidate render.

### 4. Candidate review check
Create:

- `submission/sivp/review/FIGURE_CANDIDATE_CHECK.md`
- `submission/sivp/review/FIGURE_CANDIDATE_CHECK.csv`

Record checks for:

- all six figures have one traceability row;
- Fig. 3–5 source CSV paths, headers, row counts, and numerical-token counts are verified by the dry-run script;
- Fig. 1–2 are not represented as approved/final;
- Fig. 6 is not represented as generated without real local panels;
- no final `Fig1`–`Fig6` PDF assets exist or are added by this task;
- no image/PDF artifact was written by `--dry-run`;
- the SIVP body still contains figure placeholders, as expected;
- strict preflight remains expected to fail on figures and external author/metadata inputs.

### 5. Status, blocker, and report
Update `submission/sivp/figures/FINAL_ASSET_INSERTION_MAP.md` only to add factual readiness states from the traceability ledger; retain `final artwork pending` for every figure until approved assets exist.

Create `runs/phase7d_figure_source_lock_report.md` and matching JSON with:

- inspected sources and provenance;
- dry-run result;
- all figure readiness states;
- a concise author action list for Fig. 1–2 and Fig. 6;
- a concise future local candidate-render procedure for Fig. 3–5;
- confirmation that no figures or PDFs were generated, committed, or inserted;
- remaining strict-preflight blockers.

Update `docs/TASK_BLOCKER.md` to add the figure readiness detail while keeping all genuine strict-preflight blockers. Do not remove the figure blocker merely because candidate specifications exist.

Refresh `runs/handoff_latest.md` and `.json` and `docs/EXPERIMENT_STATUS.md`. The R4 clean blocked-split publication headline must remain first; old E0–E6 wording must remain historical/exploratory.

## Acceptance Criteria
- Six figure traceability rows exist with correct source classification and explicit approval state.
- `figure_candidate_build.py --dry-run --root .` passes on the local repository and writes no image/PDF/SVG output.
- Fig. 3–5 candidate plans are bound only to their named frozen CSV sources.
- Fig. 1–2 and Fig. 6 are not misrepresented as generated or final.
- No final figure assets, candidate artwork, images, PDFs, models, metrics, data, source evidence, or LaTeX body placeholders are modified.
- Placeholder-mode preflight is executed and recorded. Strict preflight remains truthfully FAIL because figures and external facts are unresolved.
- No training, GPU inference, numerical evaluation, split mutation, source-data mutation, or core model/dataset/evaluation change occurs.
- `runs/handoff_latest.md` records the final commit SHA, changed files, command outcomes, and remaining blockers.
- Commit all permitted outputs and push the branch.

## Commit Message
`docs: lock figure sources and candidate build spec`

## Completion / Blocker Rule
Complete the source-lock and build-specification task, refresh handoff/status, commit, and push. If a figure source is absent or inconsistent, write the exact issue in `docs/TASK_BLOCKER.md`, commit the traceability findings, and stop. Do not generate candidate artwork, replace figure placeholders, or claim final submission readiness.