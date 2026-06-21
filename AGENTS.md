# RA-RepDet-TriAir Agent Rules

## Required Start Of Every Task

Before starting any task, run:

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
```

Before starting any task, read:

- `AGENTS.md`
- `docs/PROJECT_CONTEXT.md`
- `docs/EXPERIMENT_STATUS.md`
- `docs/NEXT_TASK.md`

## Scope Control

- Do not expand the task scope beyond `docs/NEXT_TASK.md` unless the user explicitly changes the task.
- Do not retrain completed E0, E1, or E2 experiments without a clear user request.
- If the current task only asks for post-processing, evaluation, or documentation, do not modify training core code.

## Protected Training Core Files

Do not modify these files during documentation, post-processing, or evaluation-only tasks:

- `rarepdet/train_early_fusion.py`
- `rarepdet/models/early_fusion_fcos.py`
- `rarepdet/models/reliability_fusion_fcos.py`
- `datasets/triair_dataset.py`

## Required End Of Every Task

Every completed task must finish with:

```powershell
powershell -ExecutionPolicy Bypass -File rarepdet/tools/finish_task.ps1
```

## Failure Protocol

If a task fails:

1. Do not repeatedly patch blindly.
2. Write `docs/TASK_BLOCKER.md`.
3. Include the last 50 error lines, attempted fixes, related files, and two proposed repair options.
4. Update the handoff.
5. Commit and push the blocker report with `rarepdet/tools/finish_task.ps1`.
