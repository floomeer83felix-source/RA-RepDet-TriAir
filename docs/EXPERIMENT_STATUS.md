# Experiment Status

Updated: 2026-07-16

## Active task

`V56_THREE_SEED_PAIRED_ALIGNMENT_CONFIRMATION_COMPLETE`

## Outcome

V56 completed the authorized local/private seed-1 and seed-2 alignment pairs. Each of the four new runs consumed exactly 7,187 optimizer steps, for 28,748 new steps total. Every final checkpoint was evaluated exactly once on all 1,845 frozen devval rows. Frozen V55 seed 0 was imported from committed evidence and was not retrained or reevaluated.

## Frozen contracts

- RGB-supervised train/devval/total: 7,187 / 1,845 / 9,032; sequence overlap 0.
- Train SHA256: `e81973b95dd6fd5ce2d3c5de526310a3bef083df49b8db584fdf39b78a34d67a`.
- Devval SHA256: `113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54`.
- V55 seed-0 common-init/order SHA256: `91fec577380f895c932ffeb090bba7d376abc1ea1d97d568ae46901a7bbcb983` / `27e98f752d4707c862c41495420cd1776a9095ad0a010becff2035deef0bf27b`.
- Seed-1 common-init/order SHA256: `03261341d1b3ceea8bf70b8727e40235017ea8a4810172fd7e1efa40ab4cab83` / `0c0dcf739cddae4f023f18aa29c88d392fd03b22b847af248108dd862c7a1f61`.
- Seed-2 common-init/order SHA256: `48da2ab1d8b88339137855f672ab0c0230414b3504fc04329aaf8badb9b28fb8` / `0174175d811a59f677039d205e9cb70a108764f8c35c27e21f4750ef3448abb8`.
- Within each new pair, shared tensors were bit-identical at step 0 and alignment residual heads were exact identity/zero. Both training logs matched the seed-specific permutation exactly.

## Frozen configuration

All new runs used 320x320 input, batch 1, FP32 with AMP off, feature width 32, FPN width 128, RepViT-M0.9 without pretrained weights, FCOS, equal fusion, AdamW, LR `1e-4`, weight decay `1e-4`, and no scheduler, clipping, augmentation, workers, tuning, early stopping, checkpoint selection, or devval optimization. Within each seed pair, the only scientific difference was `alignment_enabled`.

## Per-seed metrics

| Seed | Variant | AP50:95 | AP50 | AP75 | AR100 |
|---:|---|---:|---:|---:|---:|
| 0 | off | 0.0132693 | 0.0644206 | 0.0015649 | 0.0501191 |
| 0 | on | 0.0482695 | 0.1927830 | 0.0071779 | 0.0989042 |
| 1 | off | 0.0297855 | 0.1395956 | 0.0042524 | 0.0816579 |
| 1 | on | 0.0406207 | 0.1755067 | 0.0039763 | 0.0978085 |
| 2 | off | 0.0315013 | 0.1346480 | 0.0028816 | 0.0819676 |
| 2 | on | 0.0366245 | 0.1612194 | 0.0026850 | 0.0986899 |

Signed on-minus-off deltas:

| Seed | AP50:95 | AP50 | AP75 | AR100 |
|---:|---:|---:|---:|---:|
| 0 | +0.0350002 | +0.1283623 | +0.0056130 | +0.0487851 |
| 1 | +0.0108352 | +0.0359110 | -0.0002761 | +0.0161505 |
| 2 | +0.0051233 | +0.0265714 | -0.0001966 | +0.0167222 |

## Descriptive aggregation

- AP50:95 off mean/sample SD: 0.0248520 / 0.0100676; on: 0.0418382 / 0.0059172; paired-delta mean/median: +0.0169862 / +0.0108352; positive seeds: 3/3.
- AP50 off mean/sample SD: 0.1128881 / 0.0420469; on: 0.1765030 / 0.0158053; paired-delta mean/median: +0.0636149 / +0.0359110; positive seeds: 3/3.
- AP75 off mean/sample SD: 0.0028996 / 0.0013439; on: 0.0046131 / 0.0023132; paired-delta mean/median: +0.0017134 / -0.0001966; positive seeds: 1/3.
- AR100 off mean/sample SD: 0.0712482 / 0.0182990; on: 0.0984675 / 0.0005807; paired-delta mean/median: +0.0272193 / +0.0167222; positive seeds: 3/3.
- AP50:95 direction was positive for all three seeds. AP75 was not directionally consistent.

## Execution diagnostics

- Seed-1 off/on checkpoint SHA256: `161390717c83d74c43abe74230b355f9e63c513f8007a8b2eed66a2c8322e2e3` / `5acf026436f4a73d1f5065d2ddd02da7d68b66a91a70d77e44ecb28df3e58785`.
- Seed-2 off/on checkpoint SHA256: `3da4be90bce6603f2f9f8c7227c73fc959e69327278cb5b7d0e2f5e41e829f97` / `6733e5c18d469c31dd9ffaddf46ee4934ea19d7954b203e76dbbfdbe834e3dc9`.
- Seed-1 off/on mean step time: 0.25675 / 0.25156 seconds; seed-2: 0.47808 / 0.46379 seconds.
- New-run peak allocated memory ranged from 337,644,544 to 354,884,608 bytes; peak reserved ranged from 367,001,600 to 396,361,728 bytes.
- At step 7,187, seed-1 alignment-on IR/event theta deviations were 0.15752 / 0.13644, determinants 0.83709 / 1.11859, and grid OOB fractions 0.03109 / 0.12250. Seed-2 values were 0.14591 / 0.05385, 0.88510 / 0.95242, and 0.03469 / 0.01703.
- All training and evaluation outputs were finite. Post-run CPU/source-lock tests: 9/9 pass. Protected production/history/V51/manuscript files were unchanged.
- CUDA grid-sample backward and some CuBLAS operations emitted warn-only non-determinism notices; this remains a reproducibility limitation.

## Authorization boundary

These three seeds provide descriptive internal confirmation of the AP50:95 direction only. They do not establish statistical significance and do not authorize further seeds, tuning, RA/reliability-fusion training, manuscript edits, public claims, release, redistribution, or external sharing. Heavy checkpoints remain local under `D:\MM-UAV_v56_local` and outside Git. V51 remains separate and unchanged.
