# V48 Causal Ablation Claim Boundary

## Permitted interpretation

- All V48 comparisons are descriptive development-validation contrasts under the frozen V40 component-disjoint protocol.
- `early_moddrop - matched_early` is the architecture-specific training-time modality-dropout contrast for early fusion.
- `ra_full_p015 - ra_no_moddrop` is the training-time modality-dropout contrast within the reliability-aware architecture.
- `ra_static_equal - matched_early` combines modality-specific stems and fixed equal-weight feature fusion.
- `ra_no_moddrop - ra_static_equal` is the cleanest available dynamic-gating contrast beyond equal-weight stem fusion.
- `ra_stems_project` is a deterministic learned fixed-order fusion control; it does not isolate modality-specific stems alone.

## Required limitations

- Report only the completed shared seed coverage with descriptive means and sample SDs.
- Do not treat this same-dataset development-validation evidence as external or independent validation.
- Do not infer a universal dropout choice, calibrated reliability, sensor-health probabilities, or real fault behavior.
- The locked holdout was not used for V48 training, selection, continuation, or reporting.
