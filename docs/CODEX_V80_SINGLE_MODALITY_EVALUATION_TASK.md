# Codex Task: V80 Standardized Single-Modality COCO Evaluation

## Objective

Execute one standardized COCO evaluator pass on the nine already-retained TriAir single-modality checkpoints, reconcile AP50/AP75 against the V77 table, and integrate the completed evaluator evidence into a new V80 manuscript only if every required checkpoint and result passes the frozen contract.

This is an **evaluation-only** task. Do not retrain, tune, replace checkpoints, select better seeds, or access the guard partition.

## Repository and environment

- local repository: `E:\RepViT-main`
- GitHub repository: `floomeer83felix-source/RA-RepDet-TriAir`
- branch: `research/ra-repdet-triair`
- TriAir root: `D:\download\triair`
- current authoritative manuscript: V78
- evaluator-only implementation: V79
- required execution environment: CUDA on the authorized local RTX 3090 workspace

Start with:

```powershell
cd E:\RepViT-main
git status -sb
git branch --show-current
git log -1 --oneline
```

The active branch must be `research/ra-repdet-triair`. Do not overwrite unrelated local changes when synchronizing the branch.

Check the runtime:

```powershell
python --version
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NO CUDA')"
python -c "import pycocotools; print('pycocotools OK')"
```

CUDA is required. Do not silently fall back to CPU.

## Frozen inputs

The validation manifest is:

```text
reproducibility\v40_expanded_adjacency_component_split_v2\manifests\v40_expanded_adjacency_component_disjoint_val.txt
```

Exactly these checkpoints are authorized:

```text
runs\v76_triair_single_modality_ablation\training\rgb_seed0\weights\best.pt
runs\v76_triair_single_modality_ablation\training\rgb_seed1\weights\best.pt
runs\v76_triair_single_modality_ablation\training\rgb_seed2\weights\best.pt
runs\v76_triair_single_modality_ablation\training\thermal_seed0\weights\best.pt
runs\v76_triair_single_modality_ablation\training\thermal_seed1\weights\best.pt
runs\v76_triair_single_modality_ablation\training\thermal_seed2\weights\best.pt
runs\v76_triair_single_modality_ablation\training\event_seed0\weights\best.pt
runs\v76_triair_single_modality_ablation\training\event_seed1\weights\best.pt
runs\v76_triair_single_modality_ablation\training\event_seed2\weights\best.pt
```

If any checkpoint, dataset root, or manifest is missing:

1. stop before inference;
2. print every missing absolute path;
3. do not start training;
4. do not use `last.pt` or another epoch;
5. do not infer missing metrics;
6. record the blocker in `docs/TASK_BLOCKER.md`;
7. leave the manuscript results unchanged.

## Contract validation

Run:

```powershell
python -m py_compile rarepdet\coco_metrics.py
python -m py_compile rarepdet\tools\run_v79_single_modality_eval_only.py
python -m py_compile rarepdet\tools\build_v79_single_modality_evaluator_summary.py
python -m pytest tests\test_v79_evaluator_only_contract.py -q
```

The evaluator output must contain:

- `ap50_95`
- `ap50`
- `ap75`
- `ar1`
- `ar10`
- `ar100`
- `checkpoint_sha256`
- `split_sha256`
- `checkpoint_epoch`
- `input_mode`
- `seed`
- `backend`
- `iou_thresholds`
- `max_detections`

The fixed metric contract is:

- COCO IoU thresholds `0.50:0.05:0.95`;
- COCO 101-point recall grid;
- `maxDets = [1, 10, 100]`;
- score threshold `0.001`;
- NMS threshold `0.6`;
- at most 100 detections per image;
- frozen component-disjoint development-validation manifest;
- no guard access.

No training script may be invoked by this task.

## Execute the evaluator-only queue

Run:

```powershell
python rarepdet\tools\run_v79_single_modality_eval_only.py --data D:\download\triair --device cuda --resume
```

Required output directory:

```text
runs\v79_single_modality_evaluator_completion
```

Required files:

```text
preflight.json
raw\rgb_seed0.json
raw\rgb_seed1.json
raw\rgb_seed2.json
raw\thermal_seed0.json
raw\thermal_seed1.json
raw\thermal_seed2.json
raw\event_seed0.json
raw\event_seed1.json
raw\event_seed2.json
per_run.csv
summary.json
summary.md
```

Completion requires exactly 9/9 valid JSON results. Partial completion is not sufficient for manuscript integration.

## V77 AP50/AP75 reconciliation

Treat these supplied V77 values as the existing manuscript record:

| Modality | Seed | AP50 | AP75 |
| --- | ---: | ---: | ---: |
| RGB-only | 0 | 0.645 | 0.372 |
| RGB-only | 1 | 0.662 | 0.389 |
| RGB-only | 2 | 0.651 | 0.381 |
| Thermal-only | 0 | 0.842 | 0.616 |
| Thermal-only | 1 | 0.858 | 0.638 |
| Thermal-only | 2 | 0.849 | 0.625 |
| Event-only | 0 | 0.322 | 0.118 |
| Event-only | 1 | 0.347 | 0.134 |
| Event-only | 2 | 0.335 | 0.126 |

For each seed, compute:

```text
new_AP50 - V77_AP50
new_AP75 - V77_AP75
```

Rules:

- normal display-rounding differences may be documented;
- do not silently overwrite a discrepancy;
- report old value, new value, and delta for every mismatch;
- verify checkpoint epoch, checkpoint SHA256, evaluator thresholds, and validation manifest;
- do not select whichever result is better;
- do not retrain or replace a checkpoint;
- do not modify the manuscript until all material discrepancies are explained.

## Statistical summary

For RGB-only, thermal-only, and event-only, compute three-seed mean and **sample standard deviation** (`n-1` denominator) for:

- AP@[0.50:0.95]
- AP50
- AP75
- AR1
- AR10
- AR100

Preserve full precision in JSON. Use four decimal places in manuscript tables. Do not claim statistical significance.

## Audit requirements

Record:

1. absolute path of every evaluated checkpoint;
2. checkpoint SHA256;
3. retained checkpoint epoch;
4. validation-manifest SHA256;
5. evaluator code or Git commit identity;
6. Python, CUDA, PyTorch, torchvision, and pycocotools versions;
7. GPU name;
8. inference and metric runtime for each run;
9. seed-level AP50/AP75 reconciliation against V77;
10. confirmation that no training, tuning, seed replacement, selective rerun, or guard access occurred.

## V80 manuscript integration gate

Create a V80 manuscript only after all of the following are true:

- all nine checkpoints passed preflight;
- all nine standardized evaluator JSON records are complete;
- every checkpoint input mode matches its requested modality;
- the correct component-disjoint manifest was used;
- AP50/AP75 reconciliation is complete;
- every material difference is explained;
- no training or result-selection action occurred.

When the gate passes:

1. copy V78 into a new V80 manuscript directory; do not overwrite V78;
2. add AP@[0.50:0.95], AR1, AR10, and AR100 to the single-modality reporting;
3. retain Precision, Recall, F1, AP50, and AP75;
4. document the standardized evaluator, thresholds, `maxDets`, checkpoint selection rule, checkpoint hashes, and split hash;
5. retain all scientific boundaries:
   - component-disjoint development-validation is not an independent test;
   - the V42 holdout is internal to the same local inventory;
   - MM-UAV remains supervised target-domain adaptation on exposed devval;
   - three seeds support descriptive consistency, not significance;
   - no physical sensor-failure robustness claim;
   - TriAir paper count `24,223` remains distinct from current-archive `30,634` valid label lines;
   - no competing interests;
   - TriAir data are not redistributed.

If the gate does not pass, keep V78 authoritative and record a pending or blocked state.

## Build and visual validation

For V80, run:

```powershell
python make_figures.py
pdflatex -interaction=nonstopmode main_sivp_snjnl.tex
pdflatex -interaction=nonstopmode main_sivp_snjnl.tex
```

Require:

- fatal errors: 0;
- undefined citations: 0;
- undefined references: 0;
- overfull boxes: 0;
- no table overflow, clipping, overlap, or broken glyphs;
- clear columns for AP@[0.50:0.95], AR1, AR10, and AR100.

Render and inspect the pages containing the evaluation protocol, single-modality per-seed table, three-seed summary, discussion, declarations, and data availability.

## Status files

On success, update:

```text
docs\EXPERIMENT_STATUS.md
docs\NEXT_TASK.md
docs\NEXT_TASK_WRITE_RECORD.md
docs\TASK_BLOCKER.md
ARTICLE_EVALUATION.md
```

Preferred successful status:

```text
V80_SINGLE_MODALITY_STANDARDIZED_COCO_EVALUATION_COMPLETE
```

If evaluation or reconciliation fails, use an explicit pending or blocked status instead of `COMPLETE`.

## Commit policy

Before committing:

```powershell
git status -sb
git diff --check
```

Commit only task-related source, compact JSON/CSV/Markdown audit records, manuscript sources, and the validated PDF if repository policy permits it.

Do not commit:

- TriAir raw data or `.npy` files;
- label archives;
- the nine large checkpoint files;
- CUDA caches or temporary files;
- unapproved prediction media;
- unrelated local changes.

Recommended commit message:

```text
docs: integrate V80 standardized single-modality COCO evaluation
```

## Final Codex report

Report:

1. branch and final HEAD;
2. whether all nine checkpoints completed;
3. modality-level mean ± sample standard deviation for AP@[0.50:0.95], AP50, AP75, AR1, AR10, and AR100;
4. whether AP50/AP75 reconcile with V77;
5. whether all checkpoint SHA256 values are present;
6. PDF page count and build checks;
7. changed-file inventory;
8. all unresolved issues.

## Prohibited actions

- retraining;
- hyperparameter or threshold sweeps;
- using `last.pt` instead of `best.pt`;
- changing seeds;
- selective reruns;
- guard-partition access;
- inferring unavailable metrics;
- calling development validation an independent test;
- claiming statistical significance;
- changing manuscript numbers before 9/9 completion and reconciliation.