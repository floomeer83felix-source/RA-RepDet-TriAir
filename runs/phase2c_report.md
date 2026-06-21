# Phase 2C Report

Phase 2C evaluated MSCD as a training-only consistency-distillation strategy. E6 uses the same reliability-fusion inference architecture as E2, with zero extra inference parameters.

## E5 And E6 Decision Summary

- E5 ACRF: exact absent-modality alpha suppression, but full AP50/AP75 are below E2. Keep as an alpha-correctness ablation.
- E6 MSCD: does not meet the predefined replacement rule for E2.
- Recommended main model: E2 Reliability + Dropout 0.15.

## Evidence Table

| Method | Extra inference params | Full AP50 | Full AP75 | P@0.50 | R@0.50 | F1@0.50 | w/o RGB AP50 | w/o Thermal AP50 | w/o Event AP50 | Mean Missing-Modality AP50 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E1 Reliability Fusion | 0 | 0.979317 | 0.947634 | 0.925721 | 0.962298 | 0.943655 | 0.688697 | 0.370994 | 0.477850 | 0.512514 |
| E2 Reliability + Dropout 0.15 | 0 | 0.979990 | 0.950906 | 0.931057 | 0.956042 | 0.943384 | 0.948710 | 0.811566 | 0.978972 | 0.913083 |
| E5 ACRF + Dropout 0.15 | 48 | 0.978066 | 0.946602 | 0.938290 | 0.953737 | 0.945950 | 0.944019 | 0.846657 | 0.978531 | 0.923069 |
| E6 MSCD + Dropout 0.15 | 0 | 0.974990 | 0.945138 | 0.937297 | 0.949951 | 0.943582 | 0.941817 | 0.757718 | 0.962810 | 0.887448 |
