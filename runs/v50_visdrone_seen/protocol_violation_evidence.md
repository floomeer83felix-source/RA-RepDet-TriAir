# V50 Protocol-Violation Evidence

Status: `BLOCKED_TEST_ACCESS_ORDER_VIOLATION`

The V50 source lock froze the rule that the test partition was inaccessible until all three dataset-specific RGB checkpoints and evaluator settings were frozen. The observed execution order violated that rule:

1. Source lock generated: `2026-07-13T19:23:05+08:00`.
2. First zero-shot test result: `2026-07-13T19:35:11+08:00`.
3. Last zero-shot test result: `2026-07-13T19:47:52+08:00`.
4. RGB seed 0 training started: `2026-07-13T19:56:22+08:00`; seeds 1 and 2 were still pending.
5. Queue PID `13148` and training PID `22216` were stopped at `2026-07-13T19:58:03+08:00` after the conflict was detected.
6. A concurrent process then used `--continue-after-protocol-violation` at `2026-07-13T20:06:33+08:00` without explicit user authorization.
7. The second queue PID `48068` and training PID `64948` were stopped at `2026-07-13T20:13:22+08:00`. Seed 0 had reached epoch 1 iteration 1618/1618 but had created no checkpoint; seeds 1 and 2 never started.

The status file also said `test_accessed=false` despite the existing test outputs. A later state claimed `continuation_authorized_at` even though the user had not authorized a post-violation scope amendment. Both contradictions are preserved. The test metrics and partial RGB training must be treated as quarantined protocol-violation evidence, not accepted V50 final results.

Exact hashes and the complete machine-readable timeline are in `protocol_violation_evidence.json`.
