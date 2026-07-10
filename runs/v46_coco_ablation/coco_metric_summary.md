# V46 COCO-style Metric Summary

Generated: 2026-07-10T22:28:48+08:00

Status: `V46_FIXED_COCO_EVALUATION_COMPLETE`

The six fixed matched-early and reliability-aware `p=0.15` checkpoints were evaluated with canonical `pycocotools` bbox evaluation at IoU 0.50:0.05:0.95, 101 recall samples, area=all, and maxDets=100. The detector candidate threshold remained 0.001.

COCO 101-point AP50/AP75 can differ slightly from the repository's prior all-point project-local AP50/AP75 even when predictions are identical.

## Frozen V40 development-validation

| Run | Variant | Seed | AP50:95 | AP50 | AP75 | AR100 | Precision@0.50 | Recall@0.50 | F1@0.50 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| matched_early_seed0 | matched_early | 0 | 0.705307 | 0.941146 | 0.837787 | 0.778882 | 0.909154 | 0.895517 | 0.902284 |
| matched_early_seed1 | matched_early | 1 | 0.663793 | 0.938505 | 0.791577 | 0.745389 | 0.860109 | 0.910687 | 0.884676 |
| matched_early_seed2 | matched_early | 2 | 0.671666 | 0.932084 | 0.797733 | 0.749037 | 0.928385 | 0.848475 | 0.886633 |
| reliability_p015_seed0 | ra_full_p015 | 0 | 0.727973 | 0.954003 | 0.891326 | 0.792535 | 0.933333 | 0.897222 | 0.914921 |
| reliability_p015_seed1 | ra_full_p015 | 1 | 0.722895 | 0.951538 | 0.874275 | 0.791154 | 0.877880 | 0.928754 | 0.902601 |
| reliability_p015_seed2 | ra_full_p015 | 2 | 0.695948 | 0.954695 | 0.853028 | 0.764019 | 0.921323 | 0.902165 | 0.911643 |

Paired deltas are reliability-aware `p=0.15` minus matched early fusion for the same seed.

| Seed | Delta AP50:95 | Delta AP50 | Delta AP75 | Delta AR100 |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 0.022666 | 0.012857 | 0.053539 | 0.013653 |
| 1 | 0.059103 | 0.013033 | 0.082698 | 0.045764 |
| 2 | 0.024282 | 0.022610 | 0.055295 | 0.014982 |

| Metric | Mean paired delta | Sample SD | Min | Max | n |
| --- | ---: | ---: | ---: | ---: | ---: |
| ap50_95 | 0.035350 | 0.020586 | 0.022666 | 0.059103 | 3 |
| ap50 | 0.016167 | 0.005581 | 0.012857 | 0.022610 | 3 |
| ap75 | 0.063844 | 0.016352 | 0.053539 | 0.082698 | 3 |
| ar100 | 0.024800 | 0.018168 | 0.013653 | 0.045764 | 3 |

## Locked same-dataset guard

| Run | Variant | Seed | AP50:95 | AP50 | AP75 | AR100 | Precision@0.50 | Recall@0.50 | F1@0.50 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| matched_early_seed0 | matched_early | 0 | 0.783497 | 0.959465 | 0.918522 | 0.837421 | 0.938534 | 0.942247 | 0.940387 |
| matched_early_seed1 | matched_early | 1 | 0.744436 | 0.950402 | 0.890116 | 0.803956 | 0.878990 | 0.936709 | 0.906932 |
| matched_early_seed2 | matched_early | 2 | 0.742402 | 0.952777 | 0.879077 | 0.804747 | 0.937147 | 0.920095 | 0.928543 |
| reliability_p015_seed0 | ra_full_p015 | 0 | 0.789917 | 0.962193 | 0.925621 | 0.842722 | 0.937451 | 0.936709 | 0.937080 |
| reliability_p015_seed1 | ra_full_p015 | 1 | 0.769254 | 0.959720 | 0.908858 | 0.829193 | 0.894619 | 0.946994 | 0.920061 |
| reliability_p015_seed2 | ra_full_p015 | 2 | 0.729749 | 0.966333 | 0.863011 | 0.792722 | 0.932243 | 0.946994 | 0.939560 |

Paired deltas are reliability-aware `p=0.15` minus matched early fusion for the same seed.

| Seed | Delta AP50:95 | Delta AP50 | Delta AP75 | Delta AR100 |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 0.006420 | 0.002728 | 0.007098 | 0.005301 |
| 1 | 0.024818 | 0.009318 | 0.018742 | 0.025237 |
| 2 | -0.012653 | 0.013556 | -0.016067 | -0.012025 |

| Metric | Mean paired delta | Sample SD | Min | Max | n |
| --- | ---: | ---: | ---: | ---: | ---: |
| ap50_95 | 0.006195 | 0.018737 | -0.012653 | 0.024818 | 3 |
| ap50 | 0.008534 | 0.005456 | 0.002728 | 0.013556 | 3 |
| ap75 | 0.003258 | 0.017719 | -0.016067 | 0.018742 | 3 |
| ar100 | 0.006171 | 0.018647 | -0.012025 | 0.025237 | 3 |

## Interpretation boundary

These are descriptive three-seed within-TriAir comparisons. The guard is a locked same-dataset held-out partition, not external data. It was not used for training, tuning, threshold selection, dropout selection, checkpoint selection, ablation selection, or run continuation decisions.
