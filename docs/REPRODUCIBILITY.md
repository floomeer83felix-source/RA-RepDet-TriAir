# Reproducibility

This document records the public reproduction contract for the RA-RepDet manuscript snapshot. Raw TriAir data are not redistributed in this repository.

## Publication Snapshot

- Protocol: `block64_guard16_seed0`
- Train / validation / guard: `7439 / 2213 / 837`
- Headline variant: `R4 Reliability p=0.20`
- Report scope: frozen validation partition only
- Clean protocol: `runs/clean_block64g16_protocol.md`
- Controlled-seed report: `runs/phase4b_report.md`

## Recorded Environment

The training and evaluation environment was the conda environment named `pytorch`.

| Item | Value |
| --- | --- |
| OS | Windows 11 (`Windows-11-10.0.26200-SP0` observed during public packaging) |
| Conda environment | `pytorch` |
| Python | 3.9.21 |
| PyTorch | 2.5.1 |
| Torchvision | 0.20.1 |
| PyTorch CUDA runtime | 12.4 |
| CUDA available to PyTorch | true |
| GPU | NVIDIA GeForce RTX 3090 |
| GPU driver | 591.86 |
| GPU memory | 24576 MiB |
| NumPy | 1.26.4 |
| timm in conda environment | 1.0.22 |
| timm in repository requirements | 0.5.4 |
| fvcore | listed in `requirements.txt`; used only where available for profiling helpers |

The public `requirements.txt` preserves the original project requirement line for `timm==0.5.4`. The recorded conda environment currently reports `timm==1.0.22`; reproduce the submitted runs by preserving the original environment or by documenting any dependency refresh before rerunning experiments.

## Split Manifest

The manuscript split is stored in `runs/blocked_split_candidates/`.

| Split | Path | Count | SHA256 |
| --- | --- | --- | --- |
| train | `runs/blocked_split_candidates/block64_guard16_seed0_train.txt` | 7439 | `c4d94e5b376e862c3875314d39d79149988c479f12e97a6fcbeea72d3dfa85e5` |
| validation | `runs/blocked_split_candidates/block64_guard16_seed0_val.txt` | 2213 | `a48aff2ee29d041bd07b746947028191475a59f0df6b7b64d4882cd610746dc4` |
| guard | `runs/blocked_split_candidates/block64_guard16_seed0_guard.txt` | 837 | `25a57cea733a218ce2bbd37b22acdf76722cdcc3856861020017340357b338a8` |

Guard samples are excluded from both training and validation.

## Training Commands

The headline model is R4, reliability fusion with modality dropout `p=0.20`, trained on the frozen clean split. Run from the repository root after placing the TriAir data locally.

Seed 0:

```powershell
conda activate pytorch
python rarepdet/train_early_fusion.py --model reliability --data D:\download\triair --train-split runs/blocked_split_candidates/block64_guard16_seed0_train.txt --val-split runs/blocked_split_candidates/block64_guard16_seed0_val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --modality-dropout 0.20 --seed 0 --out runs/R4_reliability_p020_seed0_block64g16_e50
```

Seed 2:

```powershell
conda activate pytorch
python rarepdet/train_early_fusion.py --model reliability --data D:\download\triair --train-split runs/blocked_split_candidates/block64_guard16_seed0_train.txt --val-split runs/blocked_split_candidates/block64_guard16_seed0_val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --modality-dropout 0.20 --seed 2 --out runs/R4_reliability_p020_seed2_block64g16_e50
```

## Evaluation Commands

Full-modality validation at the manuscript threshold:

```powershell
conda activate pytorch
python rarepdet/eval_map.py --model reliability --data D:\download\triair --split-file runs/blocked_split_candidates/block64_guard16_seed0_val.txt --weights runs/R4_reliability_p020_seed0_block64g16_e50/weights/best.pt --img-size 640 --device cuda --batch-size 4 --score-thr 0.50 --out runs/R4_reliability_p020_seed0_block64g16_e50/eval_thr050
```

Missing-modality robustness evaluation:

```powershell
conda activate pytorch
python rarepdet/tools/eval_missing_modality.py --model reliability --data D:\download\triair --split-file runs/blocked_split_candidates/block64_guard16_seed0_val.txt --weights runs/R4_reliability_p020_seed0_block64g16_e50/weights/best.pt --img-size 640 --device cuda --batch-size 4 --score-thr 0.05 --out runs/R4_reliability_p020_seed0_block64g16_e50/missing_modality
```

Efficiency profiling, matching the clean-split manuscript workflow:

```powershell
conda activate pytorch
python rarepdet/tools/profile_model.py --model reliability --img-size 640 --device cuda --batch-size 1 --warmup 100 --iters 300 --repeats 3 --out runs/profile_clean_reliability
```

Repeat the evaluation commands with the seed-2 checkpoint path to reproduce the controlled two-seed table.

## Expected Public Output Files

- `runs/clean_block64g16_protocol.md`
- `runs/phase4b_report.md`
- `runs/clean_block64g16_seed_replication.csv`
- `runs/clean_block64g16_seed_replication.md`
- `runs/clean_efficiency_profile.csv`
- `runs/clean_efficiency_profile.md`
- `runs/R4_reliability_p020_seed0_block64g16_e50/eval_thr050/eval_results.txt`
- `runs/R4_reliability_p020_seed2_block64g16_e50/eval_thr050/eval_results.txt`
- `runs/R4_reliability_p020_seed0_block64g16_e50/missing_modality/missing_modality_results.csv`
- `runs/R4_reliability_p020_seed2_block64g16_e50/missing_modality/missing_modality_results.csv`
- `manuscript/tables/*.csv`
- `manuscript/tables/*.md`
- `manuscript/figures/*.csv`
- `manuscript/figures/*.md`

## Data Availability Boundary

Raw TriAir `.npy` arrays, labels, downloaded archives, trained weights, and rendered qualitative images are intentionally excluded from the public repository. Users must obtain TriAir through the official provider-approved route and place it at their own local path before running training or evaluation.
