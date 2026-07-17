# Experiment Status

Updated: 2026-07-17

## Active task

`V58_MMUAV_ZERO_DETECTION_DIAGNOSTIC_AUTHORIZED`

## User authorization

The user authorized continuation from completed V57 to a read-only zero-detection diagnostic. V58 may inspect the frozen V57 checkpoints, the full frozen devval inference path, raw FCOS scores, candidate filtering stages, NMS, output schema, and V55/V57 implementation differences under `docs/NEXT_TASK.md`.

The standing local/private-research instruction remains frozen and must not be repeatedly reconfirmed.

## V57 prerequisite evidence

- V57 outcome: `V57_PAIRED_SINGLE_SEED_FUSION_ABLATION_COMPLETE`.
- Equal and reliability variants each completed 7,187 optimizer steps.
- Each final checkpoint was evaluated once on all 1,845 devval rows.
- Both produced zero final detections above the frozen threshold `0.001`.
- AP50:95, AP50, AP75, and AR100 were therefore all zero for both variants.
- Zero deltas are inconclusive and are not evidence of fusion equivalence.
- Reliability scoring was active and favored RGB; all numerical and engineering checks passed.

## Frozen data and checkpoints

- Devval rows: 1,845.
- Devval SHA256: `113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54`.
- Required equal-superset checkpoint SHA256: `d298e6cf4e901a5ad9a2961ecfbcf2592391e6fa237cd5f82d43594b8ceee142`.
- Required reliability-superset checkpoint SHA256: `b1322ce43e21e7eae2d646be85e0e43628432e79d1d376924fda6f782b05e5df`.
- Optional V55 alignment-on reference SHA256: `2b4bf19c4ae8d160d5045bb85df17a065e25387313eb5539dfb328ddce76b258` when the local file remains available.

## V58 diagnostic boundary

V58 authorizes:

- exactly zero optimizer steps and no backward passes;
- read-only checkpoint verification and inference;
- one aggregate diagnostic pass per required V57 checkpoint over all 1,845 devval rows;
- one optional equivalent V55 reference pass when its hash-matching checkpoint is available;
- a frozen 32-row detailed trace subset;
- inspection of classification, centerness, combined scores, thresholding, top-k, clipping, NMS, output schema, evaluator path, feature statistics, memory, and timing;
- fixed pre-threshold candidate counts at `0, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2`.

The diagnostic ladder must not be used to calculate alternate-threshold AP/AR, choose a threshold, replace V57 metrics, or tune the system.

## Gates

- Required checkpoint and devval hashes must reproduce exactly.
- Models must remain in evaluation/inference mode and checkpoints must remain unchanged.
- Optimizer-step count must remain exactly 0.
- No repair, threshold change, retraining, fine-tuning, extra seed, architecture change, or evaluator modification is authorized.
- Production TriAir behavior, V40-V57 evidence, V51 evidence, and manuscript files remain protected.
- Raw predictions, images, feature maps, tensor dumps, and checkpoints remain local and outside Git.

## Allowed completion states

- `V58_ZERO_DETECTION_DIAGNOSIS_COMPLETE_ROOT_CAUSE_IDENTIFIED`
- `V58_ZERO_DETECTION_DIAGNOSIS_COMPLETE_CAUSE_UNRESOLVED`
- `V58_BLOCKED_SOURCE_OR_CHECKPOINT_CONTRACT`
- `V58_BLOCKED_INSTRUMENTATION_OR_INFERENCE_PATH`
- `V58_BLOCKED_TEST_OR_PROTECTED_FILE_VIOLATION`
