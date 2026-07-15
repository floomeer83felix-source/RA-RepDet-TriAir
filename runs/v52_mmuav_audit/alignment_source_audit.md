# V52 Alignment Source Audit

Official OGAA uses learned deformable offsets or a trainable feature STN. The published fixed STN matrices are only global initialization; the provider does not supply the selected source pair, keypoints, detector settings, raw-grid conventions, annotation transform, or event calibration needed to reproduce a pixel-space registration. Temporal GMC, synchronization, resizing, and event crop expansion are not spatial calibration.

**Deterministic RGB/IR/event raw-grid transform: not found.**
