# Experiment Status

Updated: 2026-07-15

## Active task

`V54_GPU_PILOT_PASS_READY_FOR_PAIRED_ALIGNMENT_ABLATION`

## V54 engineering verdict

The bounded private MM-UAV GPU verification pilot completed exactly 200 optimizer steps using the pre-registered `alignment_on_equal` variant. All smoke and primary-run losses, gradients, parameters, affine theta, and sampling grids remained finite. No OOM or contract violation occurred.

This is an engineering and numerical-stability result only. No AP/AR, model selection, accuracy comparison, or manuscript claim was produced.

## Frozen contract

- RGB-supervised train/devval/total: 7,187 / 1,845 / 9,032.
- Train manifest SHA256: `e81973b95dd6fd5ce2d3c5de526310a3bef083df49b8db584fdf39b78a34d67a`.
- Devval manifest SHA256: `113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54`.
- Optimization used only frozen train rows; sequence overlap and development-validation optimization leakage: 0.
- Primary configuration: seed 0, 320x320 branches, batch 1, FP32, AdamW, LR 1e-4, weight decay 1e-4, no scheduler/clipping/augmentation, 200-step hard limit.

## Integration and smoke matrix

- Integration: independent aligned/equal-fused features -> 1x1 projection to 3 channels -> 320x320 -> existing RepViT-M0.9-FPN-FCOS.
- RGB-only, alignment-off equal, alignment-on equal, and alignment-on reliability smoke variants all completed finite CUDA forward/backward passes with zero optimizer steps.
- Smoke peak allocated memory ranged from 261,751,808 to 300,924,416 bytes.

## Primary pilot

- Completed optimizer steps: 200/200.
- Loss first/last/min/max: 2.76808 / 2.44725 / 0.03139 / 2.95204. These are not accuracy metrics.
- Mean/min/max step time: 0.7190 / 0.5776 / 0.9808 seconds.
- Peak allocated/reserved memory: 354,884,608 / 394,264,576 bytes.
- Step-200 IR theta deviation/determinant/grid OOB: 0.01609 / 1.00614 / 1.6875%.
- Step-200 Event theta deviation/determinant/grid OOB: 0.04019 / 0.98230 / 1.5469%.
- Postrun four-sample devval inference-path smoke passed without AP/AR.

## Reproducibility and protection

- Sample order is seed-locked and hashed.
- PyTorch emitted warn-only notices that CUDA `grid_sample` backward and some CuBLAS operations are not fully deterministic.
- V54 CPU tests: 8/8 pass before and after GPU execution.
- Production TriAir files, V51 evidence, V52/V53 historical evidence, and manuscript/submission files are unchanged.
- GPU optimizer steps remain exactly 200; no further GPU work is authorized by V54.
- Local checkpoint metadata is recorded; the 27,104,577-byte checkpoint remains on D: and is not committed.
- The unresolved MM-UAV redistribution license remains a dissemination restriction.
