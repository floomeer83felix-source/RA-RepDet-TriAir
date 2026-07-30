# Next Task Write Record

Written: 2026-07-30
Branch: `research/ra-repdet-triair`

## Active handoff

`V80_BLOCKED_RESTORE_EXACT_V76_SINGLE_MODALITY_CHECKPOINTS`

The user requested that the complete Codex execution instruction be persisted in the GitHub repository. The authoritative task is now:

```text
docs/CODEX_V80_SINGLE_MODALITY_EVALUATION_TASK.md
```

`docs/NEXT_TASK.md` points to this runbook.

## Required work

Codex must:

1. verify the local CUDA environment, TriAir root, frozen validation manifest, and all nine retained `best.pt` checkpoints;
2. stop fail-closed if any required input is missing;
3. run the V79 evaluator-only queue without invoking training;
4. produce AP@[0.50:0.95], AP50, AP75, AR1, AR10, AR100, checkpoint SHA256, checkpoint epoch, and split SHA256 for all nine runs;
5. reconcile AP50/AP75 against every V77 seed-level value without silently overwriting discrepancies;
6. compute three-seed means and sample standard deviations;
7. create V80 only after 9/9 completion and reconciliation;
8. compile and visually audit the manuscript;
9. update the repository status documents and commit only compact task-related evidence.

## Frozen prohibitions

- no retraining;
- no hyperparameter or threshold sweep;
- no seed or checkpoint replacement;
- no `last.pt` substitution;
- no selective rerun;
- no guard access;
- no inferred metrics;
- no independent-test or statistical-significance claim.

## 2026-07-30 execution record

- authorized RTX 3090 CUDA environment: verified;
- TriAir root: present;
- frozen V40 component-disjoint validation manifest: present;
- manifest SHA256: `722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f`;
- evaluator compilation: pass;
- evaluator contract tests: `3 passed`;
- required retained checkpoints: `0/9` present;
- inference and training: not started;
- manuscript integration: not started.

## Current execution boundary

The task is blocked until the exact nine retained V76 `best.pt` files are restored. No alternate checkpoint may be used. If they are irrecoverable, V78 remains authoritative and retraining requires a separately authorized task.

## Task-writing commits

- `docs: add Codex V80 evaluator-only task`
- `docs: point next task to Codex V80 evaluator runbook`
- `docs: record Codex V80 task handoff`

## V81 authorization update

Written: 2026-07-30

The user explicitly authorized fresh generation of all nine missing single-modality weights: RGB-only, thermal-only, and event-only at seeds 0, 1, and 2. This supersedes the V80 missing-checkpoint stop condition for training authorization only.

The V81 run remains frozen to 50 epochs, batch size 4, image size 640, AdamW at `1e-4`, no modality dropout, V40 component-disjoint train/development-validation manifests, serial CUDA execution, and no guard access. New checkpoints remain distinct from the lost V77 checkpoint identities.
