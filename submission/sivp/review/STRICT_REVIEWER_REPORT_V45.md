# Strict Pre-Submission Reviewer Report V45

Generated: 2026-07-09

## Simulated decision

**Major revision risk remains, but the manuscript is now suitable for formal pre-submission consideration if the authors accept a bounded within-dataset claim.**

The manuscript is technically clearer than the earlier versions because the V42 locked held-out guard evidence has been integrated. However, from a strict SIVP reviewer perspective, the study still has several limitations that should be visible rather than hidden: the guard partition is within TriAir, the held-out gains are small, per-seed guard F1/AP75 deltas are mixed, AP50/AP75 are project-local rather than COCO metrics, and the method is not causally ablated.

## Major concerns and required handling

### 1. Same-dataset held-out evidence is not external validation

The paper may now move beyond validation-only language, but the guard partition is still from the same TriAir project dataset. Therefore, the manuscript must not call this an external test, independent public benchmark, or proof of generalization.

**Modification made:** The abstract was tightened to say “locked same-dataset held-out guard check” and “bounded within-dataset assessment.”

### 2. Held-out guard gains are small and mixed by seed

The held-out mean gains are positive, but they are substantially smaller than development-validation gains. In addition, seed0 F1 decreases and seed2 AP75 decreases. A strict reviewer would object if the abstract simply claimed that the method improves on held-out testing without noting this mixed behavior.

**Modification made:** The abstract now explicitly states that the guard gains are smaller and that per-seed F1/AP75 deltas are mixed.

### 3. Statistical language must remain descriptive

The manuscript reports three seed pairs only. Mean and sample standard deviation are useful, but they are not sufficient for statistical-significance claims.

**Required wording:** Use “descriptive mean gains,” “paired deltas,” and “within-dataset evidence.” Do not use “significant,” “proved,” “generalizes,” or “robust to sensor failure.”

### 4. Project-local AP metrics must be named as such

AP50/AP75 are not COCO AP@[0.50:0.95]. A reviewer will expect this distinction to be visible in the abstract and results.

**Modification retained:** The abstract and method/results wording keep “project-local AP metrics.”

### 5. Causal contribution of the fusion components remains unresolved

The current comparison evaluates a combined reliability-aware front end plus modality-dropout training configuration. It does not isolate stems, gating, and dropout.

**Required handling:** Keep this as a limitation; do not imply that the gate alone caused the held-out improvement.

### 6. Figures are acceptable for review but not visually polished

The simple schematic/table figures remove explicit placeholders, but polished vector artwork would improve perceived manuscript quality.

**Recommendation:** Optional before submission, but not scientifically required.

## Revised reviewer judgement after modifications

The current version is defensible for SIVP as an engineering-validation manuscript if the authors accept likely major revision. The evidence is stronger than a validation-only report because it includes a locked same-dataset held-out guard evaluation, but it remains weaker than a paper with external test data, COCO metrics, and causal ablations.

## Final claim boundary

Allowed:

> Component-disjoint development-validation evidence plus locked same-dataset held-out TriAir guard evaluation, using descriptive three-seed paired comparisons between matched early fusion and reliability-aware p=0.15.

Disallowed:

> External dataset generalization, independent public benchmark test, statistical significance, optimal dropout, calibrated physical sensor reliability, real sensor-fault robustness, or COCO AP@[0.50:0.95].
