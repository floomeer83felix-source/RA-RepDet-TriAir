# Author Figure Review Packet

This packet organizes figure-review decisions for the pre-final SIVP source package. It is not final approval, not a formal submission package, and not permission to copy any candidate or local panel output into final asset paths. Final Fig. 1-6 assets remain blocked until written author approval and strict preflight closure.

## Figure Decision Table

| figure_id | current_state | candidate_or_source_location | author_decision | author_comments | approval_date | approver_identity | final_asset_authorized | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Fig. 1 | author-design required | schematic checklist in this packet | pending author review |  |  |  | pending author review | Decision options: provide external source; approve a future implementation from checklist; revise checklist; defer. |
| Fig. 2 | author-design required | schematic checklist in this packet | pending author review |  |  |  | pending author review | Decision options: provide external source; approve a future implementation from checklist; revise checklist; defer. |
| Fig. 3 | local non-final candidate available; final asset missing | runs/local_candidate_figures/phase7e/Fig3_controlled_ablation_candidate.pdf | pending author review |  |  |  | pending author review | Candidate is local-only and not final. |
| Fig. 4 | local non-final candidate available; final asset missing | runs/local_candidate_figures/phase7e/Fig4_missing_modality_robustness_candidate.pdf | pending author review |  |  |  | pending author review | Candidate is local-only and not final. |
| Fig. 5 | local non-final candidate available; final asset missing | runs/local_candidate_figures/phase7e/Fig5_reliability_weight_audit_candidate.pdf | pending author review |  |  |  | pending author review | Candidate is local-only and not final. |
| Fig. 6 | local panel inventory completed; author selection required | submission/sivp/review/FIGURE6_PANEL_REVIEW_TEMPLATE.md | pending author review |  |  |  | pending author review | Only real local validation panels from the manifest are eligible. |

The editable CSV template is `submission/sivp/review/AUTHOR_FIGURE_REVIEW_DECISIONS.csv`.

## Fig. 1 Overall Architecture

Locked caption: `Fig. 1 Overall R4 architecture and training/inference flow. Final artwork pending author approval.`

Required schematic checklist from `submission/sivp/figures/FIGURE_BUILD_SPEC.md`:

- five-channel RGB/thermal/event input
- modality stems
- reliability estimator
- softmax alpha weights
- fused 16-channel tensor
- projection to 3 channels
- RepViT-M0.9
- FPN
- FCOS head
- training-only modality dropout
- standard full-modality inference
- synthetic missing-modality evaluation

Allowed author decision options: `provide external source`, `approve a future implementation from checklist`, `revise checklist`, or `defer`.

## Fig. 2 Leakage-Aware Protocol

Locked caption: `Fig. 2 Leakage-aware blocked split and RGB-content duplicate audit workflow. Final artwork pending author approval.`

Required schematic checklist from `submission/sivp/figures/FIGURE_BUILD_SPEC.md`:

- random-split RGB-content audit
- 153 exact RGB-content matched validation samples
- no claim of full 5-channel byte duplication
- rejected random split for headline evidence
- `block64_guard16_seed0`
- 7439 train images
- 2213 validation images
- 837 guard images
- zero exact RGB train/validation matches
- zero same-family guard-band violations

Allowed author decision options: `provide external source`, `approve a future implementation from checklist`, `revise checklist`, or `defer`.

## Fig. 3 Controlled Clean-Split Ablation

- Local candidate: `runs/local_candidate_figures/phase7e/Fig3_controlled_ablation_candidate.pdf`
- Source CSV: `manuscript/figures/fig3_controlled_ablation_source.csv`
- Source SHA256: `23e2984adac08ebd6584e1c8d56f82d3cdd0dfb9e5e32047d5064481076d21dc`
- Locked caption: `Fig. 3 Controlled two-seed full-modality AP50/AP75/F1 comparison. Final artwork pending author approval.`
- What is shown: seed 0 and seed 2 source rows for F1@0.50, AP50, and AP75 across R0, R1, R2, and R4.

Reviewer checklist:

- correctness against the frozen CSV source
- legibility at full width
- axis and legend clarity
- no unintended implication of statistical significance
- approve or request revision

The candidate is marked `CANDIDATE - NOT FINAL` and must not be copied into final asset paths before written approval.

## Fig. 4 Missing-Modality Robustness

- Local candidate: `runs/local_candidate_figures/phase7e/Fig4_missing_modality_robustness_candidate.pdf`
- Source CSV: `manuscript/figures/fig4_missing_modality_source.csv`
- Source SHA256: `aea82341ac37547ece40428e56bd3d98fabf299304a4b24067a7705eaf642fde`
- Locked caption: `Fig. 4 Missing-modality robustness. Final artwork pending author approval.`
- What is shown: AP50 source rows for synthetic removal of RGB, thermal, or event modalities, preserving seed and variant information.

Reviewer checklist:

- correctness against the frozen CSV source
- legibility at full width
- axis and legend clarity
- no unintended implication of statistical significance
- approve or request revision

The candidate is marked `CANDIDATE - NOT FINAL` and must not be copied into final asset paths before written approval.

## Fig. 5 Reliability-Weight Audit

- Local candidate: `runs/local_candidate_figures/phase7e/Fig5_reliability_weight_audit_candidate.pdf`
- Source CSV: `manuscript/figures/fig5_reliability_weight_source.csv`
- Source SHA256: `ef93dca475e9a1fa704856952951fbe47ebb701c9e559ea60abf46d861a1239c`
- Locked caption: `Fig. 5 Reliability-weight audit. Final artwork pending author approval.`
- What is shown: alpha RGB, thermal, and event mean weights by mode and seed, with only the provided standard-deviation columns used as variability bars.

Reviewer checklist:

- correctness against the frozen CSV source
- legibility at full width
- axis and legend clarity
- no unintended implication of statistical significance or causal modality importance
- approve or request revision

The candidate is marked `CANDIDATE - NOT FINAL` and must not be copied into final asset paths before written approval.

## Fig. 6 Qualitative Detection Panels

Only real local validation panels referenced by `runs/clean_qualitative_manifest.csv` are eligible. Phase 7F performed a local-only inventory and found 20 manifest rows with path metadata, 20 locally existing panel files, and 0 missing or unverifiable panel files. The committed aggregate check is `submission/sivp/review/FIGURE6_PANEL_INVENTORY_CHECK.md`; the local path-level JSON remains ignored under `runs/local_candidate_figures/phase7f/`.

Panel selection, cropping/redaction, and final composition require author review. This packet includes no raw local path, image preview, raw image filename, panel filename, or fabricated panel selection.

## Non-Figure Inputs

Remaining non-figure submission inputs are tracked in `submission/sivp/metadata/FINAL_SUBMISSION_INPUT_LEDGER.md`.
