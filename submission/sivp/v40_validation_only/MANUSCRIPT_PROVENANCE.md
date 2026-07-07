# V40 manuscript provenance and evidence scope

## Evidence snapshot

- Split: V40-v2 expanded-adjacency component-disjoint validation.
- Manifests: 7,439 training images and 2,213 validation images.
- Validation ground-truth boxes: 5,867.
- Core comparison: matched early fusion versus pre-specified reliability-aware `p=0.15`.
- Fixed seeds: 0 and 2 for each model group.
- Core result commit: `12a4b1c5a06cb0b862e8ef797a87ac5cfe557991`.
- Post-core evidence commit: `b37db7025413dd80016ac5d23f63e8e1737472e6`.
- Readiness: `PRE_MANUSCRIPT_VALIDATION_ONLY_READY`.

## Evidence used in the manuscript

- V40-v2 split audit and manifests.
- Compute-minimized experiment contract amendment.
- Four-run two-seed summary.
- Synthetic channel-removal report.
- Efficiency report with raw-forward and detector-inference boundaries.
- 2,000-resample image-level bootstrap report.
- Deterministic qualitative selection protocol.
- TriAir provenance and availability ledger.

## Claims intentionally excluded

- Independent-test performance.
- External or cross-site generalization.
- Universal absence of data dependence.
- V40-optimal dropout probability.
- Causal isolation of reliability gating from modality-dropout training.
- Physical sensor-failure robustness.
- Dataset public availability or license terms.

## Author action items

1. Confirm funding, competing interests, author contributions, acknowledgments, and official affiliation wording.
2. Verify TriAir provider, public URL, license, version, access route, and redistribution terms before finalizing a data-availability statement.
3. Review the bibliography and final article text under the target journal's current author instructions.
