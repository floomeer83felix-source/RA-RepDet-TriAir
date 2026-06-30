# Clean Qualitative Summary

Generated: 2026-06-27T01:35:08

These cases are illustrative only and are not cherry-picked to claim universal superiority.

Local panels are written under `runs/local_clean_qualitative_panels/` and are not committed.

## Counts

- R4 corrects R0 miss/localization failure: 5
- R4 failure/hard case: 5
- R4 missing-modality illustrative case: 5
- Shared successful detection: 5

## Manifest

| Category | Rank | Image Index | GT Count | Prediction Summary | Rationale |
| --- | --- | --- | --- | --- | --- |
| R4 corrects R0 miss/localization failure | 1 | 1074 | 12 | r0_full: TP=8 FP=0 FN=4 Pred=8; r4_full: TP=10 FP=0 FN=2 Pred=10 | R4 has fewer unmatched GT boxes than R0 at score threshold 0.50. |
| R4 corrects R0 miss/localization failure | 2 | 1077 | 12 | r0_full: TP=8 FP=0 FN=4 Pred=8; r4_full: TP=10 FP=0 FN=2 Pred=10 | R4 has fewer unmatched GT boxes than R0 at score threshold 0.50. |
| R4 corrects R0 miss/localization failure | 3 | 1080 | 12 | r0_full: TP=8 FP=1 FN=4 Pred=9; r4_full: TP=10 FP=0 FN=2 Pred=10 | R4 has fewer unmatched GT boxes than R0 at score threshold 0.50. |
| R4 corrects R0 miss/localization failure | 4 | 1081 | 12 | r0_full: TP=8 FP=1 FN=4 Pred=9; r4_full: TP=10 FP=0 FN=2 Pred=10 | R4 has fewer unmatched GT boxes than R0 at score threshold 0.50. |
| R4 corrects R0 miss/localization failure | 5 | 1113 | 13 | r0_full: TP=9 FP=0 FN=4 Pred=9; r4_full: TP=13 FP=0 FN=0 Pred=13 | R4 has fewer unmatched GT boxes than R0 at score threshold 0.50. |
| Shared successful detection | 1 | 659 | 9 | r0_full: TP=9 FP=0 FN=0 Pred=9; r4_full: TP=9 FP=0 FN=0 Pred=9 | Both R0 and R4 cover all GT boxes; this is a shared success example. |
| Shared successful detection | 2 | 660 | 9 | r0_full: TP=9 FP=0 FN=0 Pred=9; r4_full: TP=9 FP=0 FN=0 Pred=9 | Both R0 and R4 cover all GT boxes; this is a shared success example. |
| Shared successful detection | 3 | 661 | 9 | r0_full: TP=9 FP=0 FN=0 Pred=9; r4_full: TP=9 FP=0 FN=0 Pred=9 | Both R0 and R4 cover all GT boxes; this is a shared success example. |
| Shared successful detection | 4 | 668 | 9 | r0_full: TP=9 FP=0 FN=0 Pred=9; r4_full: TP=9 FP=0 FN=0 Pred=9 | Both R0 and R4 cover all GT boxes; this is a shared success example. |
| Shared successful detection | 5 | 640 | 8 | r0_full: TP=8 FP=0 FN=0 Pred=8; r4_full: TP=8 FP=0 FN=0 Pred=8 | Both R0 and R4 cover all GT boxes; this is a shared success example. |
| R4 failure/hard case | 1 | 1108 | 13 | r0_full: TP=10 FP=1 FN=3 Pred=11; r4_full: TP=9 FP=0 FN=4 Pred=9 | R4 retains at least one false positive or unmatched GT box; this is an illustrative hard case. |
| R4 failure/hard case | 2 | 1071 | 11 | r0_full: TP=8 FP=1 FN=3 Pred=9; r4_full: TP=8 FP=1 FN=3 Pred=9 | R4 retains at least one false positive or unmatched GT box; this is an illustrative hard case. |
| R4 failure/hard case | 3 | 1125 | 14 | r0_full: TP=10 FP=2 FN=4 Pred=12; r4_full: TP=11 FP=0 FN=3 Pred=11 | R4 retains at least one false positive or unmatched GT box; this is an illustrative hard case. |
| R4 failure/hard case | 4 | 1107 | 13 | r0_full: TP=10 FP=0 FN=3 Pred=10; r4_full: TP=10 FP=0 FN=3 Pred=10 | R4 retains at least one false positive or unmatched GT box; this is an illustrative hard case. |
| R4 failure/hard case | 5 | 1109 | 13 | r0_full: TP=10 FP=1 FN=3 Pred=11; r4_full: TP=10 FP=0 FN=3 Pred=10 | R4 retains at least one false positive or unmatched GT box; this is an illustrative hard case. |
| R4 missing-modality illustrative case | 1 | 263 | 5 | r4_full: TP=5 FP=1 FN=0 Pred=6; r4_no_rgb: TP=0 FP=1 FN=5 Pred=1 | Illustrates R4 behavior under synthetic no rgb input removal. |
| R4 missing-modality illustrative case | 2 | 867 | 4 | r4_full: TP=4 FP=0 FN=0 Pred=4; r4_no_rgb: TP=0 FP=5 FN=4 Pred=5 | Illustrates R4 behavior under synthetic no rgb input removal. |
| R4 missing-modality illustrative case | 3 | 1116 | 14 | r4_full: TP=13 FP=0 FN=1 Pred=13; r4_no_thermal: TP=7 FP=1 FN=7 Pred=8 | Illustrates R4 behavior under synthetic no thermal input removal. |
| R4 missing-modality illustrative case | 4 | 1957 | 5 | r4_full: TP=5 FP=0 FN=0 Pred=5; r4_no_thermal: TP=0 FP=4 FN=5 Pred=4 | Illustrates R4 behavior under synthetic no thermal input removal. |
| R4 missing-modality illustrative case | 5 | 3 | 3 | r4_full: TP=3 FP=0 FN=0 Pred=3; r4_no_event: TP=2 FP=0 FN=1 Pred=2 | Illustrates R4 behavior under synthetic no event input removal. |
