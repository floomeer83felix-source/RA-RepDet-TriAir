# Experiment Status

Updated: 2026-07-29

## Active status

`V76_MAJOR_REVISION_EXISTING_EVIDENCE_INTEGRATED_SINGLE_MODALITY_EXECUTION_AUTHORIZED`

## Major-revision evidence integration

The active manuscript now integrates the completed three-seed TriAir evidence that was omitted from V75:

| Evidence | Status | Key result |
| --- | --- | --- |
| V48 component-disjoint causal ablation | complete | full reliability minus matched early AP `+0.0354 ± 0.0206` |
| V48 dynamic gate versus fixed equal stems | complete | AP `+0.0621 ± 0.0188` |
| V48 dynamic gate versus learned deterministic projection | complete | AP `+0.0404 ± 0.0074` |
| V48 dropout increment inside dynamic gate | complete | AP `-0.0095 ± 0.0258` |
| V42 locked 837-image internal holdout | complete | AP50 `+0.0086 ± 0.0062`, positive in all three seed pairs |
| V75 corrected MM-UAV seed-level transfer | complete | best AP `0.2503 ± 0.0025` |

The manuscript no longer states that static fusion controls are absent. It distinguishes component-disjoint development-validation, locked internal holdout, and supervised exposed MM-UAV devval.

## New experiment authorization

The user explicitly authorized the missing experiments. The frozen V76 extension is:

- RGB-only, seeds 0, 1, 2;
- thermal-only, seeds 0, 1, 2;
- event-only, seeds 0, 1, 2.

All nine runs use the frozen V40 component-disjoint train/validation manifests, 50 epochs, batch size 4, image size 640, AdamW learning rate `1e-4`, no modality dropout, checkpoint retention by development-validation project-local AP50, and one standardized COCO evaluation per retained checkpoint.

No dropout sweep, schedule tuning, selective seed replacement, result-driven rerun, guard access, or public-test claim is authorized.

## Current execution boundary

The manuscript integration, code package, syntax audit, LaTeX build, and rendered-page audit are complete. The nine GPU runs are not complete because this ChatGPT execution environment does not contain the private TriAir dataset or the authorized RTX 3090 workspace. Results must not be invented.

## Validation

- revised PDF pages: `14`;
- two pdfLaTeX passes: `PASS`;
- undefined citations/references: `0`;
- overfull boxes: `0`;
- rendered-page audit: `PASS`;
- experiment package Python compile: `PASS`;
- protected training-core files changed: `false`.

## Article evaluation

Updated readiness: `4.2 / 5`. The principal remaining experimental requirement is the frozen nine-run single-modality table. Author declaration and exact local TriAir provenance also require closure.
