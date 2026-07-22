# Current Task

## Authorization

The user reported that V66 completed. Under the standing automatic task-handoff workflow, the user authorizes **V67 MM-UAV matched two-seed reliability-fusion Softplus full-training benchmark** under the standing local/private-research-only rule.

V65 and V66 are frozen as the two-seed equal-fusion Softplus baseline. V65 seed 0 produced AP@[0.50:0.95] `0.0363043928`; V66 seed 1 produced `0.0030357792`. Their mean/sample standard deviation were `0.0196700860 / 0.0235244622`, documenting substantial initialization sensitivity. V67 therefore must use both exact frozen seeds and matched protocols; a one-seed reliability result is not sufficient for a method comparison.

V67 activates the already-present V57 image-conditioned reliability scorer while retaining the same parameter superset, alignment path, Softplus detector head, data, order, optimizer, audits, recovery policy, and evaluator. No modality dropout is introduced. The only scientific difference from the V65/V66 baseline is whether the existing reliability scorer controls the three fusion weights.

## Required Start

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git rev-parse HEAD
```

Authorization base and V66 completion commit: `70a54d92b8deb8cb9a0f748230731cddad641d9f`.

Read `AGENTS.md`, project/status/blocker files, this task, V57 and V63-V66 source and evidence, the installed torchvision FCOS source, evaluator code, recovery utilities, and protected-file rules. Record the actual starting commit. Stop before CUDA on any unexpected repository, evidence, source, initialization, state-identity, data-order, scorer, evaluator, or protected-file mismatch. V51 remains untouched.

## Frozen Prior Evidence

Verify without modifying:

- V65 completion commit: `33609052b798a89fb8d3a1ab9351f8497e8f95d1`;
- V65 decision: `V65_FULLTRAIN_COMPLETE_NONZERO_AP`;
- V66 completion commit: `70a54d92b8deb8cb9a0f748230731cddad641d9f`;
- V66 decision: `V66_SEED1_FULLTRAIN_COMPLETE_NONZERO_AP`;
- V65 seed-0 metrics: AP/AP50/AP75 `0.0363043928 / 0.1493416683 / 0.0035733839`, AR@1/10/100 `0.0501429252 / 0.0753692234 / 0.0815388280`;
- V66 seed-1 metrics: AP/AP50/AP75 `0.0030357792 / 0.0174066630 / 0.0003960396`, AR@1/10/100 `0.0109337780 / 0.0180323964 / 0.0195569319`;
- both runs completed `7,187 / 7,187` ordered optimizer steps, 40 diagnostic backward calls, 19 verified recovery snapshots, one 1,845-row final-checkpoint-only devval evaluation, and 10/10 post-run tests;
- all twenty baseline audits were `GEOMETRY_AND_GRADIENT_PRESERVED`;
- no tuning, threshold selection, checkpoint selection, rerun, or extra seed/variant occurred.

All V40-V66 evidence is read-only. Do not initialize from trained checkpoints, resume baseline runs, relabel outcomes, select the better seed, or pool checkpoints.

## Frozen Data, Seeds, and Order

Use exactly:

- train manifest: `runs/v53_mmuav_feature_alignment_preflight/manifests/train_rgb_supervised.txt`;
- devval manifest: `runs/v53_mmuav_feature_alignment_preflight/manifests/devval_rgb_supervised.txt`;
- train/devval rows: `7,187 / 1,845`;
- train SHA256: `e81973b95dd6fd5ce2d3c5de526310a3bef083df49b8db584fdf39b78a34d67a`;
- devval SHA256: `113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54`;
- frozen V57 order SHA256: `27e98f752d4707c862c41495420cd1776a9095ad0a010becff2035deef0bf27b`;
- seed-0 common initialization SHA256: `846da59cc8d908dfeb429fca2acb4985e73ff5fda3915154f9f764c571977cb9`;
- seed-1 common initialization SHA256: `50612d58789b935ed8345494a7830a64d07b83c841ac9b6d24bcda3ea3f2c476`;
- frozen train geometry, gradient, and devval geometry subsets and hashes used by V65/V66;
- RGB boxes as the sole detector targets.

Each seed consumes all 7,187 frozen rows exactly once and in the same order. Run seed 0 first, then seed 1. Do not reshuffle, repeat, substitute, truncate, extend, or condition the second run on the first result.

## Frozen Model and Sole Intervention

For each seed use:

```text
independent RGB/IR/event stems
-> learned IR/event feature alignment to RGB (enabled)
-> V57 identical parameter superset
-> active shared image-conditioned reliability scorer
-> softmax RGB/IR/event weights
-> weighted feature fusion
-> 1x1 projection to 3 channels
-> RepViT-M0.9-FPN-FCOS
-> softplus(beta=1.0, threshold=20.0) bbox-distance activation
```

The reliability scorer is the existing shared `AdaptiveAvgPool2d -> Flatten -> Linear -> ReLU -> Linear` scorer from the V57 superset. Its frozen initialization remains part of each seed-specific common state. The final scorer layer is initially zero, so the active reliability model must produce exact uniform `[1/3, 1/3, 1/3]` weights and bit-identical fused/detector outputs to its matched equal-fusion baseline at step 0. After optimization begins, scorer parameters may learn normally.

Configuration remains exactly V65/V66: input `320x320`, batch size 1, FP32, AMP off, feature channels 32, FPN channels 128, no pretrained weights, AdamW LR `1e-4`, weight decay `1e-4`, no scheduler, clipping, augmentation, workers, early stopping, tuning, or adaptive extension. Losses, targets, matching, anchors, scales, decode, score threshold, top-k, NMS, preprocessing, and evaluator remain frozen.

Do not add modality dropout, static learned global weights, per-modality scorers, auxiliary reliability losses, weight regularization, entropy penalties, temperature parameters, missing-modality simulation, or any other fusion change.

## CPU and Source-Lock Gates Before CUDA

Prove before GPU work:

1. V65/V66 evidence, manifests, order, subsets, evaluator, and protected fingerprints match exactly;
2. seed-0 and seed-1 initialization files strictly reproduce their frozen SHA256 values;
3. reliability and equal variants have identical parameter names, tensors, buffers, and state dictionaries for each seed;
4. at step 0 the active scorer emits exact uniform weights, and fused features, pre-activation bbox logits, classification logits, centerness logits, alignment outputs, losses, and decoded predictions are bit-identical to the matched equal-fusion model;
5. the sole behavior switch is V57 `alignment_on_reliability_superset` versus `alignment_on_equal_superset`;
6. scorer parameters receive finite gradients after the first training backward pass while baseline-frozen contracts remain unchanged;
7. Softplus source location, call count, beta, and threshold match V65/V66;
8. the full-devval evaluator reproduces the exact frozen schema/configuration without selecting thresholds or checkpoints;
9. recovery snapshots round-trip model, optimizer, all RNG states, seed/run identity, next row, completed step count, logs, audit ledger, and hashes;
10. production, manuscript, submission, and V40-V66/V51 fingerprints remain unchanged.

Fail closed before CUDA on any mismatch.

## Frozen Run Budget

Run exactly, in order:

1. `v67_seed0_reliability_softplus_b1_t20_fulltrain` — 7,187 optimizer steps;
2. `v67_seed1_reliability_softplus_b1_t20_fulltrain` — 7,187 optimizer steps.

Total ceiling: **14,374 optimizer steps**. Each run uses its own exact seed-specific common initialization and the complete frozen order once. Only the final step-7,187 checkpoint of each run is scientific; no intermediate checkpoint selection is allowed.

Save verified local recovery snapshots before every audit and every 500 completed steps. Recovery is allowed only from the latest exact snapshot of the same seed/run, with no replayed or skipped row. Heavy artifacts remain local and outside Git.

## Audits and Evaluation

For each seed audit at:

```text
step 0, 15, 50, 200, 500, 1000, 2000, 4000, 6000, 7187
```

Maximum diagnostic backward calls: **80 total**, exactly 40 per seed. Use ephemeral copies and preserve persistent-state isolation.

Record all V65/V66 geometry, gradient, loss, activation, finite-state, timing, memory, and recovery fields. Additionally record per-sample and aggregate RGB/IR/event weights, weight sums, entropy, dominant modality fractions, scorer logits, scorer parameter/gradient norms, exact-uniform departure step, and finite-state checks. Weight concentration is evidence to report, not an automatic reason to stop unless values become non-finite.

After each run completes, evaluate only its final checkpoint exactly once on all 1,845 frozen devval rows with the frozen evaluator. Report AP@[0.50:0.95], AP50, AP75, AR@1, AR@10, AR@100, image/ground-truth/prediction counts, zero-prediction images, non-finite predictions, time, and memory.

Create a matched comparison summary containing:

- immutable V65/V66 equal-fusion metrics;
- V67 reliability-fusion metrics for seeds 0 and 1;
- per-seed reliability-minus-equal deltas for every AP/AR metric;
- two-seed reliability mean, sample standard deviation, minimum, maximum, and range;
- mean and range of the matched per-seed deltas;
- fusion-weight and scorer diagnostics by seed;
- a clear descriptive-only/no-independent-test/no-significance boundary.

Do not use either seed result to select, rerun, tune, terminate, or alter the other run.

## Completion States

Choose exactly one:

- `V67_TWO_SEED_RELIABILITY_FULLTRAIN_COMPLETE`;
- `V67_SEED0_COMPLETE_SEED1_BLOCKED`;
- `V67_RELIABILITY_BBOX_COLLAPSE` if strict zero-valid-geometry and zero-bbox-output-gradient collapse occurs on two consecutive audits in either run;
- `V67_BLOCKED_SOURCE_STATE_OR_SCORER_CONTRACT`;
- `V67_BLOCKED_TRAINING_TRACE_OR_RECOVERY_INCOMPLETE`;
- `V67_BLOCKED_OOM_OR_NUMERICAL_INSTABILITY`;
- `V67_BLOCKED_FULL_DEVVAL_EVALUATION`;
- `V67_BLOCKED_TEST_OR_PROTECTED_FILE_VIOLATION`.

Successful completion establishes a matched two-seed devval comparison between equal and image-conditioned reliability fusion under the frozen MM-UAV Softplus protocol. It does not establish independent-test performance, broad generalization, statistical significance with n=2, or the value of modality dropout.

## Stop Rules

Fail closed on any prior-evidence, source, state, step-0 identity, scorer, data/order, Softplus, evaluator, recovery, protected-file, finite-state, step-count, audit-count, or final-evaluation mismatch. Do not modify the model, scorer, optimizer, LR, loss, activation, thresholds, order, run length, or audit schedule after observing results. No extra seed, variant, rerun, ReLU run, modality-dropout experiment, static-fusion experiment, checkpoint selection, or tuning is authorized.

## Required Outputs

Create `runs/v67_mmuav_two_seed_reliability_softplus_benchmark/` with compact protocol, source/state verification, per-seed configuration/log/audit/recovery/checkpoint/evaluator/metrics files, fusion-weight diagnostics, prediction safety, timing/memory, matched comparison summary, final decision, tests, safety audit, and handoff. Keep checkpoints, optimizer states, recovery snapshots, initialization artifacts, raw predictions, tensors, images, and feature maps local and outside Git.

## Allowed Changes

- current task/status/blocker/write-record and V67 handoff files;
- `runs/v67_mmuav_two_seed_reliability_softplus_benchmark/**`;
- V67-only reliability/Softplus wrapper, runner, instrumentation, recovery utilities, and tests;
- minimal backward-compatible imports that do not change production defaults.

## Forbidden Changes

Historical evidence, V51, production TriAir defaults, manuscript/submission files, raw data/annotations, detector/loss/matching/decode/evaluator semantics, Softplus parameters, model width/depth, optimizer, modality dropout, auxiliary losses, static-weight controls, ReLU full training, extra seeds/variants, tuning, threshold/checkpoint selection, and automatic extension.

## Completion

Update `docs/EXPERIMENT_STATUS.md`, `docs/TASK_BLOCKER.md`, the V67 handoff, and the write record; run `powershell -ExecutionPolicy Bypass -File rarepdet/tools/finish_task.ps1`.

Commit message:

`exp: run V67 MM-UAV two-seed reliability Softplus benchmark`
