# Qualitative Cases Summary

Score threshold: 0.50

This report lists candidate validation images for paper qualitative panels. It records model-level TP/FP/FN summaries only; no images are committed.

## Selected Counts

- E0 miss, E2 hit: 5
- E1 miss, E2 hit: 5
- low-brightness E2-success case: 5
- representative E2 failure case: 5
- representative shared success case: 5

## Manifest Preview

| Category | Rank | Image ID | Brightness Group | GT Count | E0 TP/FP/FN | E1 TP/FP/FN | E2 TP/FP/FN |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E0 miss, E2 hit | 1 | 1261 | mid | 3 | 1/0/2 | 3/0/0 | 3/0/0 |
| E0 miss, E2 hit | 2 | 1866 | high | 4 | 2/0/2 | 3/0/1 | 4/0/0 |
| E0 miss, E2 hit | 3 | 1072 | low | 4 | 2/2/2 | 2/2/2 | 4/1/0 |
| E0 miss, E2 hit | 4 | 1860 | low | 2 | 1/0/1 | 1/0/1 | 2/0/0 |
| E0 miss, E2 hit | 5 | 756 | low | 2 | 1/0/1 | 1/0/1 | 2/0/0 |
| E1 miss, E2 hit | 1 | 188 | high | 4 | 4/0/0 | 2/0/2 | 4/0/0 |
| E1 miss, E2 hit | 2 | 1072 | low | 4 | 2/2/2 | 2/2/2 | 4/1/0 |
| E1 miss, E2 hit | 3 | 1860 | low | 2 | 1/0/1 | 1/0/1 | 2/0/0 |
| E1 miss, E2 hit | 4 | 756 | low | 2 | 1/0/1 | 1/0/1 | 2/0/0 |
| E1 miss, E2 hit | 5 | 1474 | low | 1 | 1/0/0 | 0/0/1 | 1/0/0 |
| low-brightness E2-success case | 1 | 1368 | low | 1 | 1/0/0 | 1/0/0 | 1/0/0 |
| low-brightness E2-success case | 2 | 304 | low | 1 | 1/0/0 | 1/0/0 | 1/0/0 |
| low-brightness E2-success case | 3 | 1356 | low | 2 | 2/0/0 | 2/0/0 | 2/0/0 |
| low-brightness E2-success case | 4 | 974 | low | 2 | 2/0/0 | 2/0/0 | 2/0/0 |
| low-brightness E2-success case | 5 | 1309 | low | 2 | 2/0/0 | 2/0/0 | 2/0/0 |
| representative shared success case | 1 | 1326 | low | 13 | 13/0/0 | 13/0/0 | 13/0/0 |
| representative shared success case | 2 | 683 | mid | 10 | 10/0/0 | 10/0/0 | 10/0/0 |
| representative shared success case | 3 | 1893 | high | 9 | 9/0/0 | 9/0/0 | 9/0/0 |
| representative shared success case | 4 | 604 | high | 9 | 9/0/0 | 9/0/0 | 9/0/0 |
| representative shared success case | 5 | 1970 | high | 9 | 9/0/0 | 9/0/0 | 9/0/0 |
| representative E2 failure case | 1 | 1612 | mid | 15 | 12/1/3 | 12/1/3 | 11/0/4 |
| representative E2 failure case | 2 | 2022 | mid | 14 | 12/3/2 | 12/1/2 | 11/0/3 |
| representative E2 failure case | 3 | 1649 | low | 14 | 12/1/2 | 13/2/1 | 12/3/2 |
| representative E2 failure case | 4 | 724 | high | 6 | 4/0/2 | 5/1/1 | 4/2/2 |
| representative E2 failure case | 5 | 1065 | mid | 3 | 2/0/1 | 2/2/1 | 1/2/2 |

## Proposed Figure Caption

Qualitative comparison of RepViT-FCOS variants on selected TriAir validation cases. Green boxes denote ground truth and red boxes denote predictions at score threshold 0.50; examples include missed detections recovered by the dropout-trained reliability model, low-brightness proxy successes, shared successes, and representative remaining failures.

Note: These examples are selected for qualitative illustration and should not be used as causal evidence for any single modality or scene factor.
