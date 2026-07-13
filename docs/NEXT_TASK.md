# Current Task

## Title

V50 audit and evaluate `D:\datasets\visdrone_seen` as a second external aerial vehicle-detection dataset.

## Goal

Strengthen the RA-RepDet evidence package with a source-locked second-dataset evaluation while preserving the scientific boundary between full RGB--thermal--event validation and RGB-only external evidence.

The local dataset root is:

```text
D:\datasets\visdrone_seen
```

Do not assume from the directory name alone that this is an official VisDrone release, an official split, or a multimodal dataset. First audit the local files, annotations, split provenance, categories, sequence structure, and the meaning of `seen`.

This task has three stages:

1. audit and source-lock the local dataset;
2. if it is RGB-only, run a frozen-checkpoint RGB-only external stress evaluation and a dataset-specific RGB baseline;
3. report results with explicit limits and without presenting RGB-only evidence as validation of tri-modal fusion.

Do not fabricate thermal or event channels from grayscale, edges, optical flow, color transforms, or other pseudo-modalities.

## Read First

1. `AGENTS.md`
2. `PROJECT_PROFILE.md`
3. `docs/PROJECT_CONTEXT.md`
4. `docs/EXPERIMENT_STATUS.md`
5. `docs/TASK_BLOCKER.md`
6. `docs/NEXT_TASK.md`
7. `runs/handoff_latest.md`
8. `runs/handoff_latest.json`
9. `runs/v46_coco_ablation/source_lock_v46.md`
10. `runs/v46_coco_ablation/coco_metric_summary.md`
11. `runs/v48_complete_ablation/source_lock_v48.md`
12. `runs/v48_complete_ablation/causal_ablation_summary.md`
13. `runs/v48_complete_ablation/claim_boundary.md`
14. `runs/v49_manuscript_integration/V49_MANUSCRIPT_INTEGRATION_REPORT.md`
15. the existing TriAir dataset loader, evaluator, COCO metric implementation, model builders, and training entry points needed to implement a separate external-dataset path.

## Prerequisite Boundary

- Preserve all V40--V49 evidence packages and checkpoints unchanged.
- Do not access the TriAir locked holdout again.
- V49 local Springer/BibTeX compilation may remain a separate pending closure item; V50 must not silently alter manuscript conclusions before its evidence is complete and reviewed.
- V50 is an evidence-generation task. Do not edit the SIVP manuscript during this task.

## Stage 1: Dataset Audit and Provenance Gate

Before training or evaluation, inspect `D:\datasets\visdrone_seen` and create:

```text
runs/v50_visdrone_seen/dataset_audit.md
runs/v50_visdrone_seen/dataset_audit.json
runs/v50_visdrone_seen/source_lock_v50.md
runs/v50_visdrone_seen/source_lock_v50.json
```

The audit must record:

- exact directory tree relevant to images, annotations, and split files;
- whether the data are RGB-only or contain aligned additional modalities;
- image formats, annotation formats, image dimensions, and file counts;
- category IDs, category names, ignored categories, ignored regions, and difficult/truncated/occluded flags if present;
- existing train/validation/test or `seen`/`unseen` split definitions;
- sequence, video, scene, or frame identifiers available for leakage control;
- whether test annotations are locally available;
- dataset version, provider/source information found in local files, and any local README or license text;
- exact meaning of the directory suffix `seen`, if it can be established from local evidence;
- SHA256 hashes of split lists, annotation files, conversion scripts, and any local metadata used for provenance;
- whether any images or annotation IDs are duplicated across local partitions;
- an exact-content hash check between V50 partitions and, where practical, against the accessible TriAir image inventory without modifying either dataset.

Do not call the dataset an official VisDrone benchmark or an independent test set unless the local provenance and split files support that wording.

### Audit decision gate

After the audit:

- If the dataset is RGB-only, continue with the RGB-only plan below.
- If it contains genuinely aligned thermal or event modalities, stop after the audit and write a task-scope amendment proposal before training; do not guess channel semantics.
- If category definitions, split provenance, or annotation meaning cannot be established safely, write `docs/TASK_BLOCKER.md` and stop rather than inventing a conversion.

## Stage 2: Frozen Split and Class Mapping

Create a documented vehicle-detection mapping:

```text
runs/v50_visdrone_seen/class_mapping.md
runs/v50_visdrone_seen/class_mapping.json
```

Requirements:

- list every source category ID and name;
- explicitly identify which categories are merged into the single `vehicle` class;
- keep non-vehicle categories out of the positive class;
- handle ignored regions and ignored object flags according to the local annotation specification rather than treating them blindly as background;
- preserve the original annotations unchanged;
- save any converted COCO-style annotations under `runs/v50_visdrone_seen/converted_annotations/**`, not inside the dataset directory;
- do not commit large image copies or raw dataset files.

### Split rules

Prefer a valid existing source-provided split.

If the local dataset lacks a defensible split but contains sequence/video identifiers, create a deterministic sequence-disjoint train/development-validation/test partition. Do not randomly split neighboring frames.

If neither an official split nor a sequence-aware split can be constructed, stop with a blocker.

Before any model result is inspected, freeze and hash:

```text
runs/v50_visdrone_seen/manifests/train.txt
runs/v50_visdrone_seen/manifests/devval.txt
runs/v50_visdrone_seen/manifests/test.txt
runs/v50_visdrone_seen/split_manifest.json
```

The test partition must not be used for hyperparameter tuning, threshold selection, checkpoint selection, run continuation, or architecture selection.

## Stage 3A: Frozen TriAir-Checkpoint RGB-Only External Stress Evaluation

If the dataset is RGB-only, evaluate the six already frozen TriAir checkpoints:

- matched early fusion, seeds 0/1/2;
- full reliability-aware `p=0.15`, seeds 0/1/2.

Use an explicitly documented inference-only adapter:

```text
input = [RGB, zero thermal channel, zero event channel]
```

The zero channels must be created after the same numeric scaling/normalization convention used by the model input, and the exact constant and preprocessing order must be recorded.

This is an RGB-only missing-modality and domain-shift stress evaluation. It is not:

- full RGB--thermal--event external validation;
- real sensor-failure testing;
- calibrated reliability evaluation;
- evidence that event or thermal processing generalizes to the second dataset.

Rules:

- do not retrain or reselect the six TriAir checkpoints;
- do not tune confidence or NMS thresholds on V50 test results;
- use the frozen detector candidate threshold and canonical COCO evaluator convention unless a pre-result source-lock note documents a necessary dataset-format exception;
- evaluate development-validation first only to verify the adapter and annotation conversion;
- freeze the adapter, mapping, evaluator, and thresholds before one final test evaluation;
- save exact commands, checkpoint hashes, manifests, converted-annotation hashes, environment, and results.

Required outputs:

```text
runs/v50_visdrone_seen/zero_shot_devval_per_run.csv
runs/v50_visdrone_seen/zero_shot_test_per_run.csv
runs/v50_visdrone_seen/zero_shot_paired_deltas.csv
runs/v50_visdrone_seen/zero_shot_summary.md
runs/v50_visdrone_seen/zero_shot_summary.json
```

Report at least:

- COCO AP@[0.50:0.95];
- AP50;
- AP75;
- AR100;
- AP for small/medium/large objects when the converted annotations support valid area calculation;
- per-seed matched-early versus full-RA paired deltas;
- descriptive mean and sample SD across the three frozen seed pairs.

A negative or near-zero result must be reported rather than hidden.

## Stage 3B: Dataset-Specific RGB Baseline

Train a pure RGB RepViT-M0.9--FPN--FCOS baseline on the frozen V50 train/development-validation split to contextualize dataset difficulty.

Requirements:

- use a true three-channel RGB input path;
- do not create pseudo thermal or event channels;
- reuse the shared detector stack as closely as practical;
- use seeds 0, 1, and 2;
- use 640 input size and the active 50-epoch training length unless a source-lock note made before training documents a memory or annotation-format constraint;
- select checkpoints only by the frozen development-validation rule;
- access the test partition only after all three checkpoints and evaluator settings are frozen;
- report the same canonical COCO metrics as the zero-shot evaluation;
- profile parameters and batch-one latency only if the implementation differs materially from an already measured RGB detector path.

Required outputs:

```text
runs/v50_visdrone_seen/rgb_train_commands.txt
runs/v50_visdrone_seen/rgb_run_status.json
runs/v50_visdrone_seen/rgb_devval_per_run.csv
runs/v50_visdrone_seen/rgb_test_per_run.csv
runs/v50_visdrone_seen/rgb_summary.md
runs/v50_visdrone_seen/rgb_summary.json
```

The dataset-specific RGB baseline is contextual evidence. It must not be compared as though it were trained under the same input modalities as RA-RepDet.

## Allowed Files To Modify

- `docs/NEXT_TASK.md`
- `docs/EXPERIMENT_STATUS.md`
- `docs/TASK_BLOCKER.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`
- new directory `runs/v50_visdrone_seen/**`
- a new dataset adapter such as `datasets/visdrone_seen_dataset.py`
- new conversion, audit, evaluation, reporting, and profiling tools under `rarepdet/tools/**`
- a new pure-RGB detector wrapper under `rarepdet/models/**` if no compatible existing implementation is available
- minimal training/evaluation CLI plumbing required to select the new dataset and RGB model path
- tests under `tests/**` for parsing, class mapping, split integrity, model construction, and metric conversion.

## Forbidden Changes

- raw files under `D:\datasets\visdrone_seen`;
- TriAir raw data, manifests, checkpoints, predictions, or evidence summaries;
- the TriAir locked holdout or any new TriAir holdout evaluation;
- synthetic thermal/event generation from RGB;
- random frame-level splitting when sequence identifiers are available;
- result-driven changes to category mapping or ignored-region handling;
- manuscript text, title, abstract, tables, bibliography, or conclusions during V50;
- claims of external tri-modal generalization from an RGB-only dataset;
- claims of statistical significance, universal causality, optimal dropout, calibrated reliability, or real sensor-fault robustness.

## Source Lock

Before result-producing commands, record:

- starting commit SHA and branch;
- local dataset root and audit timestamp;
- dataset metadata and annotation hashes;
- frozen manifest hashes;
- class-mapping hash;
- checkpoint paths and SHA256 values for all six frozen TriAir models;
- hashes of the dataset adapter, model builder, evaluator, metric code, and conversion scripts;
- Python, PyTorch, torchvision, CUDA, GPU, driver, and OS versions;
- exact preprocessing and zero-channel adapter semantics;
- exact checkpoint-selection and test-access rules.

## Preflight

At minimum run and save:

- image and annotation parsing tests;
- category/ignore mapping tests;
- duplicate and split-overlap checks;
- sequence-disjointness check where applicable;
- converted-annotation integrity check;
- one-image visualization or coordinate sanity check without committing large images;
- RGB-only five-channel adapter shape/range test;
- model construction and checkpoint-loading tests for all six frozen checkpoints;
- one-batch evaluator smoke test;
- canonical COCO metric smoke test;
- RGB baseline forward/backward and checkpoint save/load tests;
- final claim scan.

Save:

```text
runs/v50_visdrone_seen/preflight_commands.txt
runs/v50_visdrone_seen/preflight_outputs.txt
runs/v50_visdrone_seen/claim_scan.txt
runs/v50_visdrone_seen/claim_scan_review.md
runs/v50_visdrone_seen/claim_boundary.md
```

## Claim Boundary

Potentially allowed after successful completion:

- external RGB-only aerial vehicle-detection evidence on the audited local dataset;
- zero-shot domain-shift and missing-modality stress results for the six frozen TriAir checkpoints;
- descriptive three-seed paired differences between frozen matched-early and full-RA checkpoints under the exact zero-channel adapter;
- dataset-specific three-seed RGB baseline performance.

Always required:

- identify the dataset by the provenance actually established in the audit;
- state that RGB-only evaluation does not validate thermal or event generalization;
- state that zero-filled channels are a controlled missing-modality intervention, not a physical sensor-failure simulation;
- separate frozen zero-shot transfer results from dataset-specific RGB training results;
- report negative, mixed, or near-zero results.

## Required Completion Outputs

- dataset audit and source lock;
- class mapping and converted annotation report;
- frozen manifests and split-integrity report;
- zero-shot six-checkpoint external stress results;
- three-seed dataset-specific RGB baseline, or a precise resource blocker;
- claim boundary and claim scan;
- preflight records;
- updated `docs/EXPERIMENT_STATUS.md`;
- updated `docs/TASK_BLOCKER.md` only if a real blocker remains;
- updated `runs/handoff_latest.md/json`.

## Acceptance Criteria

- local dataset provenance, format, categories, split meaning, and `seen` naming are documented rather than assumed;
- no raw dataset file is modified or committed;
- no pseudo thermal or event modality is generated;
- split leakage and duplicate checks pass, or exact limitations are reported;
- class and ignore-region mapping are frozen before model results are inspected;
- all six frozen TriAir checkpoints are evaluated with identical external preprocessing and thresholds;
- paired zero-shot results are reported for the three matched seeds;
- a true RGB dataset-specific baseline is trained with three seeds, or a precise GPU/time blocker records the incomplete state;
- test data are not used for tuning or checkpoint selection;
- no new TriAir holdout access occurs;
- no RGB-only result is described as full tri-modal external generalization;
- exact commands, hashes, environment, and claim limits are committed.

## Commit Message

`eval: add V50 audited VisDrone-SEEN external RGB evidence`

## Completion / Blocker Rule

On completion, run the repository finish-task workflow, update status and handoff files, commit, and push.

If the local dataset cannot be identified, parsed, split without leakage, or mapped safely to vehicle detection, stop and write `docs/TASK_BLOCKER.md` with the exact observed structure, error, attempted checks, and minimal user action needed. Do not guess labels, invent split provenance, fabricate modalities, or weaken the claim boundary.
