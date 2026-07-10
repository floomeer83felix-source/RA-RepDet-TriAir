# Task Blocker

Status: `V46_PARTIAL_COMPLETION_GPU_TIME_AND_ALLOWED_SCOPE_BLOCKER`

Generated: 2026-07-10T22:28:45+08:00

This is an accepted V46 partial-completion state, not a fabricated full completion. The fixed-checkpoint COCO package is complete, and the two feasible fresh seed0 ablations are complete. Remaining seed replication and architecture-changing controls are blocked as described below.

## Completed before the blocker

- Six fixed matched-early / reliability-aware `p=0.15` checkpoints were evaluated on both frozen development-validation and locked same-dataset guard manifests with canonical COCO-style AP.
- Fresh `ra_no_moddrop_seed0` completed 50 epochs, dev-val AP50 checkpoint selection, and COCO-style dev-val evaluation.
- Fresh `early_moddrop_seed0` completed 50 epochs, dev-val AP50 checkpoint selection, and COCO-style dev-val evaluation.
- Measured training runtime: `ra_no_moddrop_seed0=12.333 h`; `early_moddrop_seed0=12.243 h`.
- No ablation guard evaluation was run.

## Blocker 1: remaining fresh seeds

Seeds 1 and 2 remain unrun for `ra_no_moddrop` and `early_moddrop`. Based on the measured seed0 runtime, four additional 50-epoch jobs require substantial additional GPU time. `docs/NEXT_TASK.md` explicitly authorizes seed0-first partial completion when GPU/time is insufficient.

Exact pending training commands:

```powershell
C:\Users\xinnan\.conda\envs\pytorch\python.exe rarepdet/train_early_fusion.py --model reliability --data D:\download\triair --train-split reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_train.txt --val-split reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --modality-dropout 0.00 --seed 1 --out runs/v46_coco_ablation/local_training/ra_no_moddrop_seed1
```

```powershell
C:\Users\xinnan\.conda\envs\pytorch\python.exe rarepdet/train_early_fusion.py --model reliability --data D:\download\triair --train-split reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_train.txt --val-split reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --modality-dropout 0.00 --seed 2 --out runs/v46_coco_ablation/local_training/ra_no_moddrop_seed2
```

```powershell
C:\Users\xinnan\.conda\envs\pytorch\python.exe rarepdet/train_early_fusion.py --model early --data D:\download\triair --train-split reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_train.txt --val-split reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --modality-dropout 0.15 --seed 1 --out runs/v46_coco_ablation/local_training/early_moddrop_seed1
```

```powershell
C:\Users\xinnan\.conda\envs\pytorch\python.exe rarepdet/train_early_fusion.py --model early --data D:\download\triair --train-split reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_train.txt --val-split reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --modality-dropout 0.15 --seed 2 --out runs/v46_coco_ablation/local_training/early_moddrop_seed2
```

Minimal action needed: explicitly authorize another long GPU window, then run the four commands one seed pair at a time and evaluate only on development-validation before considering any optional guard check.

## Blocker 2: static fusion controls

`ra_static_equal` and `ra_stems_concat_or_project` require a new model architecture and checkpoint-loading path. The V46 allowed-file list permits reporting/evaluation scripts, metric helpers, and configs, but it does not permit edits to the protected training/model core required to add these variants. Implementing them inside a reporting script would be risky architecture duplication.

Minimal action needed: explicitly expand the allowed file scope to a dedicated ablation model module plus training/evaluation plumbing, then source-lock that implementation before training.

## Attempted alternatives

1. Searched local run configs for checkpoints trained with the exact frozen V40 manifests and matching `reliability p=0.00` or `early p=0.15` settings; none existed, so incompatible older E-run checkpoints were not reused.
2. Assessed static-equal and deterministic-projection implementation against the protected/allowed file lists; both require architecture plumbing outside the authorized scope and were skipped rather than producing unreviewable duplicate model code.
3. Ran the two feasible seed0 jobs concurrently after verifying aggregate GPU memory headroom; each retained an independent process, deterministic seed state, output directory, and development-validation selection rule.

## Last 50 error lines

```text
No error lines. Both feasible seed0 runs and evaluations completed successfully.
```

## Related files

- `runs/v46_coco_ablation/ablation_train_commands.txt`
- `runs/v46_coco_ablation/ablation_execution_status.json`
- `runs/v46_coco_ablation/ablation_devval_per_run.csv`
- `runs/v46_coco_ablation/ablation_devval_summary.md/json`
- `runs/v46_coco_ablation/ablation_claim_boundary.md`
- `rarepdet/train_early_fusion.py` (executed, not modified)
- `rarepdet/models/repvit_fpn_backbone.py` (source-locked, not modified)
- `rarepdet/models/early_fusion_fcos.py` (source-locked, not modified)

## Repair options

1. GPU-replication option: retain the current architecture scope and run only the four pending seed1/2 jobs, then regenerate the descriptive summaries.
2. Architecture-expansion option: authorize a dedicated V47-style ablation architecture module for static-equal and deterministic-projection controls, source-lock it, and run seed0 first before any further seeds.
