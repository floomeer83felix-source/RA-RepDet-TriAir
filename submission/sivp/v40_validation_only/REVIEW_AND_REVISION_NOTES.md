# Reviewed manuscript changes

This review revises the V40 validation-only draft without adding experiments or changing the evidence package.

## Changes made

- Replaced reader-facing internal V40/V39 labels with `component-disjoint validation`; internal labels remain only in provenance artifacts.
- Shortened the title and made the split method explicit in the protocol instead of the title.
- Reframed the core comparison as a system-level contrast between matched early fusion and pre-specified reliability-aware `p=0.15`; no optimal-dropout or sweep claim is permitted.
- Made the split scope more exact: exact RGB, locked perceptual-hash candidates, and human-adjudicated adjacent-or-near-identical relations are component-disjoint; filename proximity is not treated as verified temporal metadata.
- Standardized the evaluation description: project-local single-class AP50/AP75, score threshold 0.001, F1 operating threshold 0.50, and no COCO AP50:95 claim.
- Clarified that bootstrap intervals are conditional on fixed checkpoints and the validation partition and are descriptive rather than selection tests.
- Clarified that channel removal is deterministic zero-channel evaluation, not physical sensor-failure evidence.
- Clarified that reliability-aware fusion has slightly higher latency and memory use and must not be called faster.
- Recorded the missing trained single-modality and static nonadaptive fusion controls as limitations.
- Repaired the broken `Table 4` cross-reference in the synthetic-channel-removal subsection.

## Required author decisions before submission

Confirm funding, competing interests, author contributions, acknowledgments, official affiliation wording, TriAir provider, public URL, license, version, access route, and redistribution terms.
