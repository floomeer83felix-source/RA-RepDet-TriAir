# Current Task

## Authorization

V73 completed at commit `eafceccdedfc0bea93170a671906619b004412f4` with:

`V73_MMUAV_THREE_SEED_TRANSFER_BENCHMARK_COMPLETE`

The active next task is:

`V74_TRIAIR_MANUSCRIPT_MMUAV_CROSS_DATASET_TRANSFER_INTEGRATION_AUTHORIZED`

V74 is a documentation, manuscript-integration, arithmetic-verification, and clean-build task. It must integrate the frozen V72 and V73 MM-UAV evidence into the TriAir research manuscript without running new training, inference, adapter searches, threshold tuning, checkpoint selection, or result-driven reruns.

## Required Start

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git status --short
git rev-parse HEAD
```

Require a clean worktree. Record the actual starting commit and verify that V73 completion commit `eafceccdedfc0bea93170a671906619b004412f4` is an ancestor of `HEAD`.

Read `AGENTS.md`, `docs/PROJECT_CONTEXT.md`, the four current task files, the active manuscript and bibliography, V72 and V73 protocol/metric/claim-boundary evidence, the original TriAir main-result tables, and protected-file rules.

## Frozen Evidence

Use the committed JSON/CSV evidence exactly. Do not recompute metrics from predictions, omit seeds, select favorable runs, replace checkpoints, or round inconsistently.

### V72 unadapted zero-shot stress test

Scientific label:

`zero-shot external-domain stress test on the exposed MM-UAV devval split using a naive normalized-grid five-channel adapter`

- frozen TriAir checkpoints received no MM-UAV training or adaptation;
- MM-UAV devval rows: `1,845`;
- modalities were independently letterboxed and concatenated without physical registration;
- Early Fusion mean AP@[.50:.95]: `9.48024496878457e-9`;
- RA-RepDet mean AP@[.50:.95]: `7.208000851646425e-7`;
- all six AP values were zero or effectively zero.

V72 establishes only that direct unregistered channel-level transfer failed under the frozen naive adapter. It is not an independent, blind, official-test, or physically registered external validation.

### V73 supervised alignment-aware transfer benchmark

Scientific label:

`MM-UAV supervised cross-dataset transfer benchmark with learned feature alignment`

All nine runs used the same frozen protocol:

- MM-UAV train rows: `7,187`;
- MM-UAV exposed devval rows: `1,845`;
- independent RGB/IR/event stems and learned feature alignment;
- `640 x 640`, batch size `1`, ten epochs and `71,870` optimizer steps per run;
- final checkpoint only, evaluated exactly once;
- three methods and seeds `0`, `1`, `2`;
- total optimizer steps: `646,830`;
- no early stopping, devval monitoring, tuning, checkpoint selection, or result-driven rerun.

Exact three-seed summaries:

| Method | AP@[.50:.95] mean ± sample std | AP50 mean | AP75 mean | AR100 mean |
| --- | ---: | ---: | ---: | ---: |
| `scratch_equal` | `0.2234327171146003 ± 0.007329674213261401` | `0.556931726947029` | `0.134019814828121` | `0.3512863268222963` |
| `triair_init_equal` | `0.2177868187542824 ± 0.0020161156114949915` | `0.5526032852323605` | `0.12540843897740625` | `0.34365570906781007` |
| `triair_init_reliability` | `0.21510604967221716 ± 0.009007102251984311` | `0.5451312175583816` | `0.1254178623160722` | `0.34215499444179764` |

Exact paired AP@[.50:.95] differences:

- `triair_init_equal - scratch_equal`: mean `-0.00564589836031786`, sample std `0.008610682137977752`, minimum `-0.01152105876572837`, maximum `0.004238315166474077`;
- `triair_init_reliability - scratch_equal`: mean `-0.008326667442383104`, sample std `0.006221064752576723`, minimum `-0.015164018070424501`, maximum `-0.003000212280563158`;
- `triair_init_reliability - triair_init_equal`: mean `-0.002680769082065243`, sample std `0.008893536424666055`, minimum `-0.011054087142635727`, maximum `0.006654739201136128`.

TriAir initialization transferred `0.9920156853111293` of destination parameters in every transfer run, but did not improve mean target-domain AP under the fixed ten-epoch protocol.

## Required Scientific Interpretation

The manuscript must present the combined evidence as follows:

1. naive, unregistered zero-shot transfer produced effectively zero AP;
2. target-domain supervision with learned feature alignment recovered useful MM-UAV detection performance to approximately `0.22` mean AP;
3. the matched from-scratch equal-fusion control achieved the highest three-seed mean AP;
4. architecture-compatible TriAir initialization did not provide an average AP benefit under the fixed protocol;
5. reliability-aware fusion did not improve the three-seed mean over matched equal fusion and was below scratch on all three paired AP comparisons;
6. the results indicate that target-domain alignment and supervision were the dominant factors, while source initialization and reliability weighting did not yield additional transfer gains in this setting;
7. this result does not invalidate the in-domain TriAir results and does not prove that transfer initialization or reliability fusion can never help under another adaptation protocol;
8. all V73 comparisons are descriptive because only three seeds were run and the devval set had prior engineering exposure.

Do not claim:

- independent or blind external validation;
- official untouched MM-UAV test performance;
- zero-shot success after V73;
- TriAir pretraining benefit on MM-UAV;
- reliability-fusion superiority on MM-UAV;
- statistically significant transfer effects;
- robust external generalization without MM-UAV labels.

## Required Manuscript Changes

1. Add a subsection or appendix section titled along the lines of `Cross-Dataset Transfer to MM-UAV`.
2. Explain the two-stage evidence chain: V72 unadapted zero-shot stress test followed by V73 supervised alignment-aware transfer.
3. Add a compact primary transfer table containing V72 method means and the three V73 method mean ± sample-standard-deviation results.
4. Add an appendix table containing all nine V73 per-seed AP, AP50, AP75, AR@1, AR@10, and AR@100 values from `per_run_metrics.csv`.
5. Report the three paired AP differences exactly and state their seed-wise direction.
6. Document the `99.20156853111293%` parameter-transfer coverage without describing it as a complete model load.
7. State that learned feature alignment plus MM-UAV supervision, rather than source initialization, explains the large recovery relative to V72 under this design.
8. Add a concise discussion/limitations paragraph noting negative transfer from TriAir initialization and the absence of an MM-UAV reliability-fusion gain.
9. Keep V72/V73 out of the abstract and headline contribution list as positive independent external validation.
10. Preserve every existing TriAir in-domain number, table, model definition, and primary conclusion.
11. Use an existing MM-UAV citation when available. When no established entry exists, retain one explicit internal citation placeholder and record it in the V74 audit without delaying integration.
12. Do not publicly release or redistribute MM-UAV data, labels, checkpoints, private paths, or provider correspondence.

## Table and Number Rules

- Use a consistent reporting precision suitable for the manuscript, while preserving full-precision traceability in V74 audit JSON.
- Recommended display precision for V73 AP/AR values is three decimals or percentage points with an explicit scale; do not mix scales within one table.
- Display V72 near-zero results as `<0.001` or scientific notation, with an explicit footnote that all values were effectively zero.
- Do not use relative ratios between V72 and V73 because the V72 denominator is effectively zero.
- Bold the best mean only when the table caption states that all comparisons are descriptive.
- Do not hide the negative paired differences or omit any seed.

## Validation and Build

After manuscript edits:

1. independently reproduce all V73 means, sample standard deviations, minima, maxima, ranges, and paired differences from the committed per-run CSV/JSON;
2. verify all V72 numbers against committed V72 JSON;
3. create a number-to-source traceability ledger for every inserted value;
4. search the manuscript for prohibited external-validation, pretraining-benefit, and reliability-superiority wording;
5. verify that original TriAir in-domain tables and conclusions are unchanged;
6. run the repository's clean LaTeX/BibTeX build procedure;
7. require zero undefined references/citations except one explicitly tracked internal MM-UAV citation placeholder when necessary;
8. inspect every rendered page containing the new subsection, tables, captions, or cross-references for overflow, clipping, illegible text, orphaned headings, and inconsistent decimal scales;
9. run protected-file and compact-artifact checks.

## Required Outputs

Create:

`runs/v74_triair_manuscript_mmuav_cross_dataset_transfer_integration/`

with compact files including:

```text
protocol.md
v72_evidence_lock.json
v73_evidence_lock.json
per_run_arithmetic_verification.json
paired_difference_verification.json
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
- `V74_BLOCKED_RESULT_TRACEABILITY_OR_ARITHMETIC`;
- `V74_BLOCKED_CLAIM_BOUNDARY`;
- `V74_BLOCKED_TABLE_LAYOUT_OR_RENDERING`;
- `V74_BLOCKED_SOURCE_PROTECTED_OR_PRIVATE_ARTIFACT_VIOLATION`.

## Forbidden Work

- new MM-UAV or TriAir training, inference, seeds, epochs, checkpoints, adapters, thresholds, or datasets;
- devval-driven tuning or rerunning V72/V73;
- selecting only favorable V73 seeds;
- changing or recomputing frozen V72/V73 metrics from raw predictions;
- presenting V73 as independent external validation or evidence of source-pretraining/reliability superiority;
- modifying original TriAir scientific evidence;
- public submission authorization solely from V74.

## Completion

Commit with exactly:

`docs: integrate V72-V73 MM-UAV cross-dataset transfer study`

Push to:

`research/ra-repdet-triair`
