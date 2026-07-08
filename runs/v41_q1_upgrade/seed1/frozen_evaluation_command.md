# V41 Seed1 Frozen Evaluation Command

Generated: 2026-07-09T00:54:22

The V40 standardized evaluator command templates were recovered verbatim from:

- `runs/v40_expanded_adjacency_v2_compute_minimized/matched_early_seed0/config.json`
- `runs/v40_expanded_adjacency_v2_compute_minimized/reliability_p015_seed0/config.json`

## V40 Verbatim Templates

### early

```powershell
C:\Users\xinnan\.conda\envs\pytorch\python.exe rarepdet/eval_map.py --model early --data D:\download\triair --split-file E:\RepViT-main\reproducibility\v40_expanded_adjacency_component_split_v2\manifests\v40_expanded_adjacency_component_disjoint_val.txt --weights runs/v40_expanded_adjacency_v2_compute_minimized/matched_early_seed0/weights/best.pt --img-size 640 --device cuda --batch-size 4 --num-workers 0 --detector-score-thr 0.001 --metric-score-thr 0.50 --nms-thresh 0.6 --detections-per-img 100 --out runs/v40_expanded_adjacency_v2_compute_minimized/matched_early_seed0/standardized_eval/eval_results.txt
```

### reliability

```powershell
C:\Users\xinnan\.conda\envs\pytorch\python.exe rarepdet/eval_map.py --model reliability --data D:\download\triair --split-file E:\RepViT-main\reproducibility\v40_expanded_adjacency_component_split_v2\manifests\v40_expanded_adjacency_component_disjoint_val.txt --weights runs/v40_expanded_adjacency_v2_compute_minimized/reliability_p015_seed0/weights/best.pt --img-size 640 --device cuda --batch-size 4 --num-workers 0 --detector-score-thr 0.001 --metric-score-thr 0.50 --nms-thresh 0.6 --detections-per-img 100 --out runs/v40_expanded_adjacency_v2_compute_minimized/reliability_p015_seed0/standardized_eval/eval_results.txt
```

## V41 Seed1 Executed Commands

### matched_early_seed1

```powershell
C:\Users\xinnan\.conda\envs\pytorch\python.exe rarepdet/eval_map.py --model early --data D:\download\triair --split-file E:\RepViT-main\reproducibility\v40_expanded_adjacency_component_split_v2\manifests\v40_expanded_adjacency_component_disjoint_val.txt --weights runs/v41_q1_upgrade/seed1/matched_early_seed1/weights/best.pt --img-size 640 --device cuda --batch-size 4 --num-workers 0 --detector-score-thr 0.001 --metric-score-thr 0.50 --nms-thresh 0.6 --detections-per-img 100 --out runs/v41_q1_upgrade/seed1/matched_early_seed1/standardized_eval/eval_results.txt
```

### reliability_p015_seed1

```powershell
C:\Users\xinnan\.conda\envs\pytorch\python.exe rarepdet/eval_map.py --model reliability --data D:\download\triair --split-file E:\RepViT-main\reproducibility\v40_expanded_adjacency_component_split_v2\manifests\v40_expanded_adjacency_component_disjoint_val.txt --weights runs/v41_q1_upgrade/seed1/reliability_p015_seed1/weights/best.pt --img-size 640 --device cuda --batch-size 4 --num-workers 0 --detector-score-thr 0.001 --metric-score-thr 0.50 --nms-thresh 0.6 --detections-per-img 100 --out runs/v41_q1_upgrade/seed1/reliability_p015_seed1/standardized_eval/eval_results.txt
```

## Verified Fixed Convention

- Development-validation split only: V40 component-disjoint validation manifest.
- Detector candidate threshold: `0.001`.
- Precision/recall/F1 metric threshold: `0.50`.
- NMS threshold: `0.6`.
- Maximum detections per image: `100`.
- Project-local AP50/AP75 via `rarepdet/eval_map.py`; no COCO, guard, channel-removal, degradation, efficiency, qualitative, gate, or aggregate analysis.
