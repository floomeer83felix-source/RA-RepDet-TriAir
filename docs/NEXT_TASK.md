# Current Task

## Authorization

`V76_TRIAIR_SINGLE_MODALITY_MAJOR_REVISION_ABLATION_AUTHORIZED`

The user explicitly authorized a major revision and all experiments necessary to address the review. Existing V42/V48/V75 evidence has already been integrated. The only newly authorized training is the fixed single-modality ablation below.

## Frozen run matrix

| Input mode | Seeds | Runs |
| --- | --- | ---: |
| RGB-only | 0, 1, 2 | 3 |
| Thermal-only | 0, 1, 2 | 3 |
| Event-only | 0, 1, 2 | 3 |

Total: exactly `9` runs.

## Frozen training contract

- dataset: local TriAir copy only;
- train split: frozen V40 component-disjoint train manifest;
- evaluation split: frozen V40 component-disjoint development-validation manifest;
- epochs: `50`;
- batch size: `4`;
- image size: `640`;
- optimizer: AdamW;
- learning rate: `1e-4`;
- modality dropout: `0`;
- seeds: exactly `0`, `1`, and `2`;
- checkpoint retention: highest development-validation project-local AP50;
- final reporting: one standardized COCO evaluation of each retained checkpoint;
- guard partition: forbidden;
- no threshold tuning, schedule tuning, adaptive epoch extension, selective rerun, or seed replacement.

## Execution command

```powershell
python rarepdet/tools/run_v76_single_modality_queue.py --data D:\\download\\triair --device cuda --resume
```

After all nine runs complete:

```powershell
python rarepdet/tools/build_v76_single_modality_summary.py
```

## Required completion outputs

Create under `runs/v76_triair_single_modality_ablation/`:

- `protocol.json`;
- nine `training/<mode>_seed<seed>/run_status.json` records;
- nine final COCO JSON records under `raw/`;
- `single_modality_per_run.csv`;
- `single_modality_summary.json`;
- manuscript integration audit;
- clean PDF build and rendered-page inspection.

## Scientific boundary

The experiment may support descriptive comparison of trained single-modality baselines under the fixed TriAir development protocol. It may not support independent-test performance, physical sensor-failure robustness, statistical significance, or selective-result claims.

## Current state

`V76_MAJOR_REVISION_EXISTING_EVIDENCE_INTEGRATED_SINGLE_MODALITY_QUEUE_READY`

The queue is ready but not executed in this environment because the private dataset and local CUDA workspace are unavailable.
