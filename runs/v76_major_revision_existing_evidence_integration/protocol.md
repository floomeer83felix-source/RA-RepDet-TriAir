# V76 Major-Revision Protocol

V76 integrates only completed, source-locked evidence from V42, V48, and V75 into the manuscript, then prepares a separately frozen nine-run single-modality extension. No completed metric is inferred from an unexecuted experiment.

Completed evidence scope:

- three-seed component-disjoint TriAir COCO evaluation;
- six-variant causal fusion ablation;
- locked 837-image internal holdout evaluated after checkpoint lock;
- corrected three-seed supervised MM-UAV transfer.

Pending experiment scope:

- RGB-only, thermal-only, and event-only, seeds 0, 1, and 2;
- fixed V40 train/devval manifests, 50 epochs, batch 4, 640 pixels, AdamW at 1e-4;
- no tuning, guard access, seed replacement, or result-driven rerun.
