# Current Task

## Phase 6B — SIVP Submission-Source Preparation

## Target Decision
The first submission target is **Signal, Image and Video Processing (SIVP, Springer Nature)**. Read `docs/TARGET_JOURNAL.md` before doing any work.

This task prepares a complete, journal-specific LaTeX source package and submission metadata placeholders. It does **not** create the final submission PDF, final figures, final tables, or perform a submission.

The assistant will separately produce and approve the final inserted figures and tables. Do not substitute local auto-rendered charts, default plots, or provisional tables as final publication artwork.

## Read First
- `docs/TARGET_JOURNAL.md`
- `manuscript/RA_RepDet_manuscript_v1.md`
- `manuscript/references/reference_inventory.csv`
- `manuscript/submission_notes/claim_ledger.md`
- `manuscript/submission_notes/manuscript_self_audit.md`
- `runs/phase6a_manuscript_report.md`
- `runs/phase5a_report.md`
- `runs/phase4b_report.md`
- `runs/clean_block64g16_protocol.md`

## Non-Negotiable Scientific Rules
1. All headline metrics must remain from the controlled clean blocked split only.
2. R4 Reliability Fusion with modality-dropout `p=0.20` is the main model.
3. Do not use former random-split E0–E6 values in the title, abstract, results, conclusion, or final tables.
4. Keep R0 versus R1/R2/R4 as the matched tri-modal ablation.
5. Label YOLO11n only as an `RGB-only external baseline`; do not call it a matched architecture baseline.
6. Keep all limitations: two controlled seeds are not a statistical-significance study; missingness is synthetic; evidence uses one dataset; thermal removal remains the hardest sensor-loss condition.
7. Do not claim exact zero absent-modality alpha.
8. Do not change any experimental number, source report, experiment script, or evidence table without creating a blocker.

## SIVP Constraints to Enforce
- Use the Springer Nature LaTeX template with `\documentclass{sn-jnl}` and two-column `[iicol]` formatting.
- Final article target: no more than 10 pages including figures, tables, and references; page 10 may contain references only.
- Abstract: 150–250 words.
- Keywords: 4–6.
- Numbered references in square brackets; retain DOI links where available.
- Single-blind review: author names/affiliations appear in the manuscript.
- PDF plus complete editable LaTeX source will be required later.
- Data Availability Statement and declarations are required.
- SIVP guidance requires transparency about non-copy-editing LLM use and states that authors remain accountable. Prepare a disclosure template; do not add it to the manuscript until the authors confirm the final wording.

## Task 0 — Create Submission Package Skeleton
Create this commit-safe directory tree:

```text
submission/sivp/
submission/sivp/tex/
submission/sivp/tables/
submission/sivp/figures/
submission/sivp/metadata/
submission/sivp/review/
```

Create `submission/sivp/README.md` explaining:
- the package is `PRE-FINAL` and cannot be submitted until final figures, final tables, author details, and final PDF are approved;
- which files are author placeholders;
- which files will be replaced by assistant-produced final artwork;
- compilation and validation steps;
- no generated-art image may be used as a scientific figure.

## Task 1 — Obtain and Freeze the Official SIVP LaTeX Base
1. Obtain the official Springer Nature LaTeX template only from the official Springer Nature source referenced in `docs/TARGET_JOURNAL.md`.
2. Store the template source under `submission/sivp/tex/` with an `UPSTREAM_TEMPLATE.md` note recording the official source, access date, and unchanged template file names.
3. Do not modify official class/style files except where the template explicitly supports local configuration.
4. Create `submission/sivp/tex/main.tex` using `sn-jnl` and `[iicol]`.
5. Use a temporary `\fbox{Final artwork pending}` placeholder for each figure and a clear `TABLE PLACEHOLDER — FINAL VERSION PENDING` marker for each table. The main source must compile even without final artwork.

## Task 2 — Convert and Tighten the Journal-Neutral Draft
Create `submission/sivp/tex/ra_repdet_sivp.tex` from `manuscript/RA_RepDet_manuscript_v1.md`.

Requirements:
- Use the selected title exactly:

```text
Reliability-Aware RGB–Thermal–Event Fusion for Lightweight UAV Vehicle Detection Under Leakage-Aware Evaluation
```

- Retain the current abstract substance but keep it between 150 and 250 words.
- Keep exactly 4–6 keywords.
- Use standard decimal section headings (no more than three heading levels).
- Ensure every metric exactly matches the clean-split reports.
- Replace `[REF: key]` placeholders with valid `\cite{...}` calls only after the matching BibTeX key is verified.
- Use author, affiliation, ORCID, corresponding-email, funding, and acknowledgment placeholders; do not infer names, institutions, grants, or ORCIDs.
- Include SIVP-compatible `Statements and Declarations` placeholders for competing interests, author contributions, funding, and data availability.
- Include an explicit short paragraph that YOLO11n is RGB-only external baseline and not a matched architecture ablation.
- Include the fixed study limitations.

## Task 3 — Build Verified SIVP Reference Files
Create:

```text
submission/sivp/tex/references.bib
submission/sivp/review/reference_key_map.csv
submission/sivp/review/reference_validation.md
```

Rules:
- Use only entries from the existing verified reference inventory.
- Do not invent or silently repair metadata.
- Every in-text citation key must resolve to exactly one BibTeX entry.
- Every BibTeX entry must be cited, unless it is explicitly documented as held for later use.
- Keep DOI URLs where existing metadata provides them.
- Flag (do not guess) any unresolved author list, venue, volume, issue, pages, or DOI field.

## Task 4 — Final-Asset Insertion Map for Assistant-Produced Artwork
Create:

```text
submission/sivp/figures/FINAL_ASSET_INSERTION_MAP.md
submission/sivp/tables/FINAL_TABLE_INSERTION_MAP.md
```

The figure map must specify the exact final target assets and reserved widths:

```text
Fig1_overall_architecture.pdf          full width 174 mm
Fig2_leakage_aware_protocol.pdf        full width 174 mm
Fig3_controlled_ablation.pdf           full width 174 mm
Fig4_missing_modality_robustness.pdf   full width 174 mm
Fig5_reliability_weight_audit.pdf      full width 174 mm
Fig6_qualitative_results.pdf           full width 174 mm
```

The table map must specify the final intended tables, caption location, source CSV, and whether it is likely single-column or full-width. Use the existing `manuscript/tables/` files as numerical sources, but do not format them as final publication tables in this task.

## Task 5 — SIVP Page-Budget and Claim Audit
Create:

```text
submission/sivp/review/page_budget.md
submission/sivp/review/sivp_compliance_audit.md
submission/sivp/review/claim_risk_audit.md
```

The page budget must reserve space for all six final figures and the necessary tables and identify content that can move to supplementary material if the final two-column article exceeds 10 pages. Do not delete scientifically necessary content at this stage.

The SIVP compliance audit must check:
- LaTeX `sn-jnl` / `[iicol]` presence;
- abstract word count;
- keyword count;
- numbered-citation readiness;
- mandatory declaration placeholders;
- data-availability placeholder;
- required editable-source inventory;
- no final PDF yet;
- final-asset placeholders clearly marked;
- no external source images or generative images used as scientific evidence.

The claim-risk audit must separately verify that:
- every headline metric maps to Phase 4B or Phase 5A;
- former random-split values do not appear as headline evidence;
- R4 naming is consistent;
- YOLO11n wording is correct;
- no statistical-significance claim is made;
- no unsupported SOTA or speed claim is introduced.

## Task 6 — Author and Submission Metadata Templates
Create:

```text
submission/sivp/metadata/author_information_template.md
submission/sivp/metadata/submission_form_answers_draft.md
submission/sivp/metadata/cover_letter_draft.md
submission/sivp/metadata/data_availability_statement_draft.md
submission/sivp/metadata/competing_interests_statement_draft.md
submission/sivp/metadata/author_contributions_template.md
submission/sivp/metadata/ai_use_disclosure_draft.md
```

Rules:
- Use explicit placeholders, e.g. `[AUTHOR 1 FULL NAME]`, `[AFFILIATION]`, `[CORRESPONDING EMAIL]`, `[FUNDING NUMBER OR NONE]`.
- Do not infer author order, correspondence, affiliation, funding, or competing interests.
- Cover letter must be a conservative SIVP-specific draft, state the paper is original/not under review elsewhere, identify practical scope fit, and not claim SOTA.
- Data availability statement must not promise dataset/code openness beyond the project’s known rights and current repository status.
- The AI-use disclosure draft must state only the actual anticipated workflow: generative AI assistance for draft language/structure or copyediting as applicable; authors verify all scientific content, methods, calculations, citations, and final wording; no AI-generated experimental data or scientific-evidence images. It must be marked `AUTHOR CONFIRMATION REQUIRED` and must not be inserted into the manuscript automatically.

## Task 7 — Compile Dry Run and Report
Compile a **placeholder-only dry run** locally if the official template environment is available. It is acceptable that the output contains placeholder boxes; do not treat it as submission PDF.

Create `runs/phase6b_sivp_preparation_report.md` listing:
- created source files;
- compilation result and warnings;
- abstract/keyword/page-count checks;
- unresolved final-asset requirements;
- unresolved author metadata;
- unresolved citation items;
- a strict readiness decision ending in exactly one:

```text
READY FOR ASSISTANT FINAL FIGURES, TABLES, AND AUTHOR METADATA
```

or

```text
STOP: SIVP SOURCE OR TEMPLATE BLOCKER
```

## Scope Restrictions
- Do not train or evaluate models.
- Do not alter experiments, metrics, code, or the journal-neutral evidence package.
- Do not create the final Word manuscript, final PDF, or final submission bundle.
- Do not auto-generate any final figure or final publication table.
- Do not submit to SIVP.
- Do not commit models, weights, datasets, raw predictions, source images, rendered local panels, or final PDFs.

## Status and Push
Update:
- `docs/EXPERIMENT_STATUS.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`

Commit only source code, LaTeX source, BibTeX, Markdown, CSV, TXT, JSON, and documentation.

Commit message:

```text
Phase 6B: prepare SIVP LaTeX submission source
```

Push to `research/ra-repdet-triair`.

If blocked, create/update `docs/TASK_BLOCKER.md` with the exact failed command, error, attempted fix, and smallest safe next action.