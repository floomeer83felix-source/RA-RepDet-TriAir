# RA-RepDet manuscript evaluation

## Overall recommendation

**Major revision before submission.** The manuscript now has a coherent narrative and the corrected MM-UAV results are integrated consistently. Its strongest elements are the leakage-aware component-disjoint validation design, the matched lightweight detector comparison, the explicit zero-shot-versus-supervised transfer separation, and careful claim boundaries. The principal remaining weakness is evidence traceability: the corrected V73 aggregate values materially reverse the earlier interpretation, but corrected seed-level records are not available for independent arithmetic or paired analysis.

This assessment uses general standards for signal, image, video, and machine-learning journals rather than a live verification of the current SIVP submission portal.

## Scorecard

| Dimension | Score | Assessment |
| --- | ---: | --- |
| Novelty and relevance | 4.0 / 5 | Lightweight RGB-thermal-event reliability fusion and leakage-aware UAV validation are relevant and reasonably distinctive. |
| Method clarity | 4.1 / 5 | Architecture, dropout, detector interface, split construction, and evaluation boundaries are clearly described. |
| Experimental rigor | 3.3 / 5 | Matched controls and deterministic protocols are strong, but TriAir uses only two seeds and validation-only reporting. |
| Evidence traceability | 3.0 / 5 | TriAir evidence is well documented; corrected V73 aggregates cannot be reproduced without corrected seed-level records. |
| Statistical support | 3.1 / 5 | Bootstrap intervals help characterize image-level uncertainty but do not replace training-seed variability; MM-UAV claims are aggregate-only. |
| Reproducibility | 4.0 / 5 | Frozen manifests, protocol details, hashes, scripts, and explicit exclusions provide a strong framework. |
| Writing and organization | 4.2 / 5 | The revised paper is readable, logically structured, and appropriately cautious. |
| Submission readiness | 3.0 / 5 | Canonical dataset citations, competing interests, access language, and V73 seed-level provenance remain unresolved. |

**Overall: 3.6 / 5 - promising, but not submission-ready without major evidence and metadata closure.**

## Main strengths

1. The component-disjoint split addresses exact and near-duplicate leakage more seriously than a random split.
2. Both primary systems share the RepViT-FPN-FCOS detector, reducing downstream architectural confounding.
3. Project-local TriAir AP50/AP75 are clearly separated from COCO-style MM-UAV metrics.
4. Frozen naive-grid failure and supervised feature alignment form a useful two-stage transfer analysis.
5. The manuscript explicitly avoids independent-test and sensor-fault claims that the evidence cannot support.
6. Efficiency reporting acknowledges higher latency and substantially higher peak memory for reliability-aware fusion.

## Major issues likely to be raised by reviewers

### 1. Corrected V73 traceability is incomplete

The corrected aggregate values reverse the scientific conclusion: source initialization and reliability-aware fusion now improve performance. Because corrected per-seed records are unavailable, reviewers cannot reproduce the means and standard deviations, inspect seed consistency, or verify paired comparisons. The manuscript correctly omits the invalidated table, but the evidence gap remains material.

**Required resolution:** provide corrected per-seed metric records, checkpoint identities, and a regenerated arithmetic audit before making consistency or significance claims. Until then, retain descriptive wording.

### 2. The main TriAir result is validation-only

The same component-disjoint validation partition participates in checkpoint retention and final reporting. This is stronger than a leaky random split but is not an independent test. Image-level bootstrap intervals do not capture checkpoint-selection bias or full training variability.

### 3. Causal attribution of the reliability gate is limited

The reliability-aware system differs from matched early fusion in both architecture and training intervention because modality dropout is used only for the reliability model. The gain cannot be attributed uniquely to input-conditioned gating.

**Recommended future controls:** equal-weight modality stems, static learned global weights, reliability gating without modality dropout, and modality dropout with a non-gated stem-fusion control.

### 4. Replication is limited

The TriAir headline comparison uses two fixed seeds. Two runs are insufficient for a robust stability claim. The manuscript appropriately avoids broad stability language.

### 5. Dataset citation and dissemination status are unresolved

Canonical citations for TriAir and MM-UAV require verification. MM-UAV public availability or redistribution must not be asserted while dissemination status remains unresolved.

### 6. External generalization remains unproven

The zero-shot adapter is intentionally unregistered and the supervised benchmark uses MM-UAV labels plus an exposed devval split. The cross-dataset section supports supervised adaptation under one protocol, not sensor-independent robustness.

## Secondary editorial issues

- A shorter title option is: **RA-RepDet: Reliability-Aware RGB-Thermal-Event Fusion with Leakage-Aware Validation and Supervised Cross-Dataset Transfer.**
- Figure 5 and Table 7 are partly redundant, though the figure is useful for rapid comparison.
- Table 6 could move to supplementary material if page limits are tight.
- Use thermal for TriAir and infrared for MM-UAV consistently, with one terminology note.
- Confirm the manually embedded bibliography against the final submission workflow.
- Replace the competing-interests placeholder with an author-approved declaration.

## Must complete before submission

1. Confirm competing interests and institutional metadata.
2. Insert verified TriAir and MM-UAV citations.
3. Confirm lawful data-access and dissemination wording.
4. Provide corrected V73 seed-level evidence or explicitly disclose aggregate-only availability.
5. Perform a final independent number audit against the authoritative correction record.

## Acceptance outlook

The core paper is technically credible and well scoped. With complete V73 provenance, verified dataset citations, and finalized declarations, it would be a plausible journal submission. Without those closures, the most likely editorial outcome is a request for major revision because the corrected result changes the central transfer conclusion but lacks seed-level auditability.
