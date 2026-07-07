# V40 R4 Synthetic Missing-Modality Report

| Mode | AP50 Mean | AP50 Stdev | AP75 Mean | F1 Mean | Seed0 AP50 | Seed2 AP50 |
|---|---:|---:|---:|---:|---:|---:|
| event_only | 0.014163 | 0.007060 | 0.000381 | 0.005123 | 0.009171 | 0.019156 |
| full | 0.905095 | 0.000848 | 0.751747 | 0.860171 | 0.905695 | 0.904495 |
| no_event | 0.898558 | 0.002077 | 0.736471 | 0.856483 | 0.897090 | 0.900027 |
| no_rgb | 0.909699 | 0.000031 | 0.761876 | 0.863383 | 0.909721 | 0.909677 |
| no_thermal | 0.377464 | 0.015269 | 0.040594 | 0.421595 | 0.366667 | 0.388261 |
| rgb_only | 0.377355 | 0.010632 | 0.038548 | 0.422670 | 0.369837 | 0.384873 |
| thermal_only | 0.909995 | 0.000539 | 0.768866 | 0.863699 | 0.910376 | 0.909613 |

Synthetic masks were evaluated with the existing V39-compatible `eval_missing_modality.py` path and the V40 component-disjoint validation split.
