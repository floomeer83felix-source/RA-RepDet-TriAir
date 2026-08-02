# V76 TriAir Single-Modality Ablation

Status: `V81_QUEUE_COMPLETE_9_OF_9`.

This directory is reserved for exactly nine authorized runs:

- RGB-only seeds 0, 1, 2;
- thermal-only seeds 0, 1, 2;
- event-only seeds 0, 1, 2.

Execute on the authorized local TriAir/CUDA workspace:

```powershell
python rarepdet/tools/run_v76_single_modality_queue.py --data D:\download\triair --device cuda --resume
```

The queue is fail-closed and resume-safe. It uses the frozen V40 component-disjoint train/devval manifests, exactly 50 epochs, batch size 4, image size 640, AdamW at 1e-4, no modality dropout, and checkpoint retention by development-validation project-local AP50. The guard partition is forbidden.

All nine runs and their first retained-checkpoint COCO evaluations completed. Compact results are stored in `single_modality_per_run.csv`, `single_modality_summary.json`, and `raw/`. Large weights remain local.

## V81 launch

The authorized fresh nine-run queue started at `2026-07-30T08:04:13+08:00` in `E:\RepViT-v74-clean`. Queue PID `57884` launched `rgb_seed0`; GPU memory and power confirmed active computation. Runtime logs are under `execution_logs/`. These are new V81 checkpoints, not recovered V77 checkpoint identities.

The queue completed on 2026-08-01 with 9/9 runs at 50 epochs and no stderr failure.
