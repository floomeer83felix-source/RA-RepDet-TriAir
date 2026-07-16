# RA-RepDet-TriAir Handoff

Generated: 2026-07-16

## Current task

- V56 decision: `V56_THREE_SEED_PAIRED_ALIGNMENT_CONFIRMATION_COMPLETE`.
- Starting commit: `05a72b0df1377bb6dce2134da1d73297b29fefe9`.
- V56 added seed 1 and seed 2 only; V55 seed 0 was imported from committed evidence without retraining or reevaluation.
- Four new runs completed exactly 7,187 optimizer steps each, 28,748 total, in the frozen off/on seed-1 then off/on seed-2 order.
- Each final checkpoint was evaluated exactly once on all 1,845 devval rows.
- Data counts/hashes, seed-specific common initializations and permutations, paired configuration symmetry, finite outputs, and source locks passed.

## Metrics

| Seed | AP50:95 off/on/delta | AP50 off/on/delta | AP75 off/on/delta | AR100 off/on/delta |
|---:|---:|---:|---:|---:|
| 0 | 0.013269/0.048269/+0.035000 | 0.064421/0.192783/+0.128362 | 0.001565/0.007178/+0.005613 | 0.050119/0.098904/+0.048785 |
| 1 | 0.029785/0.040621/+0.010835 | 0.139596/0.175507/+0.035911 | 0.004252/0.003976/-0.000276 | 0.081658/0.097808/+0.016151 |
| 2 | 0.031501/0.036625/+0.005123 | 0.134648/0.161219/+0.026571 | 0.002882/0.002685/-0.000197 | 0.081968/0.098690/+0.016722 |

- AP50:95 off/on mean: 0.024852 / 0.041838; paired-delta mean: +0.016986; direction positive for 3/3 seeds.
- AP50 and AR100 directions were also positive for 3/3 seeds. AP75 was positive for only 1/3 seeds and is not directionally consistent.
- This is descriptive three-seed internal evidence only; no p-value or statistical-significance claim is made.

## Artifacts and checks

- Seed-1 common init/order SHA256: `03261341d1b3ceea8bf70b8727e40235017ea8a4810172fd7e1efa40ab4cab83` / `0c0dcf739cddae4f023f18aa29c88d392fd03b22b847af248108dd862c7a1f61`.
- Seed-2 common init/order SHA256: `48da2ab1d8b88339137855f672ab0c0230414b3504fc04329aaf8badb9b28fb8` / `0174175d811a59f677039d205e9cb70a108764f8c35c27e21f4750ef3448abb8`.
- Seed-1 off/on checkpoint SHA256: `161390717c83d74c43abe74230b355f9e63c513f8007a8b2eed66a2c8322e2e3` / `5acf026436f4a73d1f5065d2ddd02da7d68b66a91a70d77e44ecb28df3e58785`.
- Seed-2 off/on checkpoint SHA256: `3da4be90bce6603f2f9f8c7227c73fc959e69327278cb5b7d0e2f5e41e829f97` / `6733e5c18d469c31dd9ffaddf46ee4934ea19d7954b203e76dbbfdbe834e3dc9`.
- All outputs finite; post-run tests 9/9 pass; protected files unchanged. Checkpoints remain under `D:\MM-UAV_v56_local` and were not committed.
- CUDA grid-sample backward and some CuBLAS operations emitted warn-only non-determinism notices.

## Required action

Do not run further GPU work without a new explicit task. V56 does not authorize extra seeds, tuning, RA/reliability-fusion training, manuscript claims, public release, redistribution, or external sharing. V51 remains separate and unchanged.
