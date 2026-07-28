param(
    [Parameter(Mandatory = $true)]
    [int]$TrainingPid
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$python = "C:\Users\xinnan\.conda\envs\pytorch\python.exe"
$decisionPath = Join-Path $root "runs\v73_mmuav_triair_initialized_alignment_aware_transfer_benchmark\final_decision.json"
$local = "D:\MM-UAV_v73_local"

Set-Location $root
Wait-Process -Id $TrainingPid

if (-not (Test-Path -LiteralPath $decisionPath)) {
    "Training process ended without final_decision.json at $(Get-Date -Format o)." |
        Set-Content -LiteralPath (Join-Path $local "v73_watcher_failed.txt")
    exit 1
}

$decision = Get-Content -LiteralPath $decisionPath -Raw | ConvertFrom-Json
if ($decision.decision -ne "V73_MMUAV_THREE_SEED_TRANSFER_BENCHMARK_COMPLETE") {
    "Training process ended with decision '$($decision.decision)' at $(Get-Date -Format o)." |
        Set-Content -LiteralPath (Join-Path $local "v73_watcher_failed.txt")
    exit 1
}

& $python rarepdet/tools/finalize_v73_task.py
if ($LASTEXITCODE -ne 0) {
    throw "V73 finalizer failed with exit code $LASTEXITCODE"
}

git add -- runs/v73_mmuav_triair_initialized_alignment_aware_transfer_benchmark `
    tests/test_v73_mmuav_transfer_benchmark.py
if ($LASTEXITCODE -ne 0) {
    throw "V73 compact evidence staging failed with exit code $LASTEXITCODE"
}

powershell -ExecutionPolicy Bypass -File rarepdet/tools/finish_task.ps1
if ($LASTEXITCODE -ne 0) {
    throw "V73 finish_task failed with exit code $LASTEXITCODE"
}

"V73 finalized and pushed at $(Get-Date -Format o)." |
    Set-Content -LiteralPath (Join-Path $local "v73_watcher_complete.txt")
