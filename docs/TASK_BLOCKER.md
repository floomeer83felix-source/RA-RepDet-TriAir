# Task Blocker

## Task

Execute `docs/V39_TASK_NOTES.md` on branch `research/ra-repdet-triair`: audit the candidate component-disjoint split, then only if the audit passes complete the missing V39 reliability `p=0.20` condition twice, aggregate two-run means, and run missing-channel plus efficiency evaluation for the selected reliability setting.

## Blocking Condition

The required pre-run split audit did not pass, so the V39 continuation gate is blocked before any new `p=0.20` training can start.

The generic train/validation split audit found no path overlap and no exact `.npy` byte duplicates, but returned `CAUTION: near-duplicate or adjacent-frame review required`. A V39-specific component-disjoint audit then failed the explicit continuation gate because the candidate split still contains same-family train/validation ID distances within the intended 16-frame guard band and exact RGB-content overlap between guard and train/validation partitions.

Key V39 component-disjoint audit results:

- train rows: 7439; validation rows: 2213; guard rows: 837.
- train/validation path overlap: 0.
- train/validation exact RGB-content overlap groups: 0.
- train/guard exact RGB-content overlap groups: 4.
- validation/guard exact RGB-content overlap groups: 5.
- same-family train/validation guard-band-16 violations: 353.
- minimum same-family train/validation ID distance: 1.
- component-disjoint audit status: FAIL.

Because `docs/V39_TASK_NOTES.md` says to complete new runs only if the audit passes, no `reliability_p020_seed*_e50` run was started, no training core file was modified, and the manuscript was not edited.

## Failed Command

```powershell
@'
# read-only V39 component-disjoint split audit using rarepdet.tools.split_audit_common
'@ | C:\Users\xinnan\.conda\envs\pytorch\python.exe -
```

The generic audit command that preceded it was:

```powershell
C:\Users\xinnan\.conda\envs\pytorch\python.exe rarepdet/tools/audit_split_integrity.py --data D:\download\triair --train-split E:\RepViT-main\runs\component_disjoint_candidates\candidate_component_disjoint_v1_train.txt --val-split E:\RepViT-main\runs\component_disjoint_candidates\candidate_component_disjoint_v1_val.txt --out runs\v39_component_disjoint_split_audit
```

## Last Error Lines

```text
train-val_exact_rgb_group_count: 0
train-guard_exact_rgb_group_count: 4
val-guard_exact_rgb_group_count: 5
same_family_train_val_guard_band_16_violations: 353
same_family_train_val_nearest_id_min: 1
same_family_train_val_nearest_id_p50: 32
component_disjoint_audit_status: FAIL
PASS requires counts, uniqueness, split disjointness, zero train-val exact RGB overlap, and zero same-family guard-band violations.
```

The preceding generic audit also reported:

```text
path_overlap_count: 0
exact_sha256_duplicate_pairs: 0
signature_distance_min: 0.000000
fraction_signature_distance_<=0: 0.000452
final_status: CAUTION: near-duplicate or adjacent-frame review required
```

## Attempted Fixes

- Ran the required branch switch and fast-forward pull before starting.
- Read `AGENTS.md`, `docs/PROJECT_CONTEXT.md`, `docs/EXPERIMENT_STATUS.md`, `docs/NEXT_TASK.md`, `docs/V39_TASK_NOTES.md`, and `docs/V39_COMPONENT_DISJOINT_COMPLETION_TASK.md`.
- Confirmed that current V39 artifacts include early, reliability `p=0.00`, and reliability `p=0.15`, but no completed reliability `p=0.20` condition.
- Ran the existing project split-integrity audit on the V39 candidate train/validation files.
- Ran a V39-specific component-disjoint audit for split counts, split uniqueness, path overlap, exact RGB-content overlap, and same-family guard-band violations.
- Wrote audit outputs under `runs/v39_component_disjoint_split_audit/`.
- Stopped before any new training because the audit did not pass.
- Did not modify protected training core files, model files, dataset code, manuscript files, checkpoints, raw data, labels, or final assets.

## Related Files

- `docs/V39_TASK_NOTES.md`
- `docs/V39_COMPONENT_DISJOINT_COMPLETION_TASK.md`
- `docs/TASK_BLOCKER.md`
- `runs/component_disjoint_candidates/candidate_component_disjoint_v1_train.txt`
- `runs/component_disjoint_candidates/candidate_component_disjoint_v1_val.txt`
- `runs/component_disjoint_candidates/candidate_component_disjoint_v1_guard_unchanged.txt`
- `runs/v39_component_disjoint_split_audit/split_integrity_summary.md`
- `runs/v39_component_disjoint_split_audit/split_integrity_summary.csv`
- `runs/v39_component_disjoint_split_audit/split_integrity_exact_duplicates.csv`
- `runs/v39_component_disjoint_split_audit/split_integrity_nearest_pairs.csv`
- `runs/v39_component_disjoint_split_audit/split_integrity_manual_review.csv`
- `runs/v39_component_disjoint_split_audit/component_disjoint_audit_summary.md`
- `runs/v39_component_disjoint_split_audit/component_disjoint_audit_summary.csv`
- `runs/v39_component_disjoint_split_audit/component_disjoint_exact_rgb_pairs.csv`
- `runs/v39_component_disjoint_split_audit/component_disjoint_guard_band_violations_sample.csv`

## Repair Option 1

Regenerate the component-disjoint candidate split with the same intended V39 validation-only design but enforce all continuation gates explicitly: train/validation/guard path disjointness, zero train/validation exact RGB-content overlap, zero guard/train and guard/validation exact RGB-content overlap if guard is treated as held-out exclusion evidence, and zero same-family train/validation ID distances within the chosen guard band. Rerun the audits, then start the two reliability `p=0.20` runs only after the replacement split passes.

## Repair Option 2

Keep the current candidate split as exploratory-only V39 evidence and explicitly relax the gate for adjacent-frame guard-band violations. This would allow `p=0.20` training to proceed, but the resulting evidence should be labeled validation-only and leakage-risk-qualified, not as component-disjoint confirmation. This option requires explicit user/research-owner approval before starting any new training.
