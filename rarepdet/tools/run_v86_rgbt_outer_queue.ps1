param(
    [string]$Python = "C:\Users\xinnan\.conda\envs\pytorch\python.exe",
    [string]$Data = "D:\download\triair",
    [string]$OutputRoot = "D:\RA-RepDet-V86-work\runs\v86_rgbt_dynamic_outer"
)

$ErrorActionPreference = "Stop"
$env:CUBLAS_WORKSPACE_CONFIG = ":4096:8"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$Trainer = Join-Path $RepoRoot "rarepdet\tools\train_v86_outer.py"
New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null

foreach ($fold in 0..4) {
    foreach ($seed in 0..4) {
        $run = Join-Path $OutputRoot ("fold{0}_seed{1}" -f $fold, $seed)
        $status = Join-Path $run "run_status.json"
        if (Test-Path $status) {
            $state = (Get-Content -Raw $status | ConvertFrom-Json).state
            if ($state -eq "COMPLETE") {
                continue
            }
        }
        & $Python $Trainer `
            --model reliability_rgbt `
            --outer-fold $fold `
            --seed $seed `
            --data $Data `
            --out $run `
            --device cuda `
            --epochs 50 `
            --batch-size 4 `
            --img-size 640 `
            --lr 1e-4 `
            --num-workers 0
        if ($LASTEXITCODE -ne 0) {
            throw "V86 RGB+thermal run failed: fold=$fold seed=$seed exit=$LASTEXITCODE"
        }
    }
}
