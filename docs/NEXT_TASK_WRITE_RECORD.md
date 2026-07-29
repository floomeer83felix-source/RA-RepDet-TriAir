# Next Task Write Record

Written: 2026-07-30
Branch: `research/ra-repdet-triair`

## Active handoff

`V79_SINGLE_MODALITY_EVALUATOR_ONLY_LOCAL_EXECUTION`

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

## Current execution boundary

The evaluator-only code and Codex runbook are committed. Actual GPU inference remains pending on the authorized local workspace because the ChatGPT environment does not contain the private TriAir data or nine retained checkpoints.

## Task-writing commits

- `docs: add Codex V80 evaluator-only task`
- `docs: point next task to Codex V80 evaluator runbook`
- `docs: record Codex V80 task handoff`