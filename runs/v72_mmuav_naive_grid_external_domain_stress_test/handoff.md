# V72 Handoff

Decision: `V72_MMUAV_NAIVE_GRID_EXTERNAL_DOMAIN_STRESS_TEST_COMPLETE`.

V72 completed the `zero-shot external-domain stress test on the exposed MM-UAV devval split using a naive normalized-grid five-channel adapter`.

The adapter reused V53 per-modality decoding and independent letterbox at 640 x 640, concatenated RGB + IR grayscale + event grayscale, and retained RGB annotation geometry. It does not establish physical RGB/IR/event pixel registration.

The fixed 8-row smoke pass succeeded. Early Fusion and RA-RepDet seeds 0, 1, and 2 each processed all 1,845 rows exactly once. Every checkpoint produced 184,500 finite, valid decoded predictions and one complete AP/AR record.

Mean AP@[.50:.95] was `9.48024e-9` for Early Fusion and `7.20800e-7` for RA-RepDet. Mean paired `RA-RepDet - Early Fusion` was `7.11320e-7`. AP75 was zero for all six checkpoints. The near-zero results are consistent with a severe domain/geometry mismatch under the naive unregistered-grid assumption; they must not be presented as physically registered, independent, blind, or official-test validation.

Total checkpoint inference time was 349.60 seconds and maximum peak GPU memory was 818.44 MiB. V72 focused tests and V52/V53 regressions passed 28/28 after execution. No training, adaptation, calibration, tuning, checkpoint substitution, extra variant, or rerun occurred.
