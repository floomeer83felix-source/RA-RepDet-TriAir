# V54 Training Summary

This engineering pilot completed exactly 200 optimizer steps with finite losses, gradients, parameters, affine theta, and sampling grids. Peak allocated/reserved memory was 354,884,608 / 394,264,576 bytes and mean step time was 0.7190 seconds.

At step 200, IR/Event theta maximum absolute deviations were 0.01609 / 0.04019, determinants were 1.00614 / 0.98230, and grid out-of-bounds fractions were 1.6875% / 1.5469%. No affine collapse was observed.

The seed and sample order are fixed. PyTorch emitted warn-only notices that CUDA `grid_sample` backward and some CuBLAS operations are not fully deterministic; this limitation is retained in the evidence. The pilot produced no AP/AR or accuracy claim.
