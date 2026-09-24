# Current Task

## Recovery note (2026-09-24)

The first M3OT queue stopped after early seed 0 completed and dynamic seed 0
completed 23 epochs. A native PyTorch crash interrupted dynamic epoch 24.
The unchanged queue was restarted from the intact epoch-23 checkpoint at
22:24 CST; its live log is
`runs/m3ot_supervised_rgbt_v1/orchestrator.resume2.stdout.log`. It skips
completed early seed 0, resumes dynamic seed 0, then continues seeds 1 and
2. Keep the original crash log and do not treat any partial metrics as final.

## Active user-authorized experiment (2026-09-24)

`M3OT_SUPERVISED_RGBT_SIX_SEED_AUTHORIZED`

Execution status (2026-09-24): data and visual gates passed; the six-run
sequential training queue is running from `early_seed0`. Monitor
`runs/m3ot_supervised_rgbt_v1/orchestrator.stdout.log` and each run's
`status.json`. Do not report final metrics until all six 50-epoch runs and
the best-checkpoint report have completed and been verified.

The user explicitly authorized a new M3OT supervised experiment after V87.
Execute `docs/M3OT_SUPERVISED_RGBT_SIX_SEED_PROTOCOL.md` before resuming the
previously queued V88 manuscript audit. This authorization supersedes V88's
no-new-experiment restriction **only for this M3OT protocol**. Do not change
the frozen TriAir manuscript claims or use the M3OT public test split.

First audit actual local RGB/IR/frame pairing and official RGB COCO vehicle
boxes, then visually inspect representative train/val samples. Only after
both gates pass, train early RGB+thermal and dynamic RGB+thermal detectors from
scratch (`pretrained=False`) for seeds 0/1/2 with identical 50-epoch,
batch-4, 640x640, AdamW (`lr=1e-4`, `weight_decay=1e-4`) schedules and no
augmentation. Evaluate official val each epoch, select each best checkpoint
by AP50, and produce all metrics, paired comparisons, fixed-threshold counts,
three model-independent qualitative scenes, CSV files, and a short report.

This is **supervised M3OT train/val development**, not zero-shot transfer or
blind independent test. Heavy data, weights, caches, and rendered figures
remain local; only lightweight code/docs/reports may be pushed.

## Completion

V87 is complete with:

`V87_TRIAIR_EVENT_CONTRIBUTION_MANUSCRIPT_INTEGRATION_COMPLETE`

The active manuscript now contains the authoritative V81 single-modality evidence and the V86 matched RGB+thermal versus RGB+thermal+event dynamic-gating comparison, including the negative seed-0 AP delta and the bounded `2/3`-seed interpretation. The manuscript's MM-UAV V73 section has also been restored to the frozen actual metrics, replacing an older idealized reference table that was not experimental evidence.

No new training, inference, evaluation, tuning, checkpoint selection, historical-holdout access, or V86 outer-fold access occurred in V87.

## Deferred manuscript task

`V88_MANUSCRIPT_RELEASE_CANDIDATE_CONSISTENCY_AUDIT_AUTHORIZED` (deferred until
the user-authorized M3OT experiment is resolved)

V88 is a final manuscript/submission-readiness task only.

## Required V88 work

1. Treat the current manuscript and frozen V81/V84/V85/V86/V87 evidence as read-only scientific inputs.
2. Audit every numerical statement in the abstract, results, discussion, conclusion, tables, and captions against its authoritative result artifact.
3. Verify that the active manuscript contains no idealized/reference-only numbers presented as experimental results.
4. Preserve the V86 event-contribution boundary: mean AP `+0.0339 +/- 0.0400`, positive in `2/3` seeds, AP50 nearly unchanged, no significance claim.
5. Preserve the actual V73 MM-UAV ordering: Scratch Equal has the highest three-seed mean; source initialization and reliability-aware fusion do not improve the mean under the frozen schedule.
6. Verify author metadata: Nan Xin first author; Xueting Jin corresponding author; corresponding email `jinxueting@ahpc.edu.cn`; Anhui Police College affiliation; no specific funding.
7. Verify Data Availability describes TriAir and MM-UAV as publicly available research datasets obtained from their original providers, without implying that this repository redistributes raw data or weights.
8. Check all figure/table numbering, cross-references, bibliography entries, equations, captions, page breaks, and two-column layout.
9. Run a clean multi-pass LaTeX build and rendered-page audit.
10. Freeze the final release-candidate source manifest, PDF hash, source hash, build log, and claim audit.

## Prohibited work

- no new training, fine-tuning, inference, evaluation, threshold sweep, hyperparameter search, or seed addition;
- no checkpoint replacement or result-driven rerun;
- no historical-holdout or V86 outer-fold access;
- no selective omission of unfavorable seeds;
- no statistical-significance, SOTA, calibrated sensor-health, or independent blind external-validation claim unsupported by the frozen evidence;
- no raw datasets, checkpoints, credentials, or heavy/private experiment artifacts committed to Git.

## Required output root

`runs/v88_manuscript_release_candidate_consistency_audit/`

Required outputs:

- `evidence_manifest.json`;
- `number_audit.json`;
- `claim_audit.json`;
- `author_metadata_audit.json`;
- `figure_table_reference_audit.json`;
- `build_output.txt`;
- `rendered_page_audit.md`;
- `release_candidate_manifest.json`;
- `final_decision.json`;
- `handoff.md`.

## Decision states

Choose exactly one:

- `V88_MANUSCRIPT_RELEASE_CANDIDATE_COMPLETE`;
- `V88_BLOCKED_EVIDENCE_OR_NUMBER_INCONSISTENCY`;
- `V88_BLOCKED_CLAIM_OVERREACH`;
- `V88_BLOCKED_AUTHOR_METADATA`;
- `V88_BLOCKED_BUILD_OR_LAYOUT`;
- `V88_BLOCKED_PROTECTED_ARTIFACT_VIOLATION`.

## Completion commit

`docs: finalize V88 manuscript release candidate`

Push to `research/ra-repdet-triair`.
