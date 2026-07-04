# Phase 7D Figure Source Lock Report

Generated: 2026-07-04
Workspace: `E:\RepViT-main`
Baseline commit inspected: `4f5e5dac2ac9dd1d239dc3523aefd594edb2c99d`

## Summary

- Figure source traceability is locked for Fig. 1-6.
- Fig. 3, Fig. 4, and Fig. 5 have reproducible candidate-build specifications bound only to the three frozen `manuscript/figures/fig*_source.csv` files.
- Fig. 1 and Fig. 2 remain author-design / Visio-style schematic dependencies and are not final artwork.
- Fig. 6 remains dependent on existing local real validation panels from `runs/clean_qualitative_manifest.csv`; no synthetic or regenerated panels may substitute for them.
- No figure, candidate artwork, image, PDF, SVG, JPG, PNG, EPS, final figure, final compiled PDF, metric, checkpoint, source evidence CSV, split, model, dataset, training code, evaluation code, or SIVP LaTeX body figure placeholder was changed.

## Sources Inspected

| Source | Purpose |
| --- | --- |
| `runs/phase4b_report.md` | Official R4 clean blocked-split decision and controlled seed evidence. |
| `runs/phase7b_publication_state_reconciliation.md` | Strict-preflight blocker context. |
| `runs/phase7c_table_insertion_report.md` | Completed table insertion context. |
| `submission/sivp/tex/main.tex` | Author placeholder and SIVP shell context. |
| `submission/sivp/tex/ra_repdet_sivp.tex` | Figure captions, labels, and placeholder state. |
| `submission/sivp/figures/FINAL_ASSET_INSERTION_MAP.md` | Final figure targets and reserved widths. |
| `manuscript/figures/fig3_controlled_ablation_source.csv` | Frozen Fig. 3 quantitative source. |
| `manuscript/figures/fig4_missing_modality_source.csv` | Frozen Fig. 4 quantitative source. |
| `manuscript/figures/fig5_reliability_weight_source.csv` | Frozen Fig. 5 quantitative source. |
| `runs/clean_qualitative_manifest.csv` | Fig. 6 local real validation panel manifest. |
| `runs/phase3c_report.md` | Leakage audit evidence for Fig. 2. |
| `runs/clean_block64g16_protocol.md` | Clean split protocol evidence for Fig. 2. |
| `rarepdet/models/early_fusion_fcos.py` | Actual reliability detector builder path present in this tree. |
| `rarepdet/models/repvit_fpn_backbone.py` | Actual reliability-gated backbone path present in this tree. |
| `scripts/preflight_submission.py` | Placeholder and final figure preflight behavior. |
| `rarepdet/tools/generate_handoff.py` | Handoff refresh source updated for Phase 7D summary. |
| `rarepdet/tools/update_project_status.py` | Experiment-status refresh source updated for Phase 7D summary. |

Path note: `docs/NEXT_TASK.md` listed `rarepdet/models/reliability_fusion_fcos.py`, but that file is absent in this repository state. Fig. 1 traceability therefore points to the actual reliability builder/backbone files present in the tree.

## Dry-Run Result

Command:

```powershell
python submission/sivp/figures/figure_candidate_build.py --dry-run --root .
```

Result: PASS. The script validated the three frozen CSV sources and wrote no image, PDF, SVG, JPG, PNG, EPS, or candidate output.

| Figure | Source | Headers | Rows | Numerical tokens | SHA256 | Target candidate filename |
| --- | --- | --- | ---: | ---: | --- | --- |
| Fig. 3 | `manuscript/figures/fig3_controlled_ablation_source.csv` | `Variant`, `Seed`, `F1`, `AP50`, `AP75` | 8 | 40 | `23e2984adac08ebd6584e1c8d56f82d3cdd0dfb9e5e32047d5064481076d21dc` | `Fig3_controlled_ablation_candidate.pdf` |
| Fig. 4 | `manuscript/figures/fig4_missing_modality_source.csv` | `Variant`, `Seed`, `Condition`, `AP50` | 18 | 55 | `aea82341ac37547ece40428e56bd3d98fabf299304a4b24067a7705eaf642fde` | `Fig4_missing_modality_robustness_candidate.pdf` |
| Fig. 5 | `manuscript/figures/fig5_reliability_weight_source.csv` | `Seed`, `Mode`, `alpha_rgb_mean`, `alpha_thermal_mean`, `alpha_event_mean`, `alpha_rgb_std`, `alpha_thermal_std`, `alpha_event_std` | 8 | 56 | `ef93dca475e9a1fa704856952951fbe47ebb701c9e559ea60abf46d861a1239c` | `Fig5_reliability_weight_audit_candidate.pdf` |

## Figure Readiness States

| Figure | Target filename | Current state | Author approval required | Strict preflight effect |
| --- | --- | --- | --- | --- |
| Fig. 1 | `Fig1_overall_architecture.pdf` | author-design required | yes | FAIL until approved final PDF exists |
| Fig. 2 | `Fig2_leakage_aware_protocol.pdf` | author-design required | yes | FAIL until approved final PDF exists |
| Fig. 3 | `Fig3_controlled_ablation.pdf` | candidate build spec ready | yes | FAIL until approved final PDF exists |
| Fig. 4 | `Fig4_missing_modality_robustness.pdf` | candidate build spec ready | yes | FAIL until approved final PDF exists |
| Fig. 5 | `Fig5_reliability_weight_audit.pdf` | candidate build spec ready | yes | FAIL until approved final PDF exists |
| Fig. 6 | `Fig6_qualitative_results.pdf` | local-panel inventory required | yes | FAIL until approved final PDF exists |

## Author Action List

1. Approve or provide Fig. 1 architecture schematic design source and final PDF.
2. Approve or provide Fig. 2 leakage-aware protocol schematic design source and final PDF.
3. Review any future non-final Fig. 3-5 local candidate renders before final asset insertion.
4. Verify Fig. 6 local real validation panels, select final qualitative cases, approve any redaction/cropping, and approve final PDF.

## Future Local Candidate-Render Procedure

1. Run only after a later task explicitly approves non-dry candidate rendering.
2. Use only the three frozen CSV files for Fig. 3-5.
3. Write only untracked `*_candidate.*` files into a user-provided output directory outside `figures/` and `submission/sivp/figures/`.
4. Keep a visible candidate/non-final mark until author approval.
5. Do not replace LaTeX placeholders or final asset paths until final approval exists.

## Command Outcomes

- `git switch research/ra-repdet-triair`: PASS.
- `git pull --ff-only research research/ra-repdet-triair`: PASS.
- `git status --short`: PASS; unrelated pre-existing untracked files remain outside this task.
- `python scripts/preflight_submission.py --root . --allow-placeholders`: PASS with expected warnings before Phase 7D edits.
- `python -m py_compile submission/sivp/figures/figure_candidate_build.py rarepdet/tools/generate_handoff.py rarepdet/tools/update_project_status.py`: PASS.
- `python submission/sivp/figures/figure_candidate_build.py --dry-run --root .`: PASS; wrote no artwork.
- Final/candidate artifact check after dry run: PASS; no Fig. 1-6 final PDF and no `*_candidate` image/PDF/SVG/JPG/EPS output found.
- `python rarepdet/tools/generate_handoff.py`: PASS.
- `python rarepdet/tools/update_project_status.py`: PASS.
- `python scripts/preflight_submission.py --root . --allow-placeholders`: PASS with expected warnings after Phase 7D.
- `python scripts/preflight_submission.py --root .`: FAIL as expected on unresolved author metadata, final artwork placeholders, release/data placeholders, and missing Fig. 1-6 assets.

## Remaining Strict-Preflight Blockers

- Author-confirmed metadata and declarations are missing.
- TriAir citation, version, licence, access, and redistribution facts are missing.
- Public release/archive URL, tag, commit/archive hash, date, licence, and DOI facts are missing.
- Final approved Fig. 1-6 assets are missing.
- Fig. 1-2 require author-approved schematic/Visio-style design sources.
- Fig. 6 requires verified local real validation panel inventory and author-approved selection.
- Validation-only wording approval or independent held-out evidence decision is missing.
- Final hardware/software environment record is missing.
- Strict V18 preflight and final Springer `sn-jnl` compile remain blocked.

## Decision

FIGURE SOURCES LOCKED; CANDIDATE BUILD SPEC READY FOR FIG. 3-5; STRICT PREFLIGHT REMAINS BLOCKED BY FINAL FIGURE AND EXTERNAL AUTHOR/METADATA INPUTS.

Final commit SHA: pending until the completion commit is created.
