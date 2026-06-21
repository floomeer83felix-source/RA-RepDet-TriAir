# Current Task

Establish the fixed GitHub collaboration task flow for RA-RepDet-TriAir.

# Goal

Create the task handoff documents and automation scripts needed for repeatable, scoped GitHub collaboration on the `research/ra-repdet-triair` branch.

# Why This Matters

The project now has completed E0/E1/E2 experiments and lightweight summaries. A fixed task flow prevents accidental retraining, unsafe file uploads, or unscoped edits while making the repository easy for ChatGPT/Codex to resume.

# Allowed Files To Modify

- `AGENTS.md`
- `docs/NEXT_TASK.md`
- `docs/EXPERIMENT_STATUS.md`
- `docs/PROJECT_CONTEXT.md`
- `rarepdet/tools/update_project_status.py`
- `rarepdet/tools/finish_task.ps1`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`

# Forbidden Files To Modify

- `rarepdet/train_early_fusion.py`
- `rarepdet/models/early_fusion_fcos.py`
- `rarepdet/models/reliability_fusion_fcos.py`
- `datasets/triair_dataset.py`
- Dataset files under `D:\download\triair`
- Model weights, checkpoints, prediction images, and raw `.npy` files

# Required Commands

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
python rarepdet/tools/update_project_status.py
python rarepdet/tools/generate_handoff.py
powershell -ExecutionPolicy Bypass -File rarepdet/tools/finish_task.ps1
```

# Required Outputs

- `docs/NEXT_TASK.md`
- `docs/EXPERIMENT_STATUS.md`
- `docs/PROJECT_CONTEXT.md`
- `AGENTS.md`
- `rarepdet/tools/update_project_status.py`
- `rarepdet/tools/finish_task.ps1`
- Updated `runs/handoff_latest.md`
- Updated `runs/handoff_latest.json`

# Acceptance Criteria

- The project status can be regenerated without model weights.
- Missing result files are rendered as `NA` instead of causing script failure.
- `finish_task.ps1` stages only code, docs, and lightweight summary files.
- Forbidden artifacts such as `.npy`, `.pt`, `.pth`, weights, prediction images, and large files are blocked before commit.
- The commit is pushed to `research/ra-repdet-triair`.

# Commit Message

Add fixed GitHub collaboration workflow

# After Completion

Leave this task as the latest completed workflow setup until the user assigns the next single task.
