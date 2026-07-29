# V76 TriAir Single-Modality Ablation

Status: `QUEUE_READY_NOT_EXECUTED`.

This directory is reserved for exactly nine authorized runs:

- RGB-only seeds 0, 1, 2;
- thermal-only seeds 0, 1, 2;
- event-only seeds 0, 1, 2.

Execute on the authorized local TriAir/CUDA workspace:

```powershell
python rarepdet/tools/run_v76_single_modality_queue.py --data D:\download\triair --device cuda --resume
```

The queue is fail-closed and resume-safe. It uses the frozen V40 component-disjoint train/devval manifests, exactly 50 epochs, batch size 4, image size 640, AdamW at 1e-4, no modality dropout, and checkpoint retention by development-validation project-local AP50. The guard partition is forbidden.

No metric is present until all nine runs and final retained-checkpoint COCO evaluations actually complete.
