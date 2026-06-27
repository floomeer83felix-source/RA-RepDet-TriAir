# Current Task

## Phase 6A — Journal-Neutral English Manuscript Draft

## Decision
Phase 5A is complete and its decision is `READY FOR MANUSCRIPT DRAFTING`.

The main paper model is **R4 Reliability Fusion with modality dropout p=0.20**. The paper must be built entirely around the controlled clean blocked split, not around the former random split.

This phase creates a complete, journal-neutral English manuscript source package and local figure assets. It does not add experiments, retrain models, change the method, or submit to any journal.

## Read First
- `runs/phase5a_report.md`
- `runs/phase4b_report.md`
- `runs/clean_block64g16_protocol.md`
- `runs/phase3c_report.md`
- `runs/seed_reproducibility_smoke.md`
- `runs/clean_efficiency_profile.md`
- `runs/r4_reliability_weight_audit.md`
- `runs/clean_qualitative_summary.md`
- `runs/yolo11n_rgb_baseline_protocol.md`
- `docs/EXPERIMENT_STATUS.md`
- `runs/handoff_latest.md`

## Non-Negotiable Evidence Rules
1. Use only the frozen clean blocked split headline evidence:
   - train=7439, validation=2213, guard=837;
   - exact RGB train/validation matches=0;
   - same-family guard violations=0.
2. Use controlled-seed R0/R1/R2/R4 results only for all main method tables.
3. Treat Phase 4A B-runs as exploratory pilots only; do not pool them with controlled R-runs.
4. Treat E0–E6 random-split results as historical diagnostics only; do not use them in the abstract, introduction performance claims, results tables, conclusion, or title.
5. R4 must be the main proposed model. R2 is a dropout-ratio ablation, not a co-main model.
6. Label YOLO11n strictly as an **RGB-only external baseline**. Do not attribute its performance gap solely to architecture, because its input modalities differ from R4.
7. State clearly that two seeds provide controlled replication but do not establish statistical significance.
8. State the key limitation: thermal removal remains the most difficult synthetic missing-modality condition, even though R4 is best among the evaluated variants.
9. Do not claim exact zero alpha for an absent modality. Describe the alpha audit only as observed gating behavior under synthetic modality removal.
10. Do not fabricate references, DOI values, journal metadata, numerical results, citations, or image claims.

## Target Story
Prepare the paper around this contribution logic:
1. A lightweight RepViT-FCOS RGB–thermal–event detector for UAV vehicle detection.
2. Reliability-aware tri-modal fusion improves the matched tri-modal early-fusion baseline.
3. Modality dropout improves robustness when any one sensor stream is unavailable; p=0.20 is selected by controlled clean-split two-seed evidence.
4. The paper uses a leakage-aware blocked split with a guard band after RGB-content duplication was detected in the former random split.

Do not oversell architecture novelty. Position this as a practical, reproducible multi-sensor UAV perception study with robust training and rigorous protocol control.

## Task 0 — Create Manuscript Source Package
Create directory:

```text
manuscript/
```

Create these UTF-8 source files:

```text
manuscript/README.md
manuscript/RA_RepDet_manuscript_v1.md
manuscript/tables/
manuscript/figures/
manuscript/references/
manuscript/submission_notes/
```

`manuscript/README.md` must identify:
- the draft status as journal-neutral and not yet submission-formatted;
- the data/evidence files that drive every table and claim;
- which image assets are local-only versus commit-safe source/manifest files;
- the next manual decision: choose a target SCI/EI journal before final formatting.

## Task 1 — Full English Draft in Markdown
Create `manuscript/RA_RepDet_manuscript_v1.md` with a complete first draft in polished academic English using this structure:

```text
Title
Abstract
Keywords
1. Introduction
2. Related Work
  2.1 UAV vehicle detection
  2.2 RGB–thermal–event / multi-sensor detection
  2.3 Missing-modality robustness
3. Method
  3.1 Overall architecture
  3.2 Early-fusion baseline
  3.3 Reliability-aware tri-modal fusion
  3.4 Modality-dropout training
4. Dataset and Leakage-Aware Evaluation Protocol
  4.1 TriAir data representation and labels
  4.2 RGB-content duplicate audit
  4.3 Blocked split and guard band
5. Experiments
  5.1 Experimental settings and reproducibility
  5.2 Controlled clean-split ablation
  5.3 Robustness to synthetic missing modalities
  5.4 RGB-only external baseline
  5.5 Efficiency and convergence
  5.6 Reliability-weight analysis
  5.7 Qualitative results and limitations
6. Conclusion
Data and code availability statement
```

Requirements:
- Provide a specific, conservative title plus three alternative titles in a short front-matter note.
- Keep the abstract 180–230 words. It must include the clean split protocol and controlled two-seed evidence without claiming statistical significance.
- Include `[REF: ...]` placeholders only where a verified citation will later be inserted. Do not invent a bibliography.
- Every performance number must exactly match existing clean-split reports.
- Use R4 mean values in headline prose: AP50=0.962495, AP75=0.891266, F1=0.920861.
- Report both per-seed values or mean/min/max/range in experimental tables, not mean alone.
- Explicitly distinguish: R0 vs R1/R2/R4 is the matched tri-modal ablation; YOLO11n is RGB-only external comparison.
- Include a concise limitations paragraph: two seeds, synthetic missingness, one dataset, and thermal-drop vulnerability.

## Task 2 — Reproducible Paper Tables
Create commit-safe CSV and Markdown tables under `manuscript/tables/` from existing source reports. At minimum:

```text
Table_1_dataset_and_clean_split.csv/.md
Table_2_implementation_and_reproducibility.csv/.md
Table_3_controlled_ablation.csv/.md
Table_4_missing_modality_robustness.csv/.md
Table_5_rgb_only_external_baseline.csv/.md
Table_6_efficiency_and_convergence.csv/.md
Table_7_reliability_weight_audit.csv/.md
```

Table rules:
- Values must be copied or computed directly from existing Phase 4B/5A outputs.
- Table 3 must show R0/R1/R2/R4 per seed and mean/range.
- Table 4 must show R1/R2/R4 missing-modality values per seed and mean/range; do not use a mean across sensor-loss conditions as a single selection score.
- Table 5 must label R4 as tri-modal and YOLO11n as RGB-only.
- Table 6 must report raw-forward and complete detector-inference results separately; do not call a 50.44 vs 48.07 FPS difference a definitive speed advantage. Include peak allocated CUDA memory.

## Task 3 — Figures and Figure Manifest
Create `manuscript/figures/figure_manifest.md` and `manuscript/figures/figure_manifest.csv`.

The manifest must specify the following proposed figures and exact data/input sources:

```text
Fig. 1 Overall R4 architecture and training/inference flow.
Fig. 2 Leakage-aware blocked split, guard band, and RGB-content duplicate audit workflow.
Fig. 3 Controlled two-seed full-modality AP50/AP75/F1 comparison for R0/R1/R2/R4.
Fig. 4 Three missing-modality AP50 conditions for R1/R2/R4 across both seeds.
Fig. 5 R4 fusion-weight distributions/means under full and each synthetic missing-modality condition.
Fig. 6 Qualitative panels: R0 versus R4, R4 hard cases, and R4 missing-modality cases.
```

Generate the following local-only visual assets where source data is already available:
- chart source CSV files and plotting scripts for Fig. 3–5;
- local PNG/PDF chart outputs under `manuscript/figures/local_rendered/`;
- local qualitative panel outputs from existing manifests under `manuscript/figures/local_qualitative/`.

Do not commit rendered PNG/PDF panels, source images, dataset arrays, or predictions. Commit only the manifest, plotting scripts, source CSV values, and Markdown notes necessary to recreate them locally.

## Task 4 — Verified Reference Inventory Only
Create `manuscript/references/reference_inventory.md` and `.csv`.

Include only references whose metadata can be verified from a primary source, publisher page, DOI resolver, arXiv record, or official project/paper page. For each entry record title, authors, venue, year, DOI or stable official URL, and intended manuscript section. Do not fabricate citations or use unverifiable citation details.

Target 30–40 relevant references across:
- UAV vehicle/object detection;
- RGB–thermal fusion;
- event-camera detection/vision;
- multi-modal fusion and missing-modality robustness;
- RepViT / FCOS / YOLO11 or exact baseline architectures;
- reproducibility, duplicate leakage, or leakage-aware data splits where applicable.

When a metadata item cannot be verified, omit it rather than guessing. Mark the inventory `DRAFT VERIFIED METADATA — citation style pending target journal`.

## Task 5 — Claim Ledger and Final Self-Audit
Create:

```text
manuscript/submission_notes/claim_ledger.md
manuscript/submission_notes/manuscript_self_audit.md
runs/phase6a_manuscript_report.md
```

The claim ledger must map each important claim in the manuscript to a local source report/table and label it as one of:
- `direct measurement`;
- `method description`;
- `conservative interpretation`;
- `limitation`.

The self-audit must confirm:
- all main metrics trace back to Phase 4B/5A clean-split reports;
- former random-split values never appear as headline metrics;
- R4 is consistently named main model;
- YOLO11n wording is RGB-only external baseline, not a matched architecture ablation;
- no statistical-significance statement is made from two seeds;
- title, abstract, conclusion, and tables contain no unsupported claims;
- every citation placeholder is linked to a verified inventory entry or remains explicitly unresolved.

`runs/phase6a_manuscript_report.md` must list all created files, any unresolved reference/asset limitations, and end with exactly one decision:

```text
MANUSCRIPT DRAFT READY FOR JOURNAL TARGETING
```

or

```text
STOP: MANUSCRIPT EVIDENCE OR CITATION BLOCKER
```

## Scope Restrictions
- Do not run new training, evaluations, or architecture modifications.
- Do not rewrite any experimental source report.
- Do not add 100-epoch experiments.
- Do not create or submit a Word/PDF manuscript in this phase.
- Do not select or claim compliance with a specific journal yet.
- Do not commit model weights, checkpoints, raw predictions, source images, panels, datasets, or cache exports.

## Status and Push
Update:
- `docs/EXPERIMENT_STATUS.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`

Commit only source code, Markdown, CSV, TXT, JSON, and documentation.

Commit message:

```text
Phase 6A: prepare journal-neutral English manuscript draft
```

Push to `research/ra-repdet-triair`.

If blocked, create/update `docs/TASK_BLOCKER.md` with the exact command, final error, attempted fix, and smallest safe next action.