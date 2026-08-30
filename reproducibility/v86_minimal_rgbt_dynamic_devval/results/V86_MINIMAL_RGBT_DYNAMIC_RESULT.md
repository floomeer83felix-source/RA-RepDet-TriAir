# V86 Minimal RGB+Thermal Dynamic Devval Result

Status: **COMPLETE**

| Model | AP | AP50 | AP75 | AR100 |
|---|---:|---:|---:|---:|
| RGB+thermal dynamic | 0.6912 +/- 0.0280 | 0.9461 +/- 0.0028 | 0.8409 +/- 0.0241 | 0.7673 +/- 0.0232 |
| RGB+thermal+event dynamic | 0.7251 +/- 0.0121 | 0.9475 +/- 0.0003 | 0.8742 +/- 0.0081 | 0.7917 +/- 0.0098 |

The same-seed tri-modal minus two-modal AP differences are -0.0110, +0.0657, and +0.0471. The paired mean difference is +0.0339 with sample SD 0.0400; 2/3 seeds are positive.

This supports a descriptive mean event-associated improvement within the frozen
development-validation protocol, concentrated in AP75/AR rather than AP50. It does
not support a claim of uniform per-seed improvement, statistical significance,
independent testing, or general event utility outside this dataset.

No historical guard or V86 outer fold was accessed.
