# Next Task Write Record

Written: 2026-07-29
Branch: `research/ra-repdet-triair`

## User authorization

The user requested a major revision and explicitly authorized the experiments needed to address reviewer concerns.

## Evidence already available and now integrated

- V48: three-seed six-variant causal fusion ablation;
- V42: three-seed locked 837-image internal holdout;
- V75: corrected three-seed MM-UAV transfer evidence.

These records close the earlier manuscript omissions concerning static controls, causal attribution, and three-seed internal holdout evidence.

## Newly authorized work

Exactly nine single-modality TriAir runs:

1. RGB-only seeds 0, 1, 2;
2. thermal-only seeds 0, 1, 2;
3. event-only seeds 0, 1, 2.

The complete frozen contract is in `docs/NEXT_TASK.md`. The implementation uses new experimental scripts and does not modify protected training-core files.

## Current handoff

The V76 manuscript major revision and execution package are complete. GPU execution remains pending on the authorized local TriAir workspace.
