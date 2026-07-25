# Current Task

## Authorization

The user reported that V67 completed and was pushed. Under the standing automatic task-handoff workflow, the user authorizes **V68 MM-UAV manuscript-evidence audit and integration gate** under the standing local/private-research-only rule.

V68 is a CPU/documentation task. It authorizes no CUDA training, evaluation rerun, new seed, new variant, tuning, threshold selection, checkpoint selection, or adaptive extension.

V65-V67 are frozen scientific evidence. V65/V66 provide the matched two-seed equal-fusion Softplus baseline; V67 provides the matched two-seed image-conditioned reliability-fusion Softplus comparison.

## Required Start

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git rev-parse HEAD
```

V67 completion commit: `305a49f06483923eadf7c2a60048a2ca51e7743c`.

Read `AGENTS.md`, project/status/blocker files, all V52-V67 evidence and handoffs, the current manuscript sources, data-availability statements, license/provenance records, and protected-file rules. Record the actual starting commit. Stop on evidence mismatch, missing provenance, or protected-file drift.

## Frozen V65-V67 Evidence

Verify without modification:

- equal fusion seed 0 AP/AP50/AP75: `0.0363043928 / 0.1493416683 / 0.0035733839`;
- equal fusion seed 1 AP/AP50/AP75: `0.0030357792 / 0.0174066630 / 0.0003960396`;
- reliability fusion seed 0 AP/AP50/AP75: `0.0404763204 / 0.1567504662 / 0.0056653983`;
- reliability fusion seed 1 AP/AP50/AP75: `0.0025823958 / 0.0139110456 / 0.0002883784`;
- matched AP deltas: seed 0 `+0.0041719276`, seed 1 `-0.0004533834`;
- mean matched AP delta: `+0.0018592721`;
- equal-fusion AP mean/sample standard deviation: `0.0196700860 / 0.0235244622`;
- reliability-fusion AP mean/sample standard deviation: `0.0215293581 / 0.0267950511`;
- reliability devval mean RGB/IR/event weights: seed 0 `0.5550344586 / 0.1881090552 / 0.2568564415`, seed 1 `0.5600358248 / 0.1698493063 / 0.2701148987`;
- all four full runs completed 7,187 ordered steps, final-checkpoint-only full-devval evaluation, finite-state checks, and frozen safety contracts;
- V67 completed 14,374 optimizer steps, 80 diagnostic backward calls, 38 verified recovery snapshots, 20 preserved audits, and 10/10 tests.

Do not recompute, pool checkpoints, select the better seed, relabel outcomes, or infer significance.

## Required Audit

Create a compact, source-backed paper-evidence package that:

1. verifies hashes and decision records for V65, V66, and V67;
2. builds one exact matched table containing per-seed AP, AP50, AP75, AR@1, AR@10, AR@100, method means, sample standard deviations, and reliability-minus-equal deltas;
3. documents the mixed direction of the paired result and the large initialization sensitivity;
4. summarizes the learned fusion-weight behavior without interpreting the weights as calibrated sensor reliability;
5. compares the MM-UAV protocol with the current TriAir manuscript protocol;
6. explicitly records that MM-UAV used a 320x320, one-pass, aligned-feature, Softplus path and therefore is not an exact external replication of the 640x640, 50-epoch TriAir headline configuration;
7. audits dataset name, provider, citation, license, research-use permission, reporting permission, and redistribution restrictions from available records;
8. checks whether aggregate metrics and methodological descriptions may legally and ethically appear in a submission;
9. creates a claim matrix with allowed, disallowed, and qualification-required statements;
10. recommends inclusion, appendix-only inclusion, or exclusion from the current manuscript.

## Claim Boundary

Allowed only when supported and qualified:

- V65-V67 form a matched two-seed MM-UAV devval stress test;
- both fusion methods completed the frozen protocol with finite nonzero AP;
- the reliability scorer learned non-uniform weights;
- the paired AP effect was positive for seed 0 and negative for seed 1;
- the mean paired delta was small and descriptive.

Forbidden claims include:

- reliability fusion consistently or significantly improves MM-UAV performance;
- V67 proves external generalization of the TriAir headline model;
- the softmax weights measure physical sensor health;
- the MM-UAV result is an independent test-set result;
- the result supports broad robustness or deployment claims.

## Decision States

Choose exactly one:

- `V68_MMUAV_APPENDIX_READY_DESCRIPTIVE_STRESS_TEST` — evidence and rights are sufficient for a carefully qualified appendix or supplementary subsection;
- `V68_MMUAV_INTERNAL_ONLY_EXCLUDE_FROM_CURRENT_MANUSCRIPT` — evidence is valid but too weak, too protocol-divergent, or too distracting for the current paper;
- `V68_BLOCKED_DATA_RIGHTS_OR_CITATION_INCOMPLETE` — provenance, citation, or reporting permission is unresolved;
- `V68_BLOCKED_EVIDENCE_OR_MANUSCRIPT_CONTRACT_MISMATCH` — frozen evidence or manuscript-source contracts do not match.

No decision may authorize additional GPU work automatically.

## Required Outputs

Create `runs/v68_mmuav_manuscript_evidence_audit/` containing compact files such as:

```text
protocol.md
source_evidence_manifest.json
v65_v66_v67_hash_verification.json
matched_metrics_table.csv
matched_metrics_table.md
fusion_weight_summary.json
protocol_difference_matrix.md
claim_matrix.md
data_rights_and_citation_audit.md
manuscript_inclusion_recommendation.md
final_decision.json
handoff.md
```

If and only if the decision is appendix-ready, create draft-only manuscript material under `manuscript/v68_mmuav_extension_draft/`, including a concise subsection, table source, limitations paragraph, and proposed data-availability amendment. Do not modify `main.tex`, `submission/**`, or the active compiled manuscript in V68.

## Required Checks

- all reported numbers must trace exactly to immutable V65-V67 files;
- table arithmetic must be independently reproduced and checked;
- no result may be rounded inconsistently across artifacts;
- no raw data, annotations, images, predictions, checkpoints, or local paths may enter the manuscript draft;
- no stronger claim than the frozen evidence boundary may appear;
- production, historical evidence, manuscript, and submission fingerprints must remain unchanged;
- run repository tests relevant to evidence parsing and protected-file integrity.

## Allowed Changes

- current task/status/blocker/write-record files;
- `runs/v68_mmuav_manuscript_evidence_audit/**`;
- optional draft-only files under `manuscript/v68_mmuav_extension_draft/**`;
- V68-only evidence parsing and validation tests.

## Forbidden Changes

CUDA work, new training/evaluation, new seeds or variants, tuning, threshold/checkpoint selection, historical V40-V67 evidence, raw data/annotations, production model behavior, `main.tex`, `submission/**`, and active manuscript tables or figures.

## Completion

Update status, blocker, write record, final decision, and handoff. Commit with:

`docs: audit V68 MM-UAV manuscript evidence readiness`
