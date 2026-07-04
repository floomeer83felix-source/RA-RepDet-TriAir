# Author Submission Input Packet

This is a fillable intake packet for unresolved SIVP submission facts and approvals. It is not a completed submission form. No field may be completed by inference, local machine inspection, Git metadata, or path names; every response must come from an author, release owner, data owner, or approved asset owner.

Use `submission/sivp/metadata/AUTHOR_SUBMISSION_INPUT_RESPONSES.csv` as the structured response sheet. After confirmation, update only the listed repository destinations and rerun strict preflight.

## 1. Publication Authorship And Corresponding Contact

| item_id | exact response requested | destination files after confirmation | current status | caution |
| --- | --- | --- | --- | --- |
| AUTH_001 | Final author names in publication order. | `main.tex`; `main_sivp_snjnl.tex`; `metadata/submission_metadata.yaml`; `metadata/submission_metadata.tex`; `submission/sivp/metadata/author_information_template.md` | Current status: pending author confirmation | Do not infer names from Git metadata or local paths. |
| AUTH_002 | Final institutional affiliations for every author. | `main.tex`; `main_sivp_snjnl.tex`; `metadata/submission_metadata.yaml`; `metadata/submission_metadata.tex`; `submission/sivp/metadata/author_information_template.md` | Current status: pending author confirmation | Include department, institution, city, and country as the journal requires. |
| AUTH_003 | ORCID IDs for authors where available, or an explicit confirmation that none are supplied. | `metadata/submission_metadata.yaml`; `submission/sivp/metadata/author_information_template.md` | Current status: pending author confirmation | Do not create or guess ORCID records. |
| AUTH_004 | Corresponding author email. | `main.tex`; `main_sivp_snjnl.tex`; `metadata/submission_metadata.yaml`; `metadata/submission_metadata.tex` | Current status: pending author confirmation | Use the journal-approved corresponding author and email. |

## 2. Funding, Acknowledgments, Contributions, Competing Interests, And AI Use

| item_id | exact response requested | destination files after confirmation | current status | caution |
| --- | --- | --- | --- | --- |
| DECL_001 | Funding statement with grant numbers or a no-funding statement. | `main.tex`; `main_sivp_snjnl.tex`; `metadata/submission_metadata.yaml`; `submission/sivp/metadata/submission_form_answers_draft.md` | Current status: pending author confirmation | Must match the submission form. |
| DECL_002 | Acknowledgments statement or confirmation that none is used. | `main.tex`; `main_sivp_snjnl.tex`; `metadata/submission_metadata.yaml`; `submission/sivp/metadata/submission_form_answers_draft.md` | Current status: pending author confirmation | Keep separate from funding if the journal requires it. |
| DECL_003 | Author contributions statement. | `main.tex`; `main_sivp_snjnl.tex`; `metadata/submission_metadata.yaml`; `submission/sivp/metadata/author_contributions_template.md` | Current status: pending author confirmation | Must align with final author order. |
| DECL_004 | Competing interests declaration or confirmation that none exist. | `main.tex`; `main_sivp_snjnl.tex`; `metadata/submission_metadata.yaml`; `submission/sivp/metadata/competing_interests_statement_draft.md` | Current status: pending author confirmation | Required before formal submission. |
| DECL_005 | Final AI-use disclosure wording if required by the journal. | `submission/sivp/metadata/ai_use_disclosure_draft.md`; submission form | Current status: pending author confirmation | Disclosure wording is not a scientific result and must match journal policy. |

## 3. TriAir Citation, Version, Licence, Access, And Redistribution

| item_id | exact response requested | destination files after confirmation | current status | caution |
| --- | --- | --- | --- | --- |
| DATA_001 | TriAir source publication or data-card citation, including BibTeX/source metadata if needed. | `references.bib`; `main.tex`; `main_sivp_snjnl.tex`; `metadata/submission_metadata.yaml` | Current status: pending author confirmation | Do not invent dataset citation details. |
| DATA_002 | TriAir dataset version and provider text. | `metadata/submission_metadata.yaml`; data availability statement | Current status: pending author confirmation | Needed for reproducibility. |
| DATA_003 | TriAir licence and access terms. | `metadata/submission_metadata.yaml`; data availability statement | Current status: pending author confirmation | Must match dataset provider terms. |
| DATA_004 | TriAir redistribution permission or restriction. | `metadata/submission_metadata.yaml`; `archive_manifest.txt`; data availability statement | Current status: pending author confirmation | Heavy local data must remain out of Git unless permission exists. |

## 4. Code, Archive, And Release Decision

| item_id | exact response requested | destination files after confirmation | current status | caution |
| --- | --- | --- | --- | --- |
| REL_001 | Public repository or release URL, or explicit private/no-release policy. | `archive_manifest.txt`; `SUBMISSION_PRECHECK_V18.md`; `PUBLIC_RELEASE_MANIFEST.md` if used | Current status: pending author confirmation | Do not fabricate a public URL. |
| REL_002 | Release tag. | `archive_manifest.txt`; `SUBMISSION_PRECHECK_V18.md` | Current status: pending author confirmation | Tag must match submitted source. |
| REL_003 | Immutable commit hash for public/archive source. | `archive_manifest.txt`; `SUBMISSION_PRECHECK_V18.md` | Current status: pending author confirmation | Current working branch SHA is not a public archive by itself. |
| REL_004 | Archive date. | `archive_manifest.txt`; `SUBMISSION_PRECHECK_V18.md` | Current status: pending author confirmation | Date must be factual and tied to the final archive/release action. |
| REL_005 | Release licence. | `archive_manifest.txt`; `SUBMISSION_PRECHECK_V18.md`; repository release metadata | Current status: pending author confirmation | Must not conflict with TriAir terms. |
| REL_006 | Zenodo DOI if applicable, or explicit confirmation that no DOI is claimed. | `archive_manifest.txt`; `SUBMISSION_PRECHECK_V18.md`; data/code availability statement | Current status: pending author confirmation | Do not invent DOI values. |

## 5. Figure Decisions

Use `submission/sivp/review/AUTHOR_FIGURE_REVIEW_PACKET.md` and `submission/sivp/review/AUTHOR_FIGURE_REVIEW_DECISIONS.csv` for Fig. 1-6 decisions. Use `submission/sivp/review/FIGURE6_PANEL_REVIEW_TEMPLATE.md` and `.csv` for Fig. 6 panel-selection/composition decisions. Do not repeat local panel identifiers or local paths in this packet.

| item_id | exact response requested | destination files after confirmation | current status | caution |
| --- | --- | --- | --- | --- |
| FIG_001 | Final Fig. 1 overall architecture asset decision: provide author-designed source/PDF, approve future implementation from checklist, request revision, or defer. | `figures/Fig1_overall_architecture.pdf`; `submission/sivp/figures/FINAL_ASSET_INSERTION_MAP.md`; figure review decision files | Current status: pending author confirmation | Distinguish author-designed schematics from data-derived figures. |
| FIG_002 | Final Fig. 2 leakage-aware protocol asset decision: provide author-designed source/PDF, approve future implementation from checklist, request revision, or defer. | `figures/Fig2_leakage_aware_protocol.pdf`; `submission/sivp/figures/FINAL_ASSET_INSERTION_MAP.md`; figure review decision files | Current status: pending author confirmation | Must preserve the frozen block64_guard16_seed0 protocol and leakage-audit facts. |
| FIG_003 | Final Fig. 3 controlled ablation asset decision: approve local non-final candidate for finalization, request revision, or defer. | `figures/Fig3_controlled_ablation.pdf`; `manuscript/figures/fig3_controlled_ablation_source.csv`; figure review decision files | Current status: pending author confirmation | No metric recomputation is authorized by this decision sheet. |
| FIG_004 | Final Fig. 4 missing-modality robustness asset decision: approve local non-final candidate for finalization, request revision, or defer. | `figures/Fig4_missing_modality_robustness.pdf`; `manuscript/figures/fig4_missing_modality_source.csv`; figure review decision files | Current status: pending author confirmation | Thermal-removal weakness must remain visible. |
| FIG_005 | Final Fig. 5 reliability-weight audit asset decision: approve local non-final candidate for finalization, request revision, or defer. | `figures/Fig5_reliability_weight_audit.pdf`; `manuscript/figures/fig5_reliability_weight_source.csv`; figure review decision files | Current status: pending author confirmation | Alpha values are observed gating behavior, not causal physical modality importance. |
| FIG_006 | Final Fig. 6 qualitative-results decision: select eligible panels, confirm crop/redaction choices, and approve final composition or defer. | `figures/Fig6_qualitative_results.pdf`; `runs/clean_qualitative_manifest.csv`; Fig. 6 review template files | Current status: pending author confirmation | Use only real validation panels from the manifest; do not commit local PNG panels. |

## 6. Claim Scope

| item_id | exact response requested | destination files after confirmation | current status | caution |
| --- | --- | --- | --- | --- |
| CLAIM_001 | Author approval that validation-only wording is acceptable for final submission. | `main.tex`; `main_sivp_snjnl.tex`; `submission/sivp/tex/ra_repdet_sivp.tex`; cover letter/submission form | Current status: pending author confirmation | Do not claim independent test evidence without a new frozen protocol result. |
| CLAIM_002 | Independent held-out test evidence if authors require test-set claims, or confirmation that validation-only wording remains. | new approved report and manuscript updates if produced | Current status: pending author confirmation | No new evaluation was run in Phase 7G. |

## 7. Final Training And Evaluation Environment Record

| item_id | exact response requested | destination files after confirmation | current status | caution |
| --- | --- | --- | --- | --- |
| ENV_001 | Final hardware/software environment record for training and evaluation. | `metadata/IMPLEMENTATION_DETAILS_TEMPLATE.md`; `metadata/submission_metadata.yaml`; reproducibility notes; `submission/sivp/metadata/ENVIRONMENT_RECORD_TEMPLATE.md` | Current status: pending author confirmation | Do not infer from the current machine unless authors approve. |

## 8. Final Springer sn-jnl Compile Owner And Readiness

| item_id | exact response requested | destination files after confirmation | current status | caution |
| --- | --- | --- | --- | --- |
| TEX_001 | Springer `sn-jnl` local dependency and final compile-readiness confirmation. | `submission/sivp/tex/sn-jnl.cls`; `main_sivp_snjnl.tex`; final PDF build log | Current status: pending author confirmation | Final compile must wait until strict preflight passes and approved final assets exist. |
