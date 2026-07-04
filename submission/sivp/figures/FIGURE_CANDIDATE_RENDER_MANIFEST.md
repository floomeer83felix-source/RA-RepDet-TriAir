# Figure Candidate Render Manifest

Phase 7E created local-only, non-final quantitative candidate renders for author review. The candidate PDFs and local JSON manifest are intentionally ignored by Git and are not publication assets.

| Figure | Source CSV | Source SHA256 | Local candidate | Bytes | Local-only status | Final asset status |
| --- | --- | --- | --- | ---: | --- | --- |
| Fig. 3 | `manuscript/figures/fig3_controlled_ablation_source.csv` | `23e2984adac08ebd6584e1c8d56f82d3cdd0dfb9e5e32047d5064481076d21dc` | `runs/local_candidate_figures/phase7e/Fig3_controlled_ablation_candidate.pdf` | 27440 | ignored and intentionally untracked | missing; not final |
| Fig. 4 | `manuscript/figures/fig4_missing_modality_source.csv` | `aea82341ac37547ece40428e56bd3d98fabf299304a4b24067a7705eaf642fde` | `runs/local_candidate_figures/phase7e/Fig4_missing_modality_robustness_candidate.pdf` | 26852 | ignored and intentionally untracked | missing; not final |
| Fig. 5 | `manuscript/figures/fig5_reliability_weight_source.csv` | `ef93dca475e9a1fa704856952951fbe47ebb701c9e559ea60abf46d861a1239c` | `runs/local_candidate_figures/phase7e/Fig5_reliability_weight_audit_candidate.pdf` | 25510 | ignored and intentionally untracked | missing; not final |

The local render JSON is `runs/local_candidate_figures/phase7e/candidate_render_manifest.json` and records `final_asset_status: not_final`.

Committed source-lock documentation:

- `submission/sivp/figures/FIGURE_SOURCE_TRACEABILITY.md`
- `submission/sivp/figures/FIGURE_SOURCE_TRACEABILITY.csv`

Committed candidate render specifications:

- `submission/sivp/figures/FIGURE_BUILD_SPEC.md`
- `submission/sivp/figures/figure_candidate_build.py`

Final-asset status:

- Fig. 1 and Fig. 2 remain author-design schematic dependencies.
- Fig. 3, Fig. 4, and Fig. 5 have only local non-final candidates awaiting author review.
- Fig. 6 remains dependent on verified local real validation panels.
- No candidate is inserted into `submission/sivp/tex/ra_repdet_sivp.tex`.
