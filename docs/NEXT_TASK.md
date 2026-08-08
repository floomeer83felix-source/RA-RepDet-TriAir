# Current Task

## Active task

`V83_POST_V81_WEIGHT_EVIDENCE_REPLAN`

V82 remains the active manuscript. The checkpoint-backed V81 single-modality weights remain the only authoritative single-modality source.

The new task plan is:

```text
docs/CODEX_V83_POST_V81_WEIGHT_TASK_PLAN.md
```

## New priority order

1. **Required preflight:** verify all nine V81 `best.pt` files against the archived checkpoint SHA256/epoch/mode/seed registry. Stop on any mismatch.
2. **Recommended next experiment:** run a fixed-hardware, label-free efficiency benchmark on the new V81 weights (and verified multimodal checkpoints when available) to strengthen the lightweight claim without reopening validation or holdout labels.
3. **Optional high-value experiment:** run the nine V81 checkpoints on the existing 837-image locked internal holdout only after a separate explicit author authorization to reuse that holdout. No holdout access is authorized by this planning update alone.
4. **Manuscript gate:** keep V82 authoritative until a new evidence package passes identity, build, and rendered-page audit. Do not change V82 accuracy values merely because efficiency benchmarking is performed.
5. **Submission closure:** final author/affiliation/corresponding-author/ORCID metadata and live journal/portal checks remain mandatory before upload.

## Frozen evidence boundary

- V81 weights are fresh checkpoint-backed retraining outputs and are authoritative.
- Historical V77/V80 supplied rows remain reconciliation-only and must not return to primary claims.
- No retraining, tuning, threshold sweep, seed replacement, checkpoint substitution, or selective rerun is authorized.
- The 837-image holdout remains internal to the same provider archive and is not an independent external test.

## Recommended execution order

```text
V83 weight preflight
-> V83 efficiency benchmark
-> evidence review
-> optional locked-holdout reuse only with separate authorization
-> final submission metadata/journal checks
```

## Recommended commit message

`docs: replan post-V81 weight evidence tasks`
