# V41 Seed1 Source Lock

Generated: 2026-07-09T00:54:22

- Status: `V41_SEED1_FRESH_PAIRED_DEVVAL_COMPLETE`
- Git branch: `research/ra-repdet-triair`
- Git commit before report commit: `802d9446bd359017ca93478918073808d83876d1`
- Contract verification: `PASS`
- Train manifest SHA256: `f24117e3fec5833e06e20202f8ea05cbc2242b3977bcb791d95f2099c8b4133f`
- Development-validation manifest SHA256: `722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f`
- Guard partition: not accessed or evaluated.

## Source Hashes

| Path | SHA256 |
| --- | --- |
| rarepdet/train_early_fusion.py | d9cae1e22e41ad0c7cfab13bf83ac058b5335cd1fcc41e3da9b1f8c53d05167a |
| rarepdet/eval_map.py | 94557cb80ae24b8663e9eb31955afe668b994058cd8e3e7618ae33e4c0017715 |
| rarepdet/metrics.py | 6ffa798647376594befc45f89ebb1aa1a5fbe3b50e5f484e7804c22bac13b081 |
| rarepdet/data.py | d90c472cc320ccc8553bb827487b4052a5973cdd08db7e4972a5d59499381931 |
| datasets/triair_dataset.py | f3592421394c465f469c45410e1981613223634e0dd3cfffded281777ddad705 |
| rarepdet/models/early_fusion_fcos.py | c2ad086c6dc0f0d1f390462184d496931d62ddf4c3e25c5816335f1b8c7db9f8 |
| rarepdet/models/repvit_fpn_backbone.py | a4ece2af4ec4e2280180c0bda3879f627d5b5340f589ffe6c0d50d4f7fe30a7f |

## Checkpoints

| Run | Best checkpoint SHA256 | Last checkpoint SHA256 |
| --- | --- | --- |
| matched_early_seed1 | 60a338ed887c15d94d3f274df39684c1dc6de68f9f29ba13f9f9cb4d6fbcd804 | 466f597826264af0d919d9cb5dfa756b5a97c37a412a9a1b721740969fc0ebed |
| reliability_p015_seed1 | a59366dd0687754577d23d3e21358127199345d4ebf3a55a06472b933b57813d | 7d0cfc26158ce0e634b2c50e948aeb5b0217d38831f80e20c2a19f9bbc9e55a0 |

## Commands

### matched_early_seed1 training

```powershell
python rarepdet/train_early_fusion.py --model early --data D:\download\triair --train-split reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_train.txt --val-split reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --modality-dropout 0.00 --seed 1 --out runs/v41_q1_upgrade/seed1/matched_early_seed1
```

### matched_early_seed1 evaluation

```powershell
C:\Users\xinnan\.conda\envs\pytorch\python.exe rarepdet/eval_map.py --model early --data D:\download\triair --split-file E:\RepViT-main\reproducibility\v40_expanded_adjacency_component_split_v2\manifests\v40_expanded_adjacency_component_disjoint_val.txt --weights runs/v41_q1_upgrade/seed1/matched_early_seed1/weights/best.pt --img-size 640 --device cuda --batch-size 4 --num-workers 0 --detector-score-thr 0.001 --metric-score-thr 0.50 --nms-thresh 0.6 --detections-per-img 100 --out runs/v41_q1_upgrade/seed1/matched_early_seed1/standardized_eval/eval_results.txt
```

### reliability_p015_seed1 training

```powershell
python rarepdet/train_early_fusion.py --model reliability --data D:\download\triair --train-split reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_train.txt --val-split reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --modality-dropout 0.15 --seed 1 --out runs/v41_q1_upgrade/seed1/reliability_p015_seed1
```

### reliability_p015_seed1 evaluation

```powershell
C:\Users\xinnan\.conda\envs\pytorch\python.exe rarepdet/eval_map.py --model reliability --data D:\download\triair --split-file E:\RepViT-main\reproducibility\v40_expanded_adjacency_component_split_v2\manifests\v40_expanded_adjacency_component_disjoint_val.txt --weights runs/v41_q1_upgrade/seed1/reliability_p015_seed1/weights/best.pt --img-size 640 --device cuda --batch-size 4 --num-workers 0 --detector-score-thr 0.001 --metric-score-thr 0.50 --nms-thresh 0.6 --detections-per-img 100 --out runs/v41_q1_upgrade/seed1/reliability_p015_seed1/standardized_eval/eval_results.txt
```
