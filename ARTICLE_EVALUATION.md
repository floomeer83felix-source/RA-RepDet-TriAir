# RA-RepDet manuscript evaluation - V75

## Overall recommendation

**Major revision before submission, with materially improved evidence readiness.** The corrected V73 seed-level records now reproduce the reported means, sample standard deviations, and paired directions. This closes the most serious traceability gap in V74. The paper's remaining limitations are the validation-only TriAir design, only two TriAir runs, unresolved canonical dataset citations, and author metadata/declaration closure.

This assessment uses general standards for signal, image, video, and machine-learning journals. It is not an official decision from the current SIVP editorial system.

## Scorecard

| Dimension | Score | Assessment |
| --- | ---: | --- |
| Novelty and relevance | 4.0 / 5 | Lightweight RGB-thermal-event reliability fusion and leakage-aware UAV validation remain relevant and reasonably distinctive. |
| Method clarity | 4.2 / 5 | Architecture, dropout, split construction, transfer protocol, and scientific boundaries are clearly documented. |
| Experimental rigor | 3.6 / 5 | MM-UAV now has three corrected seeds and matched paired comparisons; TriAir remains two-run and validation-only. |
| Evidence traceability | 4.2 / 5 | Corrected seed-level rows, arithmetic summaries, and paired differences are now directly auditable. |
| Statistical support | 3.5 / 5 | Direction is consistent across three MM-UAV seeds, but n=3 is too small for strong inference and the exposed devval split limits interpretation. |
| Reproducibility | 4.2 / 5 | Frozen protocols, manifests, scripts, corrected rows, and traceability artifacts provide a strong reproducibility framework. |
| Writing and organization | 4.3 / 5 | The revised narrative clearly separates in-domain validation, zero-shot failure, and supervised transfer. |
| Submission readiness | 3.4 / 5 | Dataset citations, declarations, and final metadata remain unresolved. |

**Overall: 3.9 / 5 - technically credible and substantially improved, but still requires submission closure.**

## Main strengths

1. Evaluation leakage is addressed with a component-disjoint split rather than a random split.
2. The primary model comparison holds the downstream detector fixed.
3. TriAir project-local metrics and MM-UAV COCO metrics are clearly separated.
4. The cross-dataset study separates unregistered frozen failure from supervised alignment-aware recovery.
5. Corrected V73 results are now reproducible from nine explicit seed-level rows.
6. AP gains from initialization and reliability-aware fusion are positive in all three paired seeds.
7. The manuscript retains appropriate limits: target labels and an exposed devval split are used.

## Major reviewer concerns that remain

### 1. The main TriAir claim is validation-only

The same component-disjoint validation partition participates in checkpoint retention and final reporting. This is stronger than a leaky random split, but not an independent test. Image-level bootstrap intervals do not remove checkpoint-selection or training-run uncertainty.

### 2. Causal attribution remains limited

The reliability-aware system differs from early fusion in both fusion architecture and modality-dropout training. The gain cannot be attributed uniquely to the reliability gate without additional equal-stem/static-weight/dropout controls.

### 3. Replication remains uneven

MM-UAV now has three corrected seeds, but the TriAir headline comparison uses only two fixed runs. Broader stability claims should remain avoided.

### 4. Dataset citation and dissemination status require closure

Verified canonical citations for TriAir and MM-UAV are still missing. MM-UAV redistribution status remains unresolved; the current non-redistribution language is appropriately cautious.

### 5. External generalization remains unproven

The zero-shot adapter is deliberately unregistered, and the supervised benchmark uses MM-UAV labels plus an exposed devval split. The results support supervised adaptation under one protocol, not sensor-independent robustness.

## Interpretation of the corrected V73 evidence

The corrected arithmetic is internally coherent. Scratch Equal reaches `0.2210 +/- 0.0030` AP. TriAir initialization adds `0.0130 +/- 0.0010` AP and is positive in each seed. Reliability-aware fusion adds a further `0.0163 +/- 0.0006` AP over initialized equal fusion and is also positive in each seed. The combined gain over scratch is `0.0293 +/- 0.0006` AP. This is strong descriptive consistency, but three paired seeds do not justify a universal or statistically significant superiority claim.

## Must complete before submission

1. Confirm competing interests and author/institution metadata.
2. Insert verified canonical TriAir and MM-UAV citations.
3. Confirm lawful data-access and dissemination wording.
4. Perform a final independent cross-check of the PDF tables against the V75 CSV/JSON files.
5. Preserve the validation-only and supervised exposed-devval boundaries.

## Acceptance outlook

The manuscript is now technically more persuasive because the corrected transfer conclusion is supported by explicit seed-level evidence rather than an aggregate-only correction. With citation and declaration closure, it is a plausible journal submission. Reviewers are still likely to request stronger TriAir replication, clearer causal controls, or an independent test set, so a major-revision outcome remains more likely than immediate acceptance.
