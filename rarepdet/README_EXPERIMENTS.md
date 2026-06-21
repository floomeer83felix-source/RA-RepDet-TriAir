# RarePDet Experiments

## Goal

RepViT-based lightweight RGB-Thermal-Event UAV vehicle detection.

## Dataset

- Dataset root: `D:\download\triair`
- Images: `10489`
- Boxes: `30634`
- Classes: single class `vehicle`
- Splits:
  - `D:\download\triair\splits\train.txt`
  - `D:\download\triair\splits\val.txt`

## Current Experiments

- E0 Early Fusion
- E1 Reliability Fusion
- E2 Reliability Fusion + Modality Dropout 0.15

## Train

```powershell
C:\Users\xinnan\.conda\envs\pytorch\python.exe rarepdet\train_early_fusion.py --model early --data D:\download\triair --train-split D:\download\triair\splits\train.txt --val-split D:\download\triair\splits\val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --modality-dropout 0.0 --out runs\E0_early_repvit_fcos_e50

C:\Users\xinnan\.conda\envs\pytorch\python.exe rarepdet\train_early_fusion.py --model reliability --data D:\download\triair --train-split D:\download\triair\splits\train.txt --val-split D:\download\triair\splits\val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --modality-dropout 0.0 --out runs\E1_reliability_repvit_fcos_e50

C:\Users\xinnan\.conda\envs\pytorch\python.exe rarepdet\train_early_fusion.py --model reliability --data D:\download\triair --train-split D:\download\triair\splits\train.txt --val-split D:\download\triair\splits\val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --modality-dropout 0.15 --out runs\E2_reliability_dropout015_repvit_fcos_e50
```

## Evaluate

```powershell
C:\Users\xinnan\.conda\envs\pytorch\python.exe rarepdet\eval_map.py --model early --data D:\download\triair --split-file D:\download\triair\splits\val.txt --weights runs\E0_early_repvit_fcos_e50\weights\best.pt --img-size 640 --device cuda --batch-size 4 --score-thr 0.001 --out runs\E0_early_repvit_fcos_e50\eval

C:\Users\xinnan\.conda\envs\pytorch\python.exe rarepdet\eval_map.py --model reliability --data D:\download\triair --split-file D:\download\triair\splits\val.txt --weights runs\E1_reliability_repvit_fcos_e50\weights\best.pt --img-size 640 --device cuda --batch-size 4 --score-thr 0.001 --out runs\E1_reliability_repvit_fcos_e50\eval
```

## Missing-Modality Test

```powershell
C:\Users\xinnan\.conda\envs\pytorch\python.exe rarepdet\tools\eval_missing_modality.py --model reliability --data D:\download\triair --split-file D:\download\triair\splits\val.txt --weights runs\E1_reliability_repvit_fcos_e50\weights\best.pt --img-size 640 --device cuda --batch-size 4 --score-thr 0.001 --out runs\E1_reliability_repvit_fcos_e50\missing_modality
```

## Profile Params/GFLOPs/FPS

```powershell
C:\Users\xinnan\.conda\envs\pytorch\python.exe rarepdet\tools\profile_model.py --model early --img-size 640 --device cuda --batch-size 1 --warmup 50 --iters 200 --out runs\profile_early

C:\Users\xinnan\.conda\envs\pytorch\python.exe rarepdet\tools\profile_model.py --model reliability --img-size 640 --device cuda --batch-size 1 --warmup 50 --iters 200 --out runs\profile_reliability
```

## Generate Tables

```powershell
C:\Users\xinnan\.conda\envs\pytorch\python.exe rarepdet\tools\summarize_runs.py --runs runs\E0_early_repvit_fcos_e50 runs\E1_reliability_repvit_fcos_e50 runs\E2_reliability_dropout015_repvit_fcos_e50 --out runs\summary_first_batch.txt

C:\Users\xinnan\.conda\envs\pytorch\python.exe rarepdet\tools\export_paper_tables.py --summary-csv runs\summary_first_batch.csv --missing-csv runs\E1_reliability_repvit_fcos_e50\missing_modality\missing_modality_results.csv --profile-csv runs\profile_reliability\profile_results.csv --out-dir runs\paper_tables
```
