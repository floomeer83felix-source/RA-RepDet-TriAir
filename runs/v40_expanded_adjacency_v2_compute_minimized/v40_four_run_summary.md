# V40 Four-Run Summary

- Status: `V40_FOUR_RUN_EXECUTION_COMPLETE`
- Interpretation guardrail: p=0.15 was pre-specified before V40 results; no V40 dropout selection or sweep was performed.

## Per-Run Metrics

| Run | Precision | Recall | F1 | AP50 | AP75 | GT boxes | Predictions | Checkpoint SHA-256 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `matched_early_seed0` | 0.909154 | 0.895517 | 0.902284 | 0.945549 | 0.841093 | 5867 | 5779 | `23331a6e668634f5f1ca1c7dfaddd23e9ee5445c0558e325621e8f454a0b1602` |
| `matched_early_seed2` | 0.928385 | 0.848475 | 0.886633 | 0.936133 | 0.800439 | 5867 | 5362 | `b36b4965931da68b77a6be82e85e47b34f952445d64b941337f56a722f62737e` |
| `reliability_p015_seed0` | 0.933333 | 0.897222 | 0.914921 | 0.958361 | 0.895214 | 5867 | 5640 | `4284aaa188cb7f065a01b6cf32b78265ab937da0de2d3423d4594d2102787436` |
| `reliability_p015_seed2` | 0.921323 | 0.902165 | 0.911643 | 0.958777 | 0.856719 | 5867 | 5745 | `27affa96df1b3baad3df6f0a591e0599c1f5c0f77f91fad9fdaa408e549f1415` |

## Two-Run Aggregates

| Model group | Metric | Mean | Min | Max | Range | Std |
| --- | --- | --- | --- | --- | --- | --- |
| `matched_early` | `precision` | 0.918769 | 0.909154 | 0.928385 | 0.019231 | 0.009616 |
| `matched_early` | `recall` | 0.871996 | 0.848475 | 0.895517 | 0.047043 | 0.023521 |
| `matched_early` | `f1` | 0.894458 | 0.886633 | 0.902284 | 0.015651 | 0.007826 |
| `matched_early` | `ap50` | 0.940841 | 0.936133 | 0.945549 | 0.009416 | 0.004708 |
| `matched_early` | `ap75` | 0.820766 | 0.800439 | 0.841093 | 0.040654 | 0.020327 |
| `reliability_p015` | `precision` | 0.927328 | 0.921323 | 0.933333 | 0.012010 | 0.006005 |
| `reliability_p015` | `recall` | 0.899693 | 0.897222 | 0.902165 | 0.004943 | 0.002471 |
| `reliability_p015` | `f1` | 0.913282 | 0.911643 | 0.914921 | 0.003278 | 0.001639 |
| `reliability_p015` | `ap50` | 0.958569 | 0.958361 | 0.958777 | 0.000416 | 0.000208 |
| `reliability_p015` | `ap75` | 0.875967 | 0.856719 | 0.895214 | 0.038495 | 0.019247 |
