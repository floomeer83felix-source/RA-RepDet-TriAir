# Experiment Status

Updated: 2026-07-15

## Active task

`V55_PAIRED_SINGLE_SEED_COMPLETE_METRICS_RECORDED`

## Outcome

V55 completed the authorized local/private paired MM-UAV experiment. `alignment_off_equal` and `alignment_on_equal` each consumed exactly 7,187 optimizer steps in the frozen order, for 14,374 total steps. Each final checkpoint was evaluated exactly once on all 1,845 frozen devval rows. No rerun, tuning, early stopping, checkpoint selection, or devval optimization occurred.

## Frozen data and initialization

- RGB-supervised train/devval/total: 7,187 / 1,845 / 9,032.
- Train SHA256: `e81973b95dd6fd5ce2d3c5de526310a3bef083df49b8db584fdf39b78a34d67a`.
- Devval SHA256: `113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54`.
- Train/devval sequence overlap: 0; IR-only excluded: 106; `UNLABELED` excluded: 35,898.
- Common seed-0 initialization SHA256: `91fec577380f895c932ffeb090bba7d376abc1ea1d97d568ae46901a7bbcb983`; 787 tensors; 27,041,394 bytes; shared tensors were bit-identical and alignment residual heads were exact identity/zero at step 0.
- Shared 7,187-row permutation SHA256: `27e98f752d4707c862c41495420cd1776a9095ad0a010becff2035deef0bf27b`; both logs matched it exactly.

## Frozen configuration

Both variants used seed 0, 320x320 input, batch 1, FP32 with AMP off, feature width 32, FPN width 128, RepViT-M0.9 without pretrained weights, FCOS, equal fusion, AdamW, LR `1e-4`, weight decay `1e-4`, no scheduler, clipping, augmentation, or workers. The only scientific difference was `alignment_enabled=false/true`.

## Final metrics

| Variant | AP50:95 | AP50 | AP75 | AR100 |
|---|---:|---:|---:|---:|
| `alignment_off_equal` | 0.0132693 | 0.0644206 | 0.0015649 | 0.0501191 |
| `alignment_on_equal` | 0.0482695 | 0.1927830 | 0.0071779 | 0.0989042 |
| signed delta (on - off) | +0.0350002 | +0.1283623 | +0.0056130 | +0.0487851 |

The AP50:95 direction is positive. This is single-seed preliminary evidence only, not a statistically confirmed or manuscript-ready claim.

## Execution and diagnostics

- Off checkpoint: `D:\MM-UAV_v55_local\alignment_off_equal_final_step7187.pt`, 27,111,161 bytes, SHA256 `b18b8134a2afed117f00fc097e181fa8f4155f3bc7597739b04598c70ed6a026`.
- On checkpoint: `D:\MM-UAV_v55_local\alignment_on_equal_final_step7187.pt`, 27,110,306 bytes, SHA256 `2b4bf19c4ae8d160d5045bb85df17a065e25387313eb5539dfb328ddce76b258`.
- Off/on mean step time: 0.55987 / 0.47029 seconds; peak allocated: 337,644,544 / 354,884,608 bytes; peak reserved: 367,001,600 / 394,264,576 bytes.
- All training and evaluation outputs were finite. At step 7,187, alignment-on IR/event theta max deviations were 0.18859 / 0.15319, determinants 1.05793 / 1.13692, and grid OOB fractions 0.13406 / 0.12953.
- Post-run CPU/source-lock tests: 8/8 pass. Four frozen source hashes reproduced exactly. Protected production/history/manuscript files were unchanged.
- CUDA grid-sample backward and some CuBLAS operations emitted warn-only non-determinism notices; this remains a reproducibility limitation.

## Authorization boundary

No additional GPU experiment, extra seed, RA/reliability-fusion training, manuscript edit, public claim, or redistribution is authorized by V55. V51 remains separate and unchanged. MM-UAV checkpoints and heavy artifacts remain local and outside Git.
