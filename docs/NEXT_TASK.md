# Current Task

## Authorization

V72 completed at commit `121d444e4885445e42f0755f7413c579e4ccf66e` with:

`V72_MMUAV_NAIVE_GRID_EXTERNAL_DOMAIN_STRESS_TEST_COMPLETE`

The six frozen TriAir checkpoints produced near-zero AP on the exposed MM-UAV devval split under the fixed naive unregistered five-channel adapter. The user has now authorized retraining to obtain a useful target-domain transfer result for the paper.

The previously authorized manuscript-only V73 integration task is superseded before execution. The active task is:

`V73_MMUAV_TRIAIR_INITIALIZED_ALIGNMENT_AWARE_TRANSFER_BENCHMARK_AUTHORIZED`

V73 is a supervised cross-dataset transfer benchmark. It will test whether learned feature alignment and TriAir initialization recover MM-UAV detection performance relative to a matched from-scratch baseline.

## Scientific Label

Use:

`MM-UAV supervised cross-dataset transfer benchmark with learned feature alignment`

Do not call the resulting trained models zero-shot, independent external validation, blind external testing, or untouched-test generalization. MM-UAV train labels are used for supervised target-domain training, and the devval split was exposed during prior engineering work.

V72 remains frozen as the unadapted zero-shot stress-test baseline and must not be modified or rerun.

## Required Start

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git status --short
git rev-parse HEAD
```

Require a clean worktree. Verify that V72 completion commit `121d444e4885445e42f0755f7413c579e4ccf66e` is an ancestor of `HEAD`. Read `AGENTS.md`, `docs/PROJECT_CONTEXT.md`, the current task files, V53/V63/V65-V67/V71/V72 evidence, the six authoritative TriAir checkpoint records, active MM-UAV dataset/evaluator code, and protected-file rules.

Record the actual starting commit. The authorization rewrite began from branch head `38e74e24758d94d7841a31a5bbeecc222d2a1783`; execution must use the latest branch head after all four authorization files are updated.

## Frozen Data

Use exactly the existing frozen MM-UAV manifests:

- train rows: `7,187`;
- train manifest SHA256: `e81973b95dd6fd5ce2d3c5de526310a3bef083df49b8db584fdf39b78a34d67a`;
- devval rows: `1,845`;
- devval manifest SHA256: `113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54`;
- preserve modality pairing, annotations, sequence identities, and row order;
- do not add, remove, replace, resample, or create another split.

For each seed, generate one deterministic epoch-by-epoch training order. The same order must be used by all three variants for that seed. Record the full order hash for every seed and epoch.

The devval set may not be used for early stopping, checkpoint selection, threshold selection, hyperparameter choice, adapter choice, or training extension. Evaluate only the final checkpoint of each completed run exactly once.

## Frozen Architecture

All variants must use the same MM-UAV alignment-aware detector contract:

- independent RGB, IR, and event input stems;
- independent modality decoding and deterministic letterbox to `640 x 640`;
- learned feature-level alignment using the established V53/V57-compatible alignment path;
- fusion before the shared RepViT-M0.9 backbone/FPN/FCOS detector path;
- FPN channels: `128`;
- Softplus bbox-distance activation with `beta=1.0`, `threshold=20.0` for all variants;
- one foreground vehicle ontology;
- no raw five-channel concatenation;
- no test-time fitting or alignment estimation from devval.

Exactly two fusion modes are permitted:

- `equal`: constant RGB/IR/event weights of `1/3, 1/3, 1/3`;
- `reliability`: the established shared image-conditioned reliability scorer with softmax RGB/IR/event weights.

No modality dropout or auxiliary fusion loss is permitted in V73. This isolates initialization and reliability weighting under one alignment-aware training contract.

## Required Nine Runs

Run exactly these variants for seeds `0`, `1`, and `2`, in the listed order within each seed:

1. `scratch_equal` — alignment-aware equal fusion, all trainable parameters initialized from the frozen seed-specific MM-UAV initialization scheme;
2. `triair_init_equal` — equal fusion, initialized from the corresponding frozen TriAir matched Early Fusion checkpoint wherever tensors are structurally compatible;
3. `triair_init_reliability` — reliability fusion, initialized from the corresponding frozen TriAir RA-RepDet `p=0.15` checkpoint wherever tensors are structurally compatible.

Required run identifiers:

```text
v73_seed0_scratch_equal
v73_seed0_triair_init_equal
v73_seed0_triair_init_reliability
v73_seed1_scratch_equal
v73_seed1_triair_init_equal
v73_seed1_triair_init_reliability
v73_seed2_scratch_equal
v73_seed2_triair_init_equal
v73_seed2_triair_init_reliability
```

Do not add variants, seeds, ensembles, checkpoint averaging, or fallback models.

## TriAir Weight-Transfer Contract

Use the six exact checkpoints already verified by V71/V72:

- matched Early Fusion seeds `0`, `1`, `2` for `triair_init_equal`;
- RA-RepDet `p=0.15` seeds `0`, `1`, `2` for `triair_init_reliability`.

For every transfer run:

1. reverify source checkpoint filename, byte count, SHA256, model class, seed, and strict loading in the original TriAir architecture;
2. copy only exact name-and-shape-compatible tensors into the shared backbone, FPN, and FCOS detector components;
3. record every transferred tensor, skipped tensor, source hash, destination hash, parameter count, and transferred-parameter fraction;
4. initialize MM-UAV-specific modality stems, feature-alignment modules, fusion projections, and any unmatched parameters with the same frozen seed-specific initialization used by the scratch control;
5. for the reliability variant, initialize the MM-UAV reliability scorer using the established zero-final-layer contract unless an exact compatible scorer tensor is explicitly present and documented;
6. prohibit tensor reshaping, interpolation, averaging, repair, manual editing, or seed substitution.

The transfer manifest must make clear that this is partial architecture-compatible initialization, not a strict load of the complete TriAir model into the MM-UAV architecture.

Stop with `V73_BLOCKED_TRIAIR_TRANSFER_OR_MODEL_CONTRACT` if a reproducible transfer map cannot be frozen before training.

## Frozen Training Protocol

Use the same protocol for all nine runs:

- image size: `640 x 640`;
- batch size: `1`;
- epochs: exactly `10`;
- optimizer steps per run: exactly `71,870`;
- total planned optimizer steps: exactly `646,830`;
- optimizer: AdamW;
- initial learning rate: `1e-4` for all trainable parameters;
- weight decay: `1e-4`;
- linear warmup: first `500` optimizer steps;
- cosine decay after warmup to final learning rate `1e-6`;
- AMP: disabled;
- gradient accumulation: none;
- gradient clipping: none;
- workers: `0`;
- augmentation: none beyond the frozen deterministic modality decoding/letterbox and box transformation;
- no early stopping;
- no devval evaluation during training;
- no checkpoint selection using devval;
- final epoch checkpoint only for the one authorized devval evaluation.

Save local recovery checkpoints at the end of every epoch and after any documented recoverable interruption. Keep checkpoints outside Git. Recovery must resume the same run, optimizer, scheduler, RNG, and data-order state; it may not change the scientific protocol.

## Required Training Audits

For each run record at minimum:

- initialization and transfer manifests before step `0`;
- finite parameters, losses, gradients, activations, and decoded geometry;
- alignment-module parameter and gradient norms;
- per-modality fusion weights for reliability runs;
- weight entropy, departure from uniform, and dominant modality fraction;
- optimizer/scheduler step counts;
- exact data rows consumed per epoch;
- recovery checkpoint hashes and recovery events;
- final model SHA256 and byte count;
- proof that devval inference did not occur before final training completion.

Run compact diagnostic audits at steps:

`0, 50, 200, 1000, 5000, 10000, 20000, 40000, 60000, 71870`

Diagnostic backward passes must be isolated from optimizer state and may not alter training gradients or parameters.

## Frozen Final Evaluation

Evaluate each final checkpoint exactly once on all `1,845` frozen devval rows using:

- input size: `640 x 640`;
- score threshold: `0.001`;
- NMS threshold: `0.6`;
- maximum detections: `100`;
- COCO AP@[0.50:0.95], AP50, AP75, AR@1, AR@10, and AR@100;
- prediction count and image coverage;
- finite/valid decoded boxes;
- wall-clock time and peak GPU memory.

No test-time augmentation, calibration, adaptation, threshold tuning, checkpoint substitution, or result-driven rerun is allowed.

## Required Comparisons

Report all nine runs individually and compute, for every seed and every metric:

1. `triair_init_equal - scratch_equal` — TriAir initialization benefit under equal fusion;
2. `triair_init_reliability - triair_init_equal` — reliability-aware transfer difference under the paired method-specific TriAir initialization;
3. `triair_init_reliability - scratch_equal` — total transfer-plus-reliability difference.

For each method and each paired difference report mean, sample standard deviation, minimum, maximum, and range across seeds `0`, `1`, and `2`.

Also report transfer-coverage statistics and fusion-weight summaries. With only three seeds, all inference is descriptive; do not claim statistical significance.

V65-V67 may be cited only as historical pilot evidence. Their `320 x 320`, one-pass protocol must not be mixed numerically with the formal V73 table.

## Claim Boundary

V73 may support claims about supervised MM-UAV target-domain training and TriAir initialization under the frozen alignment-aware protocol.

It may not establish:

- zero-shot external validation;
- independent or blind external testing;
- performance on an official untouched MM-UAV test set;
- generalization without MM-UAV labels;
- superiority beyond the three frozen seeds and one devval protocol;
- publication permission or dataset redistribution rights.

If TriAir initialization and/or reliability fusion improve the matched three-seed results, describe the finding as supervised cross-dataset transfer. If gains are inconsistent, report the seed dependence without adding tuning or reruns.

## Required Outputs

Create:

`runs/v73_mmuav_triair_initialized_alignment_aware_transfer_benchmark/`

Commit compact files including:

```text
protocol.md
protocol.json
data_manifest_lock.json
seed_epoch_order_hashes.json
triair_source_checkpoint_manifest.json
transfer_map_per_run.json
initialization_audit.json
training_trace_summary.json
alignment_and_fusion_diagnostics.json
recovery_ledger.json
final_checkpoint_manifest.json
per_run_metrics.csv
per_run_metrics.json
paired_transfer_comparison.csv
paired_transfer_comparison.json
three_seed_summary.json
claim_boundary.json
protected_file_audit.json
test_commands.txt
test_output.txt
final_decision.json
handoff.md
```

Keep raw MM-UAV media, annotations, full predictions, tensors, optimizer states, checkpoints, local absolute paths, and heavy/private artifacts outside Git.

## Decision States

Choose exactly one:

- `V73_MMUAV_THREE_SEED_TRANSFER_BENCHMARK_COMPLETE`;
- `V73_PARTIAL_RUNS_COMPLETE_REMAINING_RUN_BLOCKED`;
- `V73_BLOCKED_TRIAIR_TRANSFER_OR_MODEL_CONTRACT`;
- `V73_BLOCKED_TRAINING_RUNTIME_OOM_OR_FINITE_STATE`;
- `V73_BLOCKED_DATA_OR_EVALUATOR_CONTRACT`;
- `V73_BLOCKED_TEST_SOURCE_PROTECTED_OR_PRIVATE_ARTIFACT_VIOLATION`.

Do not stop or extend training based on intermediate or final AP/AR values.

## Allowed Changes

- the four current task/status/blocker/write-record files;
- `runs/v73_mmuav_triair_initialized_alignment_aware_transfer_benchmark/**` compact evidence;
- V73-only training, transfer, evaluation, recovery, and test utilities;
- minimal backward-compatible experimental model wrappers required to expose the frozen alignment/equal/reliability variants.

## Forbidden Changes

- V40-V72 historical evidence or metrics;
- active TriAir in-domain results;
- production detector behavior outside V73 experimental wrappers;
- MM-UAV split changes;
- extra variants, seeds, epochs, tuning, early stopping, checkpoint selection, ensembling, or result-driven reruns;
- naive-grid V72 metric modification or replacement;
- manuscript integration before V73 results are complete and reviewed;
- raw/private/heavy artifacts in Git.

## Completion

Update the four task files and V73 compact evidence. Commit with exactly:

`exp: run V73 MM-UAV TriAir-initialized alignment-aware transfer benchmark`

Push to `research/ra-repdet-triair`.
