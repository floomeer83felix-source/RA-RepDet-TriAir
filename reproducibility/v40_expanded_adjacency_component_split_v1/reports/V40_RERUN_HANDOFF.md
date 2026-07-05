# V40 Rerun Handoff

- Generated: 2026-07-05T23:12:04
- Git commit: `042a321ee416712b18c11b0bde3ea7425549c545`
- Split status: `V40_EXPANDED_ADJACENCY_SPLIT_READY_FOR_FROZEN_RERUN`

No training has occurred on the V40 manifests.

If and only if this V40 split remains accepted, the next task is a frozen rerun of four variants on the V40 manifests:

1. matched early fusion;
2. reliability-aware fusion with p=0.00;
3. reliability-aware fusion with p=0.15;
4. reliability-aware fusion with p=0.20.

Each future variant requires two controlled independent runs under one locked training/evaluation protocol. The future final configuration must be selected only by two-run mean AP50, then F1, then AP75, with fixed fallback order p=0.00, p=0.15, p=0.20.

Do not use the V39 guard partition for model selection or performance reporting.
