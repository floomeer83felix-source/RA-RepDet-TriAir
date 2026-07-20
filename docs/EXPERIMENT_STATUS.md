# Experiment Status

Updated: 2026-07-20

## Active task

`V63_COMPLETE_NO_FURTHER_GPU_STAGE_AUTHORIZED`

## V63 result

V63 completed with the preregistered outcome:

`V63_RELU_COLLAPSE_REPRODUCED_SOFTPLUS_PRESERVES_THROUGH_STEP200`

The native torchvision FCOS ReLU control and the exact parameter-free
`softplus(beta=1.0, threshold=20.0)` intervention each completed 200 optimizer
steps on the same frozen V57 seed-0 initialization and first 200 historical
rows. ReLU first met strict `EARLY_BBOX_COLLAPSE` at step 15. Softplus was
`GEOMETRY_AND_GRADIENT_PRESERVED` at every scheduled trace through step 200.

At step 200, the ReLU control had `0 / 272,000` valid decoded boxes on both the
frozen 32-row train and 32-row devval geometry subsets. Softplus had
`272,000 / 272,000` valid decoded boxes on both subsets. On train FPN level 0,
the mean local derivative was `0.0271021` for ReLU with exact-zero fraction
`0.972898`, versus `0.418230` for Softplus with exact-zero fraction `0`.

## Safety and completion

- Optimizer steps: `400 / 400`, exactly `200 / 200` in the authorized order.
- Diagnostic backward calls: `104 / 104`.
- Verified recovery snapshots: `26`; recovery events: `0`.
- All losses, gradients, parameters, activations, geometry, and recovery metadata were finite.
- V62 evidence and the protected V40-V62/V51/production/manuscript/submission fingerprint remained unchanged.
- Frozen devval rows: 32 per variant; full-devval rows: 0.
- No AP/AR, tuning, threshold selection, checkpoint selection, extra variant, seed, or rerun occurred.
- Post-run V63 tests: `11 / 11` passed.

## Claim boundary

V63 supports the hard ReLU zero-derivative path as a necessary contributing
mechanism under this single-seed V57 training path. It does not prove ReLU is
the sole cause, establish final localization quality or AP/AR, or authorize a
full 7,187-step corrected run. No further GPU experiment is currently
authorized.
