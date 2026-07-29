# Task Blocker

Status: `V79_EVALUATOR_ONLY_EXECUTION_REQUIRES_LOCAL_DATA_AND_NINE_RETAINED_CHECKPOINTS`

Generated: 2026-07-29

## Completed

- COCO evaluator extended from AR100-only reporting to AR1, AR10, and AR100;
- AP@[0.50:0.95], AP50, and AP75 retained under the existing 101-point COCO contract;
- fail-closed nine-checkpoint evaluator-only queue added;
- checkpoint and split SHA256 recording retained;
- V77 AP50/AP75 reconciliation added to the summary builder;
- source-contract tests passed;
- no training entrypoint is present in the V79 queue.

## Execution blocker in this environment

The current ChatGPT runtime does not contain:

1. the TriAir dataset at `D:\download\triair`;
2. the frozen V40 component-disjoint validation manifest inside the local repository checkout;
3. the nine retained checkpoints under `runs/v76_triair_single_modality_ablation/training/<mode>_seed<seed>/weights/best.pt`;
4. the authorized CUDA workspace.

The preflight therefore stops before inference and records all missing paths. No AP@[0.50:0.95] or AR value has been fabricated or estimated.

## Resolution

Run from `E:\RepViT-main`:

```powershell
python rarepdet/tools/run_v79_single_modality_eval_only.py --data D:\download\triair --device cuda --resume
```

When all nine raw JSON files and the complete summary are available, integrate the standardized AP/AR table into the manuscript only after checking the recorded AP50/AP75 deltas against V77.

## Boundary

This is evaluation-only completion on the existing component-disjoint development-validation split. It does not establish independent-test performance or statistical significance and must not involve retraining, tuning, seed replacement, or guard access.
