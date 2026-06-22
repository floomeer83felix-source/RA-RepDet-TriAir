# Current Task

## Phase 3A — Dropout-Ratio Ablation and Paper Evidence Package

## Research Decision
E5 (ACRF) and E6 (MSCD) both failed the predefined replacement rule. Stop adding new fusion or distillation methods. E2 remains the paper main model.

This phase must supply the two pieces of evidence still needed for a credible manuscript:
1. a controlled modality-dropout ratio ablation showing whether `p=0.15` is a reasonable choice;
2. paper-ready qualitative-case selection for E0/E1/E2.

## Read First
- `docs/PROJECT_CONTEXT.md`
- `docs/EXPERIMENT_STATUS.md`
- `runs/phase2a_report.md`
- `runs/acrf_evidence_report.md`
- `runs/mscd_evidence_report.md`
- `runs/handoff_latest.md`

## Frozen Assets
Do not overwrite or alter E0, E1, E2, E5, or E6.

Do not modify:
- `rarepdet/train_early_fusion.py`
- `rarepdet/models/early_fusion_fcos.py`
- `rarepdet/models/reliability_fusion_fcos.py`
- `datasets/triair_dataset.py`

Do not add a new architecture, loss, teacher, or artificial weather/noise experiment.
Never run two training jobs simultaneously.

## Task 1 — Controlled dropout-ratio ablation
Train only these two missing ratio points, using the exact E2 training recipe:

### E3: dropout 0.10
```powershell
python rarepdet/train_early_fusion.py --model reliability --data D:\download\triair --train-split D:\download\triair\splits\train.txt --val-split D:\download\triair\splits\val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --modality-dropout 0.10 --out runs/E3_reliability_dropout010_repvit_fcos_e50
```

### E4: dropout 0.20
Run only after E3 evaluation has completed:
```powershell
python rarepdet/train_early_fusion.py --model reliability --data D:\download\triair --train-split D:\download\triair\splits\train.txt --val-split D:\download\triair\splits\val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --modality-dropout 0.20 --out runs/E4_reliability_dropout020_repvit_fcos_e50
```

If batch size 4 gives CUDA OOM, rerun that experiment once with batch size 2 and record it in the output config/report. Do not change any other hyperparameter.

For E3 and E4, after each train run:
```powershell
python rarepdet/eval_map.py --model reliability --data D:\download\triair --split-file D:\download\triair\splits\val.txt --weights <BEST_WEIGHT> --img-size 640 --device cuda --batch-size 4 --score-thr 0.50 --out <RUN_DIR>/eval_thr050
python rarepdet/tools/eval_missing_modality.py --model reliability --data D:\download\triair --split-file D:\download\triair\splits\val.txt --weights <BEST_WEIGHT> --img-size 640 --device cuda --batch-size 4 --score-thr 0.05 --out <RUN_DIR>/missing_modality
```

## Task 2 — Build the ratio-ablation report
Create or update `rarepdet/tools/build_dropout_ablation_report.py` and generate:
- `runs/dropout_ablation_summary.csv`
- `runs/dropout_ablation_summary.md`

Compare exactly:
- E1: p=0.00
- E3: p=0.10
- E2: p=0.15
- E4: p=0.20

Required columns:

| Method | Dropout Ratio | P@0.50 | R@0.50 | F1@0.50 | Full AP50 | Full AP75 | w/o RGB AP50 | w/o Thermal AP50 | w/o Event AP50 | Mean Missing-Modality AP50 |

Footnote: Mean Missing-Modality AP50 is only the arithmetic mean of the three single-modality-missing AP50 values; it is a robustness summary, not a standard detection metric.

Selection rule:
- choose the default ratio based on full-modality AP50/AP75 plus the three per-condition missing-modality AP50 values;
- do not select a ratio based only on the arithmetic mean;
- state whether p=0.15 remains justified.

## Task 3 — Qualitative paper cases
Use E0/E1/E2 only. Existing comparison tools may be reused or repaired in `rarepdet/tools/`.

At `score_thr=0.50`, generate a lightweight manifest/report only; never commit images:
- `runs/qualitative_cases_summary.md`
- `runs/qualitative_cases_manifest.csv`

The manifest must include image id/path, brightness-proxy group, GT count, and per-model TP/FP/FN summary for selected examples.

Select up to five recommended cases in each category:
- E0 miss, E2 hit;
- E1 miss, E2 hit;
- low-brightness E2-success case;
- representative shared success case;
- representative E2 failure case.

In the Markdown report provide one proposed figure caption, but do not claim causal explanations from a single image.

## Task 4 — Final package
Create `runs/phase3a_report.md` containing:
1. dropout-ratio ablation table;
2. selected default ratio decision;
3. qualitative-case manifest summary;
4. final model decision: E2 remains main model unless ablation shows otherwise;
5. exact remaining gaps before manuscript drafting.

Update:
- `docs/EXPERIMENT_STATUS.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`

Commit only source code, docs, Markdown, CSV, TXT, and JSON. Never commit weights, data, npy files, images, or visual outputs.

Commit message:
`Phase 3A: dropout ablation and qualitative evidence`

Push to `research/ra-repdet-triair`.

If blocked, create/update `docs/TASK_BLOCKER.md` with the exact failed command, final error, attempted fix, and smallest safe next action.