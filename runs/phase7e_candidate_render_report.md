# Phase 7E Candidate Render Report

Generated: 2026-07-04
Workspace: `E:\RepViT-main`
Baseline commit inspected: `a37e81e5249dca722178c6b1a9ee3697bf8b3038`

## Summary

- Created local-only, non-final candidate renders for Fig. 3, Fig. 4, and Fig. 5 under `runs/local_candidate_figures/phase7e/`.
- The candidates are for author review only, visibly marked `CANDIDATE — NOT FINAL`, and include source path plus SHA256 provenance.
- The local PDFs and local JSON manifest are ignored by Git and intentionally untracked.
- No final figure asset was created, copied, renamed, inserted, or committed.
- Fig. 1, Fig. 2, and Fig. 6 remain unresolved and out of scope for this render task.

## Source Validation

| Figure | Source | SHA256 | Headers | Rows | Numerical tokens | Status |
| --- | --- | --- | --- | ---: | ---: | --- |
| Fig. 3 | `manuscript/figures/fig3_controlled_ablation_source.csv` | `23e2984adac08ebd6584e1c8d56f82d3cdd0dfb9e5e32047d5064481076d21dc` | `Variant`, `Seed`, `F1`, `AP50`, `AP75` | 8 | 40 | pass |
| Fig. 4 | `manuscript/figures/fig4_missing_modality_source.csv` | `aea82341ac37547ece40428e56bd3d98fabf299304a4b24067a7705eaf642fde` | `Variant`, `Seed`, `Condition`, `AP50` | 18 | 55 | pass |
| Fig. 5 | `manuscript/figures/fig5_reliability_weight_source.csv` | `ef93dca475e9a1fa704856952951fbe47ebb701c9e559ea60abf46d861a1239c` | `Seed`, `Mode`, `alpha_rgb_mean`, `alpha_thermal_mean`, `alpha_event_mean`, `alpha_rgb_std`, `alpha_thermal_std`, `alpha_event_std` | 8 | 56 | pass |

## Local Candidate Outputs

| Figure | Local path | Bytes | Local-only status | Final asset status |
| --- | --- | ---: | --- | --- |
| Fig. 3 | `runs/local_candidate_figures/phase7e/Fig3_controlled_ablation_candidate.pdf` | 27440 | ignored and intentionally untracked | not final |
| Fig. 4 | `runs/local_candidate_figures/phase7e/Fig4_missing_modality_robustness_candidate.pdf` | 26852 | ignored and intentionally untracked | not final |
| Fig. 5 | `runs/local_candidate_figures/phase7e/Fig5_reliability_weight_audit_candidate.pdf` | 25510 | ignored and intentionally untracked | not final |

Local JSON manifest: `runs/local_candidate_figures/phase7e/candidate_render_manifest.json` (2548 bytes), with top-level `final_asset_status: not_final`.

## Visual-Design Conformance

- Fig. 3 uses three labeled panels for F1@0.50, AP50, and AP75. Both seeds are shown as distinct overlaid points for every metric and variant. No error bars, confidence intervals, p-values, or significance marks are drawn.
- Fig. 4 shows all 18 source rows exactly once as condition/variant/seed points on an AP50 axis. The thermal-removal weakness remains visible.
- Fig. 5 uses a two-panel layout, one panel per seed. `alpha_rgb`, `alpha_thermal`, and `alpha_event` means are plotted with the provided std columns only as labeled `+/- std` variability bars.
- `pdftotext` found candidate watermark text, source path, and SHA256 text in all three candidate PDFs.

## Command Outcomes

- `git switch research/ra-repdet-triair`: PASS.
- `git pull --ff-only research research/ra-repdet-triair`: PASS.
- `git status --short`: PASS; unrelated pre-existing untracked files remain outside this task.
- `python scripts/preflight_submission.py --root . --allow-placeholders`: PASS with expected warnings before Phase 7E edits.
- `python submission/sivp/figures/figure_candidate_build.py --dry-run --root .`: PASS before rendering.
- `python -m py_compile submission/sivp/figures/figure_candidate_build.py`: PASS.
- `git check-ignore -v runs/local_candidate_figures/phase7e/Fig3_controlled_ablation_candidate.pdf`: PASS.
- `git check-ignore -v runs/local_candidate_figures/phase7e/Fig4_missing_modality_robustness_candidate.pdf`: PASS.
- `git check-ignore -v runs/local_candidate_figures/phase7e/Fig5_reliability_weight_audit_candidate.pdf`: PASS.
- `python submission/sivp/figures/figure_candidate_build.py --render-candidates --root . --output-dir runs/local_candidate_figures/phase7e`: PASS.
- `python submission/sivp/figures/figure_candidate_build.py --dry-run --root .`: PASS after rendering.
- `pdftotext` provenance check: PASS for all three candidate PDFs.
- `python -m py_compile submission/sivp/figures/figure_candidate_build.py rarepdet/tools/generate_handoff.py rarepdet/tools/update_project_status.py`: PASS.
- `python rarepdet/tools/generate_handoff.py`: PASS.
- `python rarepdet/tools/update_project_status.py`: PASS.
- `python scripts/preflight_submission.py --root . --allow-placeholders`: PASS with expected warnings after Phase 7E.
- `python scripts/preflight_submission.py --root .`: FAIL as expected on unresolved author metadata, final artwork placeholders, release/data placeholders, and missing Fig. 1-6 assets.

## Non-Modification Confirmation

Source CSVs, metrics, models, datasets, splits, checkpoints, final assets, SIVP LaTeX body, and final PDFs were unchanged. No Fig. 1, Fig. 2, Fig. 6, final Fig. 1-6 PDF, qualitative panel, model output, GPU inference, training, metric recomputation, split mutation, source-data mutation, or LaTeX compilation was run.

## Remaining Strict-Preflight Blockers

- Candidate Fig. 3-5 PDFs await author review and are not publication assets.
- Final approved Fig. 1-6 assets are still missing.
- Fig. 1-2 require author-approved schematic/Visio-style design sources.
- Fig. 6 requires verified local real validation panel inventory and author-approved selection.
- Author-confirmed metadata and declarations are missing.
- TriAir citation, version, licence, access, and redistribution facts are missing.
- Public release/archive URL, tag, commit/archive hash, date, licence, and DOI facts are missing.
- Validation-only wording approval or independent held-out evidence decision is missing.
- Final hardware/software environment record is missing.
- Strict V18 preflight and final Springer `sn-jnl` compile remain blocked.

## Decision

LOCAL NON-FINAL FIG. 3-5 CANDIDATES GENERATED FOR AUTHOR REVIEW; FINAL FIGURE AND EXTERNAL AUTHOR/METADATA BLOCKERS REMAIN OPEN.

Final commit SHA: pending until the completion commit is created.
