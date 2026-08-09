# Next Task Write Record

Written: 2026-08-08
Branch: `research/ra-repdet-triair`

## Replanned task

`V83_POST_V81_WEIGHT_EVIDENCE_REPLAN`

The author requested that the task sequence be rearranged around the new authoritative V81 checkpoint weights.

## Authoritative inputs

- checkpoint registry: `runs/v81_single_modality_retraining_reconciliation/checkpoint_manifest.json`;
- nine V81 retained `best.pt` checkpoints;
- RGB-only, thermal-only, and event-only seeds 0/1/2;
- checkpoint epoch and SHA256 archived for 9/9;
- common development-validation split SHA256: `722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f`;
- V82 remains the active manuscript.

## New execution hierarchy

1. verify local V81 weight identities against the manifest;
2. run a uniform RTX-3090 efficiency benchmark without reopening labeled validation/holdout data;
3. review whether the efficiency result materially strengthens the lightweight claim;
4. treat the 837-image locked internal holdout as a separately authorization-gated optional phase;
5. finish author metadata and live journal/portal checks before submission.

The detailed runbook is:

```text
docs/CODEX_V83_POST_V81_WEIGHT_TASK_PLAN.md
```

## Holdout boundary

This planning update does **not** authorize access to the 837-image locked internal holdout. A separate explicit author instruction is required before the V81 weights may be evaluated there. If authorized later, the holdout remains repeated internal evidence from the same provider archive, not an independent public test.

## Frozen prohibitions

- no retraining or fine-tuning;
- no threshold or hyperparameter sweep;
- no checkpoint or seed replacement;
- no selective rerun;
- no historical V77/V80 values restored to primary claims;
- no statistical-significance or independent-test claim.

## Planning commits

- `docs: add V83 post-V81 weight task plan`;
- `docs: point next task to V83 weight plan`;
- `docs: record V83 post-weight task replan`.

## Execution record - 2026-08-09

V83 Priority 0 and Priority 1 are complete. The V81 registry passed `9/9`; the exact-identity matched-early and reliability-aware controls passed `6/6`; and the fixed RTX-3090 efficiency benchmark completed `15/15` without dataset or label access.

Evidence is archived under:

```text
runs/v83_post_v81_weight_evidence/
```

The manuscript gate was reviewed. V83 does not replace the stronger repeated efficiency protocol already reported in V82, so no manuscript source or accuracy value was changed. Locked-holdout reuse remains unauthorized.
