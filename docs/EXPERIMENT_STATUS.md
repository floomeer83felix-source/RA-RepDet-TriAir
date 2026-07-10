# Experiment Status

Generated: 2026-07-10

## Current Status

`V47_STRUCTURE_AND_RECENT_LITERATURE_REVISION_COMPLETE`

The SIVP manuscript structure has been reorganized and its active cited literature has been expanded to approximately 40 references. No new training, evaluation, checkpoint selection, metric recomputation, split modification, or guard access was performed. The V46 COCO-metric and causal-ablation task remains queued in `docs/NEXT_TASK.md` and has not been treated as completed evidence.

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

- New bibliography: `submission/sivp/tex/references_recent_q12_2023_2025.bib`.
- Verification ledger: `submission/sivp/review/V47_RECENT_Q12_REFERENCE_LEDGER.md`.
- Revision report: `runs/v47_structure_literature/STRUCTURE_AND_REFERENCE_REVISION_REPORT.md`.
- Active manuscript target: 40 unique cited BibTeX keys.
- Composition: 28 newly added formal 2023--2024 Q1/Q2 journal articles, 3 recent journal references already in the repository, and 9 explicitly documented foundational primary-source exceptions.
- `Q2 or above` is interpreted as public JCR/SJR Q1--Q2 journal status, not a Chinese Academy of Sciences partition claim.

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

## Compile status

The previous V45 Springer-style PDF remains the latest compiled artifact and predates the V47 text/bibliography revision. A fresh V47 Springer/BibTeX compile was not possible in the current execution environment because the local container lacked the repository and class files and outbound Git access was unavailable. V47 compile and citation closure remain required before submission.

## Remaining tasks

- Execute V46 COCO-style metrics and causal fusion ablations from `docs/NEXT_TASK.md`.
- Run a V47/V48 Springer `sn-jnl` compile and resolve any bibliography or layout issues.
- Add active efficiency measurements: parameters, FLOPs, latency, throughput, and memory.
- Confirm event-channel generation and synchronization provenance.
- Verify the institutionally required quartile database edition.
- Confirm repository release/archive metadata and TriAir license/version details.
