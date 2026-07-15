# V52 Interval-20 Sampling Protocol

Frozen before any MM-UAV model metric: `2026-07-15T08:42:29+08:00`.

- User-authorized interval: 20.
- Source indexing begins at 1; every complete sequence keeps `1, 21, 41, ...` without renumbering.
- Complete/rejected sequences: 424 / 0.
- Train/devval sequences: 339 / 85; split is sequence-disjoint and SHA256-ranked with salt `v52-mmuav-interval20-sequence-split-v1`.
- Train/devval samples: 35,894 / 9,142.
- Frames without source GT rows remain marked `UNLABELED_OR_EMPTY_UNRESOLVED`; they are not authorized as negative training samples.
- No model metric was inspected and no GPU operation was executed.
