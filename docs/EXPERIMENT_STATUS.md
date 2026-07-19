# Experiment Status

Updated: 2026-07-19

## Active task

`V61_BLOCKED_TRAINING_OR_TRACE_INCOMPLETE`

## Execution state

V61 passed CPU preparation and all eleven pre-CUDA contract tests, with one expected CUDA-result test skipped. The GPU run then completed all 500 authorized optimizer steps for `v57_equal_control_instrumented` but failed during the step-500 devval geometry trace before the control checkpoint and recovery state were saved. The intervention variant executed zero optimizer steps.

The failure occurred because the V61 geometry helper reused the historical optimization-only `target_to_device` helper. That helper rejects rows whose ID does not start with `train:`; the first frozen devval row was `devval:00005919`.

## Consumed budget

- Control optimizer steps: `500 / 500`.
- Positive-bias optimizer steps: `0 / 500`.
- Total optimizer steps: `500 / 1,000`.
- Completed diagnostic backward probes: `44 / 96`.
- Completed persisted trace markers: steps `0, 1, 2, 5, 10, 20, 50, 100, 200, 300, 400` for control.
- V61 checkpoints or optimizer recovery snapshots: `0`.

## Partial engineering observations

These observations are not a paired V61 outcome. Control valid boxes on the frozen 32-row train geometry traces fell from `19,038` at step 1 to `192` at step 10 and `0` at steps 20, 100, 200, 300, and 400, with `2` at step 50. The 500-row training log is complete and has SHA256 `a96e0260079cbd05fd62fcc184a6908476490c42ecebe9b44373af4aebfd0965`. The bbox output gradient was already zero on the historical training row at step 1, was nonzero at step 2, and was zero at the selected rows from step 10 onward. No strict paired prevention classification is permitted because the control step-500 trace was not completed and the intervention was never run.

## Safety

- No full-devval evaluation or AP/AR was run.
- No threshold selection, tuning, bias sweep, checkpoint selection, or rerun occurred.
- The common initialization remains byte-identical at SHA256 `846da59cc8d908dfeb429fca2acb4985e73ff5fda3915154f9f764c571977cb9`.
- Protected V40-V60 evidence, V51, production TriAir, manuscript, and submission fingerprints remain unchanged.
- No heavy artifact or checkpoint is present in the repository.

## Authorization boundary

Do not restart V61 automatically. A clean paired rerun would repeat the already consumed 500 control steps and therefore requires a new explicit authorization after the devval target-transfer bug is corrected and tested. The existing partial log remains diagnostic-only blocked evidence.
