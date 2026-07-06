# V40 v2 Experiment Contract

- Status: `V40_EXPERIMENT_CONTRACT_PASS`
- Generated: `2026-07-06T09:07:21`
- Input commit: `e338ef259b8df123de8b1a9ed8f1f750000cdbfc`
- Output commit: `PENDING_FINAL_COMMIT_RECORDED_IN_GIT_HISTORY_AND_FINAL_RESPONSE`
- Evidence scope: `validation-only evidence on the V40 v2 expanded-adjacency component-disjoint split`
- Required split status: `V40_V2_READY_FOR_FROZEN_RERUN`

## Locked Inputs

- Train manifest: `reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_train.txt`
- Train manifest SHA-256: `f24117e3fec5833e06e20202f8ea05cbc2242b3977bcb791d95f2099c8b4133f`
- Validation manifest: `reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt`
- Validation manifest SHA-256: `722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f`
- Dataset root: `D:\download\triair`
- Label-count method: Resolve each manifest entry to a .npy image, match the label txt by unique stem under the TriAir label directory, count non-empty txt rows as GT boxes, and count missing txt files as zero-target images.

## Locked Training Recipe

- Epochs: `50`
- Image size: `640`
- Batch size: `4`
- Learning rate: `1e-4`
- Optimizer: `torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)`
- Scheduler: `none in trainer source`
- Data loader: `train DataLoader batch_size=4 shuffle=True num_workers=0 collate_fn=datasets.triair_dataset.collate_fn pin_memory=True on CUDA with seeded CPU generator; validation DataLoader shuffle=False.`
- Deterministic settings: `Seeds 0 and 2 set Python random, NumPy, torch, CUDA manual_seed_all, cudnn.deterministic=True, cudnn.benchmark=False, torch deterministic algorithms warn_only when supported.`
- Augmentations: `No mosaic, mixup, crop, flip, color jitter, or spatial augmentation in the project DetectionTriAirDataset path; modality dropout is the only training-time augmentation and is locked per run.`

## Locked Evaluation Recipe

- Evaluator: `rarepdet/eval_map.py`
- Detector score threshold: `0.001`
- Metric operating threshold: `0.50`
- NMS threshold: `0.6`
- Detections per image: `100`
- AP definition: Project-local single-class score-ranked AP at IoU 0.50 and 0.75 from rarepdet/metrics.py; not COCO AP50:95 and not pycocotools.

## Selection Rule

Choose one reliability-dropout setting only after all six reliability runs finish: highest two-run mean AP50, then highest two-run mean F1, then highest two-run mean AP75, with exact-tie fallback p=0.00 then p=0.15 then p=0.20.

## No Adaptive Changes

No model, loader, optimizer, scheduler, augmentation, threshold, checkpoint-selection, seed, split, command, or output-naming setting may be changed because of V40 validation performance.

## Prohibited Tuning Actions

- Do not start p=0.20 or any other V40 training until this contract is accepted.
- Do not change V40 v2 train, validation, or guard manifests.
- Do not use the guard partition for model selection or performance reporting.
- Do not change raw data, labels, model code, loader code, trainer core, evaluator core, or prior V38/V39 artifacts.
- Do not use AP, F1, loss, predictions, confidence, checkpoints, or qualitative images to change split or training settings.
- Do not use DroneVehicle or any external data in the V40 evidence pipeline.
- Do not run robustness, profiling, qualitative, manuscript, or submission work under Gate 1.
- Do not selectively retry a weak-scoring run; resolve technical failures only by documented full-contract policy.
- Do not call finish_task.ps1 for V40 master-plan gates.

## Smoke Checks

- Label-free configuration smoke: `PASS`
- Data-loader/model-forward smoke: `PASS`

This contract is a pre-run gate. Smoke outputs are not experimental results.
