# Current Task

## Authorization

V72 completed at commit `121d444e4885445e42f0755f7413c579e4ccf66e` with:

`V72_MMUAV_NAIVE_GRID_EXTERNAL_DOMAIN_STRESS_TEST_COMPLETE`

The fixed naive normalized-grid adapter, one 8-row smoke pass, and six one-time full `1,845`-row evaluations completed with finite outputs and no reruns, training, adaptation, calibration, tuning, or checkpoint substitution.

The active next task is:

`V73_TRIAIR_MANUSCRIPT_MMUAV_EXTERNAL_STRESS_TEST_INTEGRATION_AUTHORIZED`

V73 is a manuscript/result-integration task. It must convert the completed V72 evidence into an accurate appendix-level external-domain stress-test report and update the discussion/limitations accordingly. It must not run new experiments, search adapter variants, or turn the V72 result into an independent external-validation claim.

## Required Start

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git status --short
git rev-parse HEAD
```

Require a clean worktree. Record the actual starting commit and verify that V72 completion commit `121d444e4885445e42f0755f7413c579e4ccf66e` is an ancestor of `HEAD`.

Read `AGENTS.md`, `docs/PROJECT_CONTEXT.md`, the current task/status/blocker/write-record files, the active TriAir manuscript and bibliography, the V72 protocol, metrics, paired comparison, claim boundary, tests, and protected-file rules.

## Frozen V72 Evidence

Use only the committed V72 evidence. Do not recompute, round selectively, omit zero seeds, or substitute any result.

Dataset and protocol:

- MM-UAV exposed devval rows: `1,845`;
- sequences: `85`;
- ground-truth boxes: `4,198`;
- six frozen TriAir checkpoints;
- Early Fusion seeds `0`, `1`, `2`;
- reliability-aware RA-RepDet `p=0.15` seeds `0`, `1`, `2`;
- independently letterboxed RGB, IR, and event at `640 x 640`;
- five-channel input: RGB + IR grayscale + event grayscale;
- score threshold `0.001`;
- NMS `0.6`;
- maximum `100` detections per image;
- exactly one complete evaluation attempt per checkpoint.

Per-checkpoint metrics:

| Method | Seed | AP@[.50:.95] | AP50 | AP75 | AR1 | AR10 | AR100 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Early Fusion | 0 | `1.7089382511905107e-8` | `8.544691255952553e-8` | `0` | `0` | `0` | `4.764173415912339e-5` |
| Early Fusion | 1 | `1.1351352394448599e-8` | `1.1351352394448599e-7` | `0` | `0` | `0` | `2.3820867079561694e-5` |
| Early Fusion | 2 | `0` | `0` | `0` | `0` | `0` | `0` |
| RA-RepDet | 0 | `8.672098945411591e-8` | `5.150327766859084e-7` | `0` | `0` | `0` | `1.9056693663649358e-4` |
| RA-RepDet | 1 | `2.0756792660398117e-6` | `1.0378396330199058e-5` | `0` | `4.764173415912339e-5` | `4.764173415912339e-5` | `1.1910433539780849e-4` |
| RA-RepDet | 2 | `0` | `0` | `0` | `0` | `0` | `0` |

Three-seed AP@[.50:.95] summaries:

- Early Fusion mean: `9.48024496878457e-9`;
- Early Fusion sample standard deviation: `8.69698401219258e-9`;
- RA-RepDet mean: `7.208000851646425e-7`;
- RA-RepDet sample standard deviation: `1.174160691123537e-6`;
- paired `RA-RepDet - Early Fusion` mean: `7.11319840195858e-7`;
- paired sample standard deviation: `1.172256488694345e-6`.

All values are near zero. Relative ratios or positive paired differences must not be used to imply meaningful robustness or superiority.

## Required Manuscript Positioning

Use the following scientific label consistently:

`zero-shot external-domain stress test on the exposed MM-UAV devval split using a naive normalized-grid five-channel adapter`

The manuscript must state that:

1. the six checkpoints were frozen from TriAir training and received no MM-UAV training, fine-tuning, adaptation, calibration, or result-informed tuning;
2. the MM-UAV devval split had been exposed during prior engineering work and is therefore not an independent blind test;
3. each modality was independently mapped to a normalized canvas, without physical RGB/IR/event registration;
4. all six checkpoints produced nearly zero AP, despite finite predictions for every image;
5. the result indicates that severe sensor-grid and acquisition-domain mismatch dominates direct channel-level transfer under this adapter;
6. reliability-aware fusion alone does not overcome unregistered cross-sensor geometry;
7. the experiment is a negative stress-test result and not evidence of successful external generalization.

Do not use any of the following descriptions:

- independent external validation;
- blind external test;
- official MM-UAV test result;
- physically registered multimodal validation;
- robust cross-dataset generalization;
- significant or stable external improvement.

## Required Manuscript Changes

1. Add an appendix or supplementary subsection devoted to the V72 external-domain stress test.
2. Add one compact per-checkpoint table containing all six AP/AR records.
3. Add a short aggregate paragraph with the two method means, sample standard deviations, and paired mean difference.
4. Add a protocol paragraph covering the exposed split, frozen checkpoints, naive normalized-grid adapter, inference thresholds, and no-adaptation boundary.
5. Add a limitations paragraph explaining the absence of physical registration and the near-zero outcome.
6. Add one concise sentence to the main discussion or limitations section directing readers to the appendix and stating that direct unregistered cross-sensor transfer failed.
7. Do not place the result in the abstract, headline contribution list, primary TriAir performance table, or conclusion as a positive validation claim.
8. Use an existing MM-UAV bibliography entry when one is already present. Do not invent bibliographic metadata. If the manuscript lacks an established entry, leave one explicit internal citation placeholder in the draft and record it in the V73 checklist without delaying the result integration.

## Interpretation Boundary

The allowed interpretation is:

> Under an intentionally simple, parameter-free normalized-grid adapter, frozen TriAir models did not transfer meaningfully to the exposed MM-UAV devval domain. The experiment isolates a severe cross-sensor geometry/domain mismatch and motivates alignment-aware cross-domain methods; it does not invalidate the in-domain TriAir results.

Do not claim that V72 proves RA-RepDet is worse than Early Fusion, proves the architecture cannot generalize under any adapter, or establishes a dataset-wide conclusion beyond this protocol.

## Validation and Build

After manuscript edits:

1. verify every inserted number against `runs/v72_mmuav_naive_grid_external_domain_stress_test/per_checkpoint_metrics.json` and `paired_seed_comparison.json`;
2. search the manuscript for prohibited labels and overclaims;
3. verify that TriAir in-domain metrics and prior tables are unchanged;
4. run the repository's clean LaTeX/BibTeX build procedure;
5. require zero undefined references or citations, except a single explicitly tracked MM-UAV citation placeholder when no existing bibliography entry exists;
6. inspect every rendered page containing the new table or text for overflow, clipping, illegible scientific notation, orphaned headings, or broken cross-references;
7. run protected-file and compact-artifact checks.

## Required Outputs

Create `runs/v73_triair_manuscript_mmuav_stress_test_integration/` containing compact records such as:

```text
protocol.md
v72_evidence_lock.json
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

Do not add raw data, predictions, checkpoints, rendered-page raster dumps, local absolute paths, credentials, or heavy/private artifacts to Git.

## Decision States

Choose exactly one:

- `V73_TRIAIR_MANUSCRIPT_MMUAV_STRESS_TEST_INTEGRATED`;
- `V73_BLOCKED_MANUSCRIPT_SOURCE_OR_BUILD_CONTRACT`;
- `V73_BLOCKED_RESULT_TRACEABILITY_OR_CLAIM_AUDIT`;
- `V73_BLOCKED_TABLE_LAYOUT_OR_RENDERING`;
- `V73_BLOCKED_SOURCE_PROTECTED_OR_PRIVATE_ARTIFACT_VIOLATION`.

A missing established MM-UAV citation may remain as one explicit internal draft placeholder and is not by itself a reason to omit the completed experiment from the research manuscript branch.

## Forbidden Work

- new training, inference, evaluation, adapter variants, thresholds, seeds, checkpoints, or datasets;
- result-driven reruns or metric modification;
- presenting V65-V67 MM-UAV-trained results as zero-shot external validation;
- changing TriAir in-domain results or model definitions;
- upgrading the V72 result into an independent/blind/official external-validation claim;
- public release or final submission authorization solely from V73.

## Completion

Commit with exactly:

`docs: integrate V72 MM-UAV external-domain stress test into manuscript`

Push to `research/ra-repdet-triair`.