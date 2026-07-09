# V41 SIVP Replacement Text for Validation-Only Revision

Generated: 2026-07-09

Use this file as the controlled source for revising `submission/sivp/tex/ra_repdet_sivp.tex`. Do not paste claims stronger than the wording below unless new evidence is added and documented.

## Proposed Abstract

Lightweight vehicle detection from unmanned-aerial-vehicle imagery benefits from complementary sensing, but multi-modal fusion results can be difficult to interpret when evaluation splits contain visually related samples or when validation evidence is overstated as deployment robustness. This paper studies a compact RGB--thermal--event detector based on a RepViT--FPN--FCOS stack and compares a matched early-fusion front end with a reliability-aware front end using modality-specific stems, softmax fusion, and modality-dropout training. The evaluation is intentionally scoped to a frozen component-disjoint development-validation protocol for a locally represented TriAir dataset. Across three paired seeds, reliability-aware fusion with modality dropout p=0.15 improves the matched early-fusion baseline by descriptive mean deltas of +0.0185 F1, +0.0161 AP50, and +0.0647 AP75 using project-local AP metrics. The model adds only a small number of front-end parameters relative to the shared detector stack. We also document the validation-only boundary, split-audit provenance, and limitations of the evidence, including the absence of an independent held-out test, COCO AP50:95 evaluation, and physical sensor-failure experiments. The resulting study provides an auditable validation-only assessment of reliability-aware tri-modal fusion for lightweight UAV vehicle detection.

## Proposed Contribution List

\begin{enumerate}
    \item We present a lightweight RGB--thermal--event UAV vehicle detector that combines modality-specific stems, softmax reliability-aware fusion, a RepViT-M0.9 backbone, FPN, and FCOS head, together with a matched early-fusion baseline using the same detector stack.
    \item We evaluate the reliability-aware p=0.15 configuration against matched early fusion under a frozen V40 component-disjoint development-validation protocol using three paired seeds, while explicitly reporting the validation-only claim boundary.
    \item We provide seed-level results, paired deltas, and descriptive mean \(\pm\) sample standard deviation for Precision, Recall, F1, AP50, and AP75, with AP50/AP75 treated as project-local single-class metrics rather than COCO AP50:95.
    \item We document split integrity, source traceability, checkpoint hashes, and unresolved data-governance limitations so that the manuscript's claims remain aligned with the available evidence.
\end{enumerate}

## Proposed Results Paragraph

The primary comparison is the matched early-fusion baseline versus the reliability-aware p=0.15 configuration on the frozen V40 component-disjoint development-validation split. Across seed0, seed1, and seed2, the reliability-aware configuration records positive descriptive paired deltas for F1, AP50, and AP75 in every seed. The mean paired deltas across the three seed pairs are +0.018524 F1, +0.016064 AP50, and +0.064657 AP75, with sample standard deviations of 0.006208, 0.005699, and 0.016415, respectively. Precision improves on average by +0.011629, although seed2 has a negative precision delta, while recall improves on average by +0.024487. These results support the reliability-aware p=0.15 front end as the stronger configuration under this development-validation protocol, but they do not constitute independent-test, statistical-significance, or external-generalization evidence.

## Proposed Limitations Paragraph

This study is intentionally validation-only. The main evidence consists of three paired seeds on a frozen component-disjoint development-validation split, and the reported mean \(\pm\) sample standard deviation values are descriptive rather than a statistical-significance analysis. No independent held-out test set, external dataset, or COCO AP50:95 evaluation is included. The current comparison also evaluates a combined reliability-aware front end and modality-dropout training configuration; it does not fully separate the causal contributions of separate stems, dynamic gating, and dropout. Synthetic channel removal, where reported, should be interpreted only as zero-channel stress testing and not as physical RGB, thermal, or event sensor-failure robustness. Finally, TriAir provider, version, license, redistribution rights, synchronization details, and a complete label-quality review remain author-confirmation or future-work items.

## Proposed Conclusion Paragraph

RA-RepDet demonstrates that a lightweight reliability-aware RGB--thermal--event fusion front end can improve a matched early-fusion baseline under a frozen component-disjoint development-validation protocol. Across three paired seeds, the reliability-aware p=0.15 configuration shows positive descriptive mean deltas for F1, AP50, and AP75 while preserving a compact detector design. The study's contribution is therefore an auditable validation-only assessment of tri-modal fusion rather than a claim of independent-test generalization or physical sensor-failure robustness. Future work should add an independent locked test set, COCO-style metrics, stronger causal ablations, external or cross-scene validation, and completed data-provenance and label-quality audits.

## Required Manuscript Table Insertion

Insert or replace the current main results table with:

```latex
\input{../tables/Table_8_three_seed_interim_devval.tex}
```

Recommended caption if not using the bundled table environment:

```latex
\caption{Three-seed interim development-validation summary on the frozen V40 component-disjoint split. Values are project-local AP50/AP75 and descriptive only.}
```

## Text That Must Not Remain as Headline

The following statements may remain only as explicitly labeled historical context, not as the manuscript's active headline:

- R4 p=0.20 is the main manuscript variant.
- The main evidence is seed0/seed2 only.
- The split is block64/guard16 rather than V40 component-disjoint.
- Missing-modality results establish real sensor-failure robustness.
- Gate weights are calibrated sensor reliability.
