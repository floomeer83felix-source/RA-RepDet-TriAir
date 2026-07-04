# Standardized Evaluation Protocol (V23)

## Scope

This branch records the standardized evaluation protocol used for the V23 manuscript-result refresh. It does not alter model weights, the frozen split, or the data partitioning protocol.

- Frozen validation manifest: `runs/blocked_split_candidates/block64_guard16_seed0_val.txt`
- Validation-manifest SHA-256: `a48aff2ee29d041bd07b746947028191475a59f0df6b7b64d4882cd610746dc4`
- Detector-output score threshold: `0.001`
- Precision / recall / F1 operating threshold: `0.50`
- NMS threshold: `0.6`
- Maximum detections per image: `100`

AP50 and AP75 are project-local, single-class, score-ranked average-precision measurements. They are not COCO AP50:95.

## Interpretation boundary

The reported values are validation-partition estimates. The guard partition is not used for model selection or headline results. Missing-modality rows are synthetic channel-removal conditions, not measurements from physically failed sensors.

## Evidence

Lightweight aggregate tables, manifests, commands, environment records, and raw evaluator output records are stored in `reproducibility/standardized_evaluation_v23/`. Raw data, checkpoints, and trained weights are intentionally excluded from this repository.

## Standardized commands

Use the dedicated standardized evaluator scripts with explicit thresholds. The data root and checkpoint path are local paths supplied by the user.

```powershell
python rarepdet/eval_map.py --model reliability --data <LOCAL_DATASET_ROOT> --split-file runs/blocked_split_candidates/block64_guard16_seed0_val.txt --weights <LOCAL_CHECKPOINT_PATH> --img-size 640 --device cuda --batch-size 4 --detector-score-thr 0.001 --metric-score-thr 0.50 --nms-thresh 0.6 --detections-per-img 100 --out runs/standardized_eval
```

```powershell
python rarepdet/tools/eval_missing_modality.py --model reliability --data <LOCAL_DATASET_ROOT> --split-file runs/blocked_split_candidates/block64_guard16_seed0_val.txt --weights <LOCAL_CHECKPOINT_PATH> --img-size 640 --device cuda --batch-size 4 --detector-score-thr 0.001 --metric-score-thr 0.50 --nms-thresh 0.6 --detections-per-img 100 --out runs/standardized_missing_modality
```
