# V84 Component-Cluster Bootstrap

The resampling unit is the 1,298-component identity from the leakage-aware validation split. For each checkpoint, COCO AP/AP50/AP75/AR100 is first computed separately within each component. The paired component difference is averaged across seeds 0, 1, and 2, and 5,000 bootstrap samples draw components with replacement using seed 8404.

The estimand is explicitly the equally weighted component-macro metric, not the image-weighted headline COCO metric. Components without foreground boxes receive the project evaluator's zero local AP/AR and therefore do not independently penalize false positives; this is a limitation of the local component estimand. The interval is descriptive component-aware uncertainty, not a broad significance claim. The locked holdout was not accessed.
