# V79 single-modality evaluator-only completion

Status: `EVALUATOR_ONLY_CODE_READY_CHECKPOINT_EXECUTION_PENDING_LOCAL_WORKSPACE`

## Purpose

Evaluate the nine already-retained V76 single-modality checkpoints once with the same project COCO evaluator and report:

- AP@[0.50:0.95];
- AP50;
- AP75;
- AR1;
- AR10;
- AR100;
- checkpoint SHA256;
- frozen validation-manifest SHA256.

No training, threshold tuning, schedule changes, seed replacement, or guard-partition access is authorized.

## Required checkpoints

```text
runs/v76_triair_single_modality_ablation/training/rgb_seed0/weights/best.pt
runs/v76_triair_single_modality_ablation/training/rgb_seed1/weights/best.pt
runs/v76_triair_single_modality_ablation/training/rgb_seed2/weights/best.pt
runs/v76_triair_single_modality_ablation/training/thermal_seed0/weights/best.pt
runs/v76_triair_single_modality_ablation/training/thermal_seed1/weights/best.pt
runs/v76_triair_single_modality_ablation/training/thermal_seed2/weights/best.pt
runs/v76_triair_single_modality_ablation/training/event_seed0/weights/best.pt
runs/v76_triair_single_modality_ablation/training/event_seed1/weights/best.pt
runs/v76_triair_single_modality_ablation/training/event_seed2/weights/best.pt
```

## Local execution

From `E:\RepViT-main`:

```powershell
python rarepdet/tools/run_v79_single_modality_eval_only.py --data D:\download\triair --device cuda --resume
```

The queue performs a fail-closed preflight before inference. It will not generate partial manuscript evidence when any required checkpoint, the dataset root, or the frozen component-disjoint validation manifest is absent.

## Output

```text
runs/v79_single_modality_evaluator_completion/
  preflight.json
  raw/<mode>_seed<seed>.json
  per_run.csv
  summary.json
  summary.md
```

The summary also records AP50/AP75 differences relative to the user-supplied V77 table. A discrepancy is reported explicitly and never silently overwritten.

## Current environment boundary

The ChatGPT execution environment used to prepare this package contains neither `D:\download\triair` nor the nine retained `best.pt` files. Therefore no AP@[0.50:0.95] or AR value has been fabricated or inferred here.
