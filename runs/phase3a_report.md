# Phase 3A Report

Phase 3A supplies the dropout-ratio ablation and qualitative-case evidence package for the current paper path. E2 remains the main model unless this ablation provides stronger evidence for another ratio.

## Dropout-Ratio Ablation

| Method | Dropout Ratio | P@0.50 | R@0.50 | F1@0.50 | Full AP50 | Full AP75 | w/o RGB AP50 | w/o Thermal AP50 | w/o Event AP50 | Mean Missing-Modality AP50 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E1 Reliability Fusion | 0.00 | 0.925721 | 0.962298 | 0.943655 | 0.979317 | 0.947634 | 0.688697 | 0.370994 | 0.477850 | 0.512514 |
| E3 Reliability + Dropout 0.10 | 0.10 | 0.949248 | 0.945341 | 0.947290 | 0.977738 | 0.945218 | 0.930783 | 0.723911 | 0.978295 | 0.877663 |
| E2 Reliability + Dropout 0.15 | 0.15 | 0.931057 | 0.956042 | 0.943384 | 0.979990 | 0.950906 | 0.948710 | 0.811566 | 0.978972 | 0.913083 |
| E4 Reliability + Dropout 0.20 | 0.20 | 0.946437 | 0.951268 | 0.948846 | 0.978692 | 0.948514 | 0.954897 | 0.872685 | 0.979640 | 0.935741 |

Footnote: Mean Missing-Modality AP50 is only the arithmetic mean of the three single-modality-missing AP50 values; it is a robustness summary, not a standard detection metric.

## Selected Default Ratio

The ratio ablation is interpreted by separating full-modality detection quality from missing-modality robustness. Full AP50/AP75 drive the accuracy-first main-model choice; P@0.50/F1@0.50 and the three single-modality-missing AP50 values identify a robustness-first operating point. The arithmetic mean missing-modality AP50 is reported only as a summary, not as a standard metric or sole selection rule.

- Accuracy-first ratio: p=0.15 (E2 Reliability + Dropout 0.15).
- Robustness-first ratio: p=0.20 (E4 Reliability + Dropout 0.20).
- p=0.15 remains justified for the main accuracy-first result: Yes.
- No ratio is universally dominant in this single-seed 50-epoch ablation.

## Qualitative-Case Manifest Summary

- Qualitative manifest rows: 25
- E0 miss, E2 hit: 5
- E1 miss, E2 hit: 5
- low-brightness E2-success case: 5
- representative E2 failure case: 5
- representative shared success case: 5

## Final Model Decision

- Main model after Phase 3A: E2 Reliability + Dropout 0.15.
- Robustness-first variant after Phase 3A: E4 Reliability + Dropout 0.20.
- E5 and E6 remain ablations because they did not satisfy their predefined replacement rules.

## Remaining Gaps Before Manuscript Drafting

- Convert the selected qualitative manifest rows into figure panels outside Git-tracked outputs.
- Assemble final paper tables from Phase 2A, Phase 2B, Phase 2C, and Phase 3A summaries.
- Decide whether to include E5 and E6 in the main ablation table or supplementary material.
