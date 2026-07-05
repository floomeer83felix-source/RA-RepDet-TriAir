# V39 Component-Disjoint Validation Summary

Generated from local V39 artifacts under `runs/v39_component_disjoint/` after completing `reliability_p015_seed2_e50` and its standardized evaluation.

## Scope

- Experiment: `RA_RepDet_SIVP_v39_ComponentDisjointValidation`.
- Split files: `runs/component_disjoint_candidates/candidate_component_disjoint_v1_train.txt`, `candidate_component_disjoint_v1_val.txt`, and `candidate_component_disjoint_v1_guard_unchanged.txt`.
- Split sizes: 7439 train images, 2213 validation images, 837 guard images.
- Validation split SHA256: `e454695b35a4867d5f58f4351a96156436b38a02fad1e90d573e30352fd6bd3c`.
- Train split SHA256: `7fbe6372f9eca8ef2a1a9e33c3f2bbf72078a50c62a8ffcdaf06c348e8c0a7b6`.
- Guard split SHA256: `25a57cea733a218ce2bbd37b22acdf76722cdcc3856861020017340357b338a8`.
- Evaluation script: `rarepdet/eval_map.py`.
- Standardized evaluation settings: detector score threshold 0.001, metric score threshold 0.50, NMS threshold 0.6, detections per image 100, image size 640, batch size 4.
- Evaluation environment: Python 3.9.21, PyTorch 2.5.1, torchvision 0.20.1, timm 1.0.22, CUDA available on NVIDIA GeForce RTX 3090.
- Heavy artifacts are intentionally local only: `weights/*.pt` checkpoints are not committed.

## Per-Run Standardized Results

| Group | Run | Seed | Dropout | Precision | Recall | F1 | AP50 | AP75 | Predictions |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| early | early_seed0_e50 | 0 | NA | 0.846249 | 0.918732 | 0.881002 | 0.942090 | 0.807705 | 6439 |
| early | early_seed2_e50 | 2 | NA | 0.808696 | 0.909459 | 0.856123 | 0.934822 | 0.781736 | 6670 |
| reliability_p000 | reliability_p000_seed0_e50 | 0 | 0.00 | 0.919520 | 0.891924 | 0.905512 | 0.953402 | 0.879041 | 5753 |
| reliability_p000 | reliability_p000_seed2_e50 | 2 | 0.00 | 0.930882 | 0.887877 | 0.908871 | 0.955107 | 0.872105 | 5657 |
| reliability_p015 | reliability_p015_seed0_e50 | 0 | 0.15 | 0.911096 | 0.919238 | 0.915149 | 0.959206 | 0.894285 | 5984 |
| reliability_p015 | reliability_p015_seed2_e50 | 2 | 0.15 | 0.896171 | 0.931378 | 0.913435 | 0.961196 | 0.864872 | 6164 |

## Two-Seed Means

| Variant | Seeds | Mean Precision | Mean Recall | Mean F1 | Mean AP50 | Mean AP75 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Early fusion | 0, 2 | 0.827473 | 0.914095 | 0.868562 | 0.938456 | 0.794720 |
| Reliability p=0.00 | 0, 2 | 0.925201 | 0.889901 | 0.907192 | 0.954255 | 0.875573 |
| Reliability p=0.15 | 0, 2 | 0.903634 | 0.925308 | 0.914292 | 0.960201 | 0.879578 |

## Notes

- The final missing V39 run, `reliability_p015_seed2_e50`, completed 50/50 epochs and wrote `Training complete.` in `train_log.txt`.
- The training-log epoch-50 validation row for `reliability_p015_seed2_e50` was not used as the final report value. The reported row above comes from the standardized `eval_map.py` run on `weights/best.pt`.
- V39 is component-disjoint validation evidence and should be interpreted separately from the manuscript headline clean blocked-split R4 p=0.20 result already recorded in `docs/EXPERIMENT_STATUS.md`.
- No protected training core files were modified for this V39 completion and evaluation pass.
