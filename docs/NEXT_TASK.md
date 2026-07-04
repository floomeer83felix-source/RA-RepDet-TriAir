# Current Task

## Title
Phase 7E — Local Non-Final Candidate Renders for Fig. 3–5

## Goal
Create reproducible, local-only candidate renders for the three quantitative figures whose sources are frozen and validated: Fig. 3, Fig. 4, and Fig. 5. These outputs are strictly for author review. They must be visibly marked **CANDIDATE — NOT FINAL**, remain untracked, and must not be inserted into the SIVP LaTeX body or treated as approved publication assets.

## Read First
1. `AGENTS.md` if it exists.
2. `docs/PROJECT_CONTEXT.md`
3. `docs/EXPERIMENT_STATUS.md`
4. `runs/handoff_latest.md`
5. `runs/phase4b_report.md`
6. `runs/phase7b_publication_state_reconciliation.md`
7. `runs/phase7c_table_insertion_report.md`
8. `runs/phase7d_figure_source_lock_report.md`
9. `docs/TASK_BLOCKER.md`
10. `submission/sivp/README.md`
11. `submission/sivp/tex/ra_repdet_sivp.tex`
12. `submission/sivp/figures/FINAL_ASSET_INSERTION_MAP.md`
13. `submission/sivp/figures/FIGURE_SOURCE_TRACEABILITY.md`
14. `submission/sivp/figures/FIGURE_BUILD_SPEC.md`
15. `submission/sivp/review/FIGURE_CANDIDATE_CHECK.md`
16. `submission/sivp/figures/figure_candidate_build.py`
17. `manuscript/figures/fig3_controlled_ablation_source.csv`
18. `manuscript/figures/fig4_missing_modality_source.csv`
19. `manuscript/figures/fig5_reliability_weight_source.csv`
20. `scripts/preflight_submission.py`
21. `rarepdet/tools/generate_handoff.py`
22. `rarepdet/tools/update_project_status.py`

## Frozen Assets
- Remote branch: `research/ra-repdet-triair`.
- Official manuscript headline: **R4 Reliability p=0.20** on `block64_guard16_seed0`, controlled seeds `0` and `2`.
- Publication headline means: F1@0.50 `0.920861`, AP50 `0.962495`, AP75 `0.891266`, w/o RGB AP50 `0.916051`, w/o Thermal AP50 `0.718277`, and w/o Event AP50 `0.961577`.
- Phase 4B decision: `SELECT R4 AS CLEAN-SPLIT MAIN VARIANT`.
- Fig. 3 source is exactly `manuscript/figures/fig3_controlled_ablation_source.csv` with Phase 7D SHA256 `23e2984adac08ebd6584e1c8d56f82d3cdd0dfb9e5e32047d5064481076d21dc`.
- Fig. 4 source is exactly `manuscript/figures/fig4_missing_modality_source.csv` with Phase 7D SHA256 `aea82341ac37547ece40428e56bd3d98fabf299304a4b24067a7705eaf642fde`.
- Fig. 5 source is exactly `manuscript/figures/fig5_reliability_weight_source.csv` with Phase 7D SHA256 `ef93dca475e9a1fa704856952951fbe47ebb701c9e559ea60abf46d861a1239c`.
- Fig. 1–2 remain author-design / Visio-style dependencies. Fig. 6 remains dependent on verified local real validation panels. Do not work on Fig. 1, Fig. 2, or Fig. 6 in this task.
- The manuscript figure placeholders remain intentional until approved final assets exist.
- Candidate artwork is not final artwork, not a submission asset, and not author-approved.

## Allowed Files To Modify
- `.gitignore` only to add an exact ignore rule for `runs/local_candidate_figures/` if it is not already ignored.
- `docs/NEXT_TASK.md`
- `docs/EXPERIMENT_STATUS.md`
- `docs/TASK_BLOCKER.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`
- `runs/phase7e_candidate_render_report.md`
- `runs/phase7e_candidate_render_report.json`
- `submission/sivp/figures/figure_candidate_build.py`
- `submission/sivp/figures/FIGURE_BUILD_SPEC.md`
- `submission/sivp/figures/FIGURE_CANDIDATE_RENDER_MANIFEST.md`
- `submission/sivp/figures/FIGURE_CANDIDATE_RENDER_MANIFEST.csv`
- `submission/sivp/review/FIGURE_CANDIDATE_RENDER_CHECK.md`
- `submission/sivp/review/FIGURE_CANDIDATE_RENDER_CHECK.csv`
- `rarepdet/tools/generate_handoff.py`
- `rarepdet/tools/update_project_status.py`

## Local Outputs Required but Never Committed
Create only under this local directory:

```text
runs/local_candidate_figures/phase7e/
```

Required local-only files:

```text
Fig3_controlled_ablation_candidate.pdf
Fig4_missing_modality_robustness_candidate.pdf
Fig5_reliability_weight_audit_candidate.pdf
candidate_render_manifest.json
```

These files must remain untracked and ignored. They must not be copied or renamed into `submission/sivp/figures/`, `figures/`, `manuscript/figures/`, or any final-asset directory.

## Forbidden Files To Modify
- All training, model, dataset, loss, primary AP-evaluation, data-loading, and split-generation files.
- All raw `.npy` data, labels, checkpoints, weights, source evidence CSVs, source figure CSVs, qualitative panels, rendered final figure assets, final PDFs, and prior experiment outputs.
- `submission/sivp/tex/ra_repdet_sivp.tex`; do not replace any figure placeholder or add any `\includegraphics` call.
- `submission/sivp/figures/FINAL_ASSET_INSERTION_MAP.md` and `submission/sivp/figures/FIGURE_SOURCE_TRACEABILITY.*`; this task does not change final-asset readiness.
- Do not generate Fig. 1, Fig. 2, Fig. 6, any final `Fig1`–`Fig6` PDF, or a final compiled manuscript PDF.
- Do not fabricate author approval, confidence intervals, statistical significance, interpolation, model outputs, qualitative detections, citations, data-governance facts, release URLs, licences, or DOIs.
- Do not run training, GPU inference, metric recomputation, split mutation, or source-data mutation.

## Required Commands
Run only local candidate-render work. Start with:

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git status --short
python scripts/preflight_submission.py --root . --allow-placeholders
python submission/sivp/figures/figure_candidate_build.py --dry-run --root .
```

If `git pull --ff-only` cannot proceed because of genuine local/remote divergence, do not use `--allow-unrelated-histories`, reset, force push, or rewrite history. Record the blocker in `docs/TASK_BLOCKER.md`, commit only safe partial outputs if possible, and stop.

After validating source hashes, run exactly:

```powershell
python submission/sivp/figures/figure_candidate_build.py --render-candidates --root . --output-dir runs/local_candidate_figures/phase7e
```

Then run:

```powershell
python submission/sivp/figures/figure_candidate_build.py --dry-run --root .
git check-ignore -v runs/local_candidate_figures/phase7e/Fig3_controlled_ablation_candidate.pdf
git check-ignore -v runs/local_candidate_figures/phase7e/Fig4_missing_modality_robustness_candidate.pdf
git check-ignore -v runs/local_candidate_figures/phase7e/Fig5_reliability_weight_audit_candidate.pdf
python rarepdet/tools/generate_handoff.py
python rarepdet/tools/update_project_status.py
python scripts/preflight_submission.py --root . --allow-placeholders
python scripts/preflight_submission.py --root .
powershell -ExecutionPolicy Bypass -File rarepdet/tools/finish_task.ps1
```

Do not run a LaTeX compilation in this task. The strict preflight is expected to remain FAIL.

## Required Outputs

### 1. Extend the candidate builder safely
Extend `submission/sivp/figures/figure_candidate_build.py` to support exactly two mutually exclusive modes:

```text
--dry-run
--render-candidates --output-dir <path>
```

Requirements:

- Both modes must validate the same three frozen Fig. 3–5 CSV sources using the existing expected headers, row counts, numerical-token counts, and SHA256 checks.
- `--render-candidates` must reject output directories that resolve inside `submission/sivp/figures/`, `figures/`, `manuscript/figures/`, or any final-asset directory.
- It must require an output directory under `runs/local_candidate_figures/` and fail if the path is not ignored by Git after the `.gitignore` update.
- It must produce exactly the three required PDF files and one JSON manifest named above. Do not write PNG/JPG/SVG/EPS files unless separately approved in a later task.
- Every candidate PDF must include a prominent visible text watermark: `CANDIDATE — NOT FINAL`.
- Each generated PDF must embed or visibly state the exact source CSV relative path and its SHA256.
- The JSON manifest must record: build timestamp, command arguments, source paths, hashes, headers, row counts, numeric-token counts, Python and matplotlib versions, generated candidate filenames, and a literal `final_asset_status: not_final` field.
- The script must not import training code or open a GPU context.
- It must fail clearly and write no partial final-looking file if validation fails. Use a temporary filename and atomic rename for each PDF where practical.

### 2. Required candidate plot designs
Follow the locked build specification exactly and preserve every source row.

**Fig. 3 — Controlled clean-split ablation**
- One full-width candidate PDF with three labeled panels: `(a) F1@0.50`, `(b) AP50`, `(c) AP75`.
- X-axis: `R0 Early Fusion`, `R1 Reliability p=0.00`, `R2 Reliability p=0.15`, `R4 Reliability p=0.20`.
- Show both seed 0 and seed 2 as distinct overlaid points for every metric/variant.
- A two-seed mean may be shown only if explicitly labeled `mean of seeds 0 and 2`.
- Do not draw error bars, confidence intervals, p-values, or significance marks.
- Use only CSV values; do not use text copied from reports as data.

**Fig. 4 — Missing-modality robustness**
- One full-width candidate PDF showing all 18 source rows exactly once.
- X-axis groups: `w/o RGB`, `w/o Thermal`, `w/o Event`.
- Variant grouping: R1, R2, R4; show seed 0 and seed 2 as distinct overlaid points.
- Y-axis: AP50, with a visible scale appropriate to the data and an explicit `AP50` label.
- Do not hide the thermal-removal weakness; do not use statistical error bars or inferred confidence intervals.

**Fig. 5 — Reliability-weight audit**
- One full-width candidate PDF showing all eight source rows exactly once.
- X-axis: input mode `full`, `no_rgb`, `no_thermal`, `no_event`; use a two-panel layout, one panel per seed.
- Show `alpha_rgb`, `alpha_thermal`, and `alpha_event` means as grouped bars or points.
- Use the provided `alpha_*_std` values only as explicitly labeled `± std` variability bars; do not infer confidence intervals or significance.
- Retain the condition labels and do not interpret alpha as physical causal importance.

Use simple publication-legible styling, clear axis labels, a readable legend, and the specified 174 mm full-width intention. Do not rely on custom fonts or download external assets.

### 3. Candidate render manifest and integrity check
Create:

- `submission/sivp/figures/FIGURE_CANDIDATE_RENDER_MANIFEST.md`
- `submission/sivp/figures/FIGURE_CANDIDATE_RENDER_MANIFEST.csv`
- `submission/sivp/review/FIGURE_CANDIDATE_RENDER_CHECK.md`
- `submission/sivp/review/FIGURE_CANDIDATE_RENDER_CHECK.csv`

The manifest must distinguish:

- source-lock documentation committed to Git;
- candidate render specifications committed to Git;
- candidate PDF/JSON files that were generated locally but intentionally not committed;
- final assets that remain missing and author approval requirements.

The integrity check must record:

- all three source SHA256 values matched Phase 7D;
- each expected candidate PDF exists locally and is nonzero;
- each candidate filename ends `_candidate.pdf`;
- the JSON manifest marks every asset `not_final`;
- all candidate paths are ignored by Git and absent from `git status --short`;
- no final `Fig1`–`Fig6` PDF exists or was created;
- the SIVP LaTeX body still has all six figure placeholders;
- Fig. 1–2 and Fig. 6 remain unresolved;
- strict preflight remains expected to fail on figures and external author/metadata inputs.

### 4. Report, status, and blocker
Create `runs/phase7e_candidate_render_report.md` and matching JSON including:

- exact source hashes and validation results;
- candidate file paths, byte sizes, and local-only status;
- visual-design conformance checks for the three PDFs;
- confirmation that source CSVs, metrics, models, datasets, splits, final assets, LaTeX body, and final PDFs were unchanged;
- remaining strict-preflight blockers;
- explicit statement that candidates await author review and are not publication assets.

Update `docs/TASK_BLOCKER.md` to record that Fig. 3–5 local candidates exist only for review. Keep the final-figure blocker open until all Fig. 1–6 final approved PDFs exist and are verified.

Refresh `runs/handoff_latest.md` and `.json` and `docs/EXPERIMENT_STATUS.md`. The clean blocked-split R4 headline must remain first; E0–E6 remain historical/exploratory. Do not present local candidates as completed final assets.

## Acceptance Criteria
- `figure_candidate_build.py --dry-run --root .` passes before and after rendering.
- `--render-candidates` creates exactly three local-only candidate PDFs and one local JSON manifest under `runs/local_candidate_figures/phase7e/`.
- All candidates are visibly marked `CANDIDATE — NOT FINAL` and include source path/hash provenance.
- Fig. 3 shows every 8-row source record through the seed-point representation; Fig. 4 shows every 18-row record; Fig. 5 shows every 8-row record.
- All candidate outputs are ignored by Git, absent from `git status --short`, and are not committed.
- No final Fig. 1–6 asset, LaTeX body placeholder, final PDF, source CSV, metric, model, dataset, split, source data, checkpoint, or evaluation output changes.
- Placeholder-mode preflight is executed and documented. Strict preflight remains truthfully FAIL due to final figures and external author/metadata requirements.
- `runs/handoff_latest.md` records the final commit SHA, changed files, command outcomes, candidate review status, and residual blockers.
- Commit only the allowed code/documentation files and push the branch.

## Commit Message
`docs: add local candidate renders for figures 3-5`

## Completion / Blocker Rule
Complete the non-final local candidate-render task, refresh handoff/status, commit only the allowed code and documents, and push. If rendering cannot be completed without source mismatch, unignored output, a final-asset-path violation, or an ambiguous visualization choice, write the exact blocker in `docs/TASK_BLOCKER.md`, commit the safe diagnostics, and stop. Do not insert candidates into the manuscript or claim final submission readiness.