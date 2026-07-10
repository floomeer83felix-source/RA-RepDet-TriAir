# Current Task

## Title

V48 complete three-seed causal ablations, static fusion controls, and efficiency profiling.

## Goal

Complete the causal evidence needed to explain the V46 performance gains while preserving the locked-holdout boundary.

The task has three parts:

1. Finish seed1 and seed2 for the two already implemented fresh ablations:
   - `ra_no_moddrop`;
   - `early_moddrop`.
2. Add two source-locked static-control architectures that separate modality-specific stems from dynamic softmax gating:
   - `ra_static_equal`;
   - `ra_stems_project`.
3. Measure parameters, FLOPs/MACs, batch-one latency, throughput, and peak memory for the matched early and full reliability-aware models, with optional measurements for completed ablation variants.

Do not use the locked same-dataset holdout for training, checkpoint selection, architecture selection, seed continuation, threshold selection, or ablation comparison. V48 causal results are development-validation evidence only.

## Read First

1. `AGENTS.md`
2. `PROJECT_PROFILE.md`
3. `docs/PROJECT_CONTEXT.md`
4. `docs/EXPERIMENT_STATUS.md`
5. `docs/TASK_BLOCKER.md`
6. `runs/handoff_latest.md`
7. `runs/handoff_latest.json`
8. `runs/v46_coco_ablation/source_lock_v46.md`
9. `runs/v46_coco_ablation/coco_metric_summary.md`
10. `runs/v46_coco_ablation/ablation_devval_summary.md`
11. `runs/v46_coco_ablation/ablation_claim_boundary.md`
12. `runs/v46_coco_ablation/ablation_execution_status.json`
13. `runs/v46_coco_ablation/ablation_train_commands.txt`
14. `rarepdet/train_early_fusion.py`
15. `rarepdet/models/repvit_fpn_backbone.py`
16. `rarepdet/models/early_fusion_fcos.py`
17. `rarepdet/eval_map.py`
18. `rarepdet/coco_metrics.py` if present
19. `submission/sivp/tex/ra_repdet_sivp.tex` for terminology only; do not edit it during V48.

## Starting Evidence

The following V46 outputs are frozen inputs:

- canonical COCO-style evaluation for the six fixed matched-early / full-RA seed0/1/2 checkpoints;
- `ra_no_moddrop_seed0` trained for 50 epochs and selected by development-validation AP50;
- `early_moddrop_seed0` trained for 50 epochs and selected by development-validation AP50;
- no ablation guard evaluation;
- no static-equal or deterministic-projection control yet.

Existing V46 seed0 contrasts are descriptive only and must not be promoted to multi-seed conclusions until V48 is complete.

## Frozen Assets and Boundaries

- Frozen V40 training and development-validation manifests remain unchanged.
- The locked same-dataset guard manifest and all guard predictions/results remain untouched.
- Existing V40/V41/V42/V46 checkpoints, source locks, manifests, and evidence summaries are immutable.
- Existing V47 manuscript structure, 40-reference package, bibliography closure, and compile reports are immutable during V48.
- Best checkpoints must be selected only by the pre-existing development-validation AP50 rule.
- Training length, image size, optimizer, learning rate, batch size, evaluator conventions, and seeds must match the active V40/V41/V46 protocol unless a source-lock report documents an unavoidable implementation-specific exception.

## Allowed Files To Modify

- `docs/NEXT_TASK.md`
- `docs/EXPERIMENT_STATUS.md`
- `docs/TASK_BLOCKER.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`
- New directory: `runs/v48_complete_ablation/**`
- Existing V46 ablation output directories only for appending clearly named seed1/2 run artifacts if the established layout requires it; do not overwrite seed0 files
- `rarepdet/train_early_fusion.py` only for clean variant selection/plumbing required by the new controls
- `rarepdet/models/early_fusion_fcos.py`
- `rarepdet/models/repvit_fpn_backbone.py` only if strictly necessary
- New dedicated module: `rarepdet/models/ablation_fusion_fcos.py`
- New configs under `configs/v48_ablation/**`
- New evaluation/reporting/profiling scripts under `rarepdet/tools/**`
- Tests under `tests/**` for the added variants and profiling utilities

## Forbidden Files To Modify

- Raw data, labels, images, videos, original event arrays, secrets, or existing checkpoints.
- Frozen train/dev-val/guard manifests or split-generation logic.
- Existing V40/V41/V42/V46 result summaries, source locks, hashes, or prediction caches.
- SIVP manuscript narrative, tables, bibliography, title, abstract, or conclusion during V48.
- Any guard evaluation, guard prediction generation, or holdout-facing report for the new ablation variants.
- Repository release metadata, DOI, dataset-license claims, or public archive claims.

## Required Work

### 1. Create V48 source lock

Create:

```text
runs/v48_complete_ablation/source_lock_v48.md
runs/v48_complete_ablation/source_lock_v48.json
```

Record:

- starting commit SHA and branch;
- Python, PyTorch, torchvision, CUDA, GPU, driver, and OS versions;
- SHA256 of train and development-validation manifests;
- SHA256 of all relevant training, model, evaluator, COCO-metric, and profiling files;
- exact seed0 checkpoint hashes inherited from V46;
- exact training-selection rule;
- explicit statement that locked holdout access is forbidden in V48.

### 2. Finish existing fresh ablation seeds

Run the exact V46-compatible 50-epoch protocol for:

```text
ra_no_moddrop_seed1
ra_no_moddrop_seed2
early_moddrop_seed1
early_moddrop_seed2
```

Use:

- seeds `1` and `2`;
- frozen V40 train/dev-val manifests;
- development-validation AP50 checkpoint selection;
- no guard evaluation.

Preserve exact commands, stdout/stderr logs, runtime, checkpoint hash, and selected epoch.

### 3. Implement static fusion controls

Implement the controls in a dedicated, reviewable architecture module rather than duplicating model code inside a reporting script.

#### `ra_static_equal`

- same RGB/T/E modality-specific stems as the full RA model;
- fixed fusion weights `1/3, 1/3, 1/3`;
- no learned dynamic gate;
- no modality dropout;
- same post-fusion projection and shared RepViT--FPN--FCOS detector.

#### `ra_stems_project`

- same RGB/T/E modality-specific stems as the full RA model;
- concatenate stem features in a fixed modality order;
- use one learned deterministic projection to the shared fusion width;
- no dynamic softmax gate;
- no modality dropout;
- same shared detector stack.

The implementations must expose the same training/evaluation interface as existing early and reliability variants. Add smoke tests that check output structure, tensor shapes, parameter gradients, checkpoint save/load, and deterministic inference in evaluation mode.

Train seed0 first for both variants. If seed0 succeeds and the implementation/source lock remains unchanged, continue seeds1 and 2. If GPU time is insufficient, commit an explicit partial state rather than fabricating multi-seed results.

### 4. Evaluate all completed variants on development-validation

For every completed run, report:

- precision;
- recall;
- F1;
- canonical COCO AP@[0.50:0.95];
- AP50;
- AP75;
- AR100;
- selected epoch;
- training runtime.

Target final matrix:

| Variant | Separate stems | Dynamic gate | Modality dropout | Seeds |
| --- | --- | --- | --- | --- |
| `matched_early` | no | no | no | 0,1,2 frozen |
| `early_moddrop` | no | no | yes | 0,1,2 |
| `ra_static_equal` | yes | no | no | 0,1,2 if feasible |
| `ra_stems_project` | yes | no | no | 0,1,2 if feasible |
| `ra_no_moddrop` | yes | yes | no | 0,1,2 |
| `ra_full_p015` | yes | yes | yes | 0,1,2 frozen |

Compute seed-paired deltas only where the same seeds are available. Use descriptive mean and sample SD; do not run or claim significance testing unless separately authorized.

### 5. Efficiency profiling

Profile at minimum:

- `matched_early`;
- `ra_full_p015`.

Optionally profile all completed ablation variants.

Report:

- trainable and total parameter counts;
- MACs or FLOPs at input size 640, with the counting convention named;
- batch-one latency after warm-up;
- throughput/FPS;
- peak allocated GPU memory;
- hardware and precision mode;
- warm-up iterations, measured iterations, synchronization procedure, and mean/median/p95 latency.

Use identical hardware, input shape, precision mode, and measurement procedure for all compared models. Do not include data-loading time unless reported separately.

### 6. Required outputs

Create at least:

```text
runs/v48_complete_ablation/source_lock_v48.md
runs/v48_complete_ablation/source_lock_v48.json
runs/v48_complete_ablation/train_commands.txt
runs/v48_complete_ablation/run_status.json
runs/v48_complete_ablation/devval_per_run.csv
runs/v48_complete_ablation/devval_paired_deltas.csv
runs/v48_complete_ablation/causal_ablation_summary.md
runs/v48_complete_ablation/causal_ablation_summary.json
runs/v48_complete_ablation/efficiency_per_model.csv
runs/v48_complete_ablation/efficiency_summary.md
runs/v48_complete_ablation/efficiency_summary.json
runs/v48_complete_ablation/claim_boundary.md
runs/v48_complete_ablation/claim_scan.txt
runs/v48_complete_ablation/claim_scan_review.md
runs/v48_complete_ablation/preflight_commands.txt
runs/v48_complete_ablation/preflight_outputs.txt
```

Each trained run directory must contain or reference:

- exact command;
- config;
- environment;
- training log;
- selected checkpoint;
- selected epoch;
- checkpoint SHA256;
- development-validation metrics;
- runtime.

### 7. Required causal contrasts

Report the following paired contrasts where seed coverage permits:

```text
ra_full_p015 - matched_early
ra_no_moddrop - matched_early
ra_full_p015 - ra_no_moddrop
early_moddrop - matched_early
ra_static_equal - matched_early
ra_no_moddrop - ra_static_equal
ra_stems_project - matched_early
ra_no_moddrop - ra_stems_project
```

Interpretation rules:

- `early_moddrop - matched_early` estimates the architecture-specific effect of applying modality dropout to early fusion.
- `ra_full_p015 - ra_no_moddrop` estimates the incremental effect of modality dropout within the RA architecture.
- `ra_static_equal - matched_early` estimates the combined effect of modality-specific stems and equal-weight feature fusion.
- `ra_no_moddrop - ra_static_equal` provides the cleanest available estimate of dynamic gating beyond equal-weight stem fusion.
- `ra_stems_project` is a deterministic learned-fusion control and must not be described as isolating stems alone without qualification.

### 8. Claim scan

Scan all V48 outputs for prohibited claims:

```text
external generalization
independent benchmark
statistical significance
proves causality
optimal dropout
calibrated reliability
sensor health probability
real sensor-fault robustness
guard-selected
holdout-selected
```

Allowed language is descriptive multi-seed development-validation causal contrast, subject to the exact implemented controls and completed seed coverage.

### 9. Preflight

At minimum run:

- import and model-construction tests for all variants;
- forward-pass shape tests;
- backward-pass/gradient smoke test;
- checkpoint save/load test;
- deterministic evaluation-mode test;
- evaluator/COCO metric smoke tests;
- profiling-script smoke test;
- repository submission preflight if available.

## Acceptance Criteria

- `ra_no_moddrop` and `early_moddrop` have seed0/1/2 development-validation results, or a precise GPU-time blocker records the unfinished seeds.
- `ra_static_equal` and `ra_stems_project` are implemented in a dedicated source-locked module and pass model, gradient, and checkpoint tests.
- Static-control training reaches seed0 at minimum; three seeds are preferred.
- No new ablation variant is evaluated on the locked holdout.
- All completed variants use the frozen development-validation protocol and the predefined AP50 checkpoint-selection rule.
- Canonical COCO-style metrics and project metrics are reported for every completed run.
- Efficiency measurements are reproducible and use identical hardware/procedure.
- Causal statements remain bounded by seed coverage and control design.
- Existing evidence packages, manuscript files, datasets, manifests, and checkpoints remain unchanged.

## Commit Message

`eval: complete V48 causal ablations and efficiency profiling`

## Completion / Blocker Rule

On completion, update:

- `docs/EXPERIMENT_STATUS.md`;
- `docs/TASK_BLOCKER.md`;
- `runs/handoff_latest.md`;
- `runs/handoff_latest.json`.

Commit and push all source locks, code, logs, summaries, and preflight outputs.

If GPU time is insufficient, finish one complete seed block at a time and commit an explicit partial state. If a static control cannot be implemented without changing the shared detector semantics, stop and document the exact technical reason. Do not use the locked holdout to decide whether to continue, do not invent missing seeds, and do not weaken the claim boundary.
