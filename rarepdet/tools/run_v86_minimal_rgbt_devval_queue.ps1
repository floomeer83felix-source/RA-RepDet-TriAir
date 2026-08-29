param(
    [string]$Python = "C:\Users\xinnan\.conda\envs\pytorch\python.exe",
    [string]$Data = "D:\download\triair",
    [string]$OutputRoot = "D:\RA-RepDet-V86-work\runs\v86_minimal_rgbt_dynamic_devval"
)

$ErrorActionPreference = "Stop"
$env:CUBLAS_WORKSPACE_CONFIG = ":4096:8"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$Trainer = Join-Path $RepoRoot "rarepdet\train_early_fusion.py"
$Evaluator = Join-Path $RepoRoot "rarepdet\tools\eval_coco_map.py"
$TrainSplit = Join-Path $RepoRoot "reproducibility\v40_expanded_adjacency_component_split_v2\manifests\v40_expanded_adjacency_component_disjoint_train.txt"
$ValSplit = Join-Path $RepoRoot "reproducibility\v40_expanded_adjacency_component_split_v2\manifests\v40_expanded_adjacency_component_disjoint_val.txt"
New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null

foreach ($seed in 0..2) {
    $run = Join-Path $OutputRoot ("seed{0}" -f $seed)
    $status = Join-Path $run "run_status.json"
    $result = Join-Path $run "coco_eval\metrics.json"
    if (Test-Path $status) {
        $state = (Get-Content -Raw $status | ConvertFrom-Json).state
        if ($state -eq "COMPLETE" -and (Test-Path $result)) {
            continue
        }
    }
    New-Item -ItemType Directory -Force -Path $run | Out-Null
    [ordered]@{
        state = "RUNNING"
        seed = $seed
        model = "reliability_rgbt"
        started_at = (Get-Date).ToString("o")
        train_split = $TrainSplit
        val_split = $ValSplit
        historical_guard_accessed = $false
        v86_outer_folds_accessed = $false
    } | ConvertTo-Json | Set-Content -Encoding UTF8 $status

    & $Python $Trainer `
        --model reliability_rgbt `
        --data $Data `
        --train-split $TrainSplit `
        --val-split $ValSplit `
        --epochs 50 `
        --batch-size 4 `
        --img-size 640 `
        --device cuda `
        --lr 1e-4 `
        --num-workers 0 `
        --modality-dropout 0.0 `
        --seed $seed `
        --out $run
    if ($LASTEXITCODE -ne 0) {
        throw "V86 minimal RGB+thermal training failed: seed=$seed exit=$LASTEXITCODE"
    }

    & $Python $Evaluator `
        --run-id ("v86_minimal_rgbt_dynamic_seed{0}" -f $seed) `
        --protocol ablation_devval `
        --variant rgbt_dynamic `
        --model reliability_rgbt `
        --seed $seed `
        --modality-dropout 0.0 `
        --data $Data `
        --split-file $ValSplit `
        --weights (Join-Path $run "weights\best.pt") `
        --img-size 640 `
        --device cuda `
        --batch-size 4 `
        --num-workers 0 `
        --detector-score-thr 0.001 `
        --metric-score-thr 0.50 `
        --nms-thresh 0.6 `
        --detections-per-img 100 `
        --out-json $result
    if ($LASTEXITCODE -ne 0) {
        throw "V86 minimal RGB+thermal evaluation failed: seed=$seed exit=$LASTEXITCODE"
    }

    [ordered]@{
        state = "COMPLETE"
        seed = $seed
        model = "reliability_rgbt"
        completed_at = (Get-Date).ToString("o")
        checkpoint = (Join-Path $run "weights\best.pt")
        result = $result
        historical_guard_accessed = $false
        v86_outer_folds_accessed = $false
    } | ConvertTo-Json | Set-Content -Encoding UTF8 $status
}
