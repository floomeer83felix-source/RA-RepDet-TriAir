# Phase 2A Main Results

Paper-facing Precision, Recall, and F1 use score threshold 0.50. AP50/AP75 remain score-ranked AP values from the threshold sweep.

| Method | Threshold | Precision | Recall | F1 | AP50 | AP75 | GT boxes | Predictions | Mean Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E0 Early Fusion | 0.50 | 0.929133 | 0.954067 | 0.941434 | 0.976620 | 0.928824 | 6074 | 6237 | 0.769583 |
| E1 Reliability Fusion | 0.50 | 0.925721 | 0.962298 | 0.943655 | 0.979317 | 0.947634 | 6074 | 6314 | 0.794935 |
| E2 Reliability + Dropout 0.15 | 0.50 | 0.931057 | 0.956042 | 0.943384 | 0.979990 | 0.950906 | 6074 | 6237 | 0.788404 |
