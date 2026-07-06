# V40 Four-Run Execution Task

## Authority

Run this task only after the compute-minimized amendment reports:

```text
V40_COMPUTE_MINIMIZED_CONTRACT_READY
```

Accepted amendment commit:

```text
92d8ddeb4659ba2281ae5f75e11dd5a81f084c9b
```

This task executes the only four full V40-v2 trainings required for the compute-minimized validation-only evidence path.

## Fixed runs

Run exactly once each:

```text
matched_early_seed0
matched_early_seed2
reliability_p015_seed0
reliability_p015_seed2
```

Do not run reliability p=0.00 or p=0.20.

Use only the command templates and hashes recorded in:

```text
reproducibility/v40_experiment_contract_v1/amendments/compute_minimized_v1/
```

Run root:

```text
runs/v40_expanded_adjacency_v2_compute_minimized/
```

## Before launch

For each run, verify and record:

- V40-v2 train manifest SHA-256 `f24117e3fec5833e06e20202f8ea05cbc2242b3977bcb791d95f2099c8b4133f`;
- V40-v2 validation manifest SHA-256 `722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f`;
- trainer SHA-256 and evaluator SHA-256 equal the amendment locks;
- actual launch interpreter, Python, CUDA, PyTorch, torchvision, timm, GPU, driver, and CUDA runtime;
- actual launch environment matches the frozen training environment or is explicitly reported as a blocking mismatch before training begins.

The amendment-generation runtime may differ from the training runtime. The full model runs must use the locked conda training environment and record its actual values.

## Training and standardized evaluation

- Train 50 epochs with the locked data pipeline, optimizer, schedule, augmentation policy, dropout p, seed, image size, batch size, learning rate, deterministic flags, and V40-v2 manifests.
- Within each run, retain the checkpoint selected by the frozen trainer rule only: `weights/best.pt` based on in-training validation AP50.
- After each successful training run, run the frozen standardized evaluator once against the V40-v2 validation manifest.
- Do not tune threshold, NMS, checkpoint, split, seed, epoch count, or any other setting after seeing results.
- Do not train an extra substitute run because a completed score is weak.

## Per-run evidence

Each run directory must contain source-controlled lightweight artifacts:

```text
config.json
launch_environment.json
manifest_and_code_hashes.json
training_status.json
standardized_eval/eval_results.txt
standardized_eval/eval_results.json
metrics_summary.json
checkpoint_sha256.txt
```

The metrics summary must state Precision, Recall, F1, AP50, AP75, GT boxes, prediction count, checkpoint SHA-256, standard evaluator path/hash, and output paths. Do not commit weights or raw predictions.

## Aggregate results

After all four standardized evaluations succeed, create:

```text
runs/v40_expanded_adjacency_v2_compute_minimized/v40_four_run_summary.csv
runs/v40_expanded_adjacency_v2_compute_minimized/v40_four_run_summary.json
runs/v40_expanded_adjacency_v2_compute_minimized/v40_four_run_summary.md
```

Report each run and two-run means for early and pre-specified reliability p=0.15, plus min/max range and standard deviation for AP50, AP75, F1, Precision, and Recall.

Required interpretation guardrail:

```text
p=0.15 was pre-specified before V40 results; no V40 dropout selection or sweep was performed.
```

Do not describe p=0.15 as V40-optimal.

## Stop conditions

Stop and write `V40_FOUR_RUN_EXECUTION_INCOMPLETE` if any run:

- uses a non-V40-v2 manifest;
- has a hash or runtime-environment mismatch not resolved before launch;
- lacks a complete 50-epoch training status;
- lacks standardized evaluation;
- produces a missing/unreadable checkpoint;
- differs from the frozen contract;
- fails technically.

A technical failure may be rerun only after its cause and correction are documented, and only if the correction does not alter the locked recipe. A completed low-scoring run is never rerun.

If all four pass, write:

```text
V40_FOUR_RUN_EXECUTION_COMPLETE
```

This unlocks a separate non-training task for synthetic channel removal, efficiency measurement, bootstrap inference, deterministic qualitative preparation, provenance, and readiness assessment. It does not unlock manuscript editing.

## Prohibitions

- Do not modify raw data, labels, models, loaders, trainer core, evaluator core, V40-v2 manifests, V38/V39 artifacts, or manuscript files.
- Do not use guard data, DroneVehicle, or external data.
- Do not perform robustness, profiling, bootstrap, or qualitative experiments in this task.
- Do not run `finish_task.ps1`.
- Do not touch the unrelated untracked DroneVehicle scripts.

## Commit

Commit only configs, hashes, environment records, status files, standardized evaluation results, summaries, and task scripts. Do not commit model weights, raw arrays, raw labels, or raw predictions.

Use:

```text
results: add V40 four-run comparison
```

## Final response

Return only:

1. Preflight hash and runtime-environment status for each run.
2. Per-run metrics and checkpoint hashes.
3. Two-run means and ranges for early and p=0.15.
4. Completion or incomplete status.
5. Output paths and commit SHA.
6. Confirmation that only the four authorized runs occurred and no prohibited assets changed.
