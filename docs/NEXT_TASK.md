# Current Task

## User Authorization (2026-07-15)

The user authorizes one bounded **V54 MM-UAV GPU verification pilot** under the standing local, private-research-only instruction.

This authorization permits CUDA integration checks and at most **200 completed optimizer steps** for one pre-registered primary pilot. It does not authorize epoch training, AP evaluation, multi-seed experiments, hyperparameter search, manuscript edits, public release, redistribution, or external sharing.

Do not ask the user to reconfirm the private-research scope. Reconfirmation is required only before public redistribution, external sharing, commercial use, or a new manuscript/public benchmark claim.

## Title

V54 MM-UAV learned feature-alignment 200-step GPU verification pilot.

## Goal

Verify that the V53 RGB-supervised, three-branch learned feature-alignment design can be integrated with the existing RepViT-FCOS detector interface and can complete a tightly bounded GPU optimization pilot on the RTX 3090 without:

- raw RGB/IR/event channel concatenation;
- target-coordinate leakage;
- development-validation fitting;
- out-of-memory failure;
- non-finite losses or gradients;
- uncontrolled affine-grid collapse;
- accidental changes to the production TriAir path.

The V54 result is an engineering and numerical-stability verdict only. A 200-step pilot must not be reported as detector accuracy evidence.

## Required Start

Run:

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git rev-parse HEAD
```

Expected starting branch tip at authorization:

```text
b2f6e3e15c10589810d8e8c5b0f64263d9f9a14e
```

Record the actual starting commit SHA. Stop and reconcile before GPU work if the branch has unexpected uncommitted changes or the V53 source lock cannot be reproduced.

Read first:

- `AGENTS.md`
- `docs/PROJECT_CONTEXT.md`
- `docs/EXPERIMENT_STATUS.md`
- `docs/TASK_BLOCKER.md`
- `docs/NEXT_TASK.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`
- all files under `runs/v52_mmuav_audit/`
- all files under `runs/v53_mmuav_feature_alignment_preflight/`
- `datasets/mmuav_feature_alignment_dataset.py`
- `rarepdet/experimental/mmuav_feature_alignment.py`
- `rarepdet/experimental/mmuav_feature_alignment_model.py`
- current RepViT-FCOS builders, detector interfaces, optimizer setup, and training utilities needed for isolated integration

V51 remains separate and must not be modified.

## Standing Private-Research Boundary

- Work only with locally available MM-UAV files.
- Do not add raw images, event frames, annotations, transformed media, weights, or checkpoints to Git.
- Do not publish or redistribute MM-UAV media, annotations, derivative labels, converted datasets, or trained checkpoints.
- Keep the unresolved MM-UAV redistribution license visible in status and handoff records.
- The local-only scope is already frozen and must not be repeatedly reconfirmed.

## Frozen Data and Target Contract

Preserve the V53 source lock exactly unless a reproducible parser error is found:

- source root: `E:\MM-UAV_extracted\MMMUAV\train`;
- train manifest: `runs/v53_mmuav_feature_alignment_preflight/manifests/train_rgb_supervised.txt`;
- development-validation manifest: `runs/v53_mmuav_feature_alignment_preflight/manifests/devval_rgb_supervised.txt`;
- RGB-supervised rows: 7,187 train + 1,845 development-validation = 9,032;
- 106 IR-only rows remain excluded;
- 35,898 rows remain `UNLABELED` and excluded;
- train/devval sequences remain disjoint: 339 / 85;
- RGB boxes are the sole detector targets;
- IR boxes remain metadata only;
- event has no detector target;
- native modalities remain independently loaded and independently preprocessed;
- no box transfer, interpolation, pseudo-labeling, or empty-target conversion is permitted.

Before CUDA work, reproduce the V53 manifest hashes and exact counts. Fail closed if they differ.

## Frozen Architecture Contract

Use a V54-only experimental integration path. Do not change the default TriAir builder or dataset behavior.

Required dataflow:

```text
RGB input   -> RGB experimental stem ---------------------------> RGB reference features
IR input    -> IR experimental stem -> learned feature alignment -> aligned IR features
Event input -> Event experimental stem -> learned alignment ----> aligned event features
RGB reference + aligned IR + aligned event -> fixed equal fusion -> existing RepViT-FCOS detector path
```

Rules:

- RGB defines the reference feature grid and detection coordinate system.
- IR and event may be aligned only in feature space.
- The V53 STN-inspired residual affine aligners must start from exact identity initialization.
- The primary 200-step pilot must use **alignment enabled with fixed/equal fusion** to isolate alignment stability from RA dynamic gating.
- `alignment_enabled=False` must remain available as the no-alignment control.
- The reliability-aware fusion path must remain available for a smoke check but is not the primary 200-step pilot.
- Do not fit alignment from RGB/IR boxes, track IDs, development-validation GT, or detection metrics.
- Do not introduce provider constants that were not source-locked and explained by V52/V53.
- Freeze and record the exact integration stage before observing GPU losses.

Preferred implementation locations:

```text
rarepdet/experimental/mmuav_feature_alignment_detector.py
rarepdet/tools/run_v54_mmuav_gpu_pilot.py
configs/ or runs/v54_mmuav_gpu_pilot/ for the frozen pilot config
```

A different isolated path is acceptable after repository inspection, but production defaults must remain unchanged.

## Pilot Protocol

### Fixed primary run

Run exactly one primary pilot with:

- variant: learned feature alignment enabled + fixed/equal fusion;
- optimizer steps: maximum 200 completed steps;
- random seed: 0;
- branch input size: 320x320;
- batch size: 1;
- train manifest only for optimization;
- deterministic sample-order generator with the order/hash recorded;
- no hyperparameter search;
- no learning-rate selection from development-validation behavior;
- no AP, AR, checkpoint comparison, or model-selection metric.

Use the nearest existing detector optimizer and scheduler defaults after repository inspection. Freeze all selected optimizer, learning-rate, scheduler, precision, gradient-clipping, augmentation, and backbone-initialization values in `pilot_config.json` **before** the first optimizer step. Do not change them after observing pilot losses.

Use the project's existing precision policy where possible. Record whether AMP is enabled. Do not silently switch precision after optimizer steps begin.

### Pre-run CUDA smoke matrix

Before the primary pilot, run forward and backward without `optimizer.step()` for these four interfaces on a fixed train batch:

1. RGB-only detector interface;
2. three stems, alignment disabled, fixed/equal fusion;
3. learned alignment enabled, fixed/equal fusion;
4. learned alignment enabled, reliability-aware fusion.

These smoke checks must not increment the completed optimizer-step counter. Record finite losses, tensor shapes, gradient availability, and peak memory for each interface.

### Optional post-run inference smoke

After step 200, a fixed, source-locked development-validation subset of at most 16 samples may be used for no-grad inference-path validation only. Record only execution success, finite outputs, shapes, latency, and memory. Do not compute AP/AR or use the results to tune the model.

## Memory and Stop Rules

Reset and record CUDA peak-memory statistics separately for every smoke variant and the primary pilot.

Record:

- GPU model and driver/runtime versions;
- total, allocated, reserved, and peak CUDA memory;
- `nvidia-smi` snapshots before launch, after warmup, near peak, and after completion;
- data time, forward time, backward time, optimizer time, and total step time;
- checkpoint size and SHA256 if a local step-200 checkpoint is produced.

Immediate hard stop conditions:

- CUDA OOM during the primary run;
- any non-finite total or component loss;
- any non-finite gradient or parameter;
- non-finite affine theta/grid values;
- missing RGB targets or target-coordinate mismatch;
- sample-order or manifest-hash mismatch;
- accidental use of development-validation samples for optimization;
- accidental modification of protected production, V40--V53 evidence, or manuscript files.

OOM handling:

- A dry-run OOM before any optimizer step may be reported and the task must stop as `V54_BLOCKED_OOM_OR_MEMORY`.
- Do not automatically reduce resolution, batch size, model width, precision, or enabled modalities after observing an OOM.
- Do not continue with a different configuration without a new task authorization.

## Required Training Diagnostics

For every completed optimizer step, log at least:

- sample/original row ID;
- total loss and each detector loss component;
- learning rate;
- global gradient norm;
- alignment-parameter gradient norms for IR and event;
- affine theta mean, standard deviation, minimum, maximum, and maximum absolute deviation from identity for IR and event;
- affine determinant statistics where applicable;
- finite/non-finite flags;
- CUDA allocated/reserved memory;
- step and data-loading time.

At steps 0, 1, 10, 50, 100, 150, and 200, additionally record:

- representative feature shapes;
- RGB/IR/event feature mean and standard deviation before and after alignment;
- aligned-grid out-of-bounds sampling fraction or an equivalent grid-validity diagnostic;
- whether alignment parameters changed from initialization;
- fusion-interface outputs and weights when applicable.

Do not interpret lower training loss as accuracy improvement.

## Required Outputs

Create:

```text
runs/v54_mmuav_gpu_pilot/
  pilot_config.json
  source_lock_v54.json
  source_lock_v54.md
  smoke_matrix.json
  smoke_matrix.md
  training_log.csv
  training_summary.json
  training_summary.md
  memory_trace.csv
  alignment_trace.csv
  sample_order.txt
  sample_order_sha256.txt
  checkpoint_metadata.json
  postrun_inference_smoke.json
  test_commands.txt
  test_output.txt
  pilot_decision.json
  pilot_decision.md
```

Heavy local artifacts such as checkpoints and tensor dumps must remain outside Git. Commit only metadata, hashes, compact logs, and summaries.

## Required Tests

Add or update V54-specific tests to verify:

- V53 manifest hashes and counts remain exact;
- batch construction uses train RGB-supervised rows only;
- development-validation rows cannot enter the optimizer data loader;
- RGB boxes pass only through the RGB preprocessing transform;
- all three modalities use independent input branches;
- no raw-channel concatenation path exists;
- alignment-off and alignment-on detector integrations both produce finite CPU outputs;
- identity initialization remains exact before training;
- the four CUDA smoke interfaces are configured distinctly;
- the primary pilot variant is alignment-on + fixed/equal fusion;
- optimizer-step counter cannot exceed 200;
- non-finite and OOM conditions fail closed;
- pilot logs include memory, loss, gradient, theta, and sample-order fields;
- checkpoints are excluded from Git and only metadata/hashes are committed;
- production TriAir defaults, V40--V53 historical evidence, V51 evidence, and manuscript files are unchanged.

Run CPU tests before CUDA. Save exact commands and complete outputs.

## Allowed Changes

- `docs/NEXT_TASK.md`
- `docs/EXPERIMENT_STATUS.md`
- `docs/TASK_BLOCKER.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`
- `runs/v54_mmuav_gpu_pilot/**`
- V54-only experimental integration files under `rarepdet/experimental/**`
- V54-only pilot tools under `rarepdet/tools/**`
- V54-only configuration files
- V54-specific tests under `tests/**`
- minimal import/export changes needed to expose V54 experimental modules without changing defaults

## Forbidden Changes

- raw MM-UAV files or source annotations;
- V40--V53 historical evidence other than current status/handoff pointers;
- V51 process evidence or status history;
- default TriAir dataset semantics;
- production experiment defaults;
- public or redistributable MM-UAV derivatives;
- manuscript files;
- epoch training, AP/AR evaluation, multi-seed runs, hyperparameter sweeps, or more than 200 optimizer steps;
- automatic configuration fallback after OOM or instability.

## Decision Output

At completion choose exactly one:

- `V54_GPU_PILOT_PASS_READY_FOR_PAIRED_ALIGNMENT_ABLATION`
- `V54_BLOCKED_DETECTOR_INTEGRATION`
- `V54_BLOCKED_DATA_OR_TARGET_CONTRACT`
- `V54_BLOCKED_OOM_OR_MEMORY`
- `V54_BLOCKED_NUMERICAL_INSTABILITY`
- `V54_BLOCKED_TEST_OR_PROTECTED_FILE_VIOLATION`

A pass requires all 200 optimizer steps to complete with finite losses and gradients, stable logging, no contract violation, no OOM, and a locked source/config record. It does not establish accuracy or justify manuscript claims.

Update:

```text
docs/EXPERIMENT_STATUS.md
docs/TASK_BLOCKER.md
runs/handoff_latest.md
runs/handoff_latest.json
```

## Finish

Run:

```powershell
powershell -ExecutionPolicy Bypass -File rarepdet/tools/finish_task.ps1
```

Commit and push with a concise message such as:

```text
exp: run V54 MM-UAV alignment GPU pilot
```

## Final Report Requirements

The final report must state:

- starting and final commit SHA;
- exact frozen manifest counts and hashes;
- full frozen pilot configuration;
- selected detector integration point;
- smoke-matrix results;
- completed optimizer-step count;
- peak allocated/reserved GPU memory;
- step-time summary;
- loss and gradient finite-status summary;
- IR/event affine-theta and grid-validity summary;
- checkpoint metadata/hash, if produced;
- tests and protected-file verification;
- confirmation that no AP/AR or manuscript claim was produced;
- final V54 decision state.
