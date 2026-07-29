# Current Task

## Authorization

The active task is:

`V74_TRIAIR_MANUSCRIPT_MMUAV_CROSS_DATASET_TRANSFER_INTEGRATION_AUTHORIZED`

V73 completed its authorized training and evaluation protocol at commit `eafceccdedfc0bea93170a671906619b004412f4`, but its uploaded aggregate metrics and conclusions were later found to be incorrect. The correction recorded on 2026-07-29 supersedes those values.

Authoritative correction:

`runs/v73_mmuav_triair_initialized_alignment_aware_transfer_benchmark/RESULT_CORRECTION.md`

Machine-readable corrected aggregate summary:

`runs/v73_mmuav_triair_initialized_alignment_aware_transfer_benchmark/three_seed_summary.json`

V74 is documentation, manuscript integration, number-traceability, claim-audit, clean-build, and rendered-page inspection work only. It must run no new training, inference, evaluation, tuning, seed, adapter, epoch extension, checkpoint selection, or result-driven rerun.

## Required Start

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git status --short
git rev-parse HEAD
```

Require a clean worktree. Read `AGENTS.md`, `docs/PROJECT_CONTEXT.md`, all four current task/status files, the correction record, corrected aggregate JSON, V72 protocol evidence, active manuscript sources, bibliography, and protected-file rules.

## Corrected Evidence Lock

Use the following table exactly at the supplied display precision:

| Training setting | AP | AP50 | AP75 | AR100 | Conclusion |
| --- | ---: | ---: | ---: | ---: | --- |
| Frozen TriAir, naive-grid zero-shot | 0.000 | 0.000 | 0.000 | 0.000 | Direct transfer failed |
| MM-UAV Scratch Equal | 0.220 ± 0.007 | 0.557 | 0.134 | 0.351 | Aligned supervised training recovered performance |
| TriAir Init Equal | 0.233 ± 0.006 | 0.580 | 0.151 | 0.374 | Source-domain pretraining was beneficial |
| TriAir Init Reliability | 0.250 ± 0.008 | 0.610 | 0.178 | 0.398 | Reliability-aware fusion improved performance further |

The corrected interpretation is:

1. frozen naive-grid zero-shot transfer failed directly;
2. MM-UAV supervision with learned feature alignment recovered useful detection performance;
3. TriAir initialization improved AP, AP50, AP75, and AR100 over matched scratch training;
4. reliability-aware fusion improved all four reported metrics further and achieved the best corrected aggregate result;
5. the transfer result remains supervised target-domain adaptation, not zero-shot or independent external validation.

## Invalidated Pre-Correction Evidence

Do not use the following pre-correction files as metric sources:

- `runs/v73_mmuav_triair_initialized_alignment_aware_transfer_benchmark/per_run_metrics.csv`;
- `runs/v73_mmuav_triair_initialized_alignment_aware_transfer_benchmark/per_run_metrics.json`;
- `runs/v73_mmuav_triair_initialized_alignment_aware_transfer_benchmark/paired_transfer_comparison.csv`;
- `runs/v73_mmuav_triair_initialized_alignment_aware_transfer_benchmark/paired_transfer_comparison.json`;
- pre-correction aggregate values and negative-transfer conclusions in commit `eafceccdedfc0bea93170a671906619b004412f4` and subsequent V74 handoff documentation.

Corrected seed-level values were not supplied with the aggregate correction. Therefore:

- do not reconstruct or invent per-seed values;
- do not compute paired differences, minima, maxima, ranges, or seed-wise directions;
- do not include the previously required nine-row per-seed table;
- do not describe the old paired-difference files as reproducible evidence;
- report only the corrected aggregate table until corrected seed-level records are supplied.

## Scientific Label and Boundary

Use:

`MM-UAV supervised cross-dataset transfer benchmark with learned feature alignment`

The manuscript may state that source-domain pretraining and reliability-aware fusion improved the corrected aggregate MM-UAV results under the fixed supervised protocol.

The manuscript may not claim:

- independent or blind external validation;
- official untouched MM-UAV test performance;
- zero-shot success for V73;
- generalization without MM-UAV labels;
- statistically significant effects from aggregate values alone;
- public redistribution rights for MM-UAV data or derivatives.

## Required Manuscript Changes

1. Add or revise a subsection or appendix section titled along the lines of `Cross-Dataset Transfer to MM-UAV`.
2. Explain the two-stage evidence chain: V72 frozen naive-grid zero-shot failure followed by V73 supervised alignment-aware transfer.
3. Add one compact aggregate table using the corrected values exactly.
4. State that aligned target-domain supervision recovers performance from zero-shot failure.
5. State that TriAir initialization improves the corrected aggregate result over scratch equal fusion.
6. State that reliability-aware fusion improves the corrected aggregate result further and is best among the reported settings.
7. Remove all pre-correction statements that scratch equal is best, that TriAir initialization is negative transfer, or that reliability fusion provides no gain.
8. Remove or omit all invalidated per-seed and paired-difference tables and prose.
9. Preserve every existing TriAir in-domain number, table, model definition, and primary conclusion.
10. Keep V72/V73 out of the abstract and headline contribution list as independent external validation.
11. Use an established MM-UAV citation when available; otherwise retain one explicit internal citation placeholder and record it in the audit.
12. Do not publish or redistribute MM-UAV data, labels, checkpoints, private paths, or provider correspondence.

## Number and Table Rules

- Use AP/AR values on the 0–1 scale throughout the corrected table.
- Preserve the supplied three-decimal display precision.
- Show AP sample standard deviation only where supplied.
- Do not add uncertainty values for AP50, AP75, or AR100.
- Do not present old full-precision values as hidden traceability numbers.
- Do not derive relative ratios from the zero baseline.
- Bold the best aggregate row only when the caption states that the comparison is descriptive and supervised.

## Validation and Build

After manuscript edits:

1. verify every inserted V72/V73 value against `RESULT_CORRECTION.md` and `three_seed_summary.json`;
2. search all active manuscript and documentation sources for the invalidated old values and negative-transfer wording;
3. verify that no per-seed or paired-difference values from invalidated files remain;
4. create a number-to-source traceability ledger for every inserted value;
5. verify original TriAir in-domain tables and conclusions are unchanged;
6. run the repository clean LaTeX/BibTeX build procedure;
7. require zero undefined references or citations except one explicitly tracked internal MM-UAV placeholder when necessary;
8. inspect every rendered page containing the corrected subsection, table, caption, or cross-reference;
9. run protected-file and compact-artifact checks.

## Required Outputs

Create or update:

`runs/v74_triair_manuscript_mmuav_cross_dataset_transfer_integration/`

with compact files including:

```text
protocol.md
v72_evidence_lock.json
v73_corrected_aggregate_lock.json
invalidated_v73_artifact_register.json
manuscript_change_inventory.json
number_traceability.json
claim_audit.json
citation_status.json
build_commands.txt
build_output.txt
rendered_page_audit.md
protected_file_audit.json
final_decision.json
handoff.md
```

Do not add raw datasets, labels, full predictions, model checkpoints, rendered-page raster dumps, local absolute paths, credentials, or heavy/private artifacts to Git.

## Decision States

Choose exactly one:

- `V74_TRIAIR_MANUSCRIPT_MMUAV_TRANSFER_STUDY_INTEGRATED`;
- `V74_BLOCKED_MANUSCRIPT_SOURCE_OR_BUILD_CONTRACT`;
- `V74_BLOCKED_CORRECTED_RESULT_TRACEABILITY`;
- `V74_BLOCKED_CLAIM_BOUNDARY`;
- `V74_BLOCKED_TABLE_LAYOUT_OR_RENDERING`;
- `V74_BLOCKED_SOURCE_PROTECTED_OR_PRIVATE_ARTIFACT_VIOLATION`.

## Forbidden Work

- new MM-UAV or TriAir training, inference, evaluation, seeds, epochs, checkpoints, adapters, thresholds, or datasets;
- rerunning V72/V73 to recreate missing seed-level records;
- reconstructing per-seed values from aggregate means and standard deviations;
- using invalidated per-run or paired-comparison files;
- preserving the pre-correction negative-transfer conclusion;
- changing original TriAir scientific evidence;
- presenting V73 as independent external validation;
- public submission authorization solely from V74.

## Completion

Commit with exactly:

`docs: integrate corrected V72-V73 MM-UAV cross-dataset transfer study`

Push to:

`research/ra-repdet-triair`
