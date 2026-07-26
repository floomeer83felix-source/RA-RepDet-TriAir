# Current Task

## Authorization

V71 completed at commit `bfca2e21ca7a46a5087b3addfcac7dab9d7e1618` with `V71_BLOCKED_ADAPTER_OR_ONTOLOGY_CONTRACT`. The exact MM-UAV devval manifest and all six frozen TriAir checkpoints passed verification, but no metrics were produced because physical cross-modal pixel registration could not be established.

The user has directed the project to begin the external-domain experiment immediately and not spend further work on provider authority, release/version, rights, calibration acquisition, or additional preflight research.

The active task is:

`V72_MMUAV_EXISTING_DEVVAL_TRIAIR_NAIVE_GRID_EXTERNAL_DOMAIN_STRESS_TEST_AUTHORIZED`

V72 must implement one frozen naive normalized-grid adapter and immediately run all six frozen TriAir checkpoints on the existing `1,845`-row MM-UAV devval manifest.

## Required Scientific Label

Use exactly this description:

`zero-shot external-domain stress test on the exposed MM-UAV devval split using a naive normalized-grid five-channel adapter`

Do not call it an independent/blind external test, physically registered multimodal validation, or official MM-UAV test performance. The lack of physical RGB/IR/event registration is an explicit limitation, not a V72 blocker.

## Required Start

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git status --short
git rev-parse HEAD
```

Require a clean worktree and verify that `bfca2e21ca7a46a5087b3addfcac7dab9d7e1618` is an ancestor of `HEAD`.

## Frozen Dataset

Use exactly the V71-verified devval manifest:

- rows: `1,845`;
- sequences: `85`;
- manifest SHA256: `113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54`;
- row-order SHA256: `dd454cfbafa39f2556628ad45dc191b39b0c54bb926028447d5f57553456e867`;
- RGB/IR/event/annotation presence: `1,845 / 1,845 / 1,845 / 1,845`.

Do not add, remove, replace, resample, reorder, or create another split.

## Frozen Models

Use exactly the six checkpoints already verified by V71:

- matched Early Fusion: seeds `0`, `1`, `2`;
- reliability-aware RA-RepDet with modality dropout `p=0.15`: seeds `0`, `1`, `2`.

Reverify their SHA256 and strict loading. Do not use MM-UAV-trained checkpoints, learned MM-UAV alignment, the MM-UAV Softplus wrapper, checkpoint averaging, ensembling, repair, or replacement weights.

## Frozen Naive Five-Channel Adapter

Before any prediction or metric, implement exactly one deterministic parameter-free adapter:

1. reuse the existing V53 per-modality decoding and independent letterbox implementation;
2. independently letterbox RGB, IR, and event to `640 x 640` using the same interpolation, aspect-ratio, padding, dtype, clipping, scaling, and normalization rules;
3. construct channels as:

```text
RGB[0:3] + independently-letterboxed IR grayscale + independently-letterboxed event grayscale
```

4. transform ground-truth boxes using RGB annotation geometry;
5. apply no homography, calibration, optical-flow warp, feature alignment, learned alignment, registration fitting, test-time fitting, or label-informed transform;
6. fail on missing, corrupt, unreadable, unexpected-channel, or non-finite inputs;
7. prohibit randomness and record adapter source SHA256 plus deterministic fixture outputs.

This adapter places independently normalized modality coordinates on one canvas. It does not assert physical pixel correspondence. Do not change it after the smoke pass begins.

## Frozen Evaluator

- input: `640 x 640`;
- score threshold: `0.001`;
- NMS threshold: `0.6`;
- maximum detections: `100`;
- vehicle ontology: reuse the frozen V65-V67 MM-UAV mapping;
- metrics: AP@[0.50:0.95], AP50, AP75, AR@1, AR@10, AR@100;
- no TTA, calibration, dataset-specific fitting, threshold selection, checkpoint selection, or post-result protocol changes.

## Immediate Execution Order

1. Reverify manifest, six checkpoints, protected paths, adapter determinism, and evaluator constants.
2. Run focused tests.
3. Run one no-metric smoke pass on the first `8` rows with Early Fusion seed `0`.
4. Fix only implementation errors such as imports, device placement, shapes, dtypes, finite-state handling, or decoding. Do not alter the scientific adapter contract.
5. Immediately evaluate each of the six checkpoints exactly once over all `1,845` rows.
6. Compute all frozen metrics and seed-matched `RA-RepDet - Early Fusion` differences.
7. Report per-method and paired-difference mean, sample standard deviation, minimum, and maximum across seeds.
8. Repeat focused tests and protected-file checks, then commit and push.

No result-driven rerun is allowed. A checkpoint may be rerun only when the first attempt ended before producing a complete metric record because of a documented implementation/runtime failure; preserve the failed-attempt record.

## Required Per-Checkpoint Results

- AP@[0.50:0.95], AP50, AP75;
- AR@1, AR@10, AR@100;
- prediction count;
- images with/without predictions;
- finite and valid decoded boxes;
- wall-clock time;
- peak GPU memory;
- execution-attempt count and any failure reason.

## Decision States

Choose exactly one:

- `V72_MMUAV_NAIVE_GRID_EXTERNAL_DOMAIN_STRESS_TEST_COMPLETE`;
- `V72_BLOCKED_CHECKPOINT_OR_MANIFEST_CONTRACT`;
- `V72_BLOCKED_RUNTIME_OOM_OR_FINITE_STATE`;
- `V72_BLOCKED_EVALUATOR_OR_OUTPUT_CONTRACT`;
- `V72_BLOCKED_SOURCE_PROTECTED_OR_PRIVATE_ARTIFACT_VIOLATION`.

Physical registration uncertainty is not a V72 blocked state because it is already declared as the central limitation of this stress test.

## Required Outputs

Create `runs/v72_mmuav_naive_grid_external_domain_stress_test/` with compact protocol, source lock, manifest/checkpoint verification, adapter contract/tests, smoke record, per-checkpoint metrics, paired comparison, timing/memory, claim boundary, tests, final decision, and handoff files. Keep raw data, annotations, full predictions, tensors, checkpoints, local paths, and heavy/private artifacts outside Git.

## Forbidden Work

- MM-UAV training, fine-tuning, adaptation, calibration, pseudo-labeling, or threshold tuning;
- additional adapter variants or alignment methods;
- checkpoint/seed/variant additions;
- result-driven preprocessing changes or reruns;
- provider/source/version/rights investigation as part of V72;
- manuscript edits before the metric run is complete and reviewed.

## Completion

Commit with exactly:

`exp: run V72 MM-UAV naive-grid external-domain stress test`

Push to `research/ra-repdet-triair`.