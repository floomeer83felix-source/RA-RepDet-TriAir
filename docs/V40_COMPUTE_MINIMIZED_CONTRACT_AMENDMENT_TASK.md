# V40 compute-minimized contract amendment

Do not start any V40 training yet.

The frozen contract at `reproducibility/v40_experiment_contract_v1/` passed its technical checks, but its run matrix and selection rule still describe the older eight-run dropout sweep. The active research plan is `docs/V40_COMPUTE_MINIMIZED_EVIDENCE_PLAN.md`, which requires a pre-specified four-run comparison.

Create an immutable amendment under:

```text
reproducibility/v40_experiment_contract_v1/amendments/compute_minimized_v1/
```

Read and hash:

- `docs/PRE_MANUSCRIPT_V40_MASTER_PLAN.md`
- `docs/V40_COMPUTE_MINIMIZED_EVIDENCE_PLAN.md`
- the existing V40 contract and validation files
- accepted V40-v2 manifests and audit

The amendment must preserve the existing contract as archival evidence but supersede it for launch scope.

Lock exactly four future runs:

```text
matched_early_seed0
matched_early_seed2
reliability_p015_seed0
reliability_p015_seed2
```

Use the existing frozen recipe unchanged. Use only V40-v2 manifests. The new output root is:

```text
runs/v40_expanded_adjacency_v2_compute_minimized/
```

State that p=0.15 is pre-specified from archived development evidence before any V40 result is viewed. It is not selected or optimized on V40. Early fusion is the matched comparator. Do not run p=0.00 or p=0.20.

Replace the old dropout-selection rule for this launch scope with:

```text
No V40 dropout selection is performed. The paper comparison is limited to matched early fusion versus the pre-specified reliability-aware p=0.15 configuration.
```

Create amended command templates and a validator that asserts:

- exactly four run IDs;
- only seeds 0 and 2;
- only early and reliability p=0.15 models;
- V40-v2 manifest hashes and evaluator hash match the original contract;
- all training/evaluation settings equal the original contract;
- no result, checkpoint, metric, loss, validation iteration, training, profiling, robustness, qualitative, manuscript, or external-data work occurs.

Write an amendment status report with exactly one of:

```text
V40_COMPUTE_MINIMIZED_CONTRACT_READY
V40_COMPUTE_MINIMIZED_CONTRACT_BLOCKED
```

Do not edit or delete the original contract. Do not run `finish_task.ps1`. Do not touch the unrelated DroneVehicle scripts.

Commit only amendment files, validators, command templates, and reports using:

```text
docs: amend V40 contract for four-run plan
```
