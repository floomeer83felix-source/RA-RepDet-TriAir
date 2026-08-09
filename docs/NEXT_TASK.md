# Current Task

## Active task

`V83_WEIGHT_PREFLIGHT_AND_EFFICIENCY_COMPLETE`

V82 remains the active manuscript. The checkpoint-backed V81 single-modality weights remain the only authoritative single-modality source.

The completed task plan is:

```text
docs/CODEX_V83_POST_V81_WEIGHT_TASK_PLAN.md
```

## Completed work

1. All nine V81 `best.pt` files passed archived SHA256, epoch, input-mode, seed, and model-configuration checks.
2. Six exact-identity multimodal checkpoints passed their archived SHA256 and metadata checks.
3. All 15 checkpoints completed the fixed RTX-3090, batch-1, 640x640, FP32, label-free benchmark with 50 warm-up and 200 synchronized measured iterations.
4. Evidence review found that V83 corroborates but does not materially improve the stronger efficiency table already in V82, so V82 remains unchanged and authoritative.
5. No dataset, validation labels, or locked-holdout samples were accessed.

## Frozen evidence boundary

- V81 weights are fresh checkpoint-backed retraining outputs and are authoritative.
- Historical V77/V80 supplied rows remain reconciliation-only and must not return to primary claims.
- No retraining, tuning, threshold sweep, seed replacement, checkpoint substitution, or selective rerun is authorized.
- The 837-image holdout remains internal to the same provider archive and is not an independent external test.

## Next authorized work

- complete final author, affiliation, corresponding-author, and ORCID metadata;
- verify the live target-journal template and submission portal immediately before upload;
- preserve V82 as the active manuscript;
- do not reuse the locked holdout unless the author gives a separate explicit authorization.

Commit message: `results: archive V83 fixed-hardware efficiency evidence`
