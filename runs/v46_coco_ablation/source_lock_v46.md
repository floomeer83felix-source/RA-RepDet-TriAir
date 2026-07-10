# V46 COCO Metrics and Causal Ablation Source Lock

Generated: 2026-07-10T09:39:27+08:00

Status: `V46_SOURCE_LOCKED_BEFORE_EXECUTION`

## Repository

- Commit before V46 reporting commit: `0985c45a179f469adfc8b0b6326a54737c63789e`
- Branch: `research/ra-repdet-triair`
- Working tree clean at lock time: `False`
- Note: PROJECT_PROFILE.md requested by NEXT_TASK.md is absent from the repository root.

## Frozen manifests

| Role | Path | Rows | Raw SHA256 | Normalized-LF SHA256 |
| --- | --- | ---: | --- | --- |
| train | `reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_train.txt` | 7439 | `f24117e3fec5833e06e20202f8ea05cbc2242b3977bcb791d95f2099c8b4133f` | `d62cb25e7a6951e0a0da8b693a3438035fb57cf2344803a53d98f1be0369e161` |
| devval | `reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt` | 2213 | `722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f` | `c03d70dcaaa908c70a35b5c224670a4f2aa288054e6cf70d05fb110a53147a72` |
| guard | `runs/component_disjoint_v40/guard.txt` | 837 | `0cf3270c0a73d03caf8d698bb4e9ddb0adba46e688c52d8589f57ea12488881f` | `9f871c16aa60b517ffd8df530782eed1befcd652969a9f94e5cd6af5ac2c8c2e` |

## Six fixed baseline/main checkpoints

| Run | Variant | Model | Seed | Dropout | Path | SHA256 |
| --- | --- | --- | ---: | ---: | --- | --- |
| matched_early_seed0 | matched_early | early | 0 | 0.00 | `runs/v40_expanded_adjacency_v2_compute_minimized/matched_early_seed0/weights/best.pt` | `23331a6e668634f5f1ca1c7dfaddd23e9ee5445c0558e325621e8f454a0b1602` |
| matched_early_seed1 | matched_early | early | 1 | 0.00 | `runs/v41_q1_upgrade/seed1/matched_early_seed1/weights/best.pt` | `60a338ed887c15d94d3f274df39684c1dc6de68f9f29ba13f9f9cb4d6fbcd804` |
| matched_early_seed2 | matched_early | early | 2 | 0.00 | `runs/v40_expanded_adjacency_v2_compute_minimized/matched_early_seed2/weights/best.pt` | `b36b4965931da68b77a6be82e85e47b34f952445d64b941337f56a722f62737e` |
| reliability_p015_seed0 | ra_full_p015 | reliability | 0 | 0.15 | `runs/v40_expanded_adjacency_v2_compute_minimized/reliability_p015_seed0/weights/best.pt` | `4284aaa188cb7f065a01b6cf32b78265ab937da0de2d3423d4594d2102787436` |
| reliability_p015_seed1 | ra_full_p015 | reliability | 1 | 0.15 | `runs/v41_q1_upgrade/seed1/reliability_p015_seed1/weights/best.pt` | `a59366dd0687754577d23d3e21358127199345d4ebf3a55a06472b933b57813d` |
| reliability_p015_seed2 | ra_full_p015 | reliability | 2 | 0.15 | `runs/v40_expanded_adjacency_v2_compute_minimized/reliability_p015_seed2/weights/best.pt` | `27affa96df1b3baad3df6f0a591e0599c1f5c0f77f91fad9fdaa408e549f1415` |

## Evaluator and training code hashes

- `rarepdet/coco_metrics.py`: `af644845bef1442ab72bd8fc07c6a74923088e864072a9f5944148e7d771f565`
- `rarepdet/tools/eval_coco_map.py`: `1fe9023734de88b64f355d0a24cfb853d15a95084e233c40e0baab94015f783f`
- `rarepdet/tools/smoke_test_coco_metrics.py`: `48c6579d7dda452dbc6aab9cb3bfc6875ca745a731edf3fba8a51ee2f3ef9055`
- `rarepdet/tools/create_v46_source_lock.py`: `b52bcc2314dea17972a35e6170aa6605ce29ffb3dd2a9a75ad29842d720b1d88`
- `rarepdet/eval_map.py`: `94557cb80ae24b8663e9eb31955afe668b994058cd8e3e7618ae33e4c0017715`
- `rarepdet/metrics.py`: `6ffa798647376594befc45f89ebb1aa1a5fbe3b50e5f484e7804c22bac13b081`
- `rarepdet/train_early_fusion.py`: `d9cae1e22e41ad0c7cfab13bf83ac058b5335cd1fcc41e3da9b1f8c53d05167a`
- `rarepdet/data.py`: `d90c472cc320ccc8553bb827487b4052a5973cdd08db7e4972a5d59499381931`
- `rarepdet/models/early_fusion_fcos.py`: `c2ad086c6dc0f0d1f390462184d496931d62ddf4c3e25c5816335f1b8c7db9f8`
- `rarepdet/models/repvit_fpn_backbone.py`: `a4ece2af4ec4e2280180c0bda3879f627d5b5340f589ffe6c0d50d4f7fe30a7f`
- `datasets/triair_dataset.py`: `f3592421394c465f469c45410e1981613223634e0dd3cfffded281777ddad705`

## Fixed conventions

- COCO bbox AP uses `pycocotools.cocoeval.COCOeval`, IoU 0.50:0.05:0.95, 101 recall samples, area=all, and maxDets=100.
- Detector score threshold is 0.001; the project operating threshold for precision/recall/F1 is 0.50.
- Training uses 50 epochs, batch size 4, image size 640, AdamW at 1e-4 with weight decay 1e-4, and best checkpoint selection by development-validation project-local AP50.

## Environment

- platform: `Windows-10-10.0.26200-SP0`
- python_executable: `C:\Users\xinnan\.conda\envs\pytorch\python.exe`
- python: `3.9.21`
- pytorch: `2.5.1`
- torchvision: `0.20.1`
- timm: `1.0.22`
- pycocotools: `2.0.8`
- torch_cuda: `12.4`
- cuda_available: `True`
- gpu: `NVIDIA GeForce RTX 3090`
- nvidia_smi: `NVIDIA GeForce RTX 3090, 591.86, 24576 MiB`

## Guard boundary

The locked same-dataset guard is evaluation-only and is not used for training, tuning, threshold selection, dropout selection, checkpoint selection, ablation selection, or run continuation decisions.
