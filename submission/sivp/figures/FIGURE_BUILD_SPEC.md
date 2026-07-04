# SIVP Figure Build Specification

Phase 7D locks sources and build rules for the six SIVP figures. It does not generate final artwork, candidate artwork, or LaTeX figure insertions.

## Global Rules

- Target reserved dimensions for every figure: full-width `174 mm`, matching `submission/sivp/figures/FINAL_ASSET_INSERTION_MAP.md`.
- Preserve the manuscript captions and labels currently present in `submission/sivp/tex/ra_repdet_sivp.tex`.
- Any future local candidate render must use a filename ending in `_candidate.*`, include a visible "CANDIDATE - NOT FINAL" watermark if the format supports it, and be written only to a user-provided output directory outside the Git-tracked final asset path.
- Candidate files, rendered images, PDFs, SVGs, JPGs, PNGs, EPS files, local qualitative panels, final `Fig1`-`Fig6` PDFs, and final compiled PDFs must not be committed unless a later task explicitly approves final assets.
- Visual integrity rules: no data interpolation; no redrawing detection outputs; no synthetic qualitative panels; no unstated statistical error bars; no visual manipulation that changes interpretation; no omission of thermal-removal weakness; no promotion of legacy random-split E-runs as the manuscript headline.

## Fig. 1 Overall Architecture

- Target asset: `Fig1_overall_architecture.pdf`.
- Reserved width: full-width `174 mm`.
- Caption to preserve: `Fig. 1 Overall R4 architecture and training/inference flow. Final artwork pending author approval.`
- Label to preserve: `fig:fig-1-overall-r4-architecture-and-training-inference-flow`.
- Provenance: `rarepdet/models/early_fusion_fcos.py`, `rarepdet/models/repvit_fpn_backbone.py`, and the Method text in `submission/sivp/tex/ra_repdet_sivp.tex`.
- Automated work allowed: source checking and schematic checklist preparation only.
- Author approval required: yes. The final design must be author-approved before it can be called final.
- Author schematic checklist: show five-channel RGB/thermal/event input; modality stems; reliability estimator; softmax alpha weights; fused 16-channel tensor; projection to 3 channels; RepViT-M0.9; FPN; FCOS head; training-only modality dropout; standard full-modality inference; synthetic missing-modality evaluation.

## Fig. 2 Leakage-Aware Protocol

- Target asset: `Fig2_leakage_aware_protocol.pdf`.
- Reserved width: full-width `174 mm`.
- Caption to preserve: `Fig. 2 Leakage-aware blocked split and RGB-content duplicate audit workflow. Final artwork pending author approval.`
- Label to preserve: `fig:fig-2-leakage-aware-blocked-split-and-rgb-content-duplicate-audit-workflow`.
- Provenance: `runs/phase3c_report.md` and `runs/clean_block64g16_protocol.md`.
- Automated work allowed: source checking and workflow checklist preparation only.
- Author approval required: yes. The final Visio/design source remains external.
- Author schematic checklist: show random-split RGB-content audit; 153 exact RGB-content matched validation samples; no claim of full 5-channel byte duplication; rejected random split for headline evidence; `block64_guard16_seed0`; 7439 train images; 2213 validation images; 837 guard images; zero exact RGB train/validation matches; zero same-family guard-band violations.

## Fig. 3 Controlled Clean-Split Ablation

- Target asset: `Fig3_controlled_ablation.pdf`.
- Reserved width: full-width `174 mm`.
- Caption to preserve: `Fig. 3 Controlled two-seed full-modality AP50/AP75/F1 comparison. Final artwork pending author approval.`
- Label to preserve: `fig:fig-3-controlled-two-seed-full-modality-ap50-ap75-f1-comparison`.
- Provenance: exactly `manuscript/figures/fig3_controlled_ablation_source.csv`.
- Automated work allowed: dry-run validation and future non-final local candidate plotting from that CSV only.
- Author approval required: yes before final artwork or insertion.
- Candidate plot plan: three-panel grouped point/bar comparison; x-axis is variant (`R0 Early Fusion`, `R1 Reliability p=0.00`, `R2 Reliability p=0.15`, `R4 Reliability p=0.20`); seed 0 and seed 2 are shown as legend entries or overlaid points; y-axis units are F1@0.50, AP50, and AP75 in unitless [0, 1] metric units.
- Error-bar policy: no statistical error bars. If an aggregate appears, show seed points and optionally a min-max whisker labeled only as the two-seed range.
- Source-to-panel mapping: `F1` to panel A, `AP50` to panel B, and `AP75` to panel C.

## Fig. 4 Missing-Modality Robustness

- Target asset: `Fig4_missing_modality_robustness.pdf`.
- Reserved width: full-width `174 mm`.
- Caption to preserve: `Fig. 4 Missing-modality robustness. Final artwork pending author approval.`
- Label to preserve: `fig:fig-4-missing-modality-robustness`.
- Provenance: exactly `manuscript/figures/fig4_missing_modality_source.csv`.
- Automated work allowed: dry-run validation and future non-final local candidate plotting from that CSV only.
- Author approval required: yes before final artwork or insertion.
- Candidate plot plan: grouped bar or grouped point plot; x-axis is synthetic removal condition (`w/o RGB`, `w/o Thermal`, `w/o Event`); grouping is variant and seed; y-axis is AP50 in unitless [0, 1] metric units.
- Legend entries: R1 seed 0/2, R2 seed 0/2, R4 seed 0/2; alternatively variant means with seed points overlaid.
- Error-bar policy: no statistical error bars. Optional min-max whiskers must be labeled as the two-seed range.
- Source-to-panel mapping: the three condition values can be separate panels or x-axis groups, but every CSV row must remain represented.

## Fig. 5 Reliability-Weight Audit

- Target asset: `Fig5_reliability_weight_audit.pdf`.
- Reserved width: full-width `174 mm`.
- Caption to preserve: `Fig. 5 Reliability-weight audit. Final artwork pending author approval.`
- Label to preserve: `fig:fig-5-reliability-weight-audit`.
- Provenance: exactly `manuscript/figures/fig5_reliability_weight_source.csv`.
- Automated work allowed: dry-run validation and future non-final local candidate plotting from that CSV only.
- Author approval required: yes before final artwork or insertion.
- Candidate plot plan: grouped alpha-weight audit plot; x-axis is input mode (`full`, `no_rgb`, `no_thermal`, `no_event`); grouping/facet is seed; y-axis is reliability alpha mean in unitless [0, 1] weights.
- Legend entries: `alpha_rgb`, `alpha_thermal`, `alpha_event`.
- Error-bar policy: use only the provided `alpha_*_std` columns if variability bars are shown. Do not infer confidence intervals or statistical significance.
- Source-to-panel mapping: mean columns map to plotted point/bar heights; std columns map only to explicitly labeled variability bars.

## Fig. 6 Qualitative Detection Panels

- Target asset: `Fig6_qualitative_results.pdf`.
- Reserved width: full-width `174 mm`.
- Caption to preserve: `Fig. 6 Qualitative detection panels. Final artwork pending author approval.`
- Label to preserve: `fig:fig-6-qualitative-detection-panels`.
- Provenance: `runs/clean_qualitative_manifest.csv` and existing local real validation panel files under `runs/local_clean_qualitative_panels/`.
- Automated work allowed: local panel inventory checks, manifest validation, and author-review contact-sheet planning only.
- Author approval required: yes before final artwork or insertion.
- Local panel selection rules: select only manifest rows tied to real validation panels; verify every selected `Panel Path` exists locally; preserve category/rank/provenance; do not regenerate detections; do not redraw boxes; do not substitute synthetic panels.
- Redaction and integrity rules: any crop, annotation, or redaction must be author-approved and must not change detection interpretation. Raw `.npy`, local PNG panels, and rendered qualitative assets remain local unless a later final-asset task explicitly approves them.
