$ErrorActionPreference = "Stop"

$ProjectRoot = "E:\RepViT-main"
$Python = "C:\Users\xinnan\.conda\envs\pytorch\python.exe"
$Log = Join-Path $ProjectRoot "runs\first_batch_resume_wait.log"

Set-Location $ProjectRoot
New-Item -ItemType Directory -Force -Path (Join-Path $ProjectRoot "runs") | Out-Null

function Write-RunLog {
    param([string]$Message)
    $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message"
    Write-Output $line
    Add-Content -LiteralPath $Log -Value $line
}

function Invoke-PythonStep {
    param(
        [string]$Name,
        [string[]]$ArgsList,
        [string]$LogStem
    )
    Write-RunLog "START $Name"
    $stdout = Join-Path $ProjectRoot "runs\$LogStem.stdout.log"
    $stderr = Join-Path $ProjectRoot "runs\$LogStem.stderr.log"
    Remove-Item -LiteralPath $stdout, $stderr -Force -ErrorAction SilentlyContinue
    $process = Start-Process -FilePath $Python -ArgumentList $ArgsList -WorkingDirectory $ProjectRoot -RedirectStandardOutput $stdout -RedirectStandardError $stderr -WindowStyle Hidden -PassThru -Wait
    Write-RunLog "DONE $Name exit_code=$($process.ExitCode) stdout=$stdout stderr=$stderr"
    if ($process.ExitCode -ne 0) {
        if (Test-Path -LiteralPath $stderr) {
            Get-Content -LiteralPath $stderr -Tail 80 | Add-Content -LiteralPath $Log
        }
        throw "$Name failed with exit code $($process.ExitCode)"
    }
}

Invoke-PythonStep "Step 5 train E1 reliability" @(
    "rarepdet\train_early_fusion.py",
    "--model", "reliability",
    "--data", "D:\download\triair",
    "--train-split", "D:\download\triair\splits\train.txt",
    "--val-split", "D:\download\triair\splits\val.txt",
    "--epochs", "50",
    "--batch-size", "4",
    "--img-size", "640",
    "--device", "cuda",
    "--lr", "1e-4",
    "--num-workers", "0",
    "--modality-dropout", "0.0",
    "--out", "runs\E1_reliability_repvit_fcos_e50"
) "E1_train"

Invoke-PythonStep "Step 6 eval E1" @(
    "rarepdet\eval_map.py",
    "--model", "reliability",
    "--data", "D:\download\triair",
    "--split-file", "D:\download\triair\splits\val.txt",
    "--weights", "runs\E1_reliability_repvit_fcos_e50\weights\best.pt",
    "--img-size", "640",
    "--device", "cuda",
    "--batch-size", "4",
    "--score-thr", "0.001",
    "--out", "runs\E1_reliability_repvit_fcos_e50\eval"
) "E1_eval"

Invoke-PythonStep "Step 7 visualize E1" @(
    "rarepdet\val_early_fusion.py",
    "--model", "reliability",
    "--data", "D:\download\triair",
    "--split-file", "D:\download\triair\splits\val.txt",
    "--weights", "runs\E1_reliability_repvit_fcos_e50\weights\best.pt",
    "--img-size", "640",
    "--device", "cuda",
    "--num", "100",
    "--score-thr", "0.2",
    "--out", "runs\E1_reliability_repvit_fcos_e50\vis_pred"
) "E1_vis"

Invoke-PythonStep "Step 8 train E2 reliability dropout 0.15" @(
    "rarepdet\train_early_fusion.py",
    "--model", "reliability",
    "--data", "D:\download\triair",
    "--train-split", "D:\download\triair\splits\train.txt",
    "--val-split", "D:\download\triair\splits\val.txt",
    "--epochs", "50",
    "--batch-size", "4",
    "--img-size", "640",
    "--device", "cuda",
    "--lr", "1e-4",
    "--num-workers", "0",
    "--modality-dropout", "0.15",
    "--out", "runs\E2_reliability_dropout015_repvit_fcos_e50"
) "E2_train"

Invoke-PythonStep "Step 9 eval E2" @(
    "rarepdet\eval_map.py",
    "--model", "reliability",
    "--data", "D:\download\triair",
    "--split-file", "D:\download\triair\splits\val.txt",
    "--weights", "runs\E2_reliability_dropout015_repvit_fcos_e50\weights\best.pt",
    "--img-size", "640",
    "--device", "cuda",
    "--batch-size", "4",
    "--score-thr", "0.001",
    "--out", "runs\E2_reliability_dropout015_repvit_fcos_e50\eval"
) "E2_eval"

Invoke-PythonStep "Step 10 visualize E2" @(
    "rarepdet\val_early_fusion.py",
    "--model", "reliability",
    "--data", "D:\download\triair",
    "--split-file", "D:\download\triair\splits\val.txt",
    "--weights", "runs\E2_reliability_dropout015_repvit_fcos_e50\weights\best.pt",
    "--img-size", "640",
    "--device", "cuda",
    "--num", "100",
    "--score-thr", "0.2",
    "--out", "runs\E2_reliability_dropout015_repvit_fcos_e50\vis_pred"
) "E2_vis"

Invoke-PythonStep "Task 10 summarize" @(
    "tools\summarize_first_batch.py"
) "summary_first_batch"

Write-RunLog "ALL DONE"
