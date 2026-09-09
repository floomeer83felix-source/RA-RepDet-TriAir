# Current Task

## Completion

V87 is complete with:

`V87_TRIAIR_EVENT_CONTRIBUTION_MANUSCRIPT_INTEGRATION_COMPLETE`

The active manuscript now contains the authoritative V81 single-modality evidence and the V86 matched RGB+thermal versus RGB+thermal+event dynamic-gating comparison, including the negative seed-0 AP delta and the bounded `2/3`-seed interpretation. The manuscript's MM-UAV V73 section has also been restored to the frozen actual metrics, replacing an older idealized reference table that was not experimental evidence.

No new training, inference, evaluation, tuning, checkpoint selection, historical-holdout access, or V86 outer-fold access occurred in V87.

## Active next task

`V88_MANUSCRIPT_RELEASE_CANDIDATE_CONSISTENCY_AUDIT_AUTHORIZED`

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
