# Experiment Status

Updated: 2026-07-20

## Active task

`V63_MMUAV_PAIRED_BBOX_ACTIVATION_RESCUE_PILOT_AUTHORIZED`

## User authorization

The user reported that V62 completed and was pushed. Under the standing automatic task-handoff workflow, V63 is authorized as the next bounded stage: a paired 200-step-per-variant pilot testing whether replacing the historical hard ReLU bbox-distance activation with exact parameter-free Softplus prevents the early V57 geometry-and-gradient collapse.

The standing local/private-research instruction remains frozen and must not be repeatedly reconfirmed.

## V62 prerequisite evidence

- V62 completion commit: `286508ff34d4cd0ac494d803e5a146a686318f14`.
- V62 outcome: `V62_CONTROL_AND_POSITIVE_BIAS_BOTH_COLLAPSE`.
- Both the historical ReLU control and exact `+0.01` bbox-output-bias intervention were preserved at steps 0, 1, and 2.
- Both first met strict `EARLY_BBOX_COLLAPSE` at step 20.
- Both ended step 500 with `0 / 272,000` valid train boxes and `0 / 272,000` valid frozen-devval boxes.
- The `+0.01` initial bias therefore did not prevent collapse.
- V62 completed `500 / 500` optimizer steps, `96 / 96` diagnostic backward calls, and 24 verified recovery snapshots with zero recovery events.
- No full devval, AP/AR, tuning, threshold selection, or checkpoint selection occurred.

## V63 paired intervention

Run exactly, in order:

1. `v63_equal_relu_control` — exact historical V57 seed-0 equal-superset state and ReLU bbox-distance activation, 200 optimizer steps;
2. `v63_equal_softplus_b1_t20` — the same bit-identical state, replacing only the bbox-distance activation with `softplus(beta=1.0, threshold=20.0)` in both training and inference paths, 200 optimizer steps.

Both variants use alignment enabled, exact uniform equal fusion, dormant reliability scorer, the same first 200 rows of the frozen historical V57 order, historical FP32 AdamW settings, and the unchanged historical bbox-output bias. The sole paired scientific difference is the parameter-free activation.

V63 optimizer-step ceiling: **400 total**, exactly 200 per variant.

## Dense evidence contract

Trace steps are `0, 1, 2, 3, 5, 10, 15, 20, 30, 50, 100, 150, 200`.

At each trace, record pre/post-activation geometry, valid/degenerate boxes, matched anchors, bbox losses, bbox-output and regression-tower gradients, and activation local-derivative summaries. Use the frozen four-row probe subset on fresh ephemeral copies, with at most 104 no-step backward calls total.

Before every trace, atomically save and round-trip verify exact local recovery state. At step 200, run only the frozen 32-row devval geometry subset. Do not run full devval and do not compute AP/AR.

`EARLY_BBOX_COLLAPSE` retains the frozen definition: zero valid train boxes and zero bbox-output weight/bias gradients on all four probe rows at the same trace. `GEOMETRY_AND_GRADIENT_PRESERVED` requires at least one valid train box and at least one finite nonzero bbox-output gradient.

## Safety and claim boundary

- No bias intervention or sweep; both variants keep the historical common-initialization bias.
- No loss, target, matcher, anchor, scale, decode, clipping, threshold, NMS, preprocessing, detector, evaluator, or fusion changes.
- No reliability-fusion training, full 7,187-step run, full-devval evaluation, AP/AR, tuning, early stopping, checkpoint selection, extra variant/seed, rerun, or automatic budget extension.
- Production TriAir behavior, V40-V62 evidence, V51, manuscript, and submission files remain protected.
- Checkpoints, optimizer states, recovery snapshots, and heavy artifacts remain local and outside Git.

A Softplus rescue is single-seed early mechanistic evidence only. It may support hard ReLU zero-derivative behavior as a necessary contributor, but it does not establish the sole cause, final localization quality, accuracy, or authorization for a full corrected run.

## Allowed completion states

- `V63_RELU_COLLAPSE_REPRODUCED_SOFTPLUS_PRESERVES_THROUGH_STEP200`
- `V63_RELU_AND_SOFTPLUS_BOTH_COLLAPSE`
- `V63_RELU_COLLAPSE_REPRODUCED_SOFTPLUS_MIXED`
- `V63_RELU_CONTROL_COLLAPSE_NOT_REPRODUCED_WITHIN_200_STEPS`
- `V63_BLOCKED_SOURCE_INITIALIZATION_OR_ACTIVATION_CONTRACT`
- `V63_BLOCKED_TRAINING_TRACE_OR_RECOVERY_INCOMPLETE`
- `V63_BLOCKED_OOM_OR_NUMERICAL_INSTABILITY`
- `V63_BLOCKED_TEST_OR_PROTECTED_FILE_VIOLATION`
