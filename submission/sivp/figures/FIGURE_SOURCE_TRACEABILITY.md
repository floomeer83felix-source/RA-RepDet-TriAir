# Figure Source Traceability

Generated for Phase 7D from frozen manuscript and SIVP evidence. This ledger is a source lock, not final artwork approval.

| Figure | Target asset | Source classification | Frozen source paths | Source commit or hash | Count | Approval state | Current state | Strict-preflight effect |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Fig. 1 | `Fig1_overall_architecture.pdf` | Architecture schematic from model code and method text | `rarepdet/models/early_fusion_fcos.py`; `rarepdet/models/repvit_fpn_backbone.py`; method text in `submission/sivp/tex/ra_repdet_sivp.tex` | commit `4f5e5dac2ac9dd1d239dc3523aefd594edb2c99d`; code/text hashes recorded in CSV | 2 code files plus method text | author approval required | author-design required | FAIL until approved final PDF exists |
| Fig. 2 | `Fig2_leakage_aware_protocol.pdf` | Leakage-aware protocol schematic | `runs/phase3c_report.md`; `runs/clean_block64g16_protocol.md` | commit `4f5e5dac2ac9dd1d239dc3523aefd594edb2c99d`; report hashes recorded in CSV | 2 evidence reports | author approval required | author-design required | FAIL until approved final PDF exists |
| Fig. 3 | `Fig3_controlled_ablation.pdf` | Frozen CSV quantitative figure source | `manuscript/figures/fig3_controlled_ablation_source.csv` | sha256 `23e2984adac08ebd6584e1c8d56f82d3cdd0dfb9e5e32047d5064481076d21dc` | 8 rows; 40 numerical tokens | author approval required before final use | candidate build spec ready | FAIL until approved final PDF exists |
| Fig. 4 | `Fig4_missing_modality_robustness.pdf` | Frozen CSV quantitative figure source | `manuscript/figures/fig4_missing_modality_source.csv` | sha256 `aea82341ac37547ece40428e56bd3d98fabf299304a4b24067a7705eaf642fde` | 18 rows; 55 numerical tokens | author approval required before final use | candidate build spec ready | FAIL until approved final PDF exists |
| Fig. 5 | `Fig5_reliability_weight_audit.pdf` | Frozen CSV quantitative figure source | `manuscript/figures/fig5_reliability_weight_source.csv` | sha256 `ef93dca475e9a1fa704856952951fbe47ebb701c9e559ea60abf46d861a1239c` | 8 rows; 56 numerical tokens | author approval required before final use | candidate build spec ready | FAIL until approved final PDF exists |
| Fig. 6 | `Fig6_qualitative_results.pdf` | Qualitative manifest and local real validation panels | `runs/clean_qualitative_manifest.csv`; local `runs/local_clean_qualitative_panels/*.png` files | manifest sha256 `966a81923d5a91bd4d65578e7d607bc989769bad37489b90e56df76724989608` | 20 manifest rows; local panel assets | author approval required | local-panel inventory required | FAIL until approved final PDF exists |

Notes:

- Fig. 1 in the older insertion map referred to `rarepdet/models/reliability_fusion_fcos.py`, but that file is absent in this tree. The actual reliability fusion builder and backbone are in `rarepdet/models/early_fusion_fcos.py` and `rarepdet/models/repvit_fpn_backbone.py`.
- Fig. 3, Fig. 4, and Fig. 5 are the only figures with dry-run-ready quantitative CSV sources in this task.
- Fig. 6 must use existing local real validation panels from the manifest. Synthetic panels, redrawn detections, or regenerated outputs are not acceptable substitutes.
- No final figure file, candidate artwork, image, PDF, SVG, JPG, or LaTeX figure insertion is created by Phase 7D.
