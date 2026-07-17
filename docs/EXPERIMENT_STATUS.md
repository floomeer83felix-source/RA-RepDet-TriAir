# Experiment Status

Updated: 2026-07-17

## Active task

`V58_BLOCKED_INSTRUMENTATION_OR_INFERENCE_PATH`

## Outcome

V58 passed all CPU/source-lock, devval, checkpoint, state-coverage, finite-value, and protected-file preflight checks. The required V57 checkpoints and optional V55 reference were available with exact hashes. The ordered 1,845-row devval list and deterministic seed-58 32-row subset were frozen before inference.

The first V57-equal aggregate inference completed all 1,845 read-only forwards. During post-pass reduction, exact `torch.quantile` rejected the concatenated FPN-level tensor with `RuntimeError: quantile() input tensor is too large`. No compact aggregate was written for that pass. The current protocol allows one aggregate pass per checkpoint, so V57-equal cannot be rerun within V58. V57-reliability and the V55 reference were not executed after the failure.

No root-cause classification is available from this incomplete diagnostic.

## Frozen evidence

- Starting commit: `506bdea52563fdabe732c5044b37136bc9b9d8ea`.
- Devval rows/hash: 1,845 / `113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54`.
- Ordered devval SHA256: `dd454cfbafa39f2556628ad45dc191b39b0c54bb926028447d5f57553456e867`.
- Detailed subset seed/count/SHA256: 58 / 32 / `d622f6712a9bfb2faa596daa053ed207dded1a9227e80b4a10dd3b48ae3d51ee`.
- V57 equal checkpoint: 27,124,021 bytes, SHA256 `d298e6cf4e901a5ad9a2961ecfbcf2592391e6fa237cd5f82d43594b8ceee142`, 791 tensors, complete state coverage.
- V57 reliability checkpoint: 27,129,047 bytes, SHA256 `b1322ce43e21e7eae2d646be85e0e43628432e79d1d376924fda6f782b05e5df`, 791 tensors, complete state coverage.
- V55 reference: available, 27,110,306 bytes, SHA256 `2b4bf19c4ae8d160d5045bb85df17a065e25387313eb5539dfb328ddce76b258`, 787 tensors, complete state coverage.
- All checkpoint tensors were finite. Missing, unexpected, and shape-mismatched keys were empty.

## Actual score path

The inspected torchvision FCOS implementation computes `sqrt(sigmoid(class_logit) * sigmoid(centerness_logit))`, applies strict `score > 0.001`, then per-level top-k 1000, box decoding/clipping, class-aware batched NMS at 0.6, and a global 100-detection cap. The evaluator subsequently retains foreground label 1. The fixed diagnostic ladder was frozen at `0, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2`; no alternate-threshold AP/AR was computed.

## Safety result

- Optimizer steps: 0.
- Backward passes: 0.
- Training-mode executions: 0.
- Checkpoint hashes before and after the failed diagnostic were identical.
- No parameter or checkpoint mutation was observed.
- Pre-CUDA tests: 9/9 pass.
- Production TriAir, V40-V57 evidence, V51, manuscript, and submission files were unchanged.
- No raw predictions, images, feature maps, tensors, or checkpoints entered Git.

## Exact blocker

`torch.quantile` cannot process the concatenated all-row level tensor at the requested size. The failure occurred after the V57-equal full forward pass and before `aggregate_score_diagnostics.json`, stage counts, ladder counts, detailed traces, memory summaries, or a root-cause decision could be written.

## Proposed repair options

1. Authorize a new diagnostic task using pre-registered deterministic streaming histograms or a fixed-size deterministic reservoir to estimate the same quantiles with declared error bounds. Reset and rerun all three aggregate passes under one revised protocol so results remain comparable.
2. Authorize a new diagnostic task using a local, non-Git NumPy memmap or chunked external selection for exact CPU quantiles, deleting the heavy temporary file after aggregation. Reset and rerun all three passes under the revised single-pass protocol.

Neither repair is authorized by V58. Do not rerun, patch, change thresholds, or continue with the remaining checkpoints without a new task.
