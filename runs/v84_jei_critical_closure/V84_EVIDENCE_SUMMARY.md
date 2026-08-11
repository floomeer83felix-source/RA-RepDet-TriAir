# V84 JEI Critical Evidence Summary

Status: evidence computation complete; manuscript source integrated after freeze.

## Evidence Completed

- P0 passed the frozen split and 21-checkpoint identity preflight.
- P1 trained RGB+thermal seeds 0/1/2 for 50 epochs. Mean COCO AP is
  `0.6843 +/- 0.0312`, AP50 `0.9401 +/- 0.0044`, AP75 `0.8223 +/- 0.0250`,
  and AR100 `0.7614 +/- 0.0224`.
- P2 completed all 48 gate-by-dropout channel-removal evaluations. Full-input
  gate main effect is `+0.0382` AP. Under event removal, the gate main effect is
  `-0.1494`, dropout main effect `+0.2214`, and interaction `+0.3521`.
- P3 completed 30 clean/corruption evaluations and exported 6,639 clean
  sample/checkpoint weight rows. No affected-modality gate weight decreases
  monotonically across all three corruption severities.
- P4 completed 12 checkpoint evaluations and 5,000 bootstrap replicates over
  1,298 final V40 validation components. Component-macro AP intervals are
  positive for gate/no-dropout versus matched early `[0.0376, 0.0464]`, fixed
  equal stems `[0.0452, 0.0539]`, and learned projection `[0.0269, 0.0351]`.
- P5 stopped transparently: pinned TriModalDet cannot satisfy the frozen split,
  evaluator, checkpoint-selection, and license contract without substantial
  unvalidated adaptation. No cross-protocol number is reported.
- P7 freezes exact MM-UAV sequence manifests, annotation conversion, geometry,
  training/evaluation rules, and the exact interpretation of the 99.20% copied
  destination parameter/buffer fraction. No new MM-UAV training was run.
- P6 was not run: it is optional, and all required three-seed evidence was complete.
- P9 was not run. The locked 837-image internal holdout was not accessed in V84.

## Claim Effects

### Strengthened

- Dynamic gating improves nominal development-validation performance beyond
  matched early fusion, fixed equal stems, and learned deterministic projection.
- The three primary dynamic-gate contrasts remain positive under descriptive
  component-cluster bootstrap.
- MM-UAV supervised exposed-devval transfer is now documented at sequence,
  geometry, transfer-map, seed, and final-checkpoint levels.

### Weakened Or Narrowed

- RGB+thermal AP (`0.6843`) is slightly above five-channel matched early AP
  (`0.6803`); a positive isolated event-input contribution is not established.
- Missing-event robustness is mainly associated with modality-dropout training
  and its interaction with gating, not with the dynamic gate alone.
- Controlled degradation does not produce monotonic down-weighting of the
  degraded modality. Gate weights are task-driven fusion coefficients, not
  calibrated physical reliability or sensor-health probabilities.
- No same-protocol published comparator result is available, so no SOTA or
  published-method superiority claim is supported.

### Unchanged

- All TriAir headline evidence remains development-validation evidence because
  that partition participates in checkpoint retention.
- MM-UAV remains supervised target-domain adaptation on exposed devval, not
  blind zero-shot generalization.
- No statistical-significance, physical sensor-failure, or independent external
  generalization claim is authorized.
