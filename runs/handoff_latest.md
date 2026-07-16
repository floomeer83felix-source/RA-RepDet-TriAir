# RA-RepDet-TriAir Handoff

Generated: 2026-07-16

## Current task

- V57 decision: `V57_PAIRED_SINGLE_SEED_FUSION_ABLATION_COMPLETE`.
- Starting commit: `6b767d0c23ca9b918edaed601ae999c9d9b0d6ee`.
- Equal and reliability superset runs completed exactly 7,187 steps each, 14,374 total, followed by one 1,845-row final-checkpoint evaluation each.
- Both variants used identical 6,645,011-parameter supersets, common initialization `846da59c...77cb9`, and sample order `27e98f75...bf27b`; alignment was enabled in both.
- Equal scorer remained dormant and unchanged. Reliability scorer was active and departed from exact uniform weights.

## Result

| Variant | AP50:95 | AP50 | AP75 | AR100 | Detections |
|---|---:|---:|---:|---:|---:|
| equal | 0.0 | 0.0 | 0.0 | 0.0 | 0 |
| reliability | 0.0 | 0.0 | 0.0 | 0.0 | 0 |
| reliability - equal | 0.0 | 0.0 | 0.0 | 0.0 | 0 |

Both evaluations covered 1,845 images and 4,198 GT boxes with finite outputs. Because both models produced zero detections above threshold `0.001`, this accuracy comparison is inconclusive and the zero deltas are not evidence of equivalence.

## Fusion diagnostics

- Equal weights remained exact uniform; entropy 1.0986123; scorer gradient 0; scorer state unchanged.
- Reliability devval mean RGB/IR/Event weights: 0.47120 / 0.26063 / 0.26817.
- Reliability entropy mean: 1.05764; dominance mean: 0.47120; RGB had maximum weight for all 1,845 rows.
- Reliability maximum weight-sum error: `1.19209e-7`; all weights were finite and within `[0,1]`.
- Scorer activity was confirmed, but no accuracy benefit can be inferred.

## Artifacts and checks

- Equal/reliability checkpoint SHA256: `d298e6cf4e901a5ad9a2961ecfbcf2592391e6fa237cd5f82d43594b8ceee142` / `b1322ce43e21e7eae2d646be85e0e43628432e79d1d376924fda6f782b05e5df`.
- Checkpoints remain under `D:\MM-UAV_v57_local` and were not committed.
- Pre/post tests: 10/10 pass; source hashes exact; protected production/history/V51/manuscript files unchanged.
- CUDA grid-sample backward and CuBLAS/linear operations emitted warn-only non-determinism notices.

## Required action

Stop. Do not change thresholds, rerun, tune, add seeds, or alter the experiment without a new explicit task. V57 does not authorize manuscript claims, public release, redistribution, or external sharing. V51 remains separate and unchanged.
