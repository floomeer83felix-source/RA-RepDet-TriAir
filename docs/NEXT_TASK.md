# Current Task

## Phase 5A — Paper-Readiness Supplemental Evaluation

## Decision
The core method study is complete on the leakage-aware clean split:
- R1 reliability fusion beats R0 early fusion at both controlled seeds.
- R4 (`p=0.20`) beats R2 (`p=0.15`) in Full AP50 and all three individual missing-modality AP50 conditions at both seeds.
- R4 is the clean-split main variant.

Do not add a new fusion module, loss, distillation method, augmentation, or data split. Do not start 100-epoch training in this phase.

Before manuscript drafting, complete only the following paper-readiness evidence:
1. one standard RGB-only external detector baseline under the same clean split;
2. unified efficiency measurement;
3. clean-split reliability/qualitative evidence;
4. convergence audit from existing logs.

## Read First
- `runs/phase4b_report.md`
- `runs/clean_block64g16_seed_replication.md`
- `runs/seed_reproducibility_smoke.md`
- `runs/clean_block64g16_protocol.md`
- `runs/phase3c_report.md`
- `docs/EXPERIMENT_STATUS.md`
- `runs/handoff_latest.md`

## Frozen Split and Scope
Use only:

```text
train: E:\RepViT-main\runs\blocked_split_candidates\block64_guard16_seed0_train.txt
val:   E:\RepViT-main\runs\blocked_split_candidates\block64_guard16_seed0_val.txt
guard: E:\RepViT-main\runs\blocked_split_candidates\block64_guard16_seed0_guard.txt
```

Integrity values that must remain true:

```text
train=7439, validation=2213, guard=837
exact RGB train/validation matches=0
same-family guard violations=0
```

- Do not overwrite E0–E6, B0–B4, or R0–R4 outputs.
- Do not edit `datasets/triair_dataset.py` or files under `rarepdet/models/`.
- Do not modify the data-root split files.
- Do not commit checkpoints, exported RGB images, copied labels, source images, npy files, prediction dumps, or visual panels.
- Run training jobs sequentially only.

## Task 0 — Convergence audit from existing R-run logs
Create `rarepdet/tools/audit_clean_convergence.py`.

Read the existing R0/R1/R2/R4 seed-0 and seed-2 `train_log.txt` files. Produce:
- `runs/clean_block64g16_convergence.csv`
- `runs/clean_block64g16_convergence.md`

For each run, report:
- best epoch by validation AP50;
- AP50 at epochs 40, 45, 50 when present;
- change from epoch 40 to 50;
- whether the best epoch lies in the final five epochs;
- a descriptive status only: `CLEARLY_PLATEAUED`, `NEAR_PLATEAU`, or `TAIL_STILL_IMPROVING`.

Do not retrain in response to this audit. Do not claim that a run has converged solely because epoch 50 is the best checkpoint. This report only determines whether the manuscript should disclose the fixed 50-epoch schedule and whether a later reviewer-requested extension would be prudent.

## Task 1 — Unified current-code efficiency profile
Create `rarepdet/tools/profile_clean_main_models.py`.

Benchmark the architecture of:
- R0 Early Fusion;
- R4 Reliability Fusion (`p=0.20`).

Protocol:
- RTX 3090; CUDA; batch 1; input `5×640×640`;
- 100 warm-up iterations, 300 timed iterations, 3 repeats;
- report parameter count, raw model-forward latency/FPS, complete detector-inference latency/FPS, and peak CUDA allocated memory;
- do not include dataloader/file IO time;
- verify R4 seed-0 and seed-2 have identical parameter counts and benchmark the seed-0 checkpoint only, noting that dropout is a training-only setting.

Generate:
- `runs/clean_efficiency_profile.csv`
- `runs/clean_efficiency_profile.md`

Do not reuse an old profile without re-running it on the current code path.

## Task 2 — Reliability-weight audit for the selected R4
Create `rarepdet/tools/audit_r4_reliability_weights.py`.

For both R4 seed-0 and seed-2 checkpoints, use the frozen clean validation list and evaluate the following inference conditions without retraining:
- full RGB+Thermal+Event;
- no RGB;
- no Thermal;
- no Event.

Report mean and standard deviation of the three fusion weights over all validation images for each condition and seed. Also report alpha sums and finite-value checks.

Generate:
- `runs/r4_reliability_weight_audit.csv`
- `runs/r4_reliability_weight_audit.md`

Interpretation restrictions:
- report this as gating behavior under synthetic modality removal;
- do not claim causal physical modality importance;
- do not claim exact zero weight for absent modalities unless the observed value is exactly zero under the implemented model.

## Task 3 — Clean-split qualitative evidence
Create `rarepdet/tools/build_clean_qualitative_manifest.py`.

Using the frozen validation split, create a reproducible manifest with 20 rows total:
- 5 cases where R4 corrects an R0 miss or localization failure;
- 5 shared successful detections;
- 5 R4 failure/hard cases;
- 5 R4 missing-modality cases spanning no RGB, no Thermal, and no Event.

For every case record image path, GT count, category, prediction summary, and rationale. Generate local-only panels under `runs/local_clean_qualitative_panels/`; do not commit them.

Generate:
- `runs/clean_qualitative_manifest.csv`
- `runs/clean_qualitative_summary.md`

Do not cherry-pick examples to claim universal superiority. State that cases are illustrative.

## Task 4 — Standard RGB-only external baseline (YOLO11n)
Use an official Ultralytics YOLO11n detector as one RGB-only external baseline. This is the only new training in Phase 5A.

### 4.1 Preflight and cache preparation
Create `rarepdet/tools/prepare_yolo11n_rgb_baseline.py`.

It must:
1. record installed Ultralytics, Python, PyTorch, CUDA, and GPU versions;
2. confirm that the official `yolo11n.pt` checkpoint can be resolved by the installed environment; do not silently substitute another model;
3. create a local-only RGB export/cache under `runs/local_yolo11n_rgb_cache/` from channels `[0:3]` of exactly the frozen train and validation lists;
4. preserve image identity, create labels with the existing TriAir class remapped to YOLO single-class id `0`, and create empty label files for valid negative images;
5. exclude every guard sample;
6. generate a local YAML that points only to the cache;
7. verify exported train/val image counts equal 7439 / 2213 and RGB-content train/val overlap remains zero;
8. preserve aspect ratio; let official YOLO letterbox internally at image size 640;
9. document RGB dtype/range conversion and export method.

Create `runs/yolo11n_rgb_baseline_protocol.md` with all preflight results and exact commands. If `yolo11n.pt` cannot be resolved, cache integrity fails, labels are ambiguous, or class mapping cannot be verified, stop and create/update `docs/TASK_BLOCKER.md`. Do not substitute YOLOv8 or another detector automatically.

### 4.2 Controlled training and evaluation
Run YOLO11n sequentially for seed 0 and seed 2, 50 epochs each, with image size 640 and the local frozen RGB cache. Use the official Ultralytics training interface with explicit seed and deterministic mode. Keep its standard optimizer/schedule defaults; record every non-default option. Use separate outputs:

```text
runs/Y11n_rgb_seed0_block64g16_e50
runs/Y11n_rgb_seed2_block64g16_e50
```

Use the best checkpoint from each run to evaluate the matching RGB-only validation cache. Report standard score-ranked AP50/AP75 and P/R/F1 at confidence threshold 0.50. Do not evaluate YOLO11n under synthetic missing modalities because it is RGB-only.

### 4.3 Comparison restrictions
The external baseline answers: “How does the proposed full tri-modal system compare with a common lightweight RGB-only detector under the same clean split?”

It does **not** isolate architecture-only benefit because input modalities differ. Keep R0 versus R1/R4 as the architecture/fusion ablation; label YOLO11n strictly as a RGB-only external baseline.

## Task 5 — Paper-readiness report and decision gate
Create:
- `rarepdet/tools/build_phase5a_report.py`
- `runs/paper_readiness_summary.csv`
- `runs/phase5a_report.md`

The report must contain:
1. clean-split controlled R0/R1/R2/R4 aggregate results copied from Phase 4B, with R4 clearly marked as main variant;
2. YOLO11n per-seed and mean/range results;
3. efficiency table for R0 and R4;
4. convergence-audit conclusion;
5. reliability-weight audit summary;
6. qualitative-manifest summary;
7. a publication-safe interpretation separating RGB-only external comparison from tri-modal fusion ablation.

End with exactly one decision:

1. `READY FOR MANUSCRIPT DRAFTING` — when all required reports exist, clean-split integrity remains valid, external baseline runs complete, and no protocol blocker exists.
2. `STOP: BASELINE OR PROTOCOL BLOCKER` — when external baseline preparation/training/evaluation or evidence capture failed.

Do not start 100-epoch training in this phase. Do not create the manuscript yet.

## Status and Push
Update:
- `docs/EXPERIMENT_STATUS.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`

Commit only source code, Markdown, CSV, TXT, JSON, and documentation.

Commit message:
```text
Phase 5A: complete paper-readiness supplemental evaluation
```

Push to `research/ra-repdet-triair`.

If any task fails, create/update `docs/TASK_BLOCKER.md` with the exact command, final error, attempted fix, and smallest safe next action.