# RarePDet follow-up experiment commands
# Generated only; this file does not execute experiments by itself.

# A. Dropout ratio ablation
# reliability + dropout 0.05
& "C:\Users\xinnan\.conda\envs\pytorch\python.exe" rarepdet\train_early_fusion.py --model reliability --data D:\download\triair --train-split D:\download\triair\splits\train.txt --val-split D:\download\triair\splits\val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --modality-dropout 0.05 --out runs\E_dropout005_reliability_repvit_fcos_e50

# reliability + dropout 0.10
& "C:\Users\xinnan\.conda\envs\pytorch\python.exe" rarepdet\train_early_fusion.py --model reliability --data D:\download\triair --train-split D:\download\triair\splits\train.txt --val-split D:\download\triair\splits\val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --modality-dropout 0.1 --out runs\E_dropout01_reliability_repvit_fcos_e50

# reliability + dropout 0.20
& "C:\Users\xinnan\.conda\envs\pytorch\python.exe" rarepdet\train_early_fusion.py --model reliability --data D:\download\triair --train-split D:\download\triair\splits\train.txt --val-split D:\download\triair\splits\val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --modality-dropout 0.2 --out runs\E_dropout02_reliability_repvit_fcos_e50

# reliability + dropout 0.30
& "C:\Users\xinnan\.conda\envs\pytorch\python.exe" rarepdet\train_early_fusion.py --model reliability --data D:\download\triair --train-split D:\download\triair\splits\train.txt --val-split D:\download\triair\splits\val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --modality-dropout 0.3 --out runs\E_dropout03_reliability_repvit_fcos_e50

# B. Backbone scale ablation
# TODO: current train_early_fusion.py does not expose a --backbone/--timm-model argument.
# TODO: add a non-disruptive model_name argument after current E0/E1/E2 jobs finish, then run:
# repvit_m0_9, repvit_m1_0, repvit_m1_1

# C. Epoch extension
# E0 early 100 epoch
& "C:\Users\xinnan\.conda\envs\pytorch\python.exe" rarepdet\train_early_fusion.py --model early --data D:\download\triair --train-split D:\download\triair\splits\train.txt --val-split D:\download\triair\splits\val.txt --epochs 100 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --modality-dropout 0.0 --out runs\E0_early_repvit_fcos_e100

# E1 reliability 100 epoch
& "C:\Users\xinnan\.conda\envs\pytorch\python.exe" rarepdet\train_early_fusion.py --model reliability --data D:\download\triair --train-split D:\download\triair\splits\train.txt --val-split D:\download\triair\splits\val.txt --epochs 100 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --modality-dropout 0.0 --out runs\E1_reliability_repvit_fcos_e100

# E2 reliability dropout 0.15 100 epoch
& "C:\Users\xinnan\.conda\envs\pytorch\python.exe" rarepdet\train_early_fusion.py --model reliability --data D:\download\triair --train-split D:\download\triair\splits\train.txt --val-split D:\download\triair\splits\val.txt --epochs 100 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --modality-dropout 0.15 --out runs\E2_reliability_dropout015_repvit_fcos_e100

# D. Missing modality evaluation commands
# E0 missing-modality eval
& "C:\Users\xinnan\.conda\envs\pytorch\python.exe" rarepdet\tools\eval_missing_modality.py --model early --data D:\download\triair --split-file D:\download\triair\splits\val.txt --weights runs\E0_early_repvit_fcos_e50\weights\best.pt --img-size 640 --device cuda --batch-size 4 --score-thr 0.001 --out runs\E0_early_repvit_fcos_e50\missing_modality

# E1 missing-modality eval
& "C:\Users\xinnan\.conda\envs\pytorch\python.exe" rarepdet\tools\eval_missing_modality.py --model reliability --data D:\download\triair --split-file D:\download\triair\splits\val.txt --weights runs\E1_reliability_repvit_fcos_e50\weights\best.pt --img-size 640 --device cuda --batch-size 4 --score-thr 0.001 --out runs\E1_reliability_repvit_fcos_e50\missing_modality

# E2 missing-modality eval
& "C:\Users\xinnan\.conda\envs\pytorch\python.exe" rarepdet\tools\eval_missing_modality.py --model reliability --data D:\download\triair --split-file D:\download\triair\splits\val.txt --weights runs\E2_reliability_dropout015_repvit_fcos_e50\weights\best.pt --img-size 640 --device cuda --batch-size 4 --score-thr 0.001 --out runs\E2_reliability_dropout015_repvit_fcos_e50\missing_modality

