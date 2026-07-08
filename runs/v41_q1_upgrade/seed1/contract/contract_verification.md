# V41 Seed1 Contract Verification

Generated: `2026-07-08T10:36:47`
Status: **PASS**
Git commit: `802d9446bd359017ca93478918073808d83876d1`

## Frozen Hash Checks

| name | exists | sha256 | expected | status |
| --- | --- | --- | --- | --- |
| source_lock | True | `f5d205bb5fcf99aa1c1492e6564e2708e78af370f3f8dee79868050fb16eca38` | `recorded_only` | RECORDED |
| train_manifest | True | `f24117e3fec5833e06e20202f8ea05cbc2242b3977bcb791d95f2099c8b4133f` | `f24117e3fec5833e06e20202f8ea05cbc2242b3977bcb791d95f2099c8b4133f` | PASS |
| val_manifest | True | `722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f` | `722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f` | PASS |
| rarepdet/train_early_fusion.py | True | `d9cae1e22e41ad0c7cfab13bf83ac058b5335cd1fcc41e3da9b1f8c53d05167a` | `recorded_only` | RECORDED |
| rarepdet/eval_map.py | True | `94557cb80ae24b8663e9eb31955afe668b994058cd8e3e7618ae33e4c0017715` | `94557cb80ae24b8663e9eb31955afe668b994058cd8e3e7618ae33e4c0017715` | PASS |
| rarepdet/metrics.py | True | `6ffa798647376594befc45f89ebb1aa1a5fbe3b50e5f484e7804c22bac13b081` | `6ffa798647376594befc45f89ebb1aa1a5fbe3b50e5f484e7804c22bac13b081` | PASS |
| rarepdet/data.py | True | `d90c472cc320ccc8553bb827487b4052a5973cdd08db7e4972a5d59499381931` | `recorded_only` | RECORDED |
| datasets/triair_dataset.py | True | `f3592421394c465f469c45410e1981613223634e0dd3cfffded281777ddad705` | `recorded_only` | RECORDED |
| rarepdet/models/early_fusion_fcos.py | True | `c2ad086c6dc0f0d1f390462184d496931d62ddf4c3e25c5816335f1b8c7db9f8` | `recorded_only` | RECORDED |
| rarepdet/models/repvit_fpn_backbone.py | True | `a4ece2af4ec4e2280180c0bda3879f627d5b5340f589ffe6c0d50d4f7fe30a7f` | `recorded_only` | RECORDED |

## Manifest Counts

- Train manifest rows: 7439
- Development-validation manifest rows: 2213

## Environment

- Python: 3.9.21
- Platform: Windows-10-10.0.26200-SP0
- PyTorch: 2.5.1
- Torch CUDA: 12.4
- CUDA available: True
- GPU: NVIDIA GeForce RTX 3090
- GPU memory MiB: 24575
- torchvision: 0.20.1
- timm: 1.0.22
- numpy: 1.26.4

## Read-First File Presence

| path | exists | note |
| --- | --- | --- |
| AGENTS.md | True | missing file is recorded but not a frozen hash gate |
| PROJECT_PROFILE.md | False | missing file is recorded but not a frozen hash gate |
| docs/PROJECT_CONTEXT.md | True | missing file is recorded but not a frozen hash gate |
| docs/V40_PUBLICATION_SNAPSHOT.md | False | missing file is recorded but not a frozen hash gate |
| docs/REPRODUCIBILITY.md | True | missing file is recorded but not a frozen hash gate |
| runs/handoff_latest.md | True | missing file is recorded but not a frozen hash gate |
