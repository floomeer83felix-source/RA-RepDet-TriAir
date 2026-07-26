# V72 Naive-Grid External-Domain Stress-Test Summary

Scientific label: `zero-shot external-domain stress test on the exposed MM-UAV devval split using a naive normalized-grid five-channel adapter`.

| Method | Seed | AP@[.50:.95] | AP50 | AP75 | AR1 | AR10 | AR100 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| matched_early | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000048 |
| matched_early | 1 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000024 |
| matched_early | 2 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| reliability_p015 | 0 | 0.000000 | 0.000001 | 0.000000 | 0.000000 | 0.000000 | 0.000191 |
| reliability_p015 | 1 | 0.000002 | 0.000010 | 0.000000 | 0.000048 | 0.000048 | 0.000119 |
| reliability_p015 | 2 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

The adapter independently letterboxes each modality and does not establish physical RGB/IR/event pixel registration. The split was previously exposed and is not an independent or blind test.
