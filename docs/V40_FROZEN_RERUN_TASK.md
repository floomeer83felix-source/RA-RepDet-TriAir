# V40 frozen rerun task

## Goal

Run the complete core comparison on the approved V40 manifests. V40 is validation-only evidence under the expanded human-adjudicated adjacency component rule.

## Inputs

Use only:

- `reproducibility/v40_expanded_adjacency_component_split_v1/manifests/v40_expanded_adjacency_component_disjoint_train.txt`
- `reproducibility/v40_expanded_adjacency_component_split_v1/manifests/v40_expanded_adjacency_component_disjoint_val.txt`
- the existing V39 training and evaluation configuration as the frozen recipe.

Do not use the V39 or V40 guard manifest for model selection, performance reporting, or test claims.

## Fixed matrix

Run each condition twice with seeds 0 and 2:

1. matched early fusion
2. reliability-aware fusion, dropout 0.00
3. reliability-aware fusion, dropout 0.15
4. reliability-aware fusion, dropout 0.20

Use 50 epochs, image size 640, batch size 4, learning rate 1e-4, the existing optimizer/scheduler/data pipeline/evaluator, and the same standardized evaluation settings used by V39. Do not tune any setting from V40 validation results.

Create outputs under:

```text
runs/v40_expanded_adjacency/
  early_seed0_e50/
  early_seed2_e50/
  reliability_p000_seed0_e50/
  reliability_p000_seed2_e50/
  reliability_p015_seed0_e50/
  reliability_p015_seed2_e50/
  reliability_p020_seed0_e50/
  reliability_p020_seed2_e50/
```

## Required records

For every run, commit a config, standardized evaluation JSON/CSV, metrics summary, checkpoint SHA-256, train/validation manifest SHA-256, evaluator path/hash, environment record, and completion status. Weights may remain local and must not be committed.

Create:

```text
runs/v40_expanded_adjacency/v40_core_summary.csv
runs/v40_expanded_adjacency/v40_core_summary.md
runs/v40_expanded_adjacency/v40_core_summary.json
```

Report per run and two-run mean for Precision, Recall, F1, AP50, AP75, GT boxes, predictions, and checkpoint hash. Report run ranges or standard deviations as stability descriptors, not as selection criteria.

## Selection rule

After all eight runs complete, select one reliability setting using only:

1. highest two-run mean AP50;
2. then highest two-run mean F1;
3. then highest two-run mean AP75;
4. exact tie fallback: p=0.00, then p=0.15, then p=0.20.

Do not select from a single run. The matched early-fusion baseline is a comparator, not an eligible reliability-dropout selection.

## Prohibitions

- Do not edit data, labels, models, loaders, trainer core, evaluator core, V39/V40 manifests, guard files, or manuscript files.
- Do not use DroneVehicle or other external data.
- Do not run missing-modality, latency, profiling, or qualitative-result tasks yet.
- Do not claim independent testing, held-out testing, leakage-free data, verified temporal metadata, or real sensor-failure robustness.
- Do not run `finish_task.ps1`.
- Do not stage or touch the two unrelated untracked DroneVehicle scripts.

## Stop conditions

Stop and report `V40_CORE_RERUN_INCOMPLETE` if any of the eight runs fails, uses a non-V40 manifest, lacks standardized evaluation, or changes the frozen recipe. Do not retry selectively because of a weak score.

If all eight runs pass, report `V40_CORE_RERUN_COMPLETE`. This unlocks a separate task for selected-setting missing-channel and efficiency measurement; it does not unlock manuscript editing.

## Commit

Commit only source-controlled configs, run metadata, metrics artifacts, summaries, and scripts. Do not commit model weights, raw data, or checkpoints.

Use:

```text
results: add V40 frozen core rerun
```
