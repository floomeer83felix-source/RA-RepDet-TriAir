# V50 Frozen-Checkpoint RGB-Only Stress Summary

Status: `QUARANTINED_PREMATURE_TEST_ACCESS`

The devval outputs remain reproducibility records, but the test outputs below were generated before all three dataset-specific RGB checkpoints were frozen. They are preserved as protocol-violation evidence and are not accepted V50 final test results. See `protocol_violation_evidence.json`.

This is an RGB-only domain-shift and controlled missing-modality stress test. RGB is scaled to `[0,1]`; thermal and event are appended as exact `0.0` channels. It is not tri-modal external validation or a physical sensor-failure simulation.

## Devval

| run | seed | AP@[.50:.95] | AP50 | AP75 | AR100 | APs | APm | APl |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| matched_early_seed0 | 0 | 0.001539 | 0.005015 | 0.000990 | 0.018844 | 0.000070 | 0.003750 | 0.009415 |
| matched_early_seed1 | 1 | 0.001472 | 0.005488 | 0.000857 | 0.024800 | 0.000433 | 0.004307 | 0.008925 |
| matched_early_seed2 | 2 | 0.006838 | 0.013788 | 0.009901 | 0.024366 | 0.000077 | 0.002834 | 0.018037 |
| reliability_p015_seed0 | 0 | 0.008115 | 0.018877 | 0.009973 | 0.029278 | 0.003630 | 0.011577 | 0.042199 |
| reliability_p015_seed1 | 1 | 0.005682 | 0.012639 | 0.004950 | 0.022048 | 0.000179 | 0.005172 | 0.016880 |
| reliability_p015_seed2 | 2 | 0.003266 | 0.008507 | 0.001856 | 0.019219 | 0.000520 | 0.005160 | 0.016378 |

## Test

| run | seed | AP@[.50:.95] | AP50 | AP75 | AR100 | APs | APm | APl |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| matched_early_seed0 | 0 | 0.000897 | 0.002097 | 0.001042 | 0.010293 | 0.000069 | 0.004186 | 0.002259 |
| matched_early_seed1 | 1 | 0.004421 | 0.008025 | 0.006601 | 0.012902 | 0.000207 | 0.001713 | 0.005524 |
| matched_early_seed2 | 2 | 0.003585 | 0.005586 | 0.004950 | 0.011880 | 0.000003 | 0.000835 | 0.005224 |
| reliability_p015_seed0 | 0 | 0.006410 | 0.010959 | 0.009901 | 0.015835 | 0.001574 | 0.006633 | 0.011599 |
| reliability_p015_seed1 | 1 | 0.004925 | 0.010284 | 0.001980 | 0.011682 | 0.000163 | 0.007072 | 0.007157 |
| reliability_p015_seed2 | 2 | 0.002661 | 0.005238 | 0.000660 | 0.009003 | 0.000497 | 0.006030 | 0.004495 |

## Paired Test Deltas

Across the three frozen seed pairs, RA minus matched early was `0.001698 +/- 0.003381` for AP@[.50:.95], `0.003591 +/- 0.004747` for AP50, and `-0.000017 +/- 0.007689` for AP75 (mean +/- sample SD). These descriptive differences are small in absolute terms and do not establish statistical significance.

The low absolute scores are retained as a negative/mixed transfer result and must not be hidden or reframed as broad external generalization.
