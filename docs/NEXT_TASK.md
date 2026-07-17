# Current Task

## Authorization

The user authorizes **V59 MM-UAV streaming zero-detection diagnostic rerun** under the standing local/private-research-only rule.

V58 was correctly fail-closed after the first V57-equal read-only pass because exact `torch.quantile` could not process the concatenated all-row FPN tensor. V59 adopts repair option 1 from the committed V58 blocker: replace unbounded tensor concatenation with pre-registered deterministic streaming histograms and compact exact per-image summaries, then reset and rerun all three checkpoint paths under one comparable protocol.

V59 authorizes **zero optimizer steps**. It does not authorize training, fine-tuning, threshold tuning, checkpoint selection, architecture changes, additional seeds, manuscript edits, public claims, redistribution, or external sharing.

## Required Start

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git rev-parse HEAD
```

Authorization-base evidence commit: `3263d3d6ba9e01139047c1ca0b18708c9700f376`.

Read `AGENTS.md`, project/status/blocker/task/handoff files, all V52-V58 evidence, the V57 superset wrapper, V55-V58 runners/evaluators, the actual torchvision FCOS post-processing implementation, and protected-file rules. Record the actual starting commit and stop on unexpected repository changes. V51 remains untouched.

## Frozen V58 Blocker Evidence

Reproduce without modifying V58 evidence:

- V58 status: `V58_BLOCKED_INSTRUMENTATION_OR_INFERENCE_PATH`;
- exact error: `RuntimeError: quantile() input tensor is too large`;
- V58 optimizer steps/backward/training-mode executions: `0 / 0 / 0`;
- V57-equal V58 pass: full 1,845-row forward completed but compact reduction failed;
- V57-reliability and V55 reference V58 passes: not run;
- no V58 root-cause classification was produced.

V59 explicitly resets the aggregate-pass budget. The incomplete V58 pass is historical blocker evidence and must not be mixed with V59 aggregates.

## Frozen Data and Sample Sets

Use exactly:

- devval manifest: `runs/v53_mmuav_feature_alignment_preflight/manifests/devval_rgb_supervised.txt`;
- devval rows: 1,845;
- devval manifest SHA256: `113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54`;
- ordered devval SHA256: `dd454cfbafa39f2556628ad45dc191b39b0c54bb926028447d5f57553456e867`;
- detailed subset seed/count/SHA256: `58 / 32 / d622f6712a9bfb2faa596daa053ed207dded1a9227e80b4a10dd3b48ae3d51ee`;
- RGB boxes are the sole detector targets;
- IR boxes remain metadata only and event has no detector target.

Reuse the exact ordered 1,845 rows and exact 32-row subset frozen by V58. Do not regenerate a different order or subset.

## Frozen Checkpoints

All three checkpoints are required for V59:

1. V57 equal superset:
   - `D:\MM-UAV_v57_local\alignment_on_equal_superset_final_step7187.pt`;
   - SHA256 `d298e6cf4e901a5ad9a2961ecfbcf2592391e6fa237cd5f82d43594b8ceee142`;
   - expected tensors: 791.
2. V57 reliability superset:
   - `D:\MM-UAV_v57_local\alignment_on_reliability_superset_final_step7187.pt`;
   - SHA256 `b1322ce43e21e7eae2d646be85e0e43628432e79d1d376924fda6f782b05e5df`;
   - expected tensors: 791.
3. V55 alignment-on reference:
   - `D:\MM-UAV_v55_local\alignment_on_equal_final_step7187.pt`;
   - SHA256 `2b4bf19c4ae8d160d5045bb85df17a065e25387313eb5539dfb328ddce76b258`;
   - expected tensors: 787.

Verify size, SHA256, completed-step metadata, state-dict coverage, missing/unexpected keys, shapes, and finite values before inference. Checkpoint absence or mismatch fails closed. Do not modify or rewrite checkpoints.

## Actual Score Path

Source-lock the implementation actually used. The V58 inspection found:

```text
combined score = sqrt(sigmoid(class_logit) * sigmoid(centerness_logit))
strict score > 0.001
per-level top-k = 1000
box decode and clipping
class-aware batched NMS IoU = 0.6
global detections per image = 100
evaluator retains foreground label 1
```

Reverify this path against the installed source before inference. Do not alter it.

## Revised Streaming Summary Contract

Unbounded concatenation of all FPN values and exact all-value `torch.quantile` are forbidden.

Maintain deterministic CPU `int64` streaming histograms separately for every checkpoint, FPN level, and score type.

### Logit histograms

For classification and centerness logits:

- fixed range: `[-64, 64]`;
- fixed equal-width bin count: `16,384`;
- bin width: `0.0078125`;
- separate underflow and overflow counts;
- exact streamed count, minimum, maximum, mean, and second moment.

Reported quantiles must include the containing histogram interval. The interval width is the declared absolute quantile-resolution bound when the quantile is inside the fixed range. Underflow or overflow quantiles must be reported as bounded only by the observed exact minimum/maximum and the range edge.

### Probability and combined-score histograms

For classification probabilities, centerness probabilities, and combined scores:

- one exact zero count;
- one underflow count for positive values below `1e-12`;
- `16,384` fixed logarithmic bins from `1e-12` through `1`;
- exact streamed count, minimum, maximum, mean, and second moment.

Reported positive quantiles must include the containing `[lower, upper]` log-bin interval. The bin interval is the declared deterministic approximation bound. Do not present histogram midpoints as exact quantiles.

### Exact compact values

It is permitted to retain and compute exact quantiles for compact arrays whose size is bounded before inference, including:

- one maximum combined score per image: exactly 1,845 values per checkpoint;
- stage candidate counts per image;
- the fixed 32-row detailed summaries;
- modality fusion weights and compact feature statistics for the fixed subset.

No raw FPN tensor, prediction tensor, feature map, or unbounded score list may be retained.

## Histogram Validation Before CUDA

Before checkpoint inference, run synthetic CPU tests that:

1. compare streaming counts, means, minima, maxima, and second moments with direct computation;
2. verify every exact manageable-tensor quantile lies inside the reported histogram interval;
3. cover zero, probability underflow, logit underflow/overflow, repeated values, and empty-level handling;
4. verify chunking and update order do not change histogram results;
5. prove peak retained score-summary storage is bounded by the declared histogram and compact-array sizes.

A failed validation blocks V59 before any checkpoint pass.

## Frozen Run Order and Pass Budget

Run exactly one aggregate read-only pass in this order:

1. V57 equal superset;
2. V57 reliability superset;
3. V55 alignment-on reference.

Each pass uses all 1,845 ordered devval rows exactly once. V59 authorizes these three new passes despite V58's consumed V57-equal pass. No checkpoint may receive a second V59 aggregate pass.

Use `model.eval()` and `torch.inference_mode()` or `torch.no_grad()`. Optimizer construction, backward, gradient computation, training mode, parameter mutation, and checkpoint mutation are forbidden.

## Required Aggregate Diagnostics

For each checkpoint, record:

- streaming histogram summaries and bounded quantile intervals by FPN level for classification logits/probabilities, centerness logits/probabilities, and combined scores;
- exact per-image maximum-score quantiles;
- exact candidate counts before thresholding, after per-level top-k, after strict `0.001`, after box validity/clipping, after NMS, and in final outputs;
- images with at least one candidate at each stage and at least one final detection;
- valid, degenerate, non-finite, clipped, and out-of-image box counts;
- output schema, tensor shapes, dtypes, devices, labels, and finite status;
- inference timing and CUDA peak allocated/reserved memory.

Record exact candidate counts at the pre-registered diagnostic ladder:

```text
0, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2
```

The ladder remains diagnostic only. Do not compute AP/AR at alternate thresholds, select a threshold, replace V57 metrics, or claim improved accuracy.

## Detailed Trace and Path Comparison

For the exact frozen 32-row subset, save compact summaries of inputs, modality features, aligned features, fused features, fusion weights, detector input, head shapes, top classification/centerness/combined scores, stage counts, and top final boxes/scores when present.

Compare V55 and V57 on the same rows and aggregate stream for:

- wrapper/builder path;
- checkpoint state coverage and parameter norms;
- detector-head and `to_detector_image` weight/bias norms;
- preprocessing, normalization, resize, channel order, and model mode;
- feature and score distributions;
- threshold/top-k/NMS application count;
- output schema and evaluator filtering.

A code-path difference may be classified as causal only when supported by direct trace evidence or a controlled read-only replay within the single authorized pass.

## Root-Cause Classification

Choose one primary result:

- `CHECKPOINT_LOAD_MISMATCH`;
- `PREPROCESS_OR_MODEL_MODE_MISMATCH`;
- `FEATURE_OR_HEAD_SCORE_COLLAPSE`;
- `POSTPROCESS_THRESHOLD_OR_NMS_PATH`;
- `EVALUATOR_OR_OUTPUT_SCHEMA_MISMATCH`;
- `V57_SUPERSET_IMPLEMENTATION_REGRESSION`;
- `ZERO_DETECTIONS_REPRODUCED_CAUSE_UNRESOLVED`.

Supporting secondary factors may be recorded. Diagnosis does not authorize repair.

## Stop Rules

Fail closed on:

- V58 evidence, devval order, subset, or checkpoint mismatch;
- histogram specification changed after outputs are observed;
- any unbounded concatenation or all-value `torch.quantile` path;
- checkpoint or parameter mutation;
- optimizer construction/step, backward, gradients, or training-mode execution;
- non-finite diagnostics that prevent interpretation;
- more than one V59 aggregate pass per checkpoint;
- alternate-threshold AP/AR or threshold selection;
- production, historical evidence, V51, manuscript, or heavy-artifact violation.

Do not automatically patch the model, threshold, top-k, NMS, preprocessing, scorer, detector, or evaluator.

## Required Outputs

Create `runs/v59_mmuav_streaming_zero_detection_diagnostic/` containing compact protocol/source-lock files, V58 blocker verification, checkpoint verification, frozen order/subset verification, histogram specification and validation, per-checkpoint streaming summaries, stage counts, ladder counts, detailed traces, V55/V57 path comparison, memory/timing summary, root-cause decision, tests, and final decision.

Commit only compact text, metadata, hashes, histograms, counts, and summaries. Checkpoints, predictions, images, feature maps, tensor dumps, and other heavy artifacts remain local and outside Git.

## Required Tests

Verify:

- exact V58 blocker and frozen evidence hashes;
- exact devval/order/subset and checkpoint contracts;
- deterministic histogram edges and order-independent updates;
- exact compact statistics and bounded quantile intervals;
- no unbounded score retention or all-value quantile path;
- exact three-pass order and one pass per checkpoint;
- optimizer/backward/training-mode counts remain zero;
- fixed ladder and no alternate-threshold AP/AR;
- internally consistent stage counts and output schemas;
- checkpoint hashes unchanged before/after inference;
- production TriAir, V40-V58 evidence, V51, manuscript, and submission files unchanged;
- heavy artifacts outside Git.

Run CPU/source-lock and histogram-validation tests before CUDA inference and save exact commands and outputs.

## Allowed Changes

- current task/status/blocker/handoff files;
- `runs/v59_mmuav_streaming_zero_detection_diagnostic/**`;
- V59-only streaming diagnostic tools, instrumentation, and tests;
- minimal backward-compatible imports needed for read-only instrumentation without changing defaults.

## Forbidden Changes

- modification of V58 evidence or its historical runner outputs;
- training, fine-tuning, backward, optimizer construction/steps, or checkpoint mutation;
- raw data or annotations;
- historical V40-V58 evidence except current pointers;
- V51 history;
- production defaults or TriAir semantics;
- threshold, top-k, NMS, preprocessing, scorer, detector, architecture, or evaluator changes;
- alternate-threshold AP/AR, threshold selection, or metric replacement;
- public derivatives, manuscript, submission, or public benchmark files.

## Completion State

Choose exactly one:

- `V59_STREAMING_ZERO_DETECTION_DIAGNOSIS_COMPLETE_ROOT_CAUSE_IDENTIFIED`;
- `V59_STREAMING_ZERO_DETECTION_DIAGNOSIS_COMPLETE_CAUSE_UNRESOLVED`;
- `V59_BLOCKED_SOURCE_OR_CHECKPOINT_CONTRACT`;
- `V59_BLOCKED_STREAMING_INSTRUMENTATION_OR_INFERENCE_PATH`;
- `V59_BLOCKED_TEST_OR_PROTECTED_FILE_VIOLATION`.

A successful diagnosis does not authorize repair, threshold changes, retraining, extra evaluation, or manuscript claims. Any corrective action requires a new task.

Update status, blocker, and handoff files, then run:

```powershell
powershell -ExecutionPolicy Bypass -File rarepdet/tools/finish_task.ps1
```

## Commit Message

`diag: rerun V57 zero-detection diagnosis with streaming summaries`

## Final Report Requirements

Report starting/final commit SHAs, V58 blocker verification, devval/order/subset and checkpoint hashes, histogram specification and validation results, exact pass counts, zero optimizer/backward/training executions, bounded score quantile intervals, exact per-image maxima, stage and ladder counts, detailed trace evidence, V55/V57 path differences, root-cause classification, timing/memory/finite status, checkpoint immutability, tests, protected-file results, limitations, and the next authorization boundary.
