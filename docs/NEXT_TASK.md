# Current Task

## User Override (2026-07-15)

The user explicitly accepted the 424 completely extracted train sequences as the V52 local subset and changed the sampling interval from 30 to 20. Freeze source indices `1, 21, 41, ...` without renumbering. This override does not authorize treating frames without source GT rows as empty targets, bypassing geometry/license checks, or starting GPU work.

## Title

V52 audit MM-UAV tri-modal data and pre-register a compute-bounded sampling pilot.

## Goal

Audit the locally downloaded MM-UAV dataset at:

```text
D:\BaiduNetdiskDownload\MM-UAV
```

and determine whether it can support a scientifically valid second RGB--infrared--event detection experiment for RA-RepDet.

V52 has two phases:

1. a CPU-only dataset, annotation, synchronization, geometry, provenance, and sampling audit that may run while the V51 VisDrone GPU queue remains active;
2. a strictly bounded 200-iteration GPU pilot that may start only after the V51 queue has completed or the user has explicitly authorized stopping it.

Do not start full MM-UAV training in V52.

## Concurrent V51 Boundary

- Preserve the running V51 Route-B queue, its process state, manifests, checkpoints, logs, and all V50/V51 evidence.
- Do not stop, pause, resume, alter, or compete for GPU memory with V51 unless the user gives a separate explicit instruction.
- The V52 audit must remain CPU and storage-I/O only while V51 is running.
- The V52 pilot must refuse to start if a V51 training/evaluation process or another material CUDA workload is active.
- V51 remains RGB-only cross-validation evidence; V52 is a separate tri-modal dataset-feasibility task.

## Read First

1. `AGENTS.md`
2. `docs/PROJECT_CONTEXT.md`
3. `docs/EXPERIMENT_STATUS.md`
4. `docs/TASK_BLOCKER.md`
5. `docs/NEXT_TASK.md`
6. `runs/handoff_latest.md`
7. `runs/handoff_latest.json`
8. `runs/v48_complete_ablation/causal_ablation_summary.md`
9. `runs/v48_complete_ablation/claim_boundary.md`
10. `runs/v49_manuscript_integration/V49_MANUSCRIPT_INTEGRATION_REPORT.md`
11. `runs/v51_visdrone_recovery/source_lock_v51.md`
12. `runs/v51_visdrone_recovery/cv_run_status.json`
13. the existing TriAir loaders, model builders, detector preprocessing, evaluator, and COCO metric code needed only for compatibility review and the bounded pilot.

## Scientific Boundary

MM-UAV must not be treated as a second UAV-ground-vehicle dataset unless the local annotations establish that task. The expected target is airborne drone detection/tracking from another viewpoint, so V52 may support cross-dataset tri-modal fusion-mechanism evidence rather than same-task vehicle-generalization evidence.

Do not claim:

- two-dataset UAV ground-vehicle validation;
- pixel-perfect RGB/IR/event alignment before it is measured;
- official sequence counts or train/test counts based only on web descriptions;
- event-channel detection labels if only RGB/IR annotations exist;
- calibrated sensor reliability;
- real sensor-fault robustness;
- statistical significance;
- universal causality or optimal modality dropout.

## Required Output Directory

Create:

```text
runs/v52_mmuav_audit/
```

Do not copy raw images, event frames, archives, or the full dataset into the repository.

## Stage 1: Local Dataset and Provenance Audit

Create:

```text
runs/v52_mmuav_audit/dataset_audit.md
runs/v52_mmuav_audit/dataset_audit.json
runs/v52_mmuav_audit/directory_inventory.csv
runs/v52_mmuav_audit/provenance_and_license.md
```

Record from local evidence:

- exact dataset root and audit timestamp;
- total on-disk size and available free space;
- all top-level and relevant nested directories;
- actual sequence counts by split and modality;
- RGB, IR, and event file formats;
- image dimensions, channel counts, bit depths, and numeric ranges from representative files;
- annotation directories and formats, including whether RGB and IR use separate boxes;
- whether test annotations are locally available;
- local README, license, split lists, metadata, conversion scripts, and provider information;
- SHA256 hashes for split files, annotation index files, metadata, README/license files, and conversion scripts;
- incomplete archives, corrupted files, missing sequence directories, zero-byte files, or extraction errors;
- the exact local evidence supporting the dataset name and version.

Do not hash every 400 GB frame file unless required for a targeted integrity check. Use deterministic inventory hashes over sorted relative paths, sizes, and modification metadata, plus exact hashes for all manifests and a reproducible sample of media files.

## Stage 2: Tri-Modal Synchronization Audit

Create:

```text
runs/v52_mmuav_audit/synchronization_audit.md
runs/v52_mmuav_audit/synchronization_audit.json
runs/v52_mmuav_audit/sequence_alignment.csv
runs/v52_mmuav_audit/missing_frame_report.csv
```

For every sequence, determine:

- RGB frame count and frame-index range;
- IR frame count and frame-index range;
- event-frame count and frame-index range;
- whether filenames permit an exact one-to-one synchronized triplet mapping;
- missing, duplicated, non-monotonic, or unmatched frame indices;
- frame-rate or timestamp metadata when locally available;
- whether event data are rendered event frames, voxel grids, accumulations, or raw event streams;
- whether the three modalities share resolution and coordinate origin;
- whether sequence names and split membership match across modalities.

The audit must not silently align by list position when frame IDs or timestamps disagree.

## Stage 3: Annotation and Geometry Audit

Create:

```text
runs/v52_mmuav_audit/annotation_audit.md
runs/v52_mmuav_audit/annotation_audit.json
runs/v52_mmuav_audit/geometry_audit.csv
runs/v52_mmuav_audit/category_mapping.md
runs/v52_mmuav_audit/category_mapping.json
```

Determine:

- source category IDs and names;
- bounding-box format and coordinate convention;
- track-ID, visibility, occlusion, truncation, ignore, difficult, and confidence fields;
- whether RGB and IR boxes describe the same physical targets but differ geometrically;
- whether event frames have their own annotation coordinate system;
- the number of empty-target frames;
- invalid, out-of-bounds, zero-area, duplicate, or malformed boxes;
- target-size distributions and object counts after the proposed sampling rule;
- whether RGB annotations, IR annotations, or a justified transformed annotation set should define the detection coordinate system.

Measure RGB-to-IR geometric disagreement on a deterministic, source-locked sample of at least 100 annotated synchronized frames spanning at least 20 sequences, where available. Report box-center displacement, size-ratio differences, matched-target IoU, and the matching rule. Do not infer pixel alignment from matching frame numbers alone.

If no scientifically defensible common detection coordinate system can be established, stop with a blocker before pilot training.

## Stage 4: Pre-Registered 1-in-30 Sampling Protocol

Before inspecting any model metric, create and freeze:

```text
runs/v52_mmuav_audit/sampling_protocol.md
runs/v52_mmuav_audit/sampling_protocol.json
runs/v52_mmuav_audit/manifests/train_sampled.txt
runs/v52_mmuav_audit/manifests/devval_sampled.txt
runs/v52_mmuav_audit/sampled_manifest.json
runs/v52_mmuav_audit/split_integrity.md
```

Default sampling rule:

```text
for each sequence, keep synchronized frame indices 0, 30, 60, 90, ...
```

If the local indexing starts at 1, use `1, 31, 61, 91, ...` and record that fact. Do not renumber frames to make the rule appear zero-based.

Rules:

- RGB, IR, and event must use the same source frame index or verified timestamp match;
- preserve complete sequences as the split unit;
- never randomly divide neighboring frames from the same sequence between train and development-validation;
- preserve the source-provided train/test split only when its provenance and labels are established;
- when a development-validation split is needed, derive it deterministically from training sequences before any model metric is observed;
- each sequence must contribute at least one valid synchronized annotated sample;
- include the last valid synchronized frame only when this exception is pre-registered and applied identically to every sequence;
- record rejected triplets and the exact rejection reason;
- hash all frozen manifests and the sampling script;
- do not change the interval after seeing pilot losses or metrics.

Report expected sample counts, object counts, sequence counts, and estimated epochs/iterations for intervals 10, 20, and 30 for planning, but freeze interval 30 as the V52 pilot protocol unless the audit proves it invalid before any pilot run.

## Stage 5: Dataset Adapter and Preflight

Implement only the minimum new MM-UAV-specific code required for audit and pilot readiness, preferably under:

```text
datasets/mmuav_dataset.py
rarepdet/tools/audit_v52_mmuav.py
rarepdet/tools/prepare_v52_mmuav.py
rarepdet/tools/preflight_v52_mmuav.py
tests/test_v52_mmuav.py
```

The adapter must:

- load one synchronized RGB/IR/event triplet from the frozen manifest;
- expose the exact annotation coordinate system selected by the audit;
- preserve original annotations unchanged;
- resize all inputs and boxes with an explicitly tested transform;
- document normalization and channel order;
- return deterministic results for evaluation mode;
- reject mismatched frame IDs rather than substituting the nearest file silently;
- handle empty-target frames correctly;
- avoid loading whole sequences into memory.

Required preflight checks:

- parse representative files from every modality;
- validate at least 100 synchronized triplets across at least 20 sequences;
- verify sampled manifests are sequence-disjoint;
- verify every manifest row references existing files and valid annotations;
- verify input tensor shapes, dtypes, finite values, and ranges;
- verify box geometry after resize;
- visualize a small local-only set of overlaid RGB and IR boxes for human review without committing large images;
- run a dataset-loader throughput test with no GPU;
- run one forward/backward batch only when the GPU gate permits;
- run unit tests and save exact commands and outputs.

Save:

```text
runs/v52_mmuav_audit/preflight_commands.txt
runs/v52_mmuav_audit/preflight_outputs.txt
runs/v52_mmuav_audit/loader_benchmark.json
```

## Stage 6: Bounded GPU Pilot Gate

The pilot is not authorized while V51 or another material CUDA workload is active.

Before starting the pilot, create:

```text
runs/v52_mmuav_audit/pilot_gate.json
runs/v52_mmuav_audit/source_lock_v52.md
runs/v52_mmuav_audit/source_lock_v52.json
```

The gate must verify:

- V51 queue and training/evaluation processes are complete or explicitly stopped by user authorization;
- the NVIDIA device has no conflicting project process;
- all audit, mapping, synchronization, sampling, split, adapter, and evaluator hashes are frozen;
- the exact 5--10 pilot sequences are selected without reference to model results;
- pilot configuration is frozen before the first optimization step.

Default pilot:

```text
sequences: 8 total, selected deterministically across available source conditions
sampling: every 30th synchronized frame
model: matched early fusion only
initialization: same policy as the main project, recorded exactly
input: 640 x 640
precision: AMP
batch size: 2 initially; increase to 4 only if a pre-run memory probe passes
optimizer: project default unless a pre-result source-lock note identifies incompatibility
iterations: exactly 200 optimizer steps
validation: no performance claim; data/geometry smoke evaluation only
```

The pilot must stop after 200 optimizer steps. Do not convert it into an epoch-based training run.

Record:

- peak allocated and reserved GPU memory;
- mean and percentile iteration time after warm-up;
- data-loading wait time;
- AMP scaler behavior;
- loss components and non-finite checks;
- CPU RAM use where practical;
- read throughput;
- estimated wall time for 20 and 30 epochs at the frozen interval-30 sample count;
- OOM or I/O errors and exact recovery actions.

Save:

```text
runs/v52_mmuav_audit/pilot_config.json
runs/v52_mmuav_audit/pilot_log.txt
runs/v52_mmuav_audit/pilot_profile.json
runs/v52_mmuav_audit/pilot_report.md
```

No AP, mechanism, robustness, or generalization claim may be made from this pilot.

## Route Decision After Audit and Pilot

Create:

```text
runs/v52_mmuav_audit/feasibility_decision.md
runs/v52_mmuav_audit/feasibility_decision.json
runs/v52_mmuav_audit/claim_boundary.md
```

Choose exactly one outcome:

1. `GO_TRI_MODAL_CONTROLLED_EXPERIMENT` — synchronization, geometry, annotations, compute, and licensing are adequate;
2. `GO_WITH_ALIGNMENT_MODULE_REQUIRED` — data are usable, but direct channel-aligned fusion is invalid and a pre-registered alignment method is required;
3. `GO_RGB_IR_ONLY_EVENT_EXCLUDED` — event representation or synchronization is unusable, so this dataset cannot support the intended tri-modal claim;
4. `NO_GO_DATA_OR_LICENSE_BLOCKER` — provenance, labels, corruption, geometry, storage, or license prevents a defensible experiment.

A future full experiment is outside V52. Do not start matched-early, static-equal, dynamic-gate, or multi-seed full training until a new task is approved.

## Allowed Files To Modify

- `docs/NEXT_TASK.md`
- `docs/EXPERIMENT_STATUS.md`
- `docs/TASK_BLOCKER.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`
- new directory `runs/v52_mmuav_audit/**`
- new MM-UAV-specific adapters and audit/pilot tools under `datasets/**` and `rarepdet/tools/**`
- tests under `tests/**`
- minimal model-construction plumbing required only for the bounded pilot.

## Forbidden Changes

- raw files under `D:\BaiduNetdiskDownload\MM-UAV`;
- stopping or modifying V51 without separate explicit user authorization;
- deletion or rewriting of V40--V51 evidence;
- TriAir locked-holdout access;
- manuscript title, abstract, body, tables, bibliography, or conclusions;
- full MM-UAV training;
- more than 200 pilot optimizer steps;
- result-driven changes to interval, split, coordinate system, categories, or pilot sequences;
- fabrication of missing modalities, labels, timestamps, or geometric calibration;
- copying large raw media or checkpoints into GitHub.

## Required Completion Outputs

- complete local provenance and dataset audit;
- synchronization and missing-frame audit;
- annotation and geometry audit;
- frozen sequence-disjoint interval-30 manifests;
- MM-UAV loader and preflight evidence;
- CPU loader benchmark;
- bounded 200-step GPU pilot when the GPU gate permits, or an exact blocker if V51 is still running;
- feasibility decision and claim boundary;
- updated experiment status and handoff;
- `docs/TASK_BLOCKER.md` only when a real blocker remains.

## Acceptance Criteria

- the local data are described from actual files, not web-only assumptions;
- actual sequence/split/frame counts and formats are recorded;
- RGB, IR, and event synchronization is tested rather than assumed;
- annotation coordinate systems and cross-modal geometric disagreement are quantified;
- interval-30 sampling and sequence-disjoint splitting are frozen before any model result;
- no V51 process is disrupted or contended with;
- no full MM-UAV training starts;
- the pilot performs exactly 200 optimizer steps and records memory/time/I/O evidence, or records a precise GPU-availability blocker;
- the final decision states whether direct tri-modal fusion is scientifically defensible;
- no external vehicle-detection, blind-test, calibrated-reliability, real-fault, significance, or universal-causality claim is introduced;
- repository tests, source-lock checks, claim scan, handoff update, and `finish_task.ps1` complete successfully, or an exact blocker is committed.

## Commit Message

data: audit MM-UAV and prepare bounded tri-modal pilot
