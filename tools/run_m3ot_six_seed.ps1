param(
    [string]$Python = "C:\Users\xinnan\.conda\envs\pytorch\python.exe",
    [string]$Root = "D:\RA-RepDet-V86-work"
)

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $Root

$audit = Join-Path $Root "runs\m3ot_supervised_rgbt_v1\audit"
$training = Join-Path $Root "runs\m3ot_supervised_rgbt_v1\training"
$script = Join-Path $Root "tools\train_m3ot_supervised.py"
$runs = @(
    @{ Model = "early"; Seed = 0 },
    @{ Model = "reliability_rgbt"; Seed = 0 },
    @{ Model = "early"; Seed = 1 },
    @{ Model = "reliability_rgbt"; Seed = 1 },
    @{ Model = "early"; Seed = 2 },
    @{ Model = "reliability_rgbt"; Seed = 2 }
)

foreach ($run in $runs) {
    $name = "{0}_seed{1}" -f $run.Model, $run.Seed
    $out = Join-Path $training $name
    $statusPath = Join-Path $out "status.json"
    $lastPath = Join-Path $out "weights\last.pt"
    if (Test-Path -LiteralPath $statusPath) {
        $status = Get-Content -LiteralPath $statusPath -Raw | ConvertFrom-Json
        if ($status.status -eq "COMPLETE" -and $status.completed_epochs -eq 50) {
            Write-Host "SKIP completed $name"
            continue
        }
    }

    $arguments = @(
        "-u", $script,
        "--audit-dir", $audit,
        "--model", $run.Model,
        "--seed", [string]$run.Seed,
        "--out", $out,
        "--num-workers", "2"
    )
    if (Test-Path -LiteralPath $lastPath) {
        $arguments += "--resume"
    } elseif (Test-Path -LiteralPath $out) {
        throw "Existing incomplete run without last checkpoint: $out"
    }
    Write-Host "START $name $(Get-Date -Format o)"
    & $Python @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Training failed for $name with exit code $LASTEXITCODE"
    }
    Write-Host "DONE $name $(Get-Date -Format o)"
}

Write-Host "ALL_SIX_M3OT_RUNS_COMPLETE $(Get-Date -Format o)"
$results = Join-Path $Root "runs\m3ot_supervised_rgbt_v1\results"
if (Test-Path -LiteralPath $results) {
    foreach ($name in @("per_seed.csv", "summary.csv", "paired_ap_differences.csv",
                       "experiment_report.md", "figures\three_scene_comparison.png")) {
        if (-not (Test-Path -LiteralPath (Join-Path $results $name))) {
            throw "Incomplete final output: $name"
        }
    }
    Write-Host "SKIP verified existing final report"
} else {
    & $Python "-u" (Join-Path $Root "tools\report_m3ot_supervised.py") `
        "--root" (Join-Path $Root "runs\m3ot_supervised_rgbt_v1")
    if ($LASTEXITCODE -ne 0) {
        throw "Final M3OT report failed with exit code $LASTEXITCODE"
    }
}
Write-Host "M3OT_SUPERVISED_PROTOCOL_COMPLETE $(Get-Date -Format o)"
