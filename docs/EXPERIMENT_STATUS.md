# Experiment Status

Updated: 2026-07-21

## Active task

`V64_MMUAV_SEED1_PAIRED_BBOX_ACTIVATION_CONFIRMATION_AUTHORIZED`

## User authorization

The user reported that V63 completed and was pushed. Under the standing automatic task-handoff workflow, V64 is authorized as the next bounded stage: an independent-initialization paired confirmation of the V63 ReLU-versus-Softplus mechanism.

The standing local/private-research instruction remains frozen and must not be repeatedly reconfirmed.

## V63 prerequisite evidence

- Completion commit: `83bb9351a5d0a6115d81047482e23fef5eed26bb`.
- Outcome: `V63_RELU_COLLAPSE_REPRODUCED_SOFTPLUS_PRESERVES_THROUGH_STEP200`.
- Seed-0 ReLU first met strict `EARLY_BBOX_COLLAPSE` at step 15.
- Seed-0 Softplus was `GEOMETRY_AND_GRADIENT_PRESERVED` at every scheduled trace through step 200.
- Step-200 valid train/devval boxes, ReLU versus Softplus: `0 / 272,000` versus `272,000 / 272,000`.
- Optimizer steps: `200 / 200`; diagnostic backward calls: `104 / 104`.
- Verified recovery snapshots: `26`; recovery events: `0`.
- All 11 post-run tests passed; no full devval, AP/AR, tuning, threshold selection, or checkpoint selection occurred.

## V64 paired confirmation

Run exactly, in order:

1. `v64_seed1_equal_relu_control` — fresh frozen seed-1 common initialization, native ReLU, 200 optimizer steps;
2. `v64_seed1_equal_softplus_b1_t20` — the same bit-identical seed-1 state, replacing only bbox-distance activation with exact `softplus(beta=1.0, threshold=20.0)`, 200 optimizer steps.

Both variants use the same V63 first-200 historical rows and order, enabled alignment, exact uniform equal fusion, dormant reliability scorer, historical zero bbox-output bias, FP32 AdamW configuration, and unchanged FCOS losses/matching/decode. The only paired difference is the activation.

V64 optimizer-step ceiling: **400 total**, exactly 200 per variant. Maximum diagnostic backward calls: **104**.

## Evidence and safety contract

- Generate the seed-1 common initialization exactly once before CUDA, serialize locally, hash and round-trip verify it, then freeze it for both variants.
- Trace steps: `0, 1, 2, 3, 5, 10, 15, 20, 30, 50, 100, 150, 200`.
- Save and verify an atomic local recovery snapshot before every trace.
- At step 200, trace only the frozen 32-row devval geometry subset.
- No trained V55-V63 checkpoint initialization, full 7,187-step run, full-devval evaluation, AP/AR, tuning, checkpoint selection, extra seed/variant, rerun, or automatic extension.
- Production TriAir behavior, V40-V63 evidence, V51, manuscript, and submission files remain protected.
- Heavy artifacts remain local and outside Git.

## Allowed completion states

- `V64_SEED1_RELU_COLLAPSE_REPRODUCED_SOFTPLUS_PRESERVES_THROUGH_STEP200`
- `V64_SEED1_RELU_AND_SOFTPLUS_BOTH_COLLAPSE`
- `V64_SEED1_RELU_COLLAPSE_REPRODUCED_SOFTPLUS_MIXED`
- `V64_SEED1_RELU_CONTROL_COLLAPSE_NOT_REPRODUCED_WITHIN_200_STEPS`
- `V64_BLOCKED_SOURCE_INITIALIZATION_OR_ACTIVATION_CONTRACT`
- `V64_BLOCKED_TRAINING_TRACE_OR_RECOVERY_INCOMPLETE`
- `V64_BLOCKED_OOM_OR_NUMERICAL_INSTABILITY`
- `V64_BLOCKED_TEST_OR_PROTECTED_FILE_VIOLATION`

A positive seed-1 confirmation is still bounded mechanistic evidence. It does not establish final accuracy, generalization, sole causality, or authorization for full training or AP/AR.