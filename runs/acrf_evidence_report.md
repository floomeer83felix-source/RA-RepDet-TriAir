# ACRF Evidence Report

| Method | Params | Full AP50 | Full AP75 | P@0.50 | R@0.50 | F1@0.50 | w/o RGB AP50 | w/o Thermal AP50 | w/o Event AP50 | Mean Missing-Modality AP50 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E1 Reliability Fusion | 6593293 | 0.979317 | 0.947634 | 0.925721 | 0.962298 | 0.943655 | 0.688697 | 0.370994 | 0.477850 | 0.512514 |
| E2 Reliability + Dropout 0.15 | 6593293 | 0.979990 | 0.950906 | 0.931057 | 0.956042 | 0.943384 | 0.948710 | 0.811566 | 0.978972 | 0.913083 |
| E5 ACRF + Dropout 0.15 | 6593341 | 0.978066 | 0.946602 | 0.938290 | 0.953737 | 0.945950 | 0.944019 | 0.846657 | 0.978531 | 0.923069 |

## Required Answers

- Does E5 maintain or improve E2 full-modality AP50/AP75? No; keep wording conservative.
- Does E5 improve the three missing-modality AP50 values, particularly w/o Thermal? Mixed; inspect the table before claiming robustness improvement.
- Are absent-modality alpha values actually zero in E5? Yes
- Is the parameter increase <=0.03M? Yes
- Should E5 replace E2 as the paper main model, or remain an ablation? Replace E2 only if both full-modality and missing-modality metrics are maintained or improved; otherwise present E5 as an ablation targeted at alpha correctness.
