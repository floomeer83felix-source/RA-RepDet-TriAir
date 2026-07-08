# V41 Seed1 Paired Comparison

Generated: 2026-07-09T00:54:22

Comparison: reliability-aware p=0.15 seed1 minus matched early-fusion seed1 on the same frozen V40 development-validation split.

| Metric | Early | Reliability p=0.15 | Delta |
| --- | --- | --- | --- |
| Precision | 0.860109 | 0.877880 | +0.017770 |
| Recall | 0.910687 | 0.928754 | +0.018067 |
| F1 | 0.884676 | 0.902601 | +0.017925 |
| AP50 | 0.942953 | 0.955687 | +0.012734 |
| AP75 | 0.794412 | 0.877982 | +0.083570 |

Decision note: This is paired development-validation evidence only, not an independent-test, stability, significance, or manuscript-final claim.

Protocol note: one earlier reliability seed1 process terminated before completion and was archived locally under `runs/v41_q1_upgrade/seed1/reliability_p015_seed1_incomplete_attempt1_20260708`; its checkpoint and metrics were not used.
