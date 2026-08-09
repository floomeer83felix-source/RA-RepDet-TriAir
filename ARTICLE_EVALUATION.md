# RA-RepDet manuscript evaluation - V82 authoritative V81 integration

## Overall recommendation

**Proceed to final submission preparation.** V82 replaces the unidentified author-supplied single-modality table with the checkpoint-backed V81 replication selected by the author as authoritative. All nine single-modality runs completed the frozen 50-epoch protocol, and all nine retained checkpoints have selected epochs, SHA256 identities, a common validation-manifest SHA256, raw standardized COCO evaluator records, and runtime metadata.

Thermal remains the strongest standalone modality, but both matched early fusion and the full reliability-aware system exceed thermal-only for AP, AP50, and AP75 in every seed-matched comparison. The full system exceeds thermal-only by `0.1960 ± 0.0329` AP, `0.1215 ± 0.0154` AP50, and `0.2952 ± 0.0349` AP75. These are descriptive component-disjoint development-validation contrasts, not significance tests or independent-test evidence.

## Scorecard

| Dimension | Score | Assessment |
| --- | ---: | --- |
| Novelty and relevance | 4.1 / 5 | Lightweight reliability-aware tri-modal fusion remains relevant. |
| Method clarity | 4.6 / 5 | Architecture, frozen protocols, evaluator contracts, and evidence boundaries are explicit. |
| Experimental rigor | 4.5 / 5 | Three-seed systems, causal controls, checkpoint-backed single-modality replication, locked holdout, and transfer study are present. |
| Evidence traceability | 4.9 / 5 | V81 includes checkpoint epochs, hashes, split identity, raw evaluator JSON, logs, and reconciliation records. |
| Statistical support | 3.9 / 5 | Three seeds establish descriptive direction only. |
| Reproducibility | 4.8 / 5 | Frozen manifests, runtime identities, evaluator artifacts, and provider provenance are archived. |
| Writing and organization | 4.7 / 5 | Primary claims now use one coherent evidence source and distinguish all validation scopes. |
| Submission readiness | 4.6 / 5 | Scientific integration is complete; author metadata and live journal checks remain. |

**Overall: 4.6 / 5.** The paper is a credible SCI four-zone submission candidate after final administrative and target-journal formatting checks.

## Authoritative V81 evidence

| Modality | AP@[.50:.95] | AP50 | AP75 | AR1 | AR10 | AR100 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RGB-only | 0.4473 ± 0.0033 | 0.7674 ± 0.0036 | 0.4428 ± 0.0098 | 0.1650 ± 0.0009 | 0.5225 ± 0.0036 | 0.5897 ± 0.0024 |
| Thermal-only | 0.5196 ± 0.0196 | 0.8320 ± 0.0154 | 0.5776 ± 0.0244 | 0.2035 ± 0.0081 | 0.5826 ± 0.0148 | 0.6473 ± 0.0132 |
| Event-only | 0.1949 ± 0.0012 | 0.3657 ± 0.0032 | 0.1943 ± 0.0049 | 0.0751 ± 0.0033 | 0.2694 ± 0.0014 | 0.3558 ± 0.0067 |

The earlier V77/V80 author-supplied table remains a historical reconciliation artifact only. It is not used in the V82 abstract, primary tables, discussion, conclusion, or acceptance assessment.

## Remaining reviewer concerns

1. The component-disjoint validation partition participates in checkpoint retention.
2. The 837-image holdout is internal to the same provider archive.
3. The MM-UAV study uses supervised target-domain labels and an exposed devval split.
4. Three seeds do not support strong statistical inference.
5. A separately acquired sealed sensor-compatible test set is still absent.
6. No explicit dataset-archive license was located, so non-redistribution must remain.

## Final closure

- confirm final author, affiliation, corresponding-author, and ORCID metadata;
- check the live target-journal template and portal requirements immediately before upload;
- preserve the development-validation, internal-holdout, supervised exposed-devval, no-significance, no-physical-failure, 24,223-versus-30,634, no-competing-interests, and non-redistribution boundaries.

## V83 efficiency evidence addendum

V83 verified all nine authoritative V81 checkpoint identities and six exact-identity fusion controls, then completed 15 label-free RTX-3090 efficiency runs. Reliability-aware fusion adds only 1,684 parameters and approximately 0.630 profiler GFLOPs over matched early fusion; its synchronized full-detector latency is `22.2324 +/- 0.1879 ms` versus `22.0800 +/- 0.3082 ms`. Peak allocated memory is higher (`236.16 MiB` versus `122.49 MiB`), so the method should be described as having small parameter/FLOP/latency overhead but material memory overhead.

This corroborates the V82 efficiency interpretation but does not replace its stronger repeated timing table. V82 remains authoritative and unchanged. No dataset or locked-holdout content was accessed for V83.
