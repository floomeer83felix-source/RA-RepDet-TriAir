# Experiment Status

Updated: 2026-07-16

## Active task

`V57_PAIRED_SINGLE_SEED_FUSION_ABLATION_COMPLETE`

## Outcome

V57 completed the authorized local/private single-seed paired fusion experiment. `alignment_on_equal_superset` and `alignment_on_reliability_superset` each consumed exactly 7,187 optimizer steps, for 14,374 total. Each final checkpoint was evaluated exactly once on all 1,845 frozen devval rows. No rerun, tuning, early stopping, checkpoint selection, or devval optimization occurred.

The execution and fusion diagnostics passed, but the accuracy comparison is uninformative: both variants produced zero detections above the frozen detector threshold `0.001`, so AP50:95, AP50, AP75, and AR100 were all zero for both variants. Zero signed deltas must not be interpreted as evidence of fusion equivalence.

## Frozen contracts

- RGB-supervised train/devval/total: 7,187 / 1,845 / 9,032; sequence overlap 0.
- Train SHA256: `e81973b95dd6fd5ce2d3c5de526310a3bef083df49b8db584fdf39b78a34d67a`.
- Devval SHA256: `113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54`.
- V56 aggregation/decision/protocol SHA256: `fd0cad5f8c87e26fa82ad0cf13bd71bec9cb4b198a4b94e30bfc33f790dfd9cc` / `6514674b73c3694459e3abcdc4d32d2295536892737f9a1de2864b0d3851cf3b` / `4e5ec36ae220d62a282d515d67412ef42fb220d98b277221da8b980aa4104331`.
- V55/V56 evidence was read only and no historical experiment was executed.
- V57 common seed-0 initialization SHA256: `846da59cc8d908dfeb429fca2acb4985e73ff5fda3915154f9f764c571977cb9`.
- Shared 7,187-row order SHA256: `27e98f752d4707c862c41495420cd1776a9095ad0a010becff2035deef0bf27b`; both logs matched it exactly.

## Superset verification

- Both variants had identical parameter names, shapes, and bit-identical step-0 tensors.
- Total parameters: 6,645,011; reliability scorer parameters: 1,089; parameter-signature SHA256: `5a0cc8c89d500a484a13ec03db2e3e609be03f9801103e8ff5acdd09ffafd862`.
- Alignment was enabled in both variants and both alignment residual heads started at exact identity/zero.
- The reliability final layer started at exact zero. Both variants began with exact `[1/3, 1/3, 1/3]` weights and identical fused features.
- Equal active-gradient parameter count at step 1: 6,643,922; its scorer had no gradient and remained bit-identical to initialization.
- Reliability active-gradient parameter count at step 1: 6,645,011; its scorer received gradients and its weights departed from uniform.

## Frozen configuration

Both runs used seed 0, 320x320 input, batch 1, FP32 with AMP off, feature width 32, FPN width 128, RepViT-M0.9 without pretrained weights, FCOS, AdamW, LR `1e-4`, weight decay `1e-4`, no scheduler, clipping, augmentation, workers, tuning, early stopping, checkpoint selection, or devval optimization. The only scientific difference was whether the shared reliability scorer output was bypassed or used.

## Metrics

| Variant | AP50:95 | AP50 | AP75 | AR100 | Detections |
|---|---:|---:|---:|---:|---:|
| equal superset | 0.0 | 0.0 | 0.0 | 0.0 | 0 |
| reliability superset | 0.0 | 0.0 | 0.0 | 0.0 | 0 |
| reliability - equal | 0.0 | 0.0 | 0.0 | 0.0 | 0 |

Both evaluations processed 1,845 images and 4,198 RGB GT boxes with finite outputs. The zero-detection outcome makes the single-seed accuracy comparison inconclusive.

## Fusion diagnostics

- Equal remained exact `[0.33333334, 0.33333334, 0.33333334]`; scorer gradient norm was always 0; entropy was 1.0986123; normalization error was 0.
- Reliability step-7,187 sample weights were RGB/IR/Event `0.47209 / 0.26394 / 0.26398`; scorer gradient norm was 0.16405 at that trace and ranged approximately `0.000126–3.55335` over training.
- Reliability devval mean weights were `0.47120 / 0.26063 / 0.26817`; ranges were RGB `0.41859–0.49659`, IR `0.24268–0.28600`, Event `0.25824–0.29541`.
- Reliability devval entropy mean/range: `1.05764 / 1.04174–1.08276`; mean dominance fraction: 0.47120; RGB was maximum for all 1,845 rows; maximum normalization error: `1.19209e-7`.
- These diagnostics show the scorer was active and favored RGB, but they do not establish an accuracy benefit.

## Execution diagnostics

- Equal/reliability checkpoint SHA256: `d298e6cf4e901a5ad9a2961ecfbcf2592391e6fa237cd5f82d43594b8ceee142` / `b1322ce43e21e7eae2d646be85e0e43628432e79d1d376924fda6f782b05e5df`.
- Checkpoint sizes: 27,124,021 / 27,129,047 bytes; both remain local under `D:\MM-UAV_v57_local` and outside Git.
- Equal/reliability mean step time: 0.50077 / 0.48880 seconds.
- Peak allocated memory: 353,891,328 / 353,954,816 bytes; peak reserved: 396,361,728 bytes for both.
- Step-7,187 equal IR/Event theta deviations: 0.22089 / 0.08162; determinants: 1.05316 / 1.05412; grid OOB: 0.12750 / 0.09531.
- Step-7,187 reliability IR/Event theta deviations: 0.11438 / 0.35403; determinants: 0.97139 / 1.02618; grid OOB: 0.09078 / 0.14828.
- All losses, gradients, parameters, alignment values, fusion weights, predictions, and metrics were finite. Pre/post CPU/source-lock tests: 10/10 pass. Protected files were unchanged.
- CUDA grid-sample backward and CuBLAS/linear operations emitted warn-only non-determinism notices; this remains a reproducibility limitation.

## Authorization boundary

V57 is completed engineering and single-seed internal fusion evidence, but its accuracy result is inconclusive because both detector outputs were empty at the frozen threshold. No threshold change, rerun, additional seed, tuning, architecture change, RA/reliability-fusion extension, manuscript edit, public claim, release, redistribution, or external sharing is authorized. V51 remains separate and unchanged.
