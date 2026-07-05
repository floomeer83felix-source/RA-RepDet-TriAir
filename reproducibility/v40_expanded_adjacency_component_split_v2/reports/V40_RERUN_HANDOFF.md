# V40 v2 Rerun Handoff

- Generated: 2026-07-05T23:53:27
- Input commit: `a484a6165d2ce4078f7e68dbb79debcaba04ba81`
- Output commit: `PENDING_FINAL_COMMIT_RECORDED_IN_GIT_HISTORY_AND_FINAL_RESPONSE`
- Split status: `V40_V2_READY_FOR_FROZEN_RERUN`

No training has occurred on the V40 v2 manifests.

If and only if this V40 v2 split remains accepted, the next allowed action is Gate 1: freeze the V40 v2 experiment contract. Do not start model runs until that contract passes.

The later Gate 2 core rerun will cover matched early fusion and reliability-aware fusion with p=0.00, p=0.15, and p=0.20.

Each future variant requires two controlled independent runs under one locked training/evaluation protocol. The future final configuration must be selected only by two-run mean AP50, then F1, then AP75, with fixed fallback order p=0.00, p=0.15, p=0.20.

Do not use the V39 guard partition for model selection or performance reporting.
