# V40 Component-Disjoint Validation Report

Generated: 2026-07-07T16:05:00

## Scope

- Task file: `docs/NEXT_TASK.md`
- Branch: `research/ra-repdet-triair`
- Starting commit: `fd0a83d99857b1291f75bbe627152a58ee599002`
- User constraint for this run: GPU is busy; GPU-required tasks were skipped/deferred.
- Status: `AUDIT_PASSED_GPU_DEFERRED`

## CPU-Only Commands Completed

1. `git switch research/ra-repdet-triair`
2. `git pull --ff-only research research/ra-repdet-triair`
3. `python -m py_compile rarepdet/tools/build_component_disjoint_split.py rarepdet/tools/audit_component_disjoint_split.py rarepdet/tools/generate_handoff.py rarepdet/tools/update_project_status.py`
4. `python rarepdet/tools/build_component_disjoint_split.py --data D:\download\triair --target-train 7439 --target-val 2213 --target-guard 837 --guard-distance 16 --output-dir runs/component_disjoint_v40`
5. `python rarepdet/tools/audit_component_disjoint_split.py --data D:\download\triair --train-split runs/component_disjoint_v40/train.txt --val-split runs/component_disjoint_v40/val.txt --guard-split runs/component_disjoint_v40/guard.txt --guard-distance 16 --output-prefix runs/v40_component_disjoint/split_audit`

## Split Build Summary

| metric | value |
| --- | ---: |
| complete inventory count | 10489 |
| unique paths | 10489 |
| component count | 45 |
| largest component size | 4077 |
| target train / val / guard | 7439 / 2213 / 837 |
| achieved train / val / guard | 7439 / 2213 / 837 |
| deterministic rerun consistency | pass |

Split SHA256 values:

- train: `5fc7b1b2cab42e1ab7411d13e3fcfd7e19d61eb009b1900701b023d74e8fb303`
- val: `2903f4747031386f4ee7f45a87a369e20f7cd11a8a9033f930971a5b6656788b`
- guard: `9f871c16aa60b517ffd8df530782eed1befcd652969a9f94e5cd6af5ac2c8c2e`

## Strict Audit Gate

Final component-disjoint gate: **PASS**

| check | value | status |
| --- | ---: | --- |
| missing inventory paths | 0 | pass |
| unknown assigned paths | 0 | pass |
| duplicate assigned paths | 0 | pass |
| train/val path overlap | 0 | pass |
| train/guard path overlap | 0 | pass |
| val/guard path overlap | 0 | pass |
| train/val exact RGB overlap groups | 0 | pass |
| train/guard exact RGB overlap groups | 0 | pass |
| val/guard exact RGB overlap groups | 0 | pass |
| train/val same-family distance-16 violation pairs | 0 | pass |
| train/guard same-family distance-16 violation pairs | 0 | pass |
| val/guard same-family distance-16 violation pairs | 0 | pass |
| train/val minimum same-family ID distance | 17 | pass |
| train/guard minimum same-family ID distance | 17 | pass |
| val/guard minimum same-family ID distance | 17 | pass |
| connected components crossing partitions | 0 | pass |

Label inventory:

- train: 7439 images, 23011 boxes, 738 empty-target images.
- val: 2213 images, 6359 boxes, 1 empty-target image.
- guard: 837 images, 1264 boxes, 0 empty-target images.

## Deferred GPU Work

The strict audit passed, so the next authorized GPU stage is R4 reliability `p=0.20` training/evaluation for seeds `0` and `2` on the V40 split. It was not started in this run because the user stated that the GPU currently has another task running.

Skipped/deferred commands:

- `rarepdet/train_early_fusion.py` seed 0, CUDA.
- `rarepdet/eval_map.py` seed 0, CUDA.
- `rarepdet/train_early_fusion.py` seed 2, CUDA.
- `rarepdet/eval_map.py` seed 2, CUDA.
- Conditional synthetic missingness, aggregate, and efficiency package, all dependent on completed R4 checkpoints/evaluations.

## Outputs

- Split files: `runs/component_disjoint_v40/train.txt`, `runs/component_disjoint_v40/val.txt`, `runs/component_disjoint_v40/guard.txt`
- Manifest: `runs/component_disjoint_v40/split_manifest.csv`, `runs/component_disjoint_v40/split_manifest.json`
- Build report: `runs/component_disjoint_v40/split_build_report.md`
- Audit report: `runs/v40_component_disjoint/split_audit.md`, `.csv`, `.json`

## Guardrails

- No training was started.
- No CUDA evaluation, synthetic missingness, efficiency profiling, or robustness package was started.
- No protected training/evaluation core file was modified.
- No manuscript, submission, table, figure, author metadata, raw data, checkpoint, weight, prediction dump, or visual artifact was added by this CPU-only task.
