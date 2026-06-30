# RA-RepDet-TriAir

Minimal public experiment repository for RA-RepDet, a RepViT-FCOS based RGB-thermal-event UAV vehicle detection study on local TriAir-formatted data.

This public package intentionally contains only source code, split manifests, audit scripts, lightweight CSV/TXT/MD result summaries, and manuscript table/figure source files. It does not contain raw TriAir `.npy` arrays, label archives, trained weights, prediction images, local qualitative panels, or large caches.

## Publication Snapshot

- Manuscript protocol: `block64_guard16_seed0`.
- Train / validation / guard: `7439 / 2213 / 837`.
- Headline variant: `R4 Reliability p=0.20`.
- Report scope: frozen validation partition only.
- Snapshot evidence commit SHA: `700e84556c31e044d100fa9a5f6243720f023d6f`.
- Protocol references: [`runs/clean_block64g16_protocol.md`](runs/clean_block64g16_protocol.md) and [`runs/phase4b_report.md`](runs/phase4b_report.md).
- Dataset provenance and access notes: [`docs/DATA_PROVENANCE.md`](docs/DATA_PROVENANCE.md).
- Reproducibility notes: [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md).

The former E0-E6 runs are historical/exploratory diagnostics and are not manuscript headline results. The manuscript headline result is the clean blocked-split R4 comparison on the frozen validation partition.

## V23 Standardized Re-Evaluation

The V23 evaluator integration standardizes the detector-output candidate set used by full-input and missing-modality validation:

- Frozen split: `block64_guard16_seed0`.
- Detector-output threshold: `0.001`.
- Metric operating threshold: `0.50` for precision, recall, and F1.
- NMS threshold: `0.6`.
- Detections per image: `100`.
- AP50/AP75 are project-local single-class AP metrics, not COCO AP50:95.
- Results are validation-only and are not an independent test result.
- Missing-modality rows use synthetic channel removal, not physical sensor-failure measurements.

V23 lightweight evidence is stored in [`reproducibility/standardized_evaluation_v23/results_v23`](reproducibility/standardized_evaluation_v23/results_v23).

## What Is Included

- `datasets/triair_dataset.py`: TriAir five-channel dataset adapter. Missing label txt files are treated as empty-target images.
- `rarepdet/`: training, evaluation, metrics, RepViT-FPN-FCOS models, and post-processing tools used by the experiments.
- `tools/`: lightweight dataset/split/check utilities.
- `runs/`: lightweight experiment summaries, clean blocked split manifests, eval outputs, missing-modality CSV/TXT files, and profile summaries.
- `manuscript/tables` and `manuscript/figures`: source CSV/MD files used to prepare paper tables and figure data.
- `docs/`: design notes and current experiment status.

## What Is Not Included

- Raw TriAir sensor arrays or `.npy` files.
- Model checkpoints or weights (`.pt`, `.pth`, `.ckpt`).
- Rendered prediction images, qualitative panels, or visualization caches.
- Local training caches, Python environments, or large logs.
- Any claim of TriAir public redistribution rights. Obtain the dataset only through the provider/author-approved route.

## Core Evidence

The publication-safe clean split is `block64_guard16_seed0` and is documented in `runs/clean_block64g16_protocol.md` and `runs/phase4b_report.md`. The selected clean-split main variant is R4 Reliability Fusion with modality dropout `p=0.20`, using validation-partition evidence only. No independent held-out test result is claimed in this repository.

## Basic Commands

Create or inspect split manifests:

```powershell
python tools/create_triair_split.py --data <LOCAL_DATASET_ROOT> --val-ratio 0.2 --seed 0 --out <LOCAL_DATASET_ROOT>/splits
```

Train a reliability model on explicit split files:

```powershell
python rarepdet/train_early_fusion.py --model reliability --data <LOCAL_DATASET_ROOT> --train-split runs/blocked_split_candidates/block64_guard16_seed0_train.txt --val-split runs/blocked_split_candidates/block64_guard16_seed0_val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --modality-dropout 0.20 --seed 0 --out runs/R4_reliability_p020_seed0_block64g16_e50
```

Evaluate a checkpoint:

```powershell
python rarepdet/eval_map.py --model reliability --data <LOCAL_DATASET_ROOT> --split-file runs/blocked_split_candidates/block64_guard16_seed0_val.txt --weights <LOCAL_CHECKPOINT_PATH> --img-size 640 --device cuda --batch-size 4 --detector-score-thr 0.001 --metric-score-thr 0.50 --nms-thresh 0.6 --detections-per-img 100 --out runs/R4_reliability_p020_seed0_block64g16_e50/eval_thr050
```

## License

Code is released under the repository `LICENSE`. Dataset rights are separate and must be checked with the TriAir provider/author documentation.
