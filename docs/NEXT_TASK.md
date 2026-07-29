# Current Task

## Active task

`V80_BLOCKED_RESTORE_EXACT_V76_SINGLE_MODALITY_CHECKPOINTS`

V80 preflight ran on the authorized RTX 3090 workspace. The dataset, frozen validation manifest, CUDA runtime, evaluator compilation, and contract tests passed, but all nine exact retained V76 `best.pt` files are absent. The evaluator stopped before inference.

## Authoritative Codex instruction

The full executable task specification is stored at:

```text
docs/CODEX_V80_SINGLE_MODALITY_EVALUATION_TASK.md
```

Codex must follow that file as the authoritative runbook. It covers environment checks, checkpoint preflight, the evaluation-only queue, AP50/AP75 reconciliation, AP@[0.50:0.95] and AR aggregation, evidence auditing, the V80 manuscript integration gate, LaTeX validation, status updates, and commit policy.

## Frozen scope

- checkpoints: exactly `rgb`, `thermal`, and `event`, seeds `0`, `1`, and `2`;
- checkpoint identity: each run's retained `weights/best.pt`;
- split: frozen V40 component-disjoint development-validation manifest;
- metrics: AP@[0.50:0.95], AP50, AP75, AR1, AR10, AR100;
- identities: checkpoint SHA256, checkpoint epoch, split SHA256, evaluator/Git identity, and runtime environment;
- training: forbidden;
- threshold tuning, schedule changes, seed replacement, selective rerun, checkpoint substitution, and guard access: forbidden.

## Required recovery

Restore exactly the nine checkpoint files listed in `docs/CODEX_V80_SINGLE_MODALITY_EVALUATION_TASK.md` to their required paths. Do not use other `best.pt` files, `last.pt`, replacement epochs, or reconstructed metrics.

After the exact files are restored, run:

From `E:\RepViT-main`:

```powershell
python rarepdet/tools/run_v79_single_modality_eval_only.py --data D:\download\triair --device cuda --resume
```

## Required completion files

```text
runs/v79_single_modality_evaluator_completion/
  preflight.json
  raw/rgb_seed0.json ... raw/event_seed2.json
  per_run.csv
  summary.json
  summary.md
```

Completion requires 9/9 valid checkpoint evaluations. The summary builder must compare standardized AP50/AP75 with the user-supplied V77 rows and record every delta. It must not silently replace the earlier table.

## Manuscript gate

V78 remains authoritative until all nine standardized evaluator records are complete, checkpoint and split identities are verified, and every material AP50/AP75 discrepancy is explained. Only then may Codex create and compile a separate V80 manuscript.

## Current boundary

V78 remains authoritative. V80 has 0/9 completed evaluations and no manuscript integration. Retraining is outside this task and requires new explicit authorization if the retained checkpoints cannot be recovered.

## Commit Message

docs: record V80 missing-checkpoint blocker
