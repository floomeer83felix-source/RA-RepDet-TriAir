# V66 Handoff

Decision: `V66_SEED1_FULLTRAIN_COMPLETE_NONZERO_AP`.

## Frozen contracts

- Starting commit: `72f4c936dfe1b7d1007aba56c9fe503c494e73f9`.
- Authorization base / V65 completion: `33609052b798a89fb8d3a1ab9351f8497e8f95d1`.
- Train/devval manifests: `7,187 / 1,845` rows; SHA256 `e81973b95dd6fd5ce2d3c5de526310a3bef083df49b8db584fdf39b78a34d67a` and `113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54`.
- Complete one-pass order SHA256: `27e98f752d4707c862c41495420cd1776a9095ad0a010becff2035deef0bf27b`.
- Train/gradient/devval subset SHA256 values: `d1d59950d62d7b7ed5bb54b54769d2e5af36c3084d933a65a88870a0abf7204c`, `bfb526aa632b916e61357e215d7ea2f77e2f55bed5db8f20d411703569561166`, and `d622f6712a9bfb2faa596daa053ed207dded1a9227e80b4a10dd3b48ae3d51ee`.
- Frozen V64 seed-1 initialization SHA256: `50612d58789b935ed8345494a7830a64d07b83c841ac9b6d24bcda3ea3f2c476`; strict reload and bit-exact round trip passed. No alternative candidate or trained checkpoint was used.
- Configuration SHA256: `506ce0f2f9af4ffc63571708b302e7beab95600450d5a645b5721a0ecdb4c08d`.
- Installed torchvision FCOS SHA256: `dea8b8e029d4bde23b5b752eeeedfd7e0ec7e7ed894f50bdedd1207523912e88`.
- COCO evaluator SHA256: `7d59ae82f07a399bb464362ab3e5e42096847eba761953555315c271dbd397e1`.
- V66 differed from V65 only by seed and frozen initialization state. It used exact `softplus(beta=1.0, threshold=20.0)` in the shared training/inference bbox-distance head.

## Training and audits

- Exactly `7,187 / 7,187` optimizer steps consumed `7,187` unique rows once in frozen order.
- All ten audits at steps `0, 15, 50, 200, 500, 1000, 2000, 4000, 6000, 7187` were `GEOMETRY_AND_GRADIENT_PRESERVED`.
- Diagnostic backward calls: `40 / 40`.
- Verified recovery snapshots: `19 / 19`; recovery events: `0`.
- Final train/devval compact geometry: `272,000 / 272,000` valid boxes on each subset, with zero degenerate and non-finite boxes.
- Final train FPN level-0 Softplus derivative mean: `0.5559732039`; exact-zero fraction: `0`. Matched derivative mean: `0.3198866788`; exact-zero fraction: `0`.
- Training elapsed `3,144.455 s`; mean step time `0.411501 s`; peak allocated/reserved CUDA memory `523,038,720 / 578,813,952` bytes.

## Seed-1 final-checkpoint-only evaluation

- Evaluation attempts: `1`; images/GT boxes: `1,845 / 4,198`.
- AP@[0.50:0.95]: `0.0030357792`.
- AP50: `0.0174066630`; AP75: `0.0003960396`.
- AR@1: `0.0109337780`; AR@10: `0.0180323964`; AR@100: `0.0195569319`.
- Predictions: `184,500`; zero-prediction images: `0`; non-finite prediction images: `0`.
- Evaluation elapsed `123.217 s` at `14.974 FPS`.

## Two-seed descriptive baseline

Values below are V65 seed-0 / V66 seed-1 / mean / sample standard deviation / absolute difference.

- AP@[0.50:0.95]: `0.0363043928 / 0.0030357792 / 0.0196700860 / 0.0235244622 / 0.0332686135`.
- AP50: `0.1493416683 / 0.0174066630 / 0.0833741656 / 0.0932921369 / 0.1319350053`.
- AP75: `0.0035733839 / 0.0003960396 / 0.0019847118 / 0.0022467217 / 0.0031773443`.
- AR@1: `0.0501429252 / 0.0109337780 / 0.0305383516 / 0.0277250539 / 0.0392091472`.
- AR@10: `0.0753692234 / 0.0180323964 / 0.0467008099 / 0.0405432592 / 0.0573368271`.
- AR@100: `0.0815388280 / 0.0195569319 / 0.0505478799 / 0.0438278191 / 0.0619818961`.

## Local-only checkpoint and safety

- Checkpoint: `D:\MM-UAV_v66_local\v66_seed1_equal_softplus_b1_t20_fulltrain_final_step7187.pt`.
- Checkpoint SHA256: `8be20d25128f92b65dd78f2fa49ec55f8b3870d59ae0dfba3717ec67724ca6cc`; bytes: `27,135,663`.
- All losses, gradients, parameters, geometry, predictions, metrics, recovery metadata, and isolation checks were finite and valid.
- V65 evidence and protected V40-V65/V51/manuscript/submission fingerprints remained unchanged.
- Post-run tests: `10 / 10` passed.

V65 and V66 establish a two-seed equal-fusion Softplus devval baseline with substantial initialization sensitivity. They do not establish superiority, independent-test performance, or a reliability-fusion contribution. No rerun, extra seed, tuning, checkpoint selection, or further GPU stage is authorized.
