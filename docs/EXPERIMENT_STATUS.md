# Experiment Status

Updated: 2026-07-26

## Active task

`V72_MMUAV_EXISTING_DEVVAL_TRIAIR_NAIVE_GRID_EXTERNAL_DOMAIN_STRESS_TEST_AUTHORIZED`

## V71 completion evidence

V71 completed at commit `bfca2e21ca7a46a5087b3addfcac7dab9d7e1618` with:

`V71_BLOCKED_ADAPTER_OR_ONTOLOGY_CONTRACT`

V71 verified:

- frozen MM-UAV devval: `1,845` rows across `85` sequences;
- manifest SHA256: `113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54`;
- row-order SHA256: `dd454cfbafa39f2556628ad45dc191b39b0c54bb926028447d5f57553456e867`;
- modality/annotation presence: `1,845 / 1,845 / 1,845 / 1,845`;
- six frozen TriAir checkpoints: hashes matched and `6 / 6` strictly loaded on CPU;
- focused tests: `10 / 10` passed;
- V52/V53 regression tests: `18 / 18` passed.

No smoke inference, GPU evaluation, predictions, or AP/AR were produced because physical RGB/IR/event registration could not be established.

## Active V72 experiment

At the user's direction, provider/source/version/rights and calibration acquisition work will not delay the experiment. V72 freezes one naive normalized-grid adapter:

- reuse V53 per-modality decoding and independent letterbox;
- independently map RGB, IR, and event to `640 x 640`;
- concatenate RGB + IR grayscale + event grayscale into five channels;
- use RGB annotation geometry for boxes;
- use no physical registration, learned alignment, adaptation, calibration, or fitting.

V72 will run:

- Early Fusion seeds `0`, `1`, `2`;
- RA-RepDet `p=0.15` seeds `0`, `1`, `2`;
- exactly `1,845` rows per checkpoint;
- AP@[0.50:0.95], AP50, AP75, AR@1, AR@10, AR@100;
- seed-matched `RA-RepDet - Early Fusion` comparisons;
- descriptive mean, sample standard deviation, minimum, and maximum.

## Claim boundary

The result is a:

`zero-shot external-domain stress test on the exposed MM-UAV devval split using a naive normalized-grid five-channel adapter`

It is not an independent/blind external test and does not establish physical multimodal registration. Physical-registration uncertainty is an explicit limitation rather than a V72 blocker.

## Intended completion

`V72_MMUAV_NAIVE_GRID_EXTERNAL_DOMAIN_STRESS_TEST_COMPLETE`

Required completion commit:

`exp: run V72 MM-UAV naive-grid external-domain stress test`