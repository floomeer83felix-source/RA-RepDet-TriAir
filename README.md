# RA-RepDet-TriAir

Minimal public experiment repository for RA-RepDet, a RepViT-FCOS based RGB-thermal-event UAV vehicle detection study on local TriAir-formatted data.

This public package intentionally contains only source code, split manifests, audit scripts, lightweight CSV/TXT/MD result summaries, and manuscript table/figure source files. It does not contain raw TriAir `.npy` arrays, label archives, trained weights, prediction images, local qualitative panels, or large caches.

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
python tools/create_triair_split.py --data D:\download\triair --val-ratio 0.2 --seed 0 --out D:\download\triair\splits
```

Train a reliability model on explicit split files:

```powershell
python rarepdet/train_early_fusion.py --model reliability --data D:\download\triair --train-split runs/blocked_split_candidates/block64_guard16_seed0_train.txt --val-split runs/blocked_split_candidates/block64_guard16_seed0_val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --modality-dropout 0.20 --seed 0 --out runs/R4_reliability_p020_seed0_block64g16_e50
```

Evaluate a checkpoint:

```powershell
python rarepdet/eval_map.py --model reliability --data D:\download\triair --split-file runs/blocked_split_candidates/block64_guard16_seed0_val.txt --weights runs/R4_reliability_p020_seed0_block64g16_e50/weights/best.pt --img-size 640 --device cuda --batch-size 4 --score-thr 0.50 --out runs/R4_reliability_p020_seed0_block64g16_e50/eval_thr050
```

## License

Code is released under the repository `LICENSE`. Dataset rights are separate and must be checked with the TriAir provider/author documentation.
