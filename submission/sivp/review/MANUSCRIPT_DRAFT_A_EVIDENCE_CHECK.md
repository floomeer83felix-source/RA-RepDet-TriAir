# Manuscript Draft A Evidence Check

## Scope

This check records a manual evidence-consistency review of Manuscript Draft A. It is an editorial integrity record, not a strict-preflight pass and not a declaration of submission readiness.

## Source Set Reviewed

- `main.tex`
- `main_sivp_snjnl.tex`
- `submission/sivp/tex/main.tex`
- `submission/sivp/tex/ra_repdet_sivp.tex`
- `submission/sivp/tables/Table_1_dataset_and_clean_split.tex` through `Table_7_reliability_weight_audit.tex`
- frozen Phase 7B--7I reconciliation and review reports

## Front-Matter Consistency

| check | result | notes |
| --- | --- | --- |
| Title synchronized across three entry files | pass | The SIVP subdirectory entry retains only its required local input-path difference. |
| Abstract synchronized across three entry files | pass | Reports validation-only R4 results and scope limits. |
| Keyword line synchronized across three entry files | pass | Includes reliability-aware fusion and leakage-aware evaluation. |
| Author placeholders preserved | pass | No author name, affiliation, email, ORCID, or correspondence fact was filled. |
| Declaration placeholders preserved | pass | Funding, competing interests, contributions, acknowledgments, and data availability remain author-confirmation fields. |

## Body Integrity

| check | result | notes |
| --- | --- | --- |
| Required sections present | pass | Introduction; Related Work; Method; Dataset and Leakage-Aware Evaluation Protocol; Experiments; Discussion; Limitations; Conclusion. |
| Seven table inputs retained | pass | Tables 1--7 remain `\input` fragments and were not edited. |
| Six figure placeholders retained | pass | Fig. 1--6 remain final-artwork-pending placeholders; no candidate or local panel was inserted. |
| Table placeholder regression | pass | No `TABLE PLACEHOLDER` string introduced. |
| Matched comparison wording | pass | R0 versus R1/R2/R4 is the matched tri-modal ablation. |
| External-baseline wording | pass | YOLO11n is explicitly RGB-only and not treated as a matched architecture-only ablation. |
| Synthetic-missingness wording | pass | Channel zeroing is described as controlled synthetic missingness, not complete real sensor failure. |
| Reliability-weight wording | pass | Softmax weights are descriptive model observations, not causal or calibrated physical reliability claims. |

## Frozen Numeric Checks

| item | expected frozen value | Draft A status |
| --- | --- | --- |
| R4 mean AP50 | `0.962495` | present |
| R4 mean AP75 | `0.891266` | present |
| R4 mean F1@0.50 | `0.920861` | present |
| Split sizes | `7439`, `2213`, `837` | present |
| RGB duplicate audit | `153`, `0.072927` | present |
| Controlled seeds | `0`, `2` | present |
| R4 modality dropout | `p=0.20` | present |
| R4 w/o RGB AP50 | `0.916051` | present |
| R4 w/o thermal AP50 | `0.718277` | present |
| R4 w/o event AP50 | `0.961577` | present |

## Wording Guards

- The draft uses validation-only language and does not claim an independent held-out evaluation.
- The draft does not claim statistical significance, benchmark leadership, a public archive, a DOI, redistribution permission, or final figure approval.
- The random split is identified as historical/exploratory only after its exact RGB-content overlap audit.
- Thermal removal is retained as a limitation rather than omitted from the narrative.

## Status

**PASS — editorial evidence-consistency review.**

Draft A is appropriate for scientific and author review. It is **not** submission-ready: author metadata and declarations, TriAir governance facts, release/archive facts, final Fig. 1--6 assets, environment details, strict preflight closure, and Springer compile review remain pending.
