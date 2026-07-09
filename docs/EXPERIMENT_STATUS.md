# Experiment Status

Generated: 2026-07-09

## Current Status

`V42_LOCKED_HELDOUT_GUARD_EVALUATION_COMPLETE`

The V42 locked held-out guard evaluation is complete. Six fixed checkpoints were evaluated on the frozen V40 component-disjoint guard manifest: matched early fusion seed0/seed1/seed2 and reliability-aware fusion with modality dropout `p=0.15` seed0/seed1/seed2.

No training, hyperparameter tuning, checkpoint selection, split modification, robustness experiment, profiling run, manuscript edit, DroneVehicle work, or `finish_task.ps1` run was performed. The task used the user's explicit V42 guard-evaluation scope; `docs/NEXT_TASK.md` still describes the prior V41 manuscript task and was not used to expand scope.

## Evidence Inputs

- V42 source lock: `runs/v42_locked_guard_heldout/heldout_guard_source_lock.md/json`.
- V42 summary: `runs/v42_locked_guard_heldout/heldout_guard_summary.md/json`.
- V42 claim boundary: `runs/v42_locked_guard_heldout/heldout_guard_claim_boundary.md`.
- Guard source manifest: `runs/component_disjoint_v40/guard.txt`.
- Guard normalized LF SHA256: `9f871c16aa60b517ffd8df530782eed1befcd652969a9f94e5cd6af5ac2c8c2e`.
- Guard raw file SHA256 recorded by evaluator: `0cf3270c0a73d03caf8d698bb4e9ddb0adba46e688c52d8589f57ea12488881f`.
- Evaluator: `rarepdet/eval_map.py` SHA256 `94557cb80ae24b8663e9eb31955afe668b994058cd8e3e7618ae33e4c0017715`.
- Metrics helper: `rarepdet/metrics.py` SHA256 `6ffa798647376594befc45f89ebb1aa1a5fbe3b50e5f484e7804c22bac13b081`.

## Guard Source Clarification

The V42 source manifest is `runs/component_disjoint_v40/guard.txt`, which matches the normalized guard hash declared in `runs/component_disjoint_v40/split_manifest.json`.

`reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_guard_unchanged_archival.txt` has the same row count but different content and was not used for V42 evaluation.

## Fixed Checkpoints

| Run | Model | Seed | Checkpoint SHA256 | Source |
| --- | --- | ---: | --- | --- |
| matched_early_seed0 | early | 0 | `23331a6e668634f5f1ca1c7dfaddd23e9ee5445c0558e325621e8f454a0b1602` | V40 compute-minimized |
| matched_early_seed1 | early | 1 | `60a338ed887c15d94d3f274df39684c1dc6de68f9f29ba13f9f9cb4d6fbcd804` | V41 fresh paired seed1 |
| matched_early_seed2 | early | 2 | `b36b4965931da68b77a6be82e85e47b34f952445d64b941337f56a722f62737e` | V40 compute-minimized |
| reliability_p015_seed0 | reliability | 0 | `4284aaa188cb7f065a01b6cf32b78265ab937da0de2d3423d4594d2102787436` | V40 compute-minimized |
| reliability_p015_seed1 | reliability | 1 | `a59366dd0687754577d23d3e21358127199345d4ebf3a55a06472b933b57813d` | V41 fresh paired seed1 |
| reliability_p015_seed2 | reliability | 2 | `27affa96df1b3baad3df6f0a591e0599c1f5c0f77f91fad9fdaa408e549f1415` | V40 compute-minimized |

## Held-out Guard Descriptive Summary

Reliability-aware `p=0.15` minus matched early fusion, paired by seed:

| Metric | Mean delta | Sample SD | n seed pairs |
| --- | ---: | ---: | ---: |
| Precision | +0.003213 | 0.010920 | 3 |
| Recall | +0.010549 | 0.016220 | 3 |
| F1 | +0.006946 | 0.008943 | 3 |
| AP50 | +0.008562 | 0.006229 | 3 |
| AP75 | +0.002173 | 0.017305 | 3 |

Per-seed paired deltas:

| Seed | Precision | Recall | F1 | AP50 | AP75 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0 | -0.001084 | -0.005538 | -0.003307 | +0.001628 | +0.005322 |
| 1 | +0.015628 | +0.010285 | +0.013129 | +0.010372 | +0.017686 |
| 2 | -0.004904 | +0.026899 | +0.011018 | +0.013685 | -0.016491 |

## Claim Boundary

Allowed wording: locked held-out guard evaluation on the frozen V40 component-disjoint guard manifest, with descriptive three-seed paired comparisons between matched early fusion and reliability-aware `p=0.15`.

Disallowed wording: external dataset generalization, independent public benchmark test, training-time model selection or tuning using guard results, statistical significance, optimal dropout, calibrated physical sensor reliability, real sensor-fault robustness, or COCO AP@[0.50:0.95].

## Remaining Scientific Limitations

- The guard partition is within the TriAir project dataset, not an external dataset.
- The evidence is descriptive with three seed pairs only.
- The guard results must not be used for future model selection without rewriting the claim boundary.
- No causal ablation separates stems, dynamic gate, and modality dropout.
- No COCO mAP@[0.50:0.95] package is available.
- Dataset provider provenance remains only partially resolved by naming TriAir as public.
- Label-quality review remains incomplete.
