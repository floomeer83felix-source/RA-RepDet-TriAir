# Current Task

## Phase 2B — Availability-Conditioned Reliability Fusion (ACRF)

## Research Decision
Do not stack a generic attention or transformer block onto RA-RepDet. The observed E2 weakness is specific: under synthetic modality loss, the reliability gate can still allocate nonzero alpha to an absent stream. Build and evaluate one lightweight, literature-inspired correction: **Availability-Conditioned Reliability Fusion (ACRF)**.

ACRF must combine:
1. **post-stem availability masking**: a stream declared absent must become an exact zero feature after its stem, preventing convolution biases from creating phantom features;
2. **masked reliability softmax**: absent modalities receive a logit mask before softmax and therefore an alpha of exactly zero;
3. **availability-conditioned gate input**: append the three-bit modality-availability vector to the gate input.

This is a targeted extension of the project’s existing reliability fusion and modality-dropout training. It is not a copied generic module.

## Read First
- `AGENTS.md`
- `docs/PROJECT_CONTEXT.md`
- `docs/EXPERIMENT_STATUS.md`
- `runs/phase2a_report.md`
- `runs/missing_modality_summary.md`
- `rarepdet/tools/eval_missing_modality.py`

## Do Not Modify or Overwrite
- `runs/E0_early_repvit_fcos_e50`
- `runs/E1_reliability_repvit_fcos_e50`
- `runs/E2_reliability_dropout015_repvit_fcos_e50`
- `rarepdet/train_early_fusion.py`
- `rarepdet/models/early_fusion_fcos.py`
- `rarepdet/models/reliability_fusion_fcos.py`
- `datasets/triair_dataset.py`

Never commit data, weights, npy files, images, grids, or heavy visual output.

## Task 1 — Implement ACRF as new files only
Create:
- `rarepdet/models/availability_reliability_fusion_fcos.py`
- `rarepdet/train_availability_fusion.py`
- `rarepdet/tools/test_availability_fusion.py`
- `docs/ACRF_DESIGN.md`

Requirements:
- Reuse the existing RepViT-M0.9/FPN/FCOS construction and reliability-stem dimensions as far as possible.
- The model must accept the same 5-channel input convention: RGB[0:3], Thermal[3:4], Event[4:5].
- Use a batch-level `availability` tensor of shape `[B,3]` with the order RGB, Thermal, Event.
- During ordinary full-modality inference, availability is `[1,1,1]`.
- During modality-dropout training and missing-modality evaluation, use the exact dropout/masking convention already used by the project. For backward compatibility, when no availability tensor is supplied, derive it from exact all-zero modality input only; document this fallback as a synthetic-missing-mode assumption.
- After each modality stem, multiply features by availability so an absent stream is exactly zero.
- Before alpha softmax, replace unavailable logits with a very negative value; alpha for unavailable modalities must be numerically <= 1e-7.
- Return alpha and availability information for analysis without breaking torchvision FCOS train/eval return conventions.
- Use no cross-attention, no transformer, no additional detector heads, and no model-size increase larger than 0.03M parameters compared with E2.

## Task 2 — Mandatory correctness checks
`test_availability_fusion.py` must run CPU-safe checks and write `runs/acrf_smoke_test.md`.

Required checks:
1. Full mode alpha sums to 1 for every sample.
2. no_rgb: alpha_rgb <= 1e-7 and RGB post-stem feature energy is zero.
3. no_thermal: alpha_thermal <= 1e-7 and Thermal post-stem feature energy is zero.
4. no_event: alpha_event <= 1e-7 and Event post-stem feature energy is zero.
5. Full mode forward works for FCOS training loss and inference output.
6. Existing E0/E1/E2 source files remain byte-identical; report SHA256 before/after if feasible.

Do not begin any long training unless all six checks pass.

## Task 3 — Single controlled 50-epoch experiment E5
Only after Task 2 passes, train sequentially:

```powershell
python rarepdet/train_availability_fusion.py --data D:\download\triair --train-split D:\download\triair\splits\train.txt --val-split D:\download\triair\splits\val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --modality-dropout 0.15 --out runs/E5_acrf_dropout015_repvit_fcos_e50
```

If CUDA OOM occurs, rerun only with `--batch-size 2` and document the changed batch size.

After training, run:

```powershell
python rarepdet/eval_map.py --model availability_reliability --data D:\download\triair --split-file D:\download\triair\splits\val.txt --weights runs/E5_acrf_dropout015_repvit_fcos_e50/weights/best.pt --img-size 640 --device cuda --batch-size 4 --score-thr 0.50 --out runs/E5_acrf_dropout015_repvit_fcos_e50/eval_thr050
python rarepdet/tools/eval_missing_modality.py --model availability_reliability --data D:\download\triair --split-file D:\download\triair\splits\val.txt --weights runs/E5_acrf_dropout015_repvit_fcos_e50/weights/best.pt --img-size 640 --device cuda --batch-size 4 --score-thr 0.05 --out runs/E5_acrf_dropout015_repvit_fcos_e50/missing_modality
python rarepdet/tools/analyze_alpha_modes.py --model availability_reliability --data D:\download\triair --split-file D:\download\triair\splits\val.txt --weights runs/E5_acrf_dropout015_repvit_fcos_e50/weights/best.pt --img-size 640 --device cuda --batch-size 4 --out runs/E5_acrf_dropout015_repvit_fcos_e50/alpha_modes
```

## Task 4 — Evidence report
Create:
- `runs/acrf_evidence_summary.csv`
- `runs/acrf_evidence_report.md`

Compare E1, E2, and E5 using:

| Method | Params | Full AP50 | Full AP75 | P@0.50 | R@0.50 | F1@0.50 | w/o RGB AP50 | w/o Thermal AP50 | w/o Event AP50 | Mean Missing-Modality AP50 |

The report must explicitly answer:
1. Does E5 maintain or improve E2 full-modality AP50/AP75?
2. Does E5 improve the three missing-modality AP50 values, particularly w/o Thermal?
3. Are absent-modality alpha values actually zero in E5?
4. Is the parameter increase <=0.03M?
5. Should E5 replace E2 as the paper main model, or remain an ablation?

Use conservative wording. Do not claim a literature contribution until the evidence report supports it.

## Completion
1. Update `docs/EXPERIMENT_STATUS.md` and `runs/handoff_latest.md`.
2. Commit only source code, docs, Markdown, CSV, TXT, and JSON.
3. Commit message: `Phase 2B: availability-conditioned reliability fusion`.
4. Push to `research/ra-repdet-triair`.
5. If blocked, create `docs/TASK_BLOCKER.md` with the failed command, final error, attempted fix, and smallest safe next action.