# Phase 4A Report

Generated: 2026-06-24T05:11:46

## Clean Split Protocol

- Protocol: `runs/clean_block64g16_protocol.md`
- Candidate: `block64_guard16_seed0`
- Former random-split results are historical diagnostics only and are not mixed into this table.
- This is single training-seed evidence; no statistical significance is claimed.

## Main Clean-Split Table

| Method | Dropout Ratio | Params | P@0.50 | R@0.50 | F1@0.50 | Full AP50 | Full AP75 | w/o RGB AP50 | w/o Thermal AP50 | w/o Event AP50 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B0 Early Fusion | NA | 6591609 | 0.920573 | 0.881436 | 0.900580 | 0.941521 | 0.835843 | NA | NA | NA |
| B1 Reliability p=0.00 | 0.00 | 6593293 | 0.920237 | 0.894986 | 0.907436 | 0.949001 | 0.875731 | 0.675841 | 0.355645 | 0.428863 |
| B2 Reliability p=0.15 | 0.15 | 6593293 | 0.912933 | 0.914634 | 0.913783 | 0.956423 | 0.879736 | 0.906801 | 0.748108 | 0.957883 |
| B4 Reliability p=0.20 | 0.20 | 6593293 | 0.903604 | 0.925644 | 0.914491 | 0.960244 | 0.885327 | 0.907047 | 0.738021 | 0.961505 |

## Comparisons

- B1 reliability fusion improves B0 early fusion by Full AP50 (0.949001 vs 0.941521); F1 is 0.907436 vs 0.900580.
- Full-modality AP50 leader: B4 (0.960244). AP75 leader: B4. F1 leader: B4. Missing-modality AP50 per-mode wins: B2=1, B4=2, ties=0; robustness leader by per-mode wins: B4.
- The dropout-ratio decision is not based on an arithmetic mean alone.

## Missing Outputs

- none

## Next Action

REPLICATE B2 AND B4 WITH SEED 2
