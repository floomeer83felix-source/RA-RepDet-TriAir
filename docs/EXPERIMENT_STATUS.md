# Experiment Status

Updated: 2026-07-18

## Active task

`V61_MMUAV_EARLY_BBOX_COLLAPSE_PREVENTION_PILOT_AUTHORIZED`

## User authorization

The user reported that V60 completed and was pushed. Under the standing automatic task-handoff workflow, V61 is authorized as the next bounded stage: a 500-step-per-variant paired pilot testing whether one fixed positive bbox-output bias initialization prevents the early V57 geometry/gradient collapse.

The standing local/private-research instruction remains frozen and must not be repeatedly reconfirmed.

## V60 prerequisite evidence

- V60 outcome: `V60_BBOX_COLLAPSE_PROVENANCE_AUDIT_COMPLETE_CAUSE_UNRESOLVED`.
- V55 and V57 initial FCOS bbox-regression weight/bias tensors were bit-identical.
- Initial V57 geometry was usable; collapse was not present at initialization.
- Final V57 equal and reliability states had zero valid decoded boxes and zero bbox output-layer gradients on the frozen probes.
- Final V57 states retained some positive pre-ReLU components, so the strict all-dead-ReLU definition was not met.
- Historical V57 bbox loss was exactly `1.0` on nearly all target-bearing rows and never strictly between zero and one.
- Historical logs lacked dense bbox-output and bbox-gradient fields, preventing exact first-collapse timing.

## V61 paired intervention

Run exactly, in order:

1. `v57_equal_control_instrumented` — exact historical V57 seed-0 equal-superset initialization and 500 optimizer steps;
2. `v57_equal_bbox_bias_p001` — the same state except the four-element final bbox-regression output bias is initialized once to exactly `+0.01`, followed by 500 optimizer steps.

Both variants use alignment enabled, fixed equal fusion, the same first 500 rows of the historical V57 order, and the historical FP32 AdamW configuration. The only paired scientific difference is the four-element initial bbox-output bias.

V61 optimizer-step ceiling: **1,000 total**, exactly 500 per variant.

## Dense evidence contract

At steps `0, 1, 2, 5, 10, 20, 50, 100, 200, 300, 400, 500`, record bbox losses, matched anchors, pre/post-ReLU distances, decoded geometry, output-layer parameter values and gradients, and fixed-subset valid/degenerate counts.

At each trace state, use the frozen four-row probe subset on an ephemeral model copy. At most 96 no-step backward probes are authorized. Probe work may not mutate the training state.

`EARLY_BBOX_COLLAPSE` requires both zero valid boxes on the frozen 32-row train subset and zero bbox output-layer gradients on all four frozen probe rows at the same trace. `GEOMETRY_AND_GRADIENT_PRESERVED` requires at least one valid box and at least one finite nonzero bbox output-layer gradient.

## Safety and claim boundary

- No bias sweep; the sole intervention is exact `+0.01`.
- No reliability-fusion training, activation/loss change, V57 checkpoint repair, or resume.
- No full 1,845-row devval evaluation and no AP/AR.
- No tuning, early stopping, checkpoint selection, extra seed, extra variant, rerun, or automatic budget extension.
- Production TriAir behavior, V40-V60 evidence, V51 evidence, manuscript, and submission files remain protected.
- Checkpoints and heavy artifacts remain local and outside Git.

A successful step-500 prevention result is single-seed early engineering evidence only. It does not authorize a full 7,187-step corrected run or any accuracy/fusion claim.

## Allowed completion states

- `V61_CONTROL_COLLAPSE_REPRODUCED_POSITIVE_BIAS_PREVENTS_THROUGH_STEP500`
- `V61_CONTROL_AND_POSITIVE_BIAS_BOTH_COLLAPSE`
- `V61_CONTROL_COLLAPSE_REPRODUCED_INTERVENTION_RESULT_MIXED`
- `V61_CONTROL_COLLAPSE_NOT_REPRODUCED_WITHIN_500_STEPS`
- `V61_BLOCKED_SOURCE_INITIALIZATION_ORDER_OR_INTERVENTION_CONTRACT`
- `V61_BLOCKED_TRAINING_OR_TRACE_INCOMPLETE`
- `V61_BLOCKED_OOM_OR_NUMERICAL_INSTABILITY`
- `V61_BLOCKED_TEST_OR_PROTECTED_FILE_VIOLATION`