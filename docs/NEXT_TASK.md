# Current Task

## Active task

`V79_SINGLE_MODALITY_EVALUATOR_ONLY_LOCAL_EXECUTION`

The user selected the first recommended pre-submission action: run one standardized evaluator pass on each of the nine already-retained RGB-only, thermal-only, and event-only checkpoints, reconcile the results against V77, and create V80 only after all completion gates pass.

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

Completion requires 9/9 valid checkpoint evaluations. The summary builder must compare standardized AP50/AP75 with the user-supplied V77 rows and record every delta. It must not silently replace the earlier table.

## Manuscript gate

V78 remains authoritative until all nine standardized evaluator records are complete, checkpoint and split identities are verified, and every material AP50/AP75 discrepancy is explained. Only then may Codex create and compile a separate V80 manuscript.

## Current boundary

The evaluator-only implementation, AR1/AR10/AR100 extension, static compilation checks, contract tests, and fail-closed preflight are complete. Actual inference remains pending because the ChatGPT environment does not contain the local TriAir data or nine retained checkpoint files.