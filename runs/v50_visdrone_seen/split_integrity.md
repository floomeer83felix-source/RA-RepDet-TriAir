# V50 Split Integrity

- Exact cross-split image duplicate groups: `0`.
- Same-stem train/devval overlap: `0`.
- Candidate filename-prefix train/devval overlap: `24`.
- Frozen rule: preserve the local generator's source train/val/test-dev partition.
- Limitation: candidate prefix overlap prevents a claim of sequence-disjoint external testing.
- Test is reserved until all settings and RGB checkpoints are frozen.
