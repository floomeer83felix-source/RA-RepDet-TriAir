# M3OT supervised RGB+thermal result handoff

This directory contains the lightweight, Git-tracked outputs of the
user-authorized matched six-seed M3OT experiment. Both models trained from
scratch on official train and selected the best of 50 epochs by official val
AP50. This is supervised development validation, not zero-shot or a blind
test. The M3OT public test split was not used.

- `per_seed.csv`: six best-checkpoint COCO AP, AP50, AP75, AR100 plus fixed
  score >= 0.25, IoU >= 0.50 TP/FP/FN/precision/recall and checkpoint SHA256.
- `summary.csv`: model-wise mean and sample standard deviation over seeds.
- `paired_ap_differences.csv`: same-seed dynamic-minus-early AP differences.
- `experiment_report.md`: concise protocol and descriptive conclusion.
- `scene_provenance.json`: three val scenes selected before prediction review.

The audited paired train/val populations were 8,630/1,200 frames with
111,678/13,781 RGB-coordinate vehicle boxes. One train RGB frame lacking
thermal was excluded. Train and val manifest SHA256 values are respectively
`f759c1acd248b746c1fb1c3c21bf62824a00c7cfb78daaa0f94dcbab84ce9fb4`
and `760118b3aeb3d5c4e682656792a4e449823e8aaafadcd01f282a3b3eef9c9085`.
RGB and thermal are frame-paired but not perfectly pixel-aligned.

All six best checkpoints were re-evaluated with the training-time
deterministic CUDA/cuDNN settings. Their recomputed AP, AP50, AP75, and
AR100 exactly matched the saved best-epoch metrics. The local three-scene
comparison image is
`runs/m3ot_supervised_rgbt_v1/results/figures/three_scene_comparison.png`,
SHA256 `aa1a004e39784d204be4a3eb199d310405bc05fac45e057dbd2a645aa74b9495`.
Weights and rendered imagery remain local and are not redistributed here.

Dynamic-minus-early AP is positive for all three seeds, with paired mean
`+0.028421 +/- 0.011187` (sample SD). This is descriptive and does not
establish statistical significance or independent blind-test superiority.
At the fixed score threshold, seed-0 dynamic routing increases recall while
reducing precision; the per-seed operating-point counts are reported rather
than hidden.
