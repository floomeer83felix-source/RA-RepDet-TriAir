# Current Task

## Authorization

The user reported that V68 completed and was pushed. Under the standing automatic task-handoff workflow, the user authorizes **V69 TriAir manuscript submission-readiness finalization**.

V68 is frozen as `V68_BLOCKED_DATA_RIGHTS_OR_CITATION_INCOMPLETE`. Its scientific audit passed, but MM-UAV provider authority, canonical citation, version, dataset license, research-use permission, aggregate-results reporting permission, and redistribution terms remain unresolved. MM-UAV evidence must therefore remain internal and excluded from the active manuscript, submission source, abstract, tables, figures, supplement, cover letter, and data/code availability claims.

V69 is a CPU/documentation-only manuscript task. It authorizes no CUDA work, training, evaluation rerun, new seed, new variant, tuning, threshold selection, checkpoint selection, result-driven recalculation, or adaptive extension.

## Required Start

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git rev-parse HEAD
```

V68 completion commit: `805342be2aba7bc57cb41704903ec9f47a8f1482`.

Read `AGENTS.md`, `docs/PROJECT_CONTEXT.md`, `docs/EXPERIMENT_STATUS.md`, `docs/TASK_BLOCKER.md`, this task, the V40-V49 manuscript evidence and compile records, all active TriAir tables and figures, `main.tex`, `main_sivp_snjnl.tex`, `submission/sivp/**`, bibliography files, data/code availability statements, author declarations, and protected-file rules. Record the actual starting commit.

Stop on any frozen evidence mismatch, unexplained numerical drift, missing source dependency, unresolved citation, compile failure, or unauthorized MM-UAV inclusion.

## Frozen Evidence Boundary

Use only the already source-locked TriAir evidence in the active manuscript and submission package. Do not regenerate model metrics or select alternative checkpoints.

The active manuscript currently states, among other frozen results:

- three paired TriAir seeds for the main early-fusion versus reliability-aware comparison;
- component-disjoint development-validation and a locked 837-image within-dataset holdout;
- development-validation AP50:95 gain `0.0354 ± 0.0206` for the fixed full configuration over matched early fusion;
- locked-holdout AP50:95 gain `0.0062 ± 0.0187`, with mixed per-seed direction;
- three-seed development-validation static-control ablations;
- dynamic gating versus equal-weight stems: `+0.0621 ± 0.0188` AP50:95;
- dynamic gating versus deterministic learned projection: `+0.0404 ± 0.0074` AP50:95;
- modality-dropout change within the reliability-aware architecture: `-0.0095 ± 0.0258` AP50:95;
- hardware-specific RTX 3090 efficiency figures and the existing descriptive/no-external-generalization limitations.

Every manuscript number must trace to its existing source-locked table, JSON/CSV evidence, or compile record. No number may be changed merely to improve presentation.

## MM-UAV Exclusion Contract

V69 must verify that the active submission contains no MM-UAV dataset name, metric, method comparison, appendix, table, figure, citation claim, data-availability statement, or external-generalization implication.

The following V68 facts may appear only in internal audit records, not in the submission package:

- the V65-V67 matched two-seed results;
- the mixed reliability-minus-equal AP direction;
- learned MM-UAV fusion weights;
- the 320 x 320 one-pass aligned-feature Softplus protocol;
- any MM-UAV provider, path, archive, media, annotation, checkpoint, or local-only metadata.

Do not delete or rewrite historical V52-V68 evidence. Preserve it as internal research history.

## Required Manuscript Audit

Perform a source-backed, line-level audit of the complete submission package:

1. verify title, abstract, keywords, introduction contributions, method description, dataset protocol, results, discussion, limitations, declarations, data availability, and code availability are mutually consistent;
2. trace every headline number and table entry to frozen TriAir evidence;
3. verify all mean, sample-standard-deviation, delta, image-count, box-count, parameter, FLOP, latency, throughput, and memory values;
4. ensure development-validation, locked holdout, and independent/external test terminology are used correctly;
5. ensure the 837-image holdout is always described as a locked within-dataset holdout, never an external test set;
6. ensure all multi-seed conclusions remain descriptive and do not imply statistical significance;
7. ensure softmax fusion coefficients are described as adaptive representation weights, not calibrated physical sensor-health probabilities;
8. ensure modality dropout is not described as universally beneficial;
9. verify the stated architecture, input channels, resolution, seeds, epochs, checkpoint rule, thresholds, NMS, and evaluator semantics match the frozen TriAir protocol;
10. verify every table, figure, equation, section, bibliography entry, and cross-reference resolves;
11. remove obsolete comments, placeholders, duplicated prose, draft markers, internal paths, and unsupported claims;
12. confirm author names, affiliations, email, funding, competing interests, contributions, acknowledgments, data availability, and code availability are present without inventing missing facts.

Minor wording, formatting, cross-reference, bibliography, and source-package corrections are allowed when they do not alter the frozen scientific meaning.

## Compilation and Package Contract

Build the journal source using the repository's documented Springer/SIVP toolchain. At minimum:

- run a clean LaTeX/BibTeX compilation from the canonical submission root;
- require successful PDF generation;
- require zero undefined citations and zero undefined references;
- record warnings, overfull/underfull boxes, duplicate labels, font substitutions, missing files, and bibliography issues;
- visually inspect every rendered page for clipped text, broken equations, unreadable tables, missing figures, bad floats, inconsistent captions, and accidental blank pages;
- verify the source package contains every required `.tex`, `.bib`, table, figure, class/style, and support file and no unnecessary heavy experiment artifacts;
- verify the compiled PDF and source package correspond to the same commit and source manifest.

Do not commit generated auxiliary files unless repository policy explicitly requires them. Do not add raw data, annotations, checkpoints, optimizer states, predictions, tensors, local paths, or private correspondence.

## Submission-Readiness Checklist

Create a final checklist covering at least:

- journal/template identity and article type;
- title and short title;
- author order, corresponding author, affiliation, and email;
- abstract and keyword limits;
- figure/table placement, captions, resolution, and source availability;
- reference completeness and DOI/URL hygiene where already available;
- ethics, funding, competing interests, author contributions, acknowledgments, data availability, and code availability;
- dataset naming and citation consistency for TriAir;
- no MM-UAV inclusion;
- source package completeness;
- clean compile and rendered-page inspection;
- remaining items that require an author or journal-portal decision.

Do not invent ORCID IDs, postal codes, telephone numbers, suggested reviewers, editor names, cover-letter claims, ethics approvals, funding identifiers, or data-license terms.

## Decision States

Choose exactly one:

- `V69_TRIAIR_MANUSCRIPT_SUBMISSION_READY` — source, evidence, references, compilation, rendering, declarations, and package checks pass, with only journal-portal actions remaining;
- `V69_BLOCKED_EVIDENCE_OR_CLAIM_MISMATCH` — manuscript text or tables conflict with frozen TriAir evidence;
- `V69_BLOCKED_COMPILE_REFERENCE_OR_PACKAGE_FAILURE` — source does not compile cleanly or required files/references are missing;
- `V69_BLOCKED_AUTHOR_JOURNAL_OR_DATA_METADATA` — completion requires facts only the authors/provider/journal can supply;
- `V69_BLOCKED_PROTECTED_FILE_OR_SCOPE_VIOLATION` — unauthorized historical, experimental, or MM-UAV changes occurred.

No V69 outcome may authorize a new GPU experiment automatically.

## Required Outputs

Create `runs/v69_triair_manuscript_submission_readiness/` containing compact files such as:

```text
protocol.md
source_manifest.json
frozen_evidence_traceability.csv
headline_number_verification.json
claim_and_limitations_audit.md
mmuav_exclusion_audit.json
citation_reference_audit.json
compile_commands.txt
compile_output.txt
compile_warning_summary.json
rendered_page_review.md
submission_package_manifest.json
submission_readiness_checklist.md
protected_file_audit.json
test_commands.txt
test_output.txt
final_decision.json
handoff.md
```

When corrections are necessary and source-backed, update the canonical manuscript/submission files directly and record each change in the handoff. Preserve a before/after source fingerprint.

## Required Checks

- frozen TriAir evidence hashes and manuscript-source fingerprints are recorded before edits;
- every modified scientific sentence remains supported by existing evidence;
- all headline numbers and table values match their source records;
- no MM-UAV text or evidence enters the submission package;
- no unsupported external-generalization, significance, sensor-health, or universal-dropout claim remains;
- compilation succeeds from a clean state;
- citations and references resolve;
- rendered pages are inspected;
- source package is self-contained and free of heavy/private artifacts;
- relevant repository manuscript tests pass;
- final fingerprints and exact commands are saved.

## Allowed Changes

- `docs/NEXT_TASK.md`, `docs/EXPERIMENT_STATUS.md`, `docs/TASK_BLOCKER.md`, and `docs/NEXT_TASK_WRITE_RECORD.md`;
- `runs/v69_triair_manuscript_submission_readiness/**`;
- active TriAir manuscript and `submission/sivp/**` source files when required by the source-backed audit;
- bibliography, table, figure-reference, compilation-support, and manuscript-test files needed for a clean submission package;
- minimal documentation updates that do not change frozen experimental results.

## Forbidden Changes

- V40-V68 historical scientific evidence;
- raw data, annotations, checkpoints, predictions, tensors, and local-only artifacts;
- production detector/training/evaluator behavior;
- any new experiment, evaluation, seed, variant, tuning, threshold selection, or checkpoint selection;
- any MM-UAV manuscript inclusion before a separate provider-verifiable rights re-audit passes;
- invented author, journal, ethics, funding, license, citation, or dataset facts;
- strengthening claims beyond the frozen TriAir evidence.

## Completion

Update the four task/status files, V69 final decision, handoff, compile records, and submission checklist. Commit with:

`docs: finalize V69 TriAir manuscript submission readiness`
