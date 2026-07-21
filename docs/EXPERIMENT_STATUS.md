# Experiment Status

Updated: 2026-07-21

## Active task

`V64_COMPLETE_NO_FURTHER_GPU_STAGE_AUTHORIZED`

## V64 result

V64 completed with the preregistered outcome:

`V64_SEED1_RELU_CONTROL_COLLAPSE_NOT_REPRODUCED_WITHIN_200_STEPS`

One fresh seed-1 common initialization was generated exactly once, serialized
locally, round-trip verified, and frozen with SHA256
`50612d58789b935ed8345494a7830a64d07b83c841ac9b6d24bcda3ea3f2c476`.
Both paired models loaded this state strictly and were bit-identical before the
parameter-free activation difference.

The seed-1 native ReLU control and exact
`softplus(beta=1.0, threshold=20.0)` intervention each completed 200 optimizer
steps. Both were `GEOMETRY_AND_GRADIENT_PRESERVED` at every scheduled trace
through step 200. Therefore the V63 seed-0 ReLU collapse was not independently
reproduced within the V64 budget.

At step 200, ReLU had `271,931 / 272,000` valid train boxes and
`271,930 / 272,000` valid frozen-devval boxes. Softplus had
`272,000 / 272,000` valid boxes on both subsets. On train FPN level 0, ReLU's
mean local derivative was `0.996676` with exact-zero fraction `0.00332397`;
Softplus was `0.427073` with exact-zero fraction `0`.

## Safety and completion

- Optimizer steps: `400 / 400`, exactly `200 / 200` in the authorized order.
- Diagnostic backward calls: `104 / 104`.
- Verified recovery snapshots: `26`; recovery events: `0`.
- Initialization candidates generated: exactly `1`; no regeneration or checkpoint initialization occurred.
- All losses, gradients, parameters, activations, geometry, and recovery metadata were finite.
- V63 evidence and the protected V40-V63/V51/production/manuscript/submission fingerprint remained unchanged.
- Frozen devval rows: 32 per variant; full-devval rows: 0.
- No AP/AR, tuning, threshold selection, checkpoint selection, extra variant, seed, or rerun occurred.
- Post-run V64 tests: `10 / 10` passed.

## Claim boundary

V64 does not provide independent-initialization confirmation of the V63
seed-0 collapse/rescue contrast because the seed-1 ReLU control did not
collapse. The result instead demonstrates initialization sensitivity within
the bounded 200-step path. It does not refute the V63 seed-0 observation,
establish sole causality, final localization quality, generalization, or AP/AR,
and it does not authorize a full 7,187-step run. No further GPU experiment is
currently authorized.
