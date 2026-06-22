# Dropout-Ratio Ablation Summary

| Method | Dropout Ratio | P@0.50 | R@0.50 | F1@0.50 | Full AP50 | Full AP75 | w/o RGB AP50 | w/o Thermal AP50 | w/o Event AP50 | Mean Missing-Modality AP50 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E1 Reliability Fusion | 0.00 | 0.925721 | 0.962298 | 0.943655 | 0.979317 | 0.947634 | 0.688697 | 0.370994 | 0.477850 | 0.512514 |
| E3 Reliability + Dropout 0.10 | 0.10 | 0.949248 | 0.945341 | 0.947290 | 0.977738 | 0.945218 | 0.930783 | 0.723911 | 0.978295 | 0.877663 |
| E2 Reliability + Dropout 0.15 | 0.15 | 0.931057 | 0.956042 | 0.943384 | 0.979990 | 0.950906 | 0.948710 | 0.811566 | 0.978972 | 0.913083 |
| E4 Reliability + Dropout 0.20 | 0.20 | 0.946437 | 0.951268 | 0.948846 | 0.978692 | 0.948514 | 0.954897 | 0.872685 | 0.979640 | 0.935741 |

Footnote: Mean Missing-Modality AP50 is only the arithmetic mean of the three single-modality-missing AP50 values; it is a robustness summary, not a standard detection metric.

## Selection Rule

Selection uses full AP50/AP75 and the three single-modality-missing AP50 values. A value within 0.001 of the best value in a column is treated as tied; the mean missing-modality AP50 is reported as a summary only.

## Decision

- Selected default ratio: p=0.15 (E2 Reliability + Dropout 0.15).
- p=0.15 remains justified: Yes.
- E2 p=0.15 evidence: Full AP50=0.979990, Full AP75=0.950906, w/o RGB=0.948710, w/o Thermal=0.811566, w/o Event=0.978972.
