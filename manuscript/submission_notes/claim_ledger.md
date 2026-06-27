# Claim Ledger

| Claim | Type | Evidence |
| --- | --- | --- |
| R4 is the main proposed model. | conservative interpretation | runs/phase4b_report.md decision SELECT R4 AS CLEAN-SPLIT MAIN VARIANT. |
| Clean split uses 7439 train, 2213 validation, and 837 guard images. | direct measurement | runs/clean_block64g16_protocol.md. |
| Clean split has zero exact RGB train/validation matches. | direct measurement | runs/clean_block64g16_protocol.md. |
| Former random split contained 153 exact RGB-content matched validation samples. | direct measurement | runs/phase3c_report.md. |
| R4 mean AP50=0.962495, AP75=0.891266, F1=0.920861. | direct measurement | runs/phase4b_report.md aggregate table. |
| Reliability fusion improves the matched early-fusion baseline. | conservative interpretation | runs/phase4b_report.md interpretation. |
| Modality dropout improves synthetic missing-modality robustness. | conservative interpretation | runs/phase4b_report.md per-seed missing-modality columns. |
| Thermal removal remains the hardest synthetic missing-modality condition. | limitation | runs/phase4b_report.md and Table_4_missing_modality_robustness. |
| YOLO11n is RGB-only external baseline, not architecture-only ablation. | method description | runs/yolo11n_rgb_baseline_protocol.md. |
| Two seeds do not establish statistical significance. | limitation | docs/NEXT_TASK.md non-negotiable evidence rules. |
| Reliability alpha audit describes gating behavior only. | limitation | runs/r4_reliability_weight_audit.md. |
| Local rendered figures and qualitative panels are not commit-safe. | method description | manuscript/README.md and .gitignore. |
