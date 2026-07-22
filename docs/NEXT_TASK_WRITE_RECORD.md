# Next Task Write Record

Written: 2026-07-22
Branch: `research/ra-repdet-triair`
V66 completion commit: `70a54d92b8deb8cb9a0f748230731cddad641d9f`
Canonical task file: `docs/NEXT_TASK.md`

## Active next task

`V67_MMUAV_TWO_SEED_RELIABILITY_SOFTPLUS_BENCHMARK_AUTHORIZED`

Execute the frozen V67 matched reliability-fusion benchmark exactly as specified in `docs/NEXT_TASK.md`:

1. Verify immutable V65/V66 two-seed equal-fusion evidence and protected fingerprints.
2. Strictly reproduce the frozen seed-0 and seed-1 common initialization hashes.
3. Prove reliability/equal state-dictionary identity and exact uniform step-0 weights/outputs for each seed.
4. Run seed 0 reliability Softplus for exactly 7,187 ordered steps.
5. Run seed 1 reliability Softplus for exactly 7,187 ordered steps, regardless of the seed-0 result unless a fail-closed blocker occurs.
6. Preserve exact V65/V66 data, order, alignment, detector, Softplus, optimizer, audit, recovery, and evaluator contracts.
7. Permit only activation of the existing V57 shared image-conditioned reliability scorer; add no modality dropout or auxiliary change.
8. Run ten audits per seed with at most 40 diagnostic backward calls per seed.
9. Evaluate only each final checkpoint once on all 1,845 frozen devval rows.
10. Produce matched per-seed AP/AR deltas, two-seed reliability summaries, and fusion-weight/scorer diagnostics.
11. Do not tune, select checkpoints or thresholds, add seeds/variants, rerun, or automatically extend.
12. Keep checkpoints, optimizer states, recovery snapshots, predictions, tensors, and media local and outside Git.

## Handoff status

The V67 instruction is written and active. Begin with V65/V66 evidence verification, source/state/scorer identity tests, frozen evaluator tests, and recovery round trips. Stop fail-closed on any mismatch.
