# M3OT supervised RGB+thermal comparison

Protocol: official M3OT train/val, from-scratch RepViT-FPN-FCOS,
matched seeds 0/1/2, 50 epochs, batch 4, 640x640, AdamW 1e-4/1e-4,
no augmentation; best checkpoint by val AP50. No public test use.

This is supervised external-dataset development, not zero-shot or a blind test.
The two cameras share frame IDs but are not perfectly pixel-aligned.

| Model | AP mean +/- sample SD | AP50 mean +/- sample SD | AP75 mean +/- sample SD | AR100 mean +/- sample SD |
| --- | ---: | ---: | ---: | ---: |
| early | 0.2095 +/- 0.0155 | 0.5028 +/- 0.0290 | 0.1239 +/- 0.0209 | 0.3482 +/- 0.0186 |
| reliability_rgbt | 0.2380 +/- 0.0156 | 0.5533 +/- 0.0128 | 0.1518 +/- 0.0231 | 0.3792 +/- 0.0142 |

Paired dynamic-minus-early AP by seed: +0.041268, +0.020828, +0.023166.
Mean paired delta: +0.028421 +/- 0.011187 (sample SD).
Fixed score >= 0.25, IoU >= 0.50 TP/FP/FN/P/R and all per-seed metrics are in per_seed.csv.
The three figure scenes were frozen before training or prediction review.
No unfavorable seed was removed, and no significance claim is made.
