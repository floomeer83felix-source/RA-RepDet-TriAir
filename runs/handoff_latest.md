# RA-RepDet-TriAir Handoff

Generated: 2026-07-15

## Current task

- V55 decision: `V55_PAIRED_SINGLE_SEED_COMPLETE_METRICS_RECORDED`.
- Starting commit: `1dc5b48a4504e789bbe47e69153a71ac3b179532`.
- Frozen RGB-supervised train/devval/total: 7,187 / 1,845 / 9,032; hashes reproduced exactly; overlap 0.
- Common seed-0 initialization SHA256: `91fec577380f895c932ffeb090bba7d376abc1ea1d97d568ae46901a7bbcb983`; shared tensors bit-identical and identity alignment exact.
- Shared sample-order SHA256: `27e98f752d4707c862c41495420cd1776a9095ad0a010becff2035deef0bf27b`; both training logs matched all 7,187 rows exactly.
- Run order: `alignment_off_equal`, then `alignment_on_equal`; exactly 7,187 optimizer steps each and 14,374 total.
- Each final checkpoint was evaluated once on all 1,845 devval rows with no devval optimization, tuning, rerun, or checkpoint selection.

## Results

| Variant | AP50:95 | AP50 | AP75 | AR100 |
|---|---:|---:|---:|---:|
| alignment off | 0.0132693 | 0.0644206 | 0.0015649 | 0.0501191 |
| alignment on | 0.0482695 | 0.1927830 | 0.0071779 | 0.0989042 |
| on - off | +0.0350002 | +0.1283623 | +0.0056130 | +0.0487851 |

- Off checkpoint SHA256/bytes: `b18b8134a2afed117f00fc097e181fa8f4155f3bc7597739b04598c70ed6a026` / 27,111,161.
- On checkpoint SHA256/bytes: `2b4bf19c4ae8d160d5045bb85df17a065e25387313eb5539dfb328ddce76b258` / 27,110,306.
- Checkpoints remain under `D:\MM-UAV_v55_local` and were not committed.
- Off/on mean step time: 0.55987 / 0.47029 seconds; peak allocated memory: 337,644,544 / 354,884,608 bytes; peak reserved memory: 367,001,600 / 394,264,576 bytes.
- Step-7,187 alignment-on IR/event theta deviations: 0.18859 / 0.15319; determinants: 1.05793 / 1.13692; grid OOB: 0.13406 / 0.12953.
- All outputs finite; post-run CPU/source-lock tests 8/8 pass; source hashes exact; protected files unchanged.
- CUDA grid-sample backward and some CuBLAS operations emitted warn-only non-determinism notices.

## Required action

Do not run further GPU experiments without a new explicit task. The positive deltas are single-seed preliminary evidence only and do not authorize multi-seed confirmation, RA/reliability-fusion training, manuscript claims, or public redistribution. V51 remains separate and unchanged.
