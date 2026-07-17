# Experiment Status

Updated: 2026-07-17

## Active task

`V59_STREAMING_ZERO_DETECTION_DIAGNOSTIC_AUTHORIZED`

## User authorization

The user reported the committed V58 diagnostic blocker and continues the established automatic task-handoff workflow. V59 is authorized to reset the read-only aggregate-pass budget and rerun the V57 equal, V57 reliability, and V55 reference paths using bounded deterministic streaming summaries.

The standing local/private-research instruction remains frozen and must not be repeatedly reconfirmed.

## V58 blocker evidence

- V58 status: `V58_BLOCKED_INSTRUMENTATION_OR_INFERENCE_PATH`.
- V57-equal completed 1,845 read-only forwards, then exact `torch.quantile` failed because the concatenated FPN tensor was too large.
- No compact V57-equal aggregate or root-cause classification was produced.
- V57-reliability and V55 reference were not run.
- Optimizer steps/backward/training-mode executions were `0 / 0 / 0`.
- Checkpoints and protected files remained unchanged.

## V59 selected repair

V59 uses pre-registered deterministic streaming histograms rather than NumPy memmap or unbounded tensor concatenation.

- Logits: 16,384 fixed linear bins over `[-64, 64]`, with exact underflow/overflow counts and exact streamed moments.
- Probabilities and combined scores: exact zero count, positive underflow below `1e-12`, and 16,384 fixed logarithmic bins through `1`.
- Quantiles are reported as bounded containing-bin intervals, never as exact all-value quantiles.
- Exact quantiles are allowed only for bounded compact arrays such as 1,845 per-image maxima and candidate counts.
- Synthetic CPU validation must prove direct quantiles fall inside the reported intervals before CUDA inference.

## Frozen data and checkpoints

- Devval rows/hash: 1,845 / `113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54`.
- Ordered devval SHA256: `dd454cfbafa39f2556628ad45dc191b39b0c54bb926028447d5f57553456e867`.
- Detailed subset seed/count/SHA256: `58 / 32 / d622f6712a9bfb2faa596daa053ed207dded1a9227e80b4a10dd3b48ae3d51ee`.
- V57 equal checkpoint SHA256: `d298e6cf4e901a5ad9a2961ecfbcf2592391e6fa237cd5f82d43594b8ceee142`.
- V57 reliability checkpoint SHA256: `b1322ce43e21e7eae2d646be85e0e43628432e79d1d376924fda6f782b05e5df`.
- V55 alignment-on reference SHA256: `2b4bf19c4ae8d160d5045bb85df17a065e25387313eb5539dfb328ddce76b258`.

All three checkpoints are required and must be verified read-only before inference.

## V59 execution boundary

Run exactly one new 1,845-row aggregate pass in this order:

1. V57 equal superset;
2. V57 reliability superset;
3. V55 alignment-on reference.

V59 authorizes exactly zero optimizer steps, no backward, no gradients, no training mode, and no checkpoint or parameter mutation. The fixed diagnostic threshold ladder remains `0, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2`; it may not be used for alternate-threshold AP/AR or threshold selection.

## Diagnostic goal

The task must distinguish checkpoint loading, preprocessing/model mode, feature/head score collapse, score combination, threshold/top-k/NMS behavior, evaluator/output schema, V57 superset regression, or an unresolved cause using direct read-only V55/V57 comparisons.

## Gates

- No unbounded score concatenation or all-value `torch.quantile` path is permitted.
- Histogram edges and error bounds must be frozen before inference.
- Each checkpoint receives one V59 aggregate pass only.
- Data, order, subset, and checkpoint hashes must reproduce exactly.
- No repair, training, threshold change, tuning, architecture/evaluator modification, manuscript edit, public claim, release, redistribution, or external sharing is authorized.
- Production TriAir behavior, V40-V58 evidence, V51 evidence, and manuscript files remain protected.
- Heavy artifacts remain local and outside Git.

## Allowed completion states

- `V59_STREAMING_ZERO_DETECTION_DIAGNOSIS_COMPLETE_ROOT_CAUSE_IDENTIFIED`
- `V59_STREAMING_ZERO_DETECTION_DIAGNOSIS_COMPLETE_CAUSE_UNRESOLVED`
- `V59_BLOCKED_SOURCE_OR_CHECKPOINT_CONTRACT`
- `V59_BLOCKED_STREAMING_INSTRUMENTATION_OR_INFERENCE_PATH`
- `V59_BLOCKED_TEST_OR_PROTECTED_FILE_VIOLATION`
