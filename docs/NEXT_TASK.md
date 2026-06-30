# Current Task

Phase 7A - Final SIVP Asset Readiness and Author Metadata Intake

# Goal

Prepare the project to move from the pre-final SIVP LaTeX source package into final submission-asset production. This task should organize the exact final figure/table requirements, author metadata requests, and compile-readiness blockers without retraining models or changing experimental evidence.

# Why This Matters

Phase 6B created the SIVP source skeleton, but it intentionally left final figures, final tables, author details, declarations, and final PDF compilation unresolved. Phase 7A is the handoff point for turning those placeholders into author-approved submission assets while keeping all scientific numbers tied to the clean blocked-split evidence.

# Allowed Files To Modify

- `docs/NEXT_TASK.md`
- `docs/EXPERIMENT_STATUS.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`
- `runs/phase7a_asset_readiness_report.md`
- `submission/sivp/figures/*.md`
- `submission/sivp/tables/*.md`
- `submission/sivp/metadata/*.md`
- `submission/sivp/review/*.md`
- `submission/sivp/review/*.csv`
- `rarepdet/tools/generate_handoff.py`
- `rarepdet/tools/update_project_status.py`
- `rarepdet/tools/finish_task.ps1`

# Forbidden Files To Modify

- `rarepdet/train_early_fusion.py`
- `rarepdet/models/early_fusion_fcos.py`
- `rarepdet/models/reliability_fusion_fcos.py`
- `datasets/triair_dataset.py`
- Any training weights, checkpoints, raw `.npy` data, rendered qualitative images, final PDFs, or large local cache files

# Required Commands

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
python rarepdet/tools/generate_handoff.py
python rarepdet/tools/update_project_status.py
powershell -ExecutionPolicy Bypass -File rarepdet/tools/finish_task.ps1
```

# Required Outputs

- `docs/NEXT_TASK.md` must identify Phase 7A as the current unique task.
- `docs/EXPERIMENT_STATUS.md` must show Phase 7A as the current active task, not Phase 6B.
- `runs/handoff_latest.md` and `runs/handoff_latest.json` must include the latest active-task context.
- No experimental training, evaluation, or metric changes are allowed during the transition.

# Acceptance Criteria

- The repository no longer presents Phase 6B as the current active task.
- Phase 6B remains documented as completed historical output.
- Phase 7A is the only current task in `docs/NEXT_TASK.md`.
- Protected training core files are unchanged.
- No data, weights, images, or final PDFs are staged or committed.
- The branch is pushed to `research/ra-repdet-triair`.

# Commit Message

Phase 7A: enter final SIVP asset readiness

# After Completion

The next assistant turn should execute Phase 7A deliverables from this file, starting with final figure/table readiness checklists, metadata intake prompts, and a concise `runs/phase7a_asset_readiness_report.md`.
