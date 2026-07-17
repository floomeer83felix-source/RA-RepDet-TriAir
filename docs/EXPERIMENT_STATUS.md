# Experiment Status

Updated: 2026-07-17

## Active task

`V60_MMUAV_BBOX_COLLAPSE_PROVENANCE_AUDIT_AUTHORIZED`

## User authorization

The user reported that V59 completed and was pushed. Under the established automatic task-handoff workflow, V60 is authorized as the next bounded diagnostic stage: determine how the V57 bbox-regression geometry collapse arose before any corrective training is considered.

The standing local/private-research instruction remains frozen and must not be repeatedly reconfirmed.

## V59 prerequisite evidence

- V59 outcome: `V59_STREAMING_ZERO_DETECTION_DIAGNOSIS_COMPLETE_ROOT_CAUSE_IDENTIFIED`.
- Primary task classification: `EVALUATOR_OR_OUTPUT_SCHEMA_MISMATCH`.
- Direct mechanism: `V57_BBOX_REGRESSION_DEGENERATE_GEOMETRY`.
- V57 equal/reliability valid decoded boxes: `0 / 0`.
- V57 equal/reliability degenerate decoded candidates: `5,534,979 / 5,535,000`.
- V55 alignment-on reference valid/degenerate decoded candidates: `5,535,000 / 0`.
- Foreground scores were well above the frozen threshold in all three models; threshold, top-k, NMS, label filtering, checkpoint loading, preprocessing, and model mode were excluded as causes.
- V57 bbox-regression biases were non-positive and feed torchvision's ReLU distance head; V55 final bbox biases were positive.
- V59 did not prove whether collapse was present at initialization or emerged during training.

## Frozen evidence contracts

- Train/devval rows: `7,187 / 1,845`.
- Train SHA256: `e81973b95dd6fd5ce2d3c5de526310a3bef083df49b8db584fdf39b78a34d67a`.
- Devval SHA256: `113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54`.
- V55 seed-0 initialization SHA256: `91fec577380f895c932ffeb090bba7d376abc1ea1d97d568ae46901a7bbcb983`.
- V57 seed-0 superset initialization SHA256: `846da59cc8d908dfeb429fca2acb4985e73ff5fda3915154f9f764c571977cb9`.
- V55 final checkpoint SHA256: `2b4bf19c4ae8d160d5045bb85df17a065e25387313eb5539dfb328ddce76b258`.
- V57 equal final checkpoint SHA256: `d298e6cf4e901a5ad9a2961ecfbcf2592391e6fa237cd5f82d43594b8ceee142`.
- V57 reliability final checkpoint SHA256: `b1322ce43e21e7eae2d646be85e0e43628432e79d1d376924fda6f782b05e5df`.
- V59 frozen devval detailed subset: seed/count/SHA256 `58 / 32 / d622f6712a9bfb2faa596daa053ed207dded1a9227e80b4a10dd3b48ae3d51ee`.

## V60 audit boundary

V60 must:

- reconstruct the exact historical V55 and V57 seed-0 initial states and reproduce their hashes;
- audit model-construction order and RNG-state consumption;
- parse all committed V55/V57 training logs and report available bbox-loss and gradient trajectories;
- freeze a deterministic seed-60 32-row train subset and four-row gradient subset;
- compare bbox pre-ReLU outputs, post-ReLU distances, decoded geometry, parameter signs/norms, and initialization-to-final deltas for reconstructed V55/V57 initial states and all three final checkpoints;
- perform bounded no-step gradient probes on fresh ephemeral instances only;
- choose a provenance classification grounded in direct initialization, geometry, loss, and gradient evidence.

## Safety boundary

- Optimizer construction and optimizer steps: forbidden; required count `0`.
- Backward probes: at most four per audited state and at most twenty total.
- No model state from a probe may be saved or reused.
- Parameters and checkpoint files must remain unchanged.
- No AP/AR, threshold selection, checkpoint repair, positive bbox-bias initialization, activation replacement, resumed V57 training, tuning, or architecture/evaluator changes are authorized.
- Production TriAir behavior, V40-V59 evidence, V51 evidence, manuscript files, and submission files remain protected.
- Heavy artifacts remain local and outside Git.

## Allowed completion states

- `V60_BBOX_COLLAPSE_PROVENANCE_AUDIT_COMPLETE_MECHANISM_IDENTIFIED`
- `V60_BBOX_COLLAPSE_PROVENANCE_AUDIT_COMPLETE_CAUSE_UNRESOLVED`
- `V60_BLOCKED_SOURCE_INITIALIZATION_OR_CHECKPOINT_CONTRACT`
- `V60_BLOCKED_AUDIT_OR_GRADIENT_INSTRUMENTATION`
- `V60_BLOCKED_TEST_OR_PROTECTED_FILE_VIOLATION`

A completed V60 audit remains diagnostic only. Any corrected training run or checkpoint repair requires a later explicit task.