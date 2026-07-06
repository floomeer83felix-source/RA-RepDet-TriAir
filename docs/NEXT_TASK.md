# Current Task

## Title
V40 — Repair, Freeze, and Validate a Truly Component-Disjoint TriAir Split

## Goal
Repair the failed V39 candidate component-disjoint split before any new model training. Build and audit a deterministic split in which connected components induced by exact RGB-content identity and same-family temporal proximity cannot cross train, validation, or guard partitions. Only if the replacement split passes every strict gate may the task train and evaluate the missing R4 reliability model (`p=0.20`) for seeds `0` and `2` under the existing V39 protocol.

This task strengthens validation evidence; it does **not** replace the publication headline. The current manuscript headline remains R4 `p=0.20` on `block64_guard16_seed0`, seeds 0 and 2, until a later evidence-review decision explicitly changes it.

## Read First
1. `AGENTS.md` if it exists.
2. `docs/PROJECT_CONTEXT.md`
3. `docs/EXPERIMENT_STATUS.md`
4. `docs/TASK_BLOCKER.md`
5. `runs/handoff_latest.md`
6. `docs/V39_TASK_NOTES.md`
7. `docs/V39_COMPONENT_DISJOINT_COMPLETION_TASK.md`
8. `runs/v39_component_disjoint_summary.md`
9. `runs/component_disjoint_candidates/candidate_component_disjoint_v1_train.txt`
10. `runs/component_disjoint_candidates/candidate_component_disjoint_v1_val.txt`
11. `runs/component_disjoint_candidates/candidate_component_disjoint_v1_guard_unchanged.txt`
12. `rarepdet/tools/split_audit_common.py`
13. `rarepdet/tools/audit_split_integrity.py`
14. `rarepdet/train_early_fusion.py`
15. `rarepdet/eval_map.py`
16. `runs/manuscript_scientific_publishability_assessment.md`

## Frozen Assets
- Official manuscript headline remains R4 Reliability `p=0.20` on `block64_guard16_seed0`, controlled seeds `0` and `2`: F1@0.50 `0.920861`, AP50 `0.962495`, AP75 `0.891266`.
- The existing V39 candidate split is **failed evidence**, not an eligible training split: 7439 train, 2213 validation, 837 guard; zero train/validation exact RGB groups but 4 train/guard exact RGB groups, 5 validation/guard exact RGB groups, 353 same-family train/validation guard-band-16 violations, and minimum same-family train/validation ID distance of 1.
- V39 early, reliability `p=0.00`, and reliability `p=0.15` outputs remain historical candidate evidence only. Do not modify or overwrite them.
- Current model architecture, source data, labels, training implementation, evaluation implementation, frozen Tables 1--7, manuscript source, and existing publication headline are frozen.
- Existing V39 protocol for any permitted R4 completion: model `reliability`; modality dropout `0.20`; epochs `50`; image size `640`; batch size `4`; learning rate `0.0001`; workers `0`; deterministic seed settings; standardized `eval_map.py` metrics with detector score threshold `0.001`, metric score threshold `0.50`, NMS `0.6`, detections per image `100`.

## Allowed Files To Modify
- `docs/NEXT_TASK.md`
- `docs/UPCOMING_TASKS.md`
- `docs/TASK_BLOCKER.md`
- `docs/EXPERIMENT_STATUS.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`
- `runs/v40_component_disjoint/**`
- `runs/component_disjoint_v40/**`
- `runs/phase_v40_component_disjoint_report.md`
- `runs/phase_v40_component_disjoint_report.json`
- `rarepdet/tools/build_component_disjoint_split.py`
- `rarepdet/tools/audit_component_disjoint_split.py`
- `rarepdet/tools/generate_handoff.py`
- `rarepdet/tools/update_project_status.py`

## Forbidden Files To Modify
- `data/**`, `labels/**`, raw `.npy` samples, source dataset manifests, original split files, and any existing V39 candidate split or output.
- Checkpoints, weights, raw prediction dumps, image/video artifacts, and final PDFs. Keep all heavy artifacts local and out of Git.
- `datasets/**`, `rarepdet/data/**`, `rarepdet/models/**`, `rarepdet/train_early_fusion.py`, `rarepdet/eval_map.py`, and all other training/evaluation core code.
- `main.tex`, `main_sivp_snjnl.tex`, `submission/sivp/**`, tables, figures, references, author metadata, declarations, release files, and final submission assets.
- Do not alter the R4 manuscript headline, previously frozen clean-split values, or V39 historical outputs.
- Do not use network access, data mutation, force-push, branch rewrite, or concurrent GPU runs.

## Required Commands

### A. Start on the correct branch

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git status --short
```

If the fast-forward pull cannot proceed, do not reset, merge unrelated histories, or force-push. Record the blocker and stop.

### B. Repair and audit the split before GPU work

Implement deterministic CPU-only tools using `rarepdet/tools/split_audit_common.py` helpers. The split-builder must construct a transitive component graph over the complete local inventory using both of these undirected edge rules:

1. identical exact RGB-content SHA256; and
2. same parsed family (`frame` or `nframe`) with absolute numeric-ID distance less than or equal to 16.

Assign complete connected components, never individual samples, to train, validation, or guard. Aim for the existing counts 7439/2213/837, but do not break a component to force exact counts. If exact counts are infeasible, minimize deviation from the target proportions and report the component-size reason.

```powershell
python -m py_compile rarepdet/tools/build_component_disjoint_split.py rarepdet/tools/audit_component_disjoint_split.py rarepdet/tools/generate_handoff.py rarepdet/tools/update_project_status.py
python rarepdet/tools/build_component_disjoint_split.py --data D:\download\triair --target-train 7439 --target-val 2213 --target-guard 837 --guard-distance 16 --output-dir runs/component_disjoint_v40
python rarepdet/tools/audit_component_disjoint_split.py --data D:\download\triair --train-split runs/component_disjoint_v40/train.txt --val-split runs/component_disjoint_v40/val.txt --guard-split runs/component_disjoint_v40/guard.txt --guard-distance 16 --output-prefix runs/v40_component_disjoint/split_audit
```

The builder and auditor must report: complete inventory count; unique paths; component count; largest-component size; target and achieved partition counts; component allocation; pairwise path overlaps; pairwise exact RGB-content overlap groups; pairwise same-family distance-16 violations; minimum cross-partition same-family ID distance; component-crossing count; split SHA256 values; deterministic rerun consistency; and label/box inventory by split.

### C. Hard continuation gate

Do not start training unless the audit reports all of the following:

- all local samples are allocated exactly once to one of train, validation, or guard;
- zero pairwise path overlaps across train/validation/guard;
- zero pairwise exact RGB-content overlap groups across train/validation/guard;
- zero pairwise same-family distance-16 violations across train/validation/guard;
- zero connected components crossing partitions;
- deterministic rerun reproduces identical split SHA256 values; and
- no unresolved audit error.

If any condition fails, write the audit report, update `docs/TASK_BLOCKER.md`, handoff, and status, commit the CPU-only blocked result, and stop. Do not train.

### D. Conditional R4 completion after a passing audit only

Run exactly one GPU job at a time. Use the new V40 split and preserve all V39 settings.

```powershell
python rarepdet/train_early_fusion.py --model reliability --modality-dropout 0.20 --data D:\download\triair --train-split runs/component_disjoint_v40/train.txt --val-split runs/component_disjoint_v40/val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 0.0001 --num-workers 0 --seed 0 --out runs/v40_component_disjoint/reliability_p020_seed0_e50
python rarepdet/eval_map.py --model reliability --data D:\download\triair --split-file runs/component_disjoint_v40/val.txt --weights runs/v40_component_disjoint/reliability_p020_seed0_e50/weights/best.pt --img-size 640 --device cuda --batch-size 4 --num-workers 0 --detector-score-thr 0.001 --metric-score-thr 0.50 --nms-thresh 0.6 --detections-per-img 100 --out runs/v40_component_disjoint/reliability_p020_seed0_e50/standardized_eval/eval_results.txt

python rarepdet/train_early_fusion.py --model reliability --modality-dropout 0.20 --data D:\download\triair --train-split runs/component_disjoint_v40/train.txt --val-split runs/component_disjoint_v40/val.txt --epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 0.0001 --num-workers 0 --seed 2 --out runs/v40_component_disjoint/reliability_p020_seed2_e50
python rarepdet/eval_map.py --model reliability --data D:\download\triair --split-file runs/component_disjoint_v40/val.txt --weights runs/v40_component_disjoint/reliability_p020_seed2_e50/weights/best.pt --img-size 640 --device cuda --batch-size 4 --num-workers 0 --detector-score-thr 0.001 --metric-score-thr 0.50 --nms-thresh 0.6 --detections-per-img 100 --out runs/v40_component_disjoint/reliability_p020_seed2_e50/standardized_eval/eval_results.txt
```

### E. Conditional V40 aggregate and robustness package

Only after both standardized R4 evaluations complete, create CPU-only aggregate tables from the recorded CSV outputs. Run the same synthetic `w/o RGB`, `w/o Thermal`, and `w/o Event` conditions for each R4 seed using the established V39-compatible evaluation path. Record efficiency with the existing project profiling path, using the same checkpoint-selection and measurement conditions as prior results. Do not claim comparisons to V39 early/p=0.00/p=0.15 unless all variants use the same audited V40 split.

Finally run:

```powershell
python rarepdet/tools/generate_handoff.py
python rarepdet/tools/update_project_status.py
powershell -ExecutionPolicy Bypass -File rarepdet/tools/finish_task.ps1
```

## Required Outputs
- `runs/component_disjoint_v40/train.txt`, `val.txt`, and `guard.txt` only if a deterministic split can be built.
- `runs/component_disjoint_v40/split_manifest.csv` and `.json` with component IDs, allocated split, path, family, numeric ID, RGB hash, and provenance.
- `runs/v40_component_disjoint/split_audit.md`, `.csv`, and `.json`.
- `runs/phase_v40_component_disjoint_report.md` and `.json`.
- If and only if the audit passes: R4 seed-0 and seed-2 configs, standardized evaluation CSVs, a two-seed aggregate CSV/Markdown report, synthetic-missingness CSV/Markdown report, and efficiency report under `runs/v40_component_disjoint/`.
- Updated task blocker, experiment status, and handoff that clearly distinguish `blocked`, `audit-passed`, and `R4-completed` states.

## Acceptance Criteria
- The work occurs on `research/ra-repdet-triair` and the report records the starting commit SHA.
- The old V39 candidate is never overwritten or relabeled as passing.
- The V40 component graph uses both exact RGB identity and same-family distance-16 relations transitively.
- Training never begins before the strict audit passes.
- A blocked result is successful completion if the new split cannot meet all strict criteria; it must include quantified failure diagnostics and no GPU run.
- If training is reached, exactly two R4 p=0.20 runs use seeds 0 and 2, unchanged V39 hyperparameters, standardized evaluation, and no overlapping GPU jobs.
- No raw data, checkpoints, weights, prediction dumps, figures, manuscript files, tables, references, or submission metadata are committed.
- V40 evidence remains validation-only and separate from the official manuscript headline until an explicit later decision.

## Commit Message
`results: audit and complete V40 component-disjoint validation`

## Completion / Blocker Rule
A passing split audit is the gate for every GPU command in this task. If split repair cannot satisfy the strict component-disjoint criteria, commit the auditable blocked state and stop. If the audit passes but either R4 run or standardized evaluation fails, retain completed evidence, record the exact failed stage, do not substitute another checkpoint or seed, and stop. Do not edit the manuscript in this task.