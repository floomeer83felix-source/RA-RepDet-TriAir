# Current Task

## Active task

`V79_SINGLE_MODALITY_EVALUATOR_ONLY_LOCAL_EXECUTION`

The user selected the first recommended pre-submission action: run one standardized evaluator pass on each of the nine already-retained RGB-only, thermal-only, and event-only checkpoints.

## Frozen scope

- checkpoints: exactly `rgb`, `thermal`, and `event`, seeds `0`, `1`, and `2`;
- checkpoint identity: each run's retained `weights/best.pt`;
- split: frozen V40 component-disjoint development-validation manifest;
- metrics: AP@[0.50:0.95], AP50, AP75, AR1, AR10, AR100;
- identities: checkpoint SHA256 and split SHA256;
- training: forbidden;
- threshold tuning, schedule changes, seed replacement, selective rerun, and guard access: forbidden.

## Execution command

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

The summary builder compares standardized AP50/AP75 with the user-supplied V77 rows and records every delta. It must not silently replace the earlier table.

## Current boundary

The evaluator-only implementation and static checks are complete. Actual inference remains pending because the current ChatGPT environment does not contain the local dataset or nine retained checkpoint files.
