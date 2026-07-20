# Experiment Status

Updated: 2026-07-20

## Active task

`V62_MMUAV_CLEAN_BBOX_BIAS_PAIRED_RERUN_AUTHORIZED`

## User authorization

The user explicitly selected V61 blocker repair option 2 and authorized V62 as a newly numbered clean paired pilot. V61 remains closed as `V61_BLOCKED_TRAINING_OR_TRACE_INCOMPLETE`; its partial control run is diagnostic-only evidence and may not be resumed, pooled with V62, or used to skip the V62 control run.

The standing local/private-research instruction remains frozen and must not be repeatedly reconfirmed.

## V61 prerequisite evidence

- V61 control completed 500 optimizer steps; the `+0.01` intervention completed 0 steps.
- The run failed during the control step-500 frozen devval geometry trace on `devval:00005919`.
- The trace path incorrectly reused a train-only target-transfer helper.
- No control checkpoint, optimizer state, RNG state, or exact recovery snapshot was saved.
- V61 training-log SHA256: `a96e0260079cbd05fd62fcc184a6908476490c42ecebe9b44373af4aebfd0965`.
- V57 common initialization SHA256 remained `846da59cc8d908dfeb429fca2acb4985e73ff5fda3915154f9f764c571977cb9`.
- V61 protected evidence remains immutable and cannot support a paired prevention conclusion.

## V62 trace-path correction

V62 must introduce a trace-specific, split-agnostic RGB-target tensor mover that accepts train and devval rows without weakening the historical train-only optimization guard. Before CUDA work, CPU tests must use the actual frozen failing row `devval:00005919`, verify exact boxes/labels preservation, verify that the optimization helper still rejects devval, and exercise the bounded geometry trace call chain.

## V62 clean pair

Run exactly, in order:

1. `v62_equal_control_instrumented` — exact historical V57 seed-0 common initialization, 500 optimizer steps;
2. `v62_equal_bbox_bias_p001` — the same initial state except the four-element final bbox-regression output bias is set once to exact `+0.01`, 500 optimizer steps.

Both variants use alignment enabled, exact equal fusion, dormant reliability scorer, the same first 500 rows of the frozen historical V57 order, and the historical FP32 AdamW configuration. Every initial tensor except the four intervention bias elements must be bit-identical.

V62 optimizer-step ceiling: **1,000 total**, exactly 500 per variant. This new authorization explicitly permits repeating the blocked V61 control budget, but no V61 trained state may be reused.

## Dense evidence and recovery contract

Trace steps are `0, 1, 2, 5, 10, 20, 50, 100, 200, 300, 400, 500`. Record bbox losses, matched anchors, pre/post-ReLU geometry, valid/degenerate boxes, output-layer parameters, and output-layer gradients. At most 96 no-step diagnostic backward calls are authorized.

Immediately before every trace, write and round-trip verify an atomic local technical recovery snapshot containing model, optimizer, RNG, order, step, log, and trace-ledger state. A technical restart is allowed only from an exact verified V62 snapshot and may not replay or skip optimizer steps.

At step 500, run only the frozen 32-row devval geometry subset through the corrected trace path. Do not run the complete 1,845-row devval set and do not compute AP/AR.

## Safety and claim boundary

- No bias sweep; the sole intervention is exact `+0.01`.
- No reliability-fusion training, activation/loss changes, V57/V61 checkpoint repair, or resume.
- No full 7,187-step run, full-devval evaluation, AP/AR, tuning, early stopping, checkpoint selection, extra variant, extra seed, or automatic budget extension.
- Production TriAir behavior, V40-V61 evidence, V51, manuscript, and submission files remain protected.
- Checkpoints, optimizer states, recovery snapshots, and heavy artifacts remain local and outside Git.

A positive step-500 prevention result is single-seed early engineering evidence only. It does not authorize a full corrected training run or an accuracy/reliability-fusion claim.

## Allowed completion states

- `V62_CONTROL_COLLAPSE_REPRODUCED_POSITIVE_BIAS_PREVENTS_THROUGH_STEP500`
- `V62_CONTROL_AND_POSITIVE_BIAS_BOTH_COLLAPSE`
- `V62_CONTROL_COLLAPSE_REPRODUCED_INTERVENTION_RESULT_MIXED`
- `V62_CONTROL_COLLAPSE_NOT_REPRODUCED_WITHIN_500_STEPS`
- `V62_BLOCKED_SOURCE_INITIALIZATION_ORDER_OR_TRACE_FIX_CONTRACT`
- `V62_BLOCKED_TRAINING_TRACE_OR_RECOVERY_INCOMPLETE`
- `V62_BLOCKED_OOM_OR_NUMERICAL_INSTABILITY`
- `V62_BLOCKED_TEST_OR_PROTECTED_FILE_VIOLATION`