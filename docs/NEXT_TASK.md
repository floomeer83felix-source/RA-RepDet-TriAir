# Current Task

## Authorization

The user authorizes **V58 MM-UAV V57 zero-detection inference diagnostic** under the standing local/private-research-only rule.

V57 completed both frozen fusion variants, but both produced zero final detections above the frozen detector threshold `0.001`. V58 is a read-only checkpoint and inference-path diagnostic intended to isolate why the V57 superset path produced empty detections while earlier V55/V56 alignment-on runs produced non-zero metrics.

V58 authorizes **zero optimizer steps**. It does not authorize retraining, fine-tuning, threshold tuning, checkpoint selection, new seeds, architecture changes, manuscript edits, public claims, redistribution, or external sharing.

## Required Start

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git rev-parse HEAD
```

Authorization-base evidence commit: `d0a227b4a3dc4f1106beb37085eaa2f8021d9358`.

Read `AGENTS.md`, project/status/blocker/task/handoff files, all V52-V57 evidence, the MM-UAV adapter, V54 detector integration, V55-V57 runners/evaluators, the V57 superset wrapper, FCOS post-processing code, and protected-file rules. Record the actual starting commit and stop on unexpected repository changes. V51 remains untouched.

## Frozen Data Contract

Use exactly:

- devval manifest: `runs/v53_mmuav_feature_alignment_preflight/manifests/devval_rgb_supervised.txt`;
- devval rows: 1,845;
- devval SHA256: `113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54`;
- train/devval sequence overlap: 0;
- RGB boxes are the sole detector targets;
- IR boxes remain metadata only and event has no detector target.

No pseudo labels, interpolation, box transfer, nearest-frame substitution, empty-target conversion, or data-contract changes are allowed.

## Frozen Checkpoint Contract

Required V57 checkpoints:

1. `D:\MM-UAV_v57_local\alignment_on_equal_superset_final_step7187.pt`
   - SHA256: `d298e6cf4e901a5ad9a2961ecfbcf2592391e6fa237cd5f82d43594b8ceee142`;
2. `D:\MM-UAV_v57_local\alignment_on_reliability_superset_final_step7187.pt`
   - SHA256: `b1322ce43e21e7eae2d646be85e0e43628432e79d1d376924fda6f782b05e5df`.

Verify checkpoint size, SHA256, completed-step metadata, state-dict key coverage, missing/unexpected keys, tensor shapes, and finite values before inference. Do not modify or rewrite checkpoints.

Optional read-only reference, when still available locally:

- V55 seed-0 `alignment_on_equal` checkpoint: `D:\MM-UAV_v55_local\alignment_on_equal_final_step7187.pt`;
- expected SHA256: `2b4bf19c4ae8d160d5045bb85df17a065e25387313eb5539dfb328ddce76b258`.

The optional V55 reference may be used only to compare raw score and post-processing behavior. Its absence does not block the core V57 diagnostic and must be reported explicitly.

## Diagnostic Questions

V58 must determine, as far as the frozen evidence permits, whether zero detections arise from:

1. checkpoint loading or state-dict mismatch;
2. detector train/eval mode or preprocessing mismatch;
3. feature or detector-head score collapse;
4. classification/centerness score-combination behavior;
5. score threshold, top-k, box clipping, or NMS post-processing;
6. evaluator/output-schema mismatch or double filtering;
7. another isolated implementation difference between the V55/V56 path and V57 superset path;
8. an unresolved cause after all required checks.

Do not assume the exact FCOS score formula. Inspect and record the implementation actually used, including sigmoid, centerness combination, square root, per-level top-k, score threshold, NMS, and final detection cap.

## Frozen Diagnostic Protocol

### Execution boundary

- Optimizer construction and `optimizer.step()` are forbidden.
- Training mode, backward, gradient computation, checkpoint mutation, and parameter mutation are forbidden.
- Use `model.eval()` and `torch.no_grad()` or inference mode.
- CUDA inference is allowed; optimizer-step count must remain exactly 0.
- V57 checkpoints must each be loaded and evaluated once for the required aggregate diagnostic pass.
- The optional V55 reference may receive one equivalent aggregate pass only.

### Source-locked sample sets

Before reading model outputs, create and hash:

1. the full ordered 1,845-row devval list for aggregate diagnostics;
2. a deterministic 32-row detailed-trace subset derived from seed 58 and the frozen devval manifest.

Do not change the subset after observing outputs.

### All-row aggregate diagnostics

For each required checkpoint, record across all 1,845 rows:

- raw classification-logit and probability quantiles by FPN level;
- centerness-logit and probability quantiles by level;
- exact combined-score quantiles used by the implementation;
- maximum score per image and its quantiles;
- candidate counts before thresholding, after per-level top-k, after the frozen `0.001` threshold, after NMS, and in final outputs;
- valid, clipped, degenerate, non-finite, and out-of-image box counts;
- images with at least one candidate or final detection;
- output schema, tensor shapes, dtypes, device, and finite status;
- inference timing and peak allocated/reserved memory.

Record pre-threshold candidate-count curves for the fixed diagnostic ladder:

```text
0, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2
```

This ladder is diagnostic only. Do not compute AP/AR at alternate thresholds, select a threshold, replace V57 metrics, or claim an improved result.

### Detailed 32-row traces

For the frozen 32-row subset, save compact per-image summaries of:

- RGB/IR/event input and feature statistics;
- aligned feature and fused-feature statistics;
- equal or reliability fusion weights;
- detector input after the 1x1 projection and resize;
- per-level head output shapes;
- top raw classification, centerness, and combined scores;
- candidate counts at every post-processing stage;
- top final boxes/scores when any exist.

Do not commit raw images, tensors, feature maps, predictions, or visualizations.

### V55/V57 path comparison

Inspect and record differences between the non-zero V55/V56 detector path and the V57 superset path, including:

- builder and wrapper classes;
- parameter names/shapes and checkpoint loading coverage;
- detector-head weight/bias norms and finite status;
- `to_detector_image` weight/bias norms;
- normalization, resize, channel order, and model mode;
- returned detection schema;
- score-threshold and NMS application count;
- evaluator configuration;
- feature and score distributions on the same frozen rows when the optional V55 checkpoint is available.

A code-path difference may be identified as causal only when supported by a direct trace or controlled read-only replay. Do not patch and rerun within V58.

## Root-Cause Classification

Choose one primary classification:

- `CHECKPOINT_LOAD_MISMATCH`;
- `PREPROCESS_OR_MODEL_MODE_MISMATCH`;
- `FEATURE_OR_HEAD_SCORE_COLLAPSE`;
- `POSTPROCESS_THRESHOLD_OR_NMS_PATH`;
- `EVALUATOR_OR_OUTPUT_SCHEMA_MISMATCH`;
- `V57_SUPERSET_IMPLEMENTATION_REGRESSION`;
- `ZERO_DETECTIONS_REPRODUCED_CAUSE_UNRESOLVED`.

Supporting secondary factors may also be recorded. V58 is diagnostic evidence only and does not authorize a repair.

## Stop Rules

Fail closed on:

- devval count/hash mismatch;
- required V57 checkpoint absence or hash mismatch;
- checkpoint mutation or parameter mutation;
- any optimizer step, backward pass, or training-mode execution;
- non-finite diagnostic values that prevent interpretation;
- unauthorized AP/AR recomputation at alternate thresholds;
- modification of production code, historical evidence, V51, manuscript files, or heavy artifacts entering Git.

Do not automatically change thresholds, NMS, top-k, preprocessing, model architecture, checkpoint contents, or evaluator behavior.

## Required Outputs

Create `runs/v58_mmuav_zero_detection_diagnostic/` containing compact files such as:

```text
protocol.json
protocol.md
source_lock_v58.json
source_lock_v58.md
checkpoint_verification.json
v55_reference_availability.json
devval_order.txt
devval_order_sha256.txt
detailed_subset_indices.json
detailed_subset_sha256.txt
implementation_score_path.md
aggregate_score_diagnostics.json
aggregate_stage_counts.json
threshold_ladder_counts.json
detailed_trace_summary.json
v55_v57_path_diff.md
root_cause_decision.json
root_cause_decision.md
memory_timing_summary.json
test_commands.txt
test_output.txt
```

Commit only compact text, metadata, hashes, and aggregate summaries. Heavy checkpoints, raw predictions, images, and tensor dumps remain local and outside Git.

## Required Tests

Verify:

- exact devval count/hash;
- exact required checkpoint hashes and read-only loading;
- optimizer steps remain 0 and no backward/training path exists;
- deterministic 32-row subset generation;
- score instrumentation matches the actual FCOS implementation;
- all diagnostic ladder values are fixed before inference;
- no AP/AR is computed at alternate thresholds;
- candidate-stage counts are internally consistent;
- output schema and finite checks are complete;
- optional V55 absence is handled without fabricating results;
- production TriAir, V40-V57 evidence, V51 evidence, and manuscript files remain unchanged;
- heavy artifacts stay outside Git.

Run CPU/source-lock tests before CUDA diagnostic inference and save exact commands and outputs.

## Allowed Changes

- current task/status/blocker/handoff files;
- `runs/v58_mmuav_zero_detection_diagnostic/**`;
- V58-only read-only diagnostic tools, wrappers, instrumentation, and tests;
- minimal imports needed to expose read-only V58 instrumentation without changing production defaults.

## Forbidden Changes

- training, fine-tuning, backward passes, optimizer construction/steps, or checkpoint mutation;
- raw data or annotations;
- historical V40-V57 evidence except current pointers;
- V51 history;
- production defaults or TriAir semantics;
- score-threshold, NMS, top-k, preprocessing, or architecture changes;
- alternate-threshold AP/AR, threshold selection, or metric replacement;
- public derivatives, manuscript, submission, or public benchmark files.

## Completion State

Choose exactly one:

- `V58_ZERO_DETECTION_DIAGNOSIS_COMPLETE_ROOT_CAUSE_IDENTIFIED`;
- `V58_ZERO_DETECTION_DIAGNOSIS_COMPLETE_CAUSE_UNRESOLVED`;
- `V58_BLOCKED_SOURCE_OR_CHECKPOINT_CONTRACT`;
- `V58_BLOCKED_INSTRUMENTATION_OR_INFERENCE_PATH`;
- `V58_BLOCKED_TEST_OR_PROTECTED_FILE_VIOLATION`.

A successful diagnosis does not authorize a repair, threshold change, retraining, extra evaluation, or manuscript claim. Any corrective experiment requires a new task.

Update status, blocker, and handoff files, then run:

```powershell
powershell -ExecutionPolicy Bypass -File rarepdet/tools/finish_task.ps1
```

## Commit Message

diag: analyze V57 zero-detection outputs

## Final Report Requirements

Report starting/final commit SHAs, devval and checkpoint hashes, optional V55 availability, exact score/post-processing implementation, 0 optimizer steps, aggregate score quantiles, threshold-ladder candidate counts, stage counts, detailed subset hash, V55/V57 path differences, root-cause classification and evidence, timing/memory/finite status, tests, protected-file results, unresolved limitations, and the next authorization boundary.
