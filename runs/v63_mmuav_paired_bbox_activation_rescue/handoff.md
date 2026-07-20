# V63 Handoff

Decision: `V63_RELU_COLLAPSE_REPRODUCED_SOFTPLUS_PRESERVES_THROUGH_STEP200`.

## Locked inputs

- Starting commit: `08783ed02856403d5cb0171f728f6244cef4bcd6`.
- Authorization-base/V62 completion commit: `286508ff34d4cd0ac494d803e5a146a686318f14`.
- Train manifest: `e81973b95dd6fd5ce2d3c5de526310a3bef083df49b8db584fdf39b78a34d67a`.
- Devval manifest: `113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54`.
- V57 order: `27e98f752d4707c862c41495420cd1776a9095ad0a010becff2035deef0bf27b`.
- First-200 prefix: `6345848e3287bea04f5c89927be7a714a6eed549a6b73d352779a6192b5c86ec`.
- Train/gradient/devval subsets: `d1d59950d62d7b7ed5bb54b54769d2e5af36c3084d933a65a88870a0abf7204c`, `bfb526aa632b916e61357e215d7ea2f77e2f55bed5db8f20d411703569561166`, `d622f6712a9bfb2faa596daa053ed207dded1a9227e80b4a10dd3b48ae3d51ee`.
- Common initialization: `846da59cc8d908dfeb429fca2acb4985e73ff5fda3915154f9f764c571977cb9`.

## Activation contract

Installed torchvision FCOS source SHA256 is
`dea8b8e029d4bde23b5b752eeeedfd7e0ec7e7ed894f50bdedd1207523912e88`.
The historical source location is `fcos.py:251`,
`nn.functional.relu(self.bbox_reg(bbox_feature))`. V63 replaced only that
shared training/inference activation with
`F.softplus(pre_activation, beta=1.0, threshold=20.0)` in the intervention.

Both step-0 state dictionaries, bbox pre-activation logits, classification
logits, centerness logits, and fused features were bit-identical. Only
post-activation bbox distances differed. State-dict keys, parameters, buffers,
historical four-element zero bbox bias, losses, matching, anchors, scales,
decode, clipping, fusion, and evaluator behavior were unchanged.

## Trace result

ReLU classifications at steps 0/1/2/3 were preserved; steps 5/10 were neither;
steps 15/20/30 were collapsed; step 50 was neither; and steps 100/150/200 were
collapsed. Its first strict collapse was step 15.

Softplus was `GEOMETRY_AND_GRADIENT_PRESERVED` at every trace step:
0/1/2/3/5/10/15/20/30/50/100/150/200. At step 200, ReLU versus Softplus valid
box counts were `0` versus `272,000` on train and `0` versus `272,000` on the
frozen devval subset. On train FPN level 0, ReLU derivative mean/exact-zero
fraction was `0.0271021 / 0.972898`; Softplus was `0.418230 / 0`.

## Execution and artifacts

- Optimizer steps: `200 + 200 = 400`; diagnostic backward calls: `104`.
- Verified local recovery snapshots: `26`; recovery events: `0`.
- ReLU checkpoint: `D:\MM-UAV_v63_local\v63_equal_relu_control_final_step200.pt`, SHA256 `ddd6b79e4695672c981f9083865f881c6b623ea818a3236e72acc691b148b2e6`.
- Softplus checkpoint: `D:\MM-UAV_v63_local\v63_equal_softplus_b1_t20_final_step200.pt`, SHA256 `6df9b915a2f520cbe1e51dc5ee962bd1e0b8fbb11465314377c9a3ba08a6269d`.
- All numerical and protected-file checks passed; V62 evidence remained byte-identical.
- Post-run tests: `11 / 11` passed.
- CUDA emitted a warn-only `grid_sampler_2d_backward_cuda` deterministic-implementation warning. `CUBLAS_WORKSPACE_CONFIG=:4096:8` was set.

This is single-seed early mechanistic evidence only. No full run, full devval,
AP/AR, tuning, threshold selection, checkpoint selection, extra seed, or rerun
was performed or authorized.
