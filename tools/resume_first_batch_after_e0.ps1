$ErrorActionPreference = "Stop"

$ProjectRoot = "E:\RepViT-main"
$Python = "C:\Users\xinnan\.conda\envs\pytorch\python.exe"
$Log = Join-Path $ProjectRoot "runs\first_batch_resume.log"

Set-Location $ProjectRoot
New-Item -ItemType Directory -Force -Path (Join-Path $ProjectRoot "runs") | Out-Null

function Write-RunLog {
    param([string]$Message)
    $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message"
    Write-Output $line
    Add-Content -LiteralPath $Log -Value $line
}

function Invoke-Step {
    param(
        [string]$Name,
        [scriptblock]$Command
    )
    Write-RunLog "START $Name"
    & $Command 2>&1 | Tee-Object -FilePath $Log -Append
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $LASTEXITCODE"
    }
    Write-RunLog "DONE $Name"
}

Invoke-Step "Step 4 visualize E0" {
    & $Python rarepdet\val_early_fusion.py --model early --data D:\download\triair --split-file D:\download\triair\splits\val.txt --weights runs\E0_early_repvit_fcos_e50\weights\best.pt --img-size 640 --device cuda --num 100 --score-thr 0.2 --out runs\E0_early_repvit_fcos_e50\vis_pred
}

Invoke-Step "Step 5 train E1 reliability" {
    & $Python rarepdet\train_early_fusion.py --model reliability --data D:\download\triair --train-split D:\download\triair\splits\train.txt --val-split D:\download\triair\splits\val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --modality-dropout 0.0 --out runs\E1_reliability_repvit_fcos_e50
}

Invoke-Step "Step 6 eval E1" {
    & $Python rarepdet\eval_map.py --model reliability --data D:\download\triair --split-file D:\download\triair\splits\val.txt --weights runs\E1_reliability_repvit_fcos_e50\weights\best.pt --img-size 640 --device cuda --batch-size 4 --score-thr 0.001 --out runs\E1_reliability_repvit_fcos_e50\eval
}

Invoke-Step "Step 7 visualize E1" {
    & $Python rarepdet\val_early_fusion.py --model reliability --data D:\download\triair --split-file D:\download\triair\splits\val.txt --weights runs\E1_reliability_repvit_fcos_e50\weights\best.pt --img-size 640 --device cuda --num 100 --score-thr 0.2 --out runs\E1_reliability_repvit_fcos_e50\vis_pred
}

Invoke-Step "Step 8 train E2 reliability dropout 0.15" {
    & $Python rarepdet\train_early_fusion.py --model reliability --data D:\download\triair --train-split D:\download\triair\splits\train.txt --val-split D:\download\triair\splits\val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --modality-dropout 0.15 --out runs\E2_reliability_dropout015_repvit_fcos_e50
}

Invoke-Step "Step 9 eval E2" {
    & $Python rarepdet\eval_map.py --model reliability --data D:\download\triair --split-file D:\download\triair\splits\val.txt --weights runs\E2_reliability_dropout015_repvit_fcos_e50\weights\best.pt --img-size 640 --device cuda --batch-size 4 --score-thr 0.001 --out runs\E2_reliability_dropout015_repvit_fcos_e50\eval
}

Invoke-Step "Step 10 visualize E2" {
    & $Python rarepdet\val_early_fusion.py --model reliability --data D:\download\triair --split-file D:\download\triair\splits\val.txt --weights runs\E2_reliability_dropout015_repvit_fcos_e50\weights\best.pt --img-size 640 --device cuda --num 100 --score-thr 0.2 --out runs\E2_reliability_dropout015_repvit_fcos_e50\vis_pred
}

Invoke-Step "Task 10 summarize" {
    & $Python tools\summarize_first_batch.py
}

Write-RunLog "ALL DONE"
