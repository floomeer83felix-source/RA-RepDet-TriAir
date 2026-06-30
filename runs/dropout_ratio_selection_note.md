# Dropout-Ratio Selection Note

Phase 3A does not show a universally dominant modality-dropout ratio in the current single-seed 50-epoch ablation.

- E2 (`p=0.15`) yields the highest full-modality AP50/AP75.
- E4 (`p=0.20`) yields the highest P@0.50/F1@0.50 and the strongest AP50 in `w/o RGB`, `w/o Thermal`, and `w/o Event` conditions.
- For an accuracy-first main result, retain E2.
- For a robustness-first operating point, report E4 as a separate variant.
- The arithmetic mean missing-modality AP50 is only a compact robustness summary, not a standard detection metric.

