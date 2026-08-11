# V84 Matched Channel-Removal Analysis

This is a seed-matched 2x2 gate-by-training-modality-dropout analysis on the frozen 2,213-image development-validation split. At inference, removal deterministically sets RGB channels 0:3, thermal channel 3, or event channel 4 to zero; all other channels and evaluator settings are unchanged.

`factorial_effects.json` reports the gate and dropout main effects as averages over the opposite factor, plus the difference-in-differences interaction. `paired_deltas.csv` also records every seed-level effect and modality-specific removal-minus-full degradation. Interpret robustness attribution from these matched effects rather than from an unmatched pair. This analysis is development-validation evidence only. The locked holdout was not accessed.
