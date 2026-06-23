param(
    [string]$Branch = "research/ra-repdet-triair",
    [string]$Remote = "research"
)

$ErrorActionPreference = "Stop"

function Get-RepoRoot {
    $root = git rev-parse --show-toplevel
    if (-not $root) {
        throw "Not inside a Git repository."
    }
    return $root.Trim()
}

function Get-PythonCommand {
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }
    $fallback = "C:\Users\xinnan\.conda\envs\pytorch\python.exe"
    if (Test-Path -LiteralPath $fallback) {
        return $fallback
    }
    throw "python was not found."
}

function Get-CommitMessage {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Missing NEXT_TASK file: $Path"
    }

    $lines = Get-Content -LiteralPath $Path
    $capture = $false
    $buffer = New-Object System.Collections.Generic.List[string]
    foreach ($line in $lines) {
        if ($line -match '^\s*#+\s*Commit Message\s*$') {
            $capture = $true
            continue
        }
        if ($capture -and $line -match '^\s*#+\s+\S+') {
            break
        }
        if ($capture) {
            $trimmed = $line.Trim()
            if ($trimmed) {
                $buffer.Add($trimmed.Trim('"'))
            }
        }
    }
    $message = ($buffer -join " ").Trim()
    if (-not $message) {
        for ($i = 0; $i -lt $lines.Count; $i++) {
            $line = $lines[$i]
            if ($line -match '^\s*(?:\d+\.\s*)?Commit message:\s*(.*?)\s*$') {
                $message = $Matches[1].Trim().Trim(".").Trim([char]0x60).Trim()
                if (-not $message) {
                    for ($j = $i + 1; $j -lt $lines.Count; $j++) {
                        $candidate = $lines[$j].Trim()
                        if ($candidate) {
                            $message = $candidate.Trim(".").Trim([char]0x60).Trim()
                            break
                        }
                    }
                }
                if ($message) {
                    break
                }
            }
        }
    }
    if (-not $message) {
        throw "Commit Message section is empty in docs/NEXT_TASK.md."
    }
    return $message
}

function Add-FilesSafely {
    $allowedRoots = @(".gitignore", "AGENTS.md", "docs", "rarepdet", "datasets", "tools")
    $topLevelPatterns = @("README*.md", "requirements*.txt")
    $runPatterns = @(
        "runs\handoff_latest.md",
        "runs\handoff_latest.json",
        "runs\*.csv",
        "runs\*.md",
        "runs\*.txt",
        "runs\*\eval\eval_results.txt",
        "runs\*\missing_modality\*.csv",
        "runs\*\missing_modality\*.txt",
        "runs\*\brightness\*.csv",
        "runs\*\brightness\*.txt",
        "runs\*\alpha\*.csv",
        "runs\*\alpha\*.txt",
        "runs\threshold_sweep\*.csv",
        "runs\threshold_sweep\*.txt",
        "runs\phase2a_*.csv",
        "runs\phase2a_*.md",
        "runs\phase2a_*.txt",
        "runs\phase2a_*\*.csv",
        "runs\phase2a_*\*.txt",
        "runs\phase2a_*\*.md",
        "runs\acrf_*.csv",
        "runs\acrf_*.md",
        "runs\acrf_*.txt",
        "runs\mscd_*.csv",
        "runs\mscd_*.md",
        "runs\mscd_*.txt",
        "runs\phase2c_*.csv",
        "runs\phase2c_*.md",
        "runs\phase2c_*.txt",
        "runs\blocked_split_candidates\*.txt",
        "runs\blocked_split_candidates\*.csv",
        "runs\rgb_separation_subsets\*.txt",
        "runs\phase3c_*.csv",
        "runs\phase3c_*.md",
        "runs\phase3c_*.txt",
        "runs\E*_*\config.txt",
        "runs\E*_*\eval_thr050\*.txt",
        "runs\E*_*\missing_modality\*.csv",
        "runs\E*_*\missing_modality\*.txt",
        "runs\E*_*\alpha_modes\*.csv",
        "runs\E*_*\alpha_modes\*.txt",
        "runs\B*_*\config.txt",
        "runs\B*_*\eval_thr050\*.txt",
        "runs\B*_*\missing_modality\*.csv",
        "runs\B*_*\missing_modality\*.txt"
    )

    $files = New-Object System.Collections.Generic.List[string]

    foreach ($root in $allowedRoots) {
        if (Test-Path -LiteralPath $root -PathType Leaf) {
            $files.Add($root)
        } elseif (Test-Path -LiteralPath $root -PathType Container) {
            Get-ChildItem -LiteralPath $root -Recurse -File -Force |
                ForEach-Object { $files.Add($_.FullName) }
        }
    }

    foreach ($pattern in $topLevelPatterns + $runPatterns) {
        Get-ChildItem -Path $pattern -File -ErrorAction SilentlyContinue |
            ForEach-Object { $files.Add($_.FullName) }
    }

    $forbidden = '(^|[\\/])data([\\/]|$)|(^|[\\/])datasets_cache([\\/]|$)|(^|[\\/])weights([\\/]|$)|(^|[\\/])vis_pred([\\/]|$)|(^|[\\/])__pycache__([\\/]|$)|\.(npy|npz|pt|pth|ckpt|zip|rar|png|jpg|jpeg|bmp|tif|tiff|pyc|pyo|pyd)$'
    $safeFiles = $files |
        Sort-Object -Unique |
        Where-Object {
            $rel = Resolve-Path -LiteralPath $_ -Relative
            $rel -notmatch $forbidden
        }

    if (-not $safeFiles) {
        Write-Host "No safe files found for git add."
        return
    }

    $batch = New-Object System.Collections.Generic.List[string]
    foreach ($file in $safeFiles) {
        $batch.Add($file)
        if ($batch.Count -ge 100) {
            git add -- @($batch.ToArray())
            $batch.Clear()
        }
    }
    if ($batch.Count -gt 0) {
        git add -- @($batch.ToArray())
    }
}

function Test-StagedSafety {
    $staged = @(git diff --cached --name-only)
    if ($staged.Count -eq 0) {
        return
    }

    $forbidden = $staged | Where-Object {
        $_ -match '(^|/)data(/|$)|(^|/)datasets_cache(/|$)|(^|/)weights(/|$)|(^|/)vis_pred(/|$)|\.(npy|npz|pt|pth|ckpt|zip|rar|png|jpg|jpeg|bmp|tif|tiff|pyc|pyo|pyd)$'
    }
    if ($forbidden) {
        $forbidden | ForEach-Object { Write-Error "Forbidden staged file: $_" }
        throw "Aborting: forbidden files are staged."
    }

    $large = foreach ($path in $staged) {
        if (Test-Path -LiteralPath $path -PathType Leaf) {
            $item = Get-Item -LiteralPath $path
            if ($item.Length -gt 50MB) {
                $item
            }
        }
    }
    if ($large) {
        $large | ForEach-Object { Write-Error "Staged file exceeds 50 MB: $($_.FullName)" }
        throw "Aborting: staged file exceeds 50 MB."
    }
}

$repoRoot = Get-RepoRoot
Set-Location $repoRoot

Write-Host "== git status =="
git status

$python = Get-PythonCommand
Write-Host "== update handoff =="
& $python rarepdet/tools/generate_handoff.py

Write-Host "== update project status =="
& $python rarepdet/tools/update_project_status.py

Write-Host "== git add safe files =="
Add-FilesSafely
Test-StagedSafety

$stagedFiles = @(git diff --cached --name-only)
if ($stagedFiles.Count -eq 0) {
    Write-Host "No staged changes to commit."
    exit 0
}

Write-Host "== staged files =="
$stagedFiles | ForEach-Object { Write-Host $_ }

$message = Get-CommitMessage -Path "docs/NEXT_TASK.md"
Write-Host "== commit =="
git commit -m $message

Write-Host "== push =="
git push $Remote $Branch
