# Current Task

## Phase 2C — Modality-Subset Consistency Distillation (MSCD)

## Decision
E5 ACRF proves exact absent-modality suppression, but it lowers full-modality AP50/AP75 versus E2. Do not add another inference-time fusion block.

Implement one training-only, high-level-method-inspired improvement: **Modality-Subset Consistency Distillation (MSCD)**. It is motivated by masked multimodal representation learning and self-distillation for incomplete modalities, but must be adapted to the current lightweight RepViT-FPN-FCOS detector rather than copied from another architecture.

## Goal
Improve missing-modality robustness while preserving E2 full-modality quality. Inference architecture, parameter count, and runtime must remain identical to E2.

## Read First
- `docs/PROJECT_CONTEXT.md`
- `docs/EXPERIMENT_STATUS.md`
- `runs/phase2a_report.md`
- `runs/acrf_evidence_report.md`
- existing E2 training and reliability-model source files

## Frozen Assets
Do not overwrite or modify E0, E1, E2, or E5 runs.

Do not modify these source files:
- `rarepdet/train_early_fusion.py`
- `rarepdet/models/early_fusion_fcos.py`
- `rarepdet/models/reliability_fusion_fcos.py`
- `datasets/triair_dataset.py`

Do not add an inference-time attention block, extra detector head, cross-attention, transformer, reconstruction decoder, or parameterized projection layer.

## Method Specification
Create new files only:
- `rarepdet/train_mscd.py`
- `rarepdet/tools/test_mscd.py`
- `rarepdet/tools/build_mscd_report.py`
- `docs/MSCD_DESIGN.md`

### Teacher
- Frozen E2 checkpoint: `runs/E2_reliability_dropout015_repvit_fcos_e50/weights/best.pt`.
- Teacher always receives the full 5-channel input.
- Teacher is `eval()` and fully `no_grad()`.

### Student
- Same inference architecture as E2 reliability fusion.
- Student receives the existing modality-dropout 0.15 training input.
- Student must be initialized from the same base/pretrained initialization convention used by E2, not from E5.
- Do not alter the E2 model source. Use a new training wrapper/script and non-invasive forward hooks or an equivalent wrapper to capture FPN outputs.

### Consistency loss
- Capture corresponding FPN feature maps from teacher and student at P3, P4, and P5.
- L2-normalize each feature map along channel dimension before comparison.
- Use smooth L1 or MSE feature consistency loss averaged over P3/P4/P5.
- Total loss: `L = L_detector + lambda_cons * L_cons`.
- Use `lambda_cons=0` for epochs 1–5, then linearly ramp to `0.05` by epoch 15 and keep `0.05` thereafter.
- Full-modality samples must not be removed; modality-dropout masks should use the current E2 convention.
- The consistency term is training-only and must add zero parameters and zero inference computation.

## Mandatory Tests
Before long training, `test_mscd.py` must produce `runs/mscd_smoke_test.md` and pass:
1. Teacher parameters receive no gradients.
2. Student parameters receive gradients from detector loss and consistency loss.
3. Hooks capture matching P3/P4/P5 shapes for teacher and student.
4. Consistency loss is finite for full and one missing-modality synthetic batch.
5. Inference output of the student is unchanged in structure relative to E2.
6. Parameter count of student equals E2 exactly.
7. Existing E0/E1/E2/E5 source files remain unmodified.

Do not start 50-epoch training unless all checks pass.

## Experiment E6
Train exactly one controlled run:

```powershell
python rarepdet/train_mscd.py --data D:\download\triair --train-split D:\download\triair\splits\train.txt --val-split D:\download\triair\splits\val.txt --teacher-weights runs/E2_reliability_dropout015_repvit_fcos_e50/weights/best.pt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --modality-dropout 0.15 --lambda-cons-max 0.05 --cons-warmup-epochs 5 --cons-ramp-end-epoch 15 --out runs/E6_mscd_dropout015_repvit_fcos_e50
```

If CUDA OOM occurs, rerun only with batch size 2 and document it.

After training:

```powershell
python rarepdet/eval_map.py --model reliability --data D:\download\triair --split-file D:\download\triair\splits\val.txt --weights runs/E6_mscd_dropout015_repvit_fcos_e50/weights/best.pt --img-size 640 --device cuda --batch-size 4 --score-thr 0.50 --out runs/E6_mscd_dropout015_repvit_fcos_e50/eval_thr050
python rarepdet/tools/eval_missing_modality.py --model reliability --data D:\download\triair --split-file D:\download\triair\splits\val.txt --weights runs/E6_mscd_dropout015_repvit_fcos_e50/weights/best.pt --img-size 640 --device cuda --batch-size 4 --score-thr 0.05 --out runs/E6_mscd_dropout015_repvit_fcos_e50/missing_modality
```

## Evidence Report
Create:
- `runs/mscd_evidence_summary.csv`
- `runs/mscd_evidence_report.md`

Compare E1, E2, E5, E6:

| Method | Extra inference params | Full AP50 | Full AP75 | P@0.50 | R@0.50 | F1@0.50 | w/o RGB AP50 | w/o Thermal AP50 | w/o Event AP50 | Mean Missing-Modality AP50 |

Required decision rule:
- E6 replaces E2 only if it retains full AP50 within 0.001 of E2 **and** improves mean missing-modality AP50, or if it improves full AP50/AP75 outright.
- Otherwise E2 remains the paper main model and E6 is reported only as a training-strategy ablation.
- Do not use a non-standard mean robustness value as the sole selection criterion.

## Completion
1. Update `docs/EXPERIMENT_STATUS.md`, `runs/handoff_latest.md`, and `.json`.
2. Create `runs/phase2c_report.md` summarizing E5 and E6 decisions.
3. Commit source code, docs, Markdown, CSV, TXT, and JSON only.
4. Never commit weights, datasets, npy files, images, or visual outputs.
5. Commit message: `Phase 2C: modality-subset consistency distillation`.
6. Push to `research/ra-repdet-triair`.
7. If blocked, create/update `docs/TASK_BLOCKER.md` with the exact failed command, final error, attempted fix, and smallest safe next action.