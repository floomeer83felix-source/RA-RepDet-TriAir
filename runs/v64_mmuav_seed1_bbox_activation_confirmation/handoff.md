# V64 Handoff

Decision: `V64_SEED1_RELU_CONTROL_COLLAPSE_NOT_REPRODUCED_WITHIN_200_STEPS`.

## Locked inputs and evidence

- Starting commit: `2d257de8dbc5164c3cd36b3d0b6dd1ef5c258c34`.
- Authorization-base/V63 completion commit: `83bb9351a5d0a6115d81047482e23fef5eed26bb`.
- V63 decision/safety/training-log/source-lock hashes: `2985ac382639dca8da6b3303b9e0e3fdb74bc6b54485de7c140f3f8dbda818bd`, `90f2a837e480d8947616ea60401805843487cf47541e50837522e766f7871e18`, `4b6e0ba9f89fe0314dff58a3a1b6ef9eefe021974643a384fe7e00a00c593dc9`, `489db6a090c8b38c4aa36c72bf238d116743ded91916ff006785ab382762776a`.
- Train/devval manifests: `e81973b95dd6fd5ce2d3c5de526310a3bef083df49b8db584fdf39b78a34d67a`, `113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54`.
- V57 order and V63 first-200 prefix: `27e98f752d4707c862c41495420cd1776a9095ad0a010becff2035deef0bf27b`, `6345848e3287bea04f5c89927be7a714a6eed549a6b73d352779a6192b5c86ec`.
- Train/gradient/devval subsets: `d1d59950d62d7b7ed5bb54b54769d2e5af36c3084d933a65a88870a0abf7204c`, `bfb526aa632b916e61357e215d7ea2f77e2f55bed5db8f20d411703569561166`, `d622f6712a9bfb2faa596daa053ed207dded1a9227e80b4a10dd3b48ae3d51ee`.

## Seed-1 initialization

Python, NumPy, CPU Torch, and all CUDA seeds were set to exact integer `1`
before constructing one CPU `V63BBoxActivationDetector(relu)`. Its complete
791-tensor state was atomically serialized once to
`D:\MM-UAV_v64_local\seed1_common_init.pt`, SHA256
`50612d58789b935ed8345494a7830a64d07b83c841ac9b6d24bcda3ea3f2c476`.
The artifact was round-trip verified and strictly loaded into two independent
models. No second candidate was generated and no trained checkpoint was used.

Both step-0 state dictionaries, bbox pre-activation logits, classification and
centerness logits, RGB/aligned-IR/aligned-event/fused features, fusion weights,
and alignment theta tensors were bit-identical. Historical bbox bias remained
exactly `[0, 0, 0, 0]`; only post-activation bbox distances differed.

## Activation and result

Installed torchvision FCOS source SHA256 is
`dea8b8e029d4bde23b5b752eeeedfd7e0ec7e7ed894f50bdedd1207523912e88`.
The native location is `fcos.py:251`,
`nn.functional.relu(self.bbox_reg(bbox_feature))`. The intervention used only
`F.softplus(pre_activation, beta=1.0, threshold=20.0)` in the same shared
training/inference head.

Both ReLU and Softplus were `GEOMETRY_AND_GRADIENT_PRESERVED` at every trace:
0/1/2/3/5/10/15/20/30/50/100/150/200. Neither had a first-collapse step; both
first met preservation at step 0.

At step 200, ReLU train/devval valid counts were `271,931 / 271,930` out of
272,000 each. Softplus counts were `272,000 / 272,000`. Train FPN level-0 ReLU
derivative mean/exact-zero fraction was `0.996676 / 0.00332397`; Softplus was
`0.427073 / 0`.

## Execution and artifacts

- Optimizer steps: `200 + 200 = 400`; diagnostic backward calls: `104`.
- Verified local recovery snapshots: `26`; recovery events: `0`.
- ReLU elapsed/peak allocated: `398.269 s / 581,344,256 bytes`.
- Softplus elapsed/peak allocated: `272.133 s / 582,654,976 bytes`.
- ReLU checkpoint: `D:\MM-UAV_v64_local\v64_seed1_equal_relu_control_final_step200.pt`, SHA256 `f8778088aec12a38ec288c6cfb2e683eac86788ae25a805939d7a95b6022c390`.
- Softplus checkpoint: `D:\MM-UAV_v64_local\v64_seed1_equal_softplus_b1_t20_final_step200.pt`, SHA256 `b2b74bb2d4f67dcb651e6348b5bc33ce056d630b03b33997938e2ef1bd210104`.
- All numerical, initialization, recovery, and protected-file checks passed; V63 evidence remained byte-identical.
- Post-run tests: `10 / 10` passed.
- CUDA emitted the expected warn-only `grid_sampler_2d_backward_cuda` deterministic-implementation warning. `CUBLAS_WORKSPACE_CONFIG=:4096:8` was set.

V64 does not confirm the V63 contrast because seed-1 ReLU did not collapse.
This bounded result indicates initialization sensitivity; it neither refutes
V63 nor establishes sole causality, final accuracy, generalization, or AP/AR.
No full run, full devval, tuning, checkpoint selection, extra seed, or rerun
was performed or authorized.
