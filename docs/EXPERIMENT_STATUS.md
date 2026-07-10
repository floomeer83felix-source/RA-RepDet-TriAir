# Experiment Status

Generated: 2026-07-10

## Current Status

`V47_STRUCTURE_LITERATURE_AND_COMPILE_COMPLETE`

The SIVP manuscript structure has been reorganized, its active cited literature has been expanded to exactly 40 references, and a fresh Springer-style compile and citation-closure check has been completed. No new training, evaluation, checkpoint selection, metric recomputation, split modification, or holdout access was performed. The V46 COCO-metric and causal-ablation task remains queued in `docs/NEXT_TASK.md` and has not been treated as completed evidence.

## V47 manuscript changes

- Reorganized the paper into Introduction, four-part Related Work, four-part Method, four-part Dataset and Evaluation Protocol, three-part Results, Discussion, Limitations, and Conclusion.
- Removed the weak standalone literature appendix from the active manuscript entry files and integrated its useful scope into the main body.
- Shortened the manuscript title to focus on RA-RepDet rather than embedding the entire evaluation protocol in the title.
- Reduced the contribution list to three substantive contributions.
- Replaced manuscript-facing `guard` wording with `locked within-dataset holdout` where appropriate.
- Clarified that the locked protocol is methodologically more conservative without assuming that the holdout images are intrinsically harder.
- Reframed the held-out conclusion around the stable AP50 trend and explicitly retained mixed F1/AP75 interpretation.
- Expanded Limitations to cover causal ablations, COCO-style metrics, efficiency reporting, event-channel provenance, component-graph completeness, external evaluation, and data-governance gaps.

## V47 literature package

- Active bibliography: `submission/sivp/tex/references_recent_q12_2023_2025.bib`.
- Verification ledger: `submission/sivp/review/V47_RECENT_Q12_REFERENCE_LEDGER.md`.
- Revision report: `runs/v47_structure_literature/STRUCTURE_AND_REFERENCE_REVISION_REPORT.md`.
- Compile report: `runs/v47_structure_literature/V47_COMPILE_AND_CITATION_CLOSURE.md`.
- Active manuscript citations: exactly 40 unique BibTeX keys.
- Composition: 28 newly added formal 2023--2024 Q1/Q2 journal articles, 3 recent journal references already in the repository, and 9 explicitly documented foundational primary-source exceptions.
- `Q2 or above` is interpreted as public JCR/SJR Q1--Q2 journal status, not a Chinese Academy of Sciences partition claim.

## Compile and citation closure

- Springer-style PDF generated: `RA_RepDet_SIVP_V47_structure_recent_literature_snjnl.pdf`.
- Page count: 10.
- Static cited-key count: 40.
- Matching bibliography entries: 40.
- Missing cited keys: 0.
- Undefined citations after final pass: 0.
- Undefined cross-references after final pass: 0.
- Render verification: 10 pages inspected; no obvious page-level clipping or broken pages observed.
- Tables 8 and 9 remained within the page area, and the reference list rendered through pages 8--10 without visible truncation.

## Evidence state

The paper remains based on:

1. three-seed component-disjoint development-validation evidence; and
2. locked same-dataset TriAir holdout evaluation using six fixed checkpoints.

The V41/V42 numerical evidence is unchanged.

## Development-validation descriptive summary

Reliability-aware `p=0.15` minus matched early fusion, paired by seed:

| Metric | Mean delta | Sample SD | n seed pairs |
| --- | ---: | ---: | ---: |
| Precision | +0.011629 | 0.016501 | 3 |
| Recall | +0.024487 | 0.026581 | 3 |
| F1 | +0.018524 | 0.006208 | 3 |
| AP50 | +0.016064 | 0.005699 | 3 |
| AP75 | +0.064657 | 0.016415 | 3 |

## Locked holdout descriptive summary

Reliability-aware `p=0.15` minus matched early fusion, paired by seed:

| Metric | Mean delta | Sample SD | n seed pairs |
| --- | ---: | ---: | ---: |
| Precision | +0.003213 | 0.010920 | 3 |
| Recall | +0.010549 | 0.016220 | 3 |
| F1 | +0.006946 | 0.008943 | 3 |
| AP50 | +0.008562 | 0.006229 | 3 |
| AP75 | +0.002173 | 0.017305 | 3 |

## Current claim boundary

Allowed wording: component-disjoint development-validation evidence plus locked same-dataset held-out TriAir evaluation, using descriptive three-seed paired comparisons between matched early fusion and reliability-aware `p=0.15`.

Disallowed wording: external dataset generalization, independent public benchmark test, training-time model selection or tuning using holdout results, statistical significance, optimal dropout, calibrated physical sensor reliability, real sensor-fault robustness, or COCO AP@[0.50:0.95] until V46 is completed.

## Remaining tasks

- Execute V46 COCO-style metrics and causal fusion ablations from `docs/NEXT_TASK.md`.
- Add active efficiency measurements: parameters, FLOPs, latency, throughput, and memory.
- Confirm event-channel generation and synchronization provenance.
- Verify the institutionally required quartile database edition.
- Confirm repository release/archive metadata and TriAir license/version details.
