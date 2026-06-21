# MSCD Evidence Report

| Method | Extra inference params | Full AP50 | Full AP75 | P@0.50 | R@0.50 | F1@0.50 | w/o RGB AP50 | w/o Thermal AP50 | w/o Event AP50 | Mean Missing-Modality AP50 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E1 Reliability Fusion | 0 | 0.979317 | 0.947634 | 0.925721 | 0.962298 | 0.943655 | 0.688697 | 0.370994 | 0.477850 | 0.512514 |
| E2 Reliability + Dropout 0.15 | 0 | 0.979990 | 0.950906 | 0.931057 | 0.956042 | 0.943384 | 0.948710 | 0.811566 | 0.978972 | 0.913083 |
| E5 ACRF + Dropout 0.15 | 48 | 0.978066 | 0.946602 | 0.938290 | 0.953737 | 0.945950 | 0.944019 | 0.846657 | 0.978531 | 0.923069 |
| E6 MSCD + Dropout 0.15 | 0 | 0.974990 | 0.945138 | 0.937297 | 0.949951 | 0.943582 | 0.941817 | 0.757718 | 0.962810 | 0.887448 |

## Decision

- E6 keeps full AP50 within 0.001 of E2: No
- E6 improves mean missing-modality AP50 over E2: No
- E6 improves full AP50 or AP75 outright: No
- Decision: E2 remains the paper main model; E6 is a training-strategy ablation.
