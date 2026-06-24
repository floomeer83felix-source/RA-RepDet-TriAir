# Current Task

## Phase 4B — Controlled Seed Replication on the Clean Blocked Split

## Decision
Phase 4A is a valid clean-split pilot, not yet a reproducible final comparison. Its blocked split is integrity-checked, but the current training entry point has no explicit seed argument. Therefore, do not start 100-epoch training or manuscript drafting.

First add minimal, documented seed control to the training entry point. Then repeat the four core clean-split variants at two controlled seeds (`0` and `2`) using the frozen `block64_guard16_seed0` lists.

The former random-split experiments are historical diagnostics only. The Phase 4A B0/B1/B2/B4 results are pilot evidence and must not be merged with the controlled-seed results as though they used the same seed protocol.

## Read First
- `runs/phase4a_report.md`
- `runs/clean_block64g16_protocol.md`
- `runs/clean_block64g16_summary.md`
- `runs/phase3c_report.md`
- `docs/EXPERIMENT_STATUS.md`
- `runs/handoff_latest.md`

## Frozen Split
Use exactly these already-validated local list files:

```text
train: E:\RepViT-main\runs\blocked_split_candidates\block64_guard16_seed0_train.txt
val:   E:\RepViT-main\runs\blocked_split_candidates\block64_guard16_seed0_val.txt
guard: E:\RepViT-main\runs\blocked_split_candidates\block64_guard16_seed0_guard.txt
```

Required integrity values:

```text
train=7439, validation=2213, guard=837
exact RGB train/validation matches=0
same-family guard violations=0
```

Guard samples must never be passed to training or validation.

## Scope Restrictions
- Do not modify `datasets/triair_dataset.py` or any file under `rarepdet/models/`.
- Do not add an architecture, attention block, loss, distillation, augmentation, or new data split.
- Do not overwrite E0–E6 or B0/B1/B2/B4 pilot outputs.
- Do not run jobs in parallel.
- Do not commit weights, raw predictions, source images, npy files, or visual panels.

## Task 0 — Minimal reproducibility-only patch
The current `rarepdet/train_early_fusion.py` has no seed argument. Make only the following reproducibility changes to that file; do not change its model construction, optimizer, dataset semantics, loss, schedule, evaluation logic, or output checkpoint format.

1. Add `--seed` as an optional integer argument. It must default to `None` so legacy invocation remains valid.
2. When `--seed` is set, seed Python `random`, NumPy, PyTorch CPU, and all CUDA devices before model construction and DataLoader creation.
3. For seeded runs, set deterministic CuDNN behavior and disable CuDNN benchmarking. Use deterministic-algorithm warning mode rather than failing a long run on a known nondeterministic CUDA op.
4. Seed the shuffled training DataLoader with an explicit `torch.Generator`; add a worker initializer compatible with `num_workers > 0` even though this phase uses 0 workers.
5. Log the requested seed and determinism settings to `config.txt` and `train_log.txt`.
6. Preserve legacy behavior when no seed is supplied.

Create `rarepdet/tools/test_seed_reproducibility.py` and run it before long training. Generate `runs/seed_reproducibility_smoke.md` with all required checks:
- same seed gives identical initial model-state SHA256 twice;
- seed 0 and seed 2 give different initial model-state SHA256;
- same seed gives identical first 32 shuffled training indices twice;
- config/log output records the seed;
- the clean split integrity values above still match.

Do not start long training unless every check passes. If the patch changes model parameter count or changes legacy unseeded command behavior, stop and create `docs/TASK_BLOCKER.md`.

## Task 1 — Train controlled clean-split matrix
Run all eight jobs sequentially. All jobs are 50 epochs, 640 image size, `lr=1e-4`, `batch-size=4`, `num-workers=0`, and device CUDA. If and only if an individual job encounters CUDA OOM, rerun that same job once with `--batch-size 2` and document it. Do not change other hyperparameters.

### Seed 0
```powershell
python rarepdet/train_early_fusion.py --model early --data D:\download\triair --train-split E:\RepViT-main\runs\blocked_split_candidates\block64_guard16_seed0_train.txt --val-split E:\RepViT-main\runs\blocked_split_candidates\block64_guard16_seed0_val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --seed 0 --out runs/R0_early_seed0_block64g16_e50

python rarepdet/train_early_fusion.py --model reliability --data D:\download\triair --train-split E:\RepViT-main\runs\blocked_split_candidates\block64_guard16_seed0_train.txt --val-split E:\RepViT-main\runs\blocked_split_candidates\block64_guard16_seed0_val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --seed 0 --modality-dropout 0.00 --out runs/R1_reliability_p000_seed0_block64g16_e50

python rarepdet/train_early_fusion.py --model reliability --data D:\download\triair --train-split E:\RepViT-main\runs\blocked_split_candidates\block64_guard16_seed0_train.txt --val-split E:\RepViT-main\runs\blocked_split_candidates\block64_guard16_seed0_val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --seed 0 --modality-dropout 0.15 --out runs/R2_reliability_p015_seed0_block64g16_e50

python rarepdet/train_early_fusion.py --model reliability --data D:\download\triair --train-split E:\RepViT-main\runs\blocked_split_candidates\block64_guard16_seed0_train.txt --val-split E:\RepViT-main\runs\blocked_split_candidates\block64_guard16_seed0_val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --seed 0 --modality-dropout 0.20 --out runs/R4_reliability_p020_seed0_block64g16_e50
```

### Seed 2
Run only after all seed-0 evaluations finish:

```powershell
python rarepdet/train_early_fusion.py --model early --data D:\download\triair --train-split E:\RepViT-main\runs\blocked_split_candidates\block64_guard16_seed0_train.txt --val-split E:\RepViT-main\runs\blocked_split_candidates\block64_guard16_seed0_val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --seed 2 --out runs/R0_early_seed2_block64g16_e50

python rarepdet/train_early_fusion.py --model reliability --data D:\download\triair --train-split E:\RepViT-main\runs\blocked_split_candidates\block64_guard16_seed0_train.txt --val-split E:\RepViT-main\runs\blocked_split_candidates\block64_guard16_seed0_val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --seed 2 --modality-dropout 0.00 --out runs/R1_reliability_p000_seed2_block64g16_e50

python rarepdet/train_early_fusion.py --model reliability --data D:\download\triair --train-split E:\RepViT-main\runs\blocked_split_candidates\block64_guard16_seed0_train.txt --val-split E:\RepViT-main\runs\blocked_split_candidates\block64_guard16_seed0_val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --seed 2 --modality-dropout 0.15 --out runs/R2_reliability_p015_seed2_block64g16_e50

python rarepdet/train_early_fusion.py --model reliability --data D:\download\triair --train-split E:\RepViT-main\runs\blocked_split_candidates\block64_guard16_seed0_train.txt --val-split E:\RepViT-main\runs\blocked_split_candidates\block64_guard16_seed0_val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --seed 2 --modality-dropout 0.20 --out runs/R4_reliability_p020_seed2_block64g16_e50
```

## Task 2 — Evaluate each controlled run
For each of R0/R1/R2/R4 at both seeds:
- evaluate full modality using the matching model type, selected `best.pt`, the frozen validation list, image size 640, batch size 4, and `score_thr=0.50` for P/R/F1;
- retain standard score-ranked AP50/AP75;
- output to `<RUN_DIR>/eval_thr050`.

For R1/R2/R4 at both seeds:
- run `rarepdet/tools/eval_missing_modality.py` on the frozen validation list;
- use `score_thr=0.05` and output to `<RUN_DIR>/missing_modality`.

Do not evaluate R0 under missing modalities in this phase.

## Task 3 — Build controlled-seed report
Create:
- `rarepdet/tools/build_clean_seed_replication_report.py`
- `runs/clean_block64g16_seed_replication.csv`
- `runs/clean_block64g16_seed_replication.md`
- `runs/phase4b_report.md`

Provide two tables.

### Per-run table
| Variant | Seed | Dropout Ratio | P@0.50 | R@0.50 | F1@0.50 | AP50 | AP75 | w/o RGB AP50 | w/o Thermal AP50 | w/o Event AP50 |

### Aggregate table
For each variant, report `mean`, `min`, `max`, and `range` across seeds 0 and 2 for Full AP50, Full AP75, F1, and each missing-modality AP50 where applicable.

Rules:
- All headline results must be from the frozen blocked split only.
- Report the Phase 4A B-runs only as exploratory pilots in an appendix note; never pool them with controlled-seed R-runs.
- Do not claim statistical significance from two seeds.
- Do not use arithmetic mean missing-modality AP50 as the sole selection criterion.
- State whether reliability fusion (R1) improves early fusion (R0) consistently at both seeds.
- State whether p=0.15 (R2) or p=0.20 (R4) leads full-modality AP50/AP75 and the three individual missing-modality conditions across seeds.

## Task 4 — Decision gate
`runs/phase4b_report.md` must end with exactly one decision:

1. `SELECT R2 AS CLEAN-SPLIT MAIN VARIANT` — only when R2 has the stronger or tied full-modality evidence and a clear relevant robustness advantage across both seeds.
2. `SELECT R4 AS CLEAN-SPLIT MAIN VARIANT` — only when R4 has the stronger or tied full-modality evidence and a clear relevant robustness advantage across both seeds.
3. `KEEP R2 AND R4 AS CO-EQUAL OPERATING POINTS` — when R2 is accuracy-first and R4 is robustness-first, or results differ materially by seed.
4. `STOP: REPRODUCIBILITY OR PROTOCOL PROBLEM` — when seeded execution, clean-split integrity, or result capture is invalid.

Do not start 100-epoch training in this phase. Do not create manuscript text yet.

## Status and Push
Update:
- `docs/EXPERIMENT_STATUS.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`

Commit only source code, Markdown, CSV, TXT, JSON, and documentation.

Commit message:
```text
Phase 4B: controlled seed replication on clean split
```

Push to `research/ra-repdet-triair`.

If blocked, create/update `docs/TASK_BLOCKER.md` with the exact failed command, final error, attempted fix, and smallest safe next action.