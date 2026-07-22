# V65 Handoff

Decision: `V65_FULLTRAIN_COMPLETE_NONZERO_AP`.

## Frozen contracts

- Starting commit: `89cf93a3f0ac053a2a1f3ac217dbbc746a76ba72`.
- Authorization base / V64 completion: `402eabb23896f7908b6a3eccd4d394d3ce41d487`.
- Train/devval manifests: `7,187 / 1,845` rows; SHA256 `e81973b95dd6fd5ce2d3c5de526310a3bef083df49b8db584fdf39b78a34d67a` and `113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54`.
- Complete one-pass historical order SHA256: `27e98f752d4707c862c41495420cd1776a9095ad0a010becff2035deef0bf27b`.
- Train/gradient/devval audit-subset SHA256 values: `d1d59950d62d7b7ed5bb54b54769d2e5af36c3084d933a65a88870a0abf7204c`, `bfb526aa632b916e61357e215d7ea2f77e2f55bed5db8f20d411703569561166`, and `d622f6712a9bfb2faa596daa053ed207dded1a9227e80b4a10dd3b48ae3d51ee`.
- Historical seed-0 initialization SHA256: `846da59cc8d908dfeb429fca2acb4985e73ff5fda3915154f9f764c571977cb9`; strict reload and bit-exact state round trip passed. No trained checkpoint initialized V65.
- Configuration SHA256: `d67933dabb55929ab714eec2f2148e27a75013e81df4145df4ccaf56e509d73c`.
- Installed torchvision FCOS SHA256: `dea8b8e029d4bde23b5b752eeeedfd7e0ec7e7ed894f50bdedd1207523912e88`; native ReLU location `fcos.py:251`.
- V65 used only `F.softplus(pre_activation, beta=1.0, threshold=20.0)` in the shared training/inference bbox-distance head.
- COCO evaluator source SHA256: `7d59ae82f07a399bb464362ab3e5e42096847eba761953555315c271dbd397e1`.

## Training and audits

- Exactly `7,187 / 7,187` optimizer steps consumed `7,187` unique rows once in frozen order.
- All ten audits at steps `0, 15, 50, 200, 500, 1000, 2000, 4000, 6000, 7187` were `GEOMETRY_AND_GRADIENT_PRESERVED`.
- Diagnostic backward calls: `40 / 40`.
- Verified recovery snapshots: `19 / 19`; recovery events: `0`.
- Final train/devval compact geometry: `272,000 / 272,000` valid boxes for each subset, zero degenerate and zero non-finite boxes.
- Final train FPN level-0 Softplus derivative mean was `0.4882243881`, with exact-zero fraction `0`; matched-anchor derivative mean was `0.3154935222`, with exact-zero fraction `0`.
- Training elapsed `4,174.904 s`; mean optimizer-step time `0.548782 s`; peak allocated/reserved CUDA memory `523,202,560 / 578,813,952` bytes.

## Final-checkpoint-only devval evaluation

- Evaluation attempts: exactly `1`; evaluated images/GT boxes: `1,845 / 4,198`.
- AP@[0.50:0.95]: `0.0363043928`.
- AP50: `0.1493416683`; AP75: `0.0035733839`.
- AR@1: `0.0501429252`; AR@10: `0.0753692234`; AR@100: `0.0815388280`.
- Predictions: `184,500`; zero-prediction images: `0`; non-finite prediction images: `0`.
- Evaluation elapsed `204.214 s` at `9.035 FPS`; peak allocated/reserved CUDA memory `239,424,512 / 325,058,560` bytes.
- Fixed detector settings: score threshold `0.001`, NMS threshold `0.6`, maximum detections `100`. No threshold or checkpoint selection occurred.

## Local-only checkpoint and safety

- Final checkpoint: `D:\MM-UAV_v65_local\v65_seed0_equal_softplus_b1_t20_fulltrain_final_step7187.pt`.
- Checkpoint SHA256: `50ae3b6148742794f1c26f2d5733809736005cee8e86ea80ffccad9e2d96a5e7`; bytes: `27,135,663`.
- All losses, gradients, parameters, activations, geometry, predictions, metrics, and recovery metadata were finite.
- V63/V64 evidence, initialization, protected source, V51, manuscript, and submission fingerprints remained unchanged.
- Post-run tests: `10 / 10` passed.
- CUDA emitted the preregistered warn-only `grid_sampler_2d_backward_cuda` deterministic-implementation warning.

V65 is one seed-0 equal-fusion Softplus feasibility result. It establishes that this frozen path can complete one full pass and produce nonzero full-devval AP. It does not establish superiority over ReLU or reliability fusion, multi-seed generalization, independent-test performance, or a manuscript comparison claim. No rerun, extra seed, extra variant, tuning, or further GPU stage is authorized.
