# Current Task

## Title

V46 COCO metrics and causal fusion ablations.

## Goal

Strengthen the SIVP evidence package by adding project-consistent COCO-style AP@[0.50:0.95] evaluation and causal fusion ablations, without using held-out guard results for model selection or tuning.

The task has two parts:

1. Add COCO-style AP metrics for the already fixed matched early and reliability-aware `p=0.15` seed0/seed1/seed2 checkpoints on the frozen V40 development-validation manifest and the locked V40 same-dataset guard manifest.
2. Run a minimal causal ablation package to separate, as much as practical, the contributions of stems, dynamic softmax gating, and modality dropout.

This is an evidence-generation task. Do not modify the SIVP manuscript text unless explicitly required for recording generated tables after the evidence is complete. Do not use guard results to tune, select, or discard models.

## Read First

1. `AGENTS.md`
2. `PROJECT_PROFILE.md`
3. `docs/PROJECT_CONTEXT.md`
4. `docs/EXPERIMENT_STATUS.md`
5. `docs/TASK_BLOCKER.md`
6. `docs/NEXT_TASK.md`
7. `runs/handoff_latest.md`
8. `runs/handoff_latest.json`
9. `runs/v42_locked_guard_heldout/heldout_guard_source_lock.md`
10. `runs/v42_locked_guard_heldout/heldout_guard_summary.md`
11. `runs/v42_locked_guard_heldout/heldout_guard_claim_boundary.md`
12. `runs/v41_q1_upgrade/interim_devval/three_seed_interim_devval_summary.md`
13. `runs/v41_q1_upgrade/interim_devval/interim_claim_boundary.md`
14. `submission/sivp/review/STRICT_REVIEWER_REPORT_V45.md`
15. `runs/v45_strict_review/STRICT_REVIEW_AND_COMPILE_REPORT.md`
16. `rarepdet/eval_map.py`
17. `rarepdet/metrics.py`
18. Existing training/evaluation entry scripts and configs needed to reproduce the fixed V40/V41 runs.

## Frozen Assets

- Active development-validation split: frozen V40 component-disjoint development-validation manifest.
- Locked same-dataset guard manifest: `runs/component_disjoint_v40/guard.txt`.
- V42 guard source lock and claim boundary are frozen.
- Existing fixed checkpoints for matched early and reliability-aware `p=0.15`, seed0/seed1/seed2, must remain unchanged.
- Existing V40/V41/V42 result packages must remain immutable except for new V46 cross-reference reports.
- Guard results must not be used for training, tuning, checkpoint reselection, threshold selection, dropout selection, or ablation selection.

## Allowed Files To Modify

- `docs/NEXT_TASK.md`
- `docs/EXPERIMENT_STATUS.md`
- `docs/TASK_BLOCKER.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`
- New directory: `runs/v46_coco_ablation/**`
- New or modified reporting/evaluation scripts under `rarepdet/tools/**`
- New or modified evaluation metric helpers under `rarepdet/metrics.py` or a new `rarepdet/coco_metrics.py` only if needed for COCO-style AP computation
- New ablation config files under `configs/**` only if the repository already uses that config pattern
- New review tables under `submission/sivp/tables/Table_10_*` or `Table_11_*` only after metrics are generated and source-locked
- New review notes under `submission/sivp/review/V46_*`

## Forbidden Files To Modify

- Raw data, labels, images, videos, `.npy` arrays, prediction caches not created by this task, secrets, or checkpoints.
- Existing V40/V41/V42 source-lock files, manifests, metrics CSV/JSON/MD, or checkpoint hashes.
- Existing training data splits or guard manifest.
- Any model-selection result based on guard performance.
- SIVP main manuscript narrative files unless the generated evidence is complete and the change is limited to adding a clearly bounded future-ready evidence table or note.
- Repository default branch, release metadata, archive DOI, or public data-governance claims unless explicitly authorized by the user.

## Required Commands

### 1. Create V46 output directory and source lock

Create:

```text
runs/v46_coco_ablation/
```

Write a source lock before running new evaluation/training:

```text
runs/v46_coco_ablation/source_lock_v46.md
runs/v46_coco_ablation/source_lock_v46.json
```

The source lock must include:

- current commit SHA;
- branch name;
- training/dev-val/guard manifest paths and SHA256 values;
- evaluator script SHA256 values;
- checkpoint paths and SHA256 values for the six fixed baseline/main runs;
- exact environment summary;
- explicit statement that guard is not used for tuning or selection.

### 2. Add COCO-style AP@[0.50:0.95] evaluation

Implement or reuse a project-local COCO-style AP routine that computes at least:

- AP@[0.50:0.95] averaged over IoU thresholds 0.50:0.05:0.95;
- AP50;
- AP75;
- per-threshold AP values if practical.

Run it on the six fixed checkpoints:

- matched early seed0/seed1/seed2;
- reliability-aware `p=0.15` seed0/seed1/seed2.

Evaluate both:

- frozen V40 development-validation manifest;
- locked V40 guard manifest.

Save outputs:

```text
runs/v46_coco_ablation/coco_devval_per_run.csv
runs/v46_coco_ablation/coco_guard_per_run.csv
runs/v46_coco_ablation/coco_devval_paired_deltas.csv
runs/v46_coco_ablation/coco_guard_paired_deltas.csv
runs/v46_coco_ablation/coco_metric_summary.md
runs/v46_coco_ablation/coco_metric_summary.json
```

### 3. Run minimal causal ablations

Run ablations on the frozen V40 development-validation protocol first. Do not evaluate ablation variants on guard until the dev-val ablation package and checkpoint-selection rule are frozen.

Minimum ablation variants:

1. `matched_early`: existing matched early fusion baseline.
2. `ra_full_p015`: existing reliability-aware full model with modality dropout `p=0.15`.
3. `ra_no_moddrop`: reliability-aware stems + dynamic softmax gate with modality dropout disabled.
4. `ra_static_equal`: modality-specific stems with static equal-weight fusion, no dynamic gate.
5. `ra_stems_concat_or_project`: modality-specific stems with a deterministic learned projection but no dynamic gate, if implementation is straightforward.
6. `early_moddrop`: matched early fusion with training-time modality dropout, if implementation is straightforward and scientifically valid.

For any ablation variant that is not feasible without risky architecture surgery, write a blocker note explaining why and skip only that variant. Do not invent results.

Use seeds `0, 1, 2` if GPU/time allows. If GPU/time is insufficient, run seed0 first and write a partial-completion report with exact commands, runtime, and blocker details.

Training rules:

- Use the same training length, input size, optimizer, evaluator convention, and checkpoint-selection rule as the active V40/V41 comparison unless an explicit source-lock note explains why not.
- Select best checkpoint only by development-validation AP50 or the pre-existing project rule; do not use guard.
- After ablation checkpoints are frozen, optional guard evaluation may be run once and labelled as post-selection guard check.

Save outputs:

```text
runs/v46_coco_ablation/ablation_train_commands.txt
runs/v46_coco_ablation/ablation_devval_per_run.csv
runs/v46_coco_ablation/ablation_devval_summary.md
runs/v46_coco_ablation/ablation_devval_summary.json
runs/v46_coco_ablation/ablation_guard_per_run.csv        # only if guard is run after freezing
runs/v46_coco_ablation/ablation_guard_summary.md         # only if guard is run after freezing
runs/v46_coco_ablation/ablation_guard_summary.json       # only if guard is run after freezing
runs/v46_coco_ablation/ablation_claim_boundary.md
```

### 4. Claim scan and reporting

Run a scan over all new V46 reports for prohibited overclaims:

```text
external generalization
independent public benchmark
statistical significance
optimal dropout
calibrated sensor reliability
real sensor-fault robustness
COCO proof
```

Save:

```text
runs/v46_coco_ablation/v46_claim_scan.txt
runs/v46_coco_ablation/v46_claim_scan_review.md
```

### 5. Preflight checks

Run appropriate tests/preflight commands for any changed code. At minimum, run a smoke test for the COCO AP routine on a tiny known input or one short prediction file if available.

Save command outputs:

```text
runs/v46_coco_ablation/preflight_commands.txt
runs/v46_coco_ablation/preflight_outputs.txt
```

## Required Outputs

- `runs/v46_coco_ablation/source_lock_v46.md/json`
- COCO-style metric outputs listed above
- Ablation outputs listed above, or a precise partial-completion/blocker report
- `runs/v46_coco_ablation/v46_claim_scan.txt`
- `runs/v46_coco_ablation/v46_claim_scan_review.md`
- `runs/v46_coco_ablation/preflight_commands.txt`
- `runs/v46_coco_ablation/preflight_outputs.txt`
- Updated `docs/EXPERIMENT_STATUS.md`
- Updated `runs/handoff_latest.md`
- Updated `runs/handoff_latest.json`
- Updated `docs/TASK_BLOCKER.md` only if a real blocker appears

## Acceptance Criteria

- COCO-style AP@[0.50:0.95] is reported for the six fixed matched early / RA `p=0.15` seed0/1/2 checkpoints on development-validation and guard, or a precise blocker explains why it cannot be computed.
- Causal ablation variants are trained/evaluated on the frozen development-validation protocol, or infeasible variants are explicitly documented.
- Guard is not used for model selection, threshold tuning, dropout selection, or ablation selection.
- All outputs include exact commands, source locks, checkpoint hashes, manifest hashes, and claim boundaries.
- No raw data, existing checkpoints, existing evidence packages, or split manifests are modified.
- No claim of external generalization, statistical significance, optimal dropout, calibrated sensor reliability, real sensor-fault robustness, or COCO AP proof is introduced.
- If full seed0/1/2 ablation is not feasible, a partial result plus blocker report is committed rather than fabricated.

## Commit Message

`eval: add V46 COCO metrics and causal ablation evidence`

## Completion / Blocker Rule

On completion, update `docs/EXPERIMENT_STATUS.md`, `runs/handoff_latest.md`, and `runs/handoff_latest.json`; commit and push.

If COCO AP computation, ablation training, checkpoint discovery, GPU execution, or guard-boundary enforcement cannot be completed safely, write `docs/TASK_BLOCKER.md` with the exact file, command, observed issue, and minimal action needed. Commit and push the blocker state. Do not invent results, do not relax the claim boundary, and do not use guard results for tuning or selection.
