# Experiment Status

Updated: 2026-07-22

## Active task

`V65_COMPLETE_NO_FURTHER_GPU_STAGE_AUTHORIZED`

## V65 result

V65 completed with the preregistered outcome:

`V65_FULLTRAIN_COMPLETE_NONZERO_AP`

The exact historical seed-0 equal-fusion initialization was strictly loaded into one Softplus model. The complete frozen 7,187-row V57 order was consumed exactly once, followed by one final-checkpoint-only evaluation on all 1,845 frozen devval rows.

Final COCO-style metrics were AP@[0.50:0.95] `0.0363043928`, AP50 `0.1493416683`, AP75 `0.0035733839`, AR@1 `0.0501429252`, AR@10 `0.0753692234`, and AR@100 `0.0815388280`.

## Geometry and safety

- All ten scheduled audits through step 7,187 were `GEOMETRY_AND_GRADIENT_PRESERVED`.
- Final compact train/devval geometry was `272,000 / 272,000` valid boxes for each subset.
- Optimizer steps: `7,187 / 7,187`; unique ordered rows: `7,187 / 7,187`.
- Diagnostic backward calls: `40 / 40`.
- Verified recovery snapshots: `19 / 19`; recovery events: `0`.
- Full-devval evaluation attempts: `1`; evaluated rows: `1,845`.
- All finite-state, source-lock, initialization, protected-file, and diagnostic-isolation checks passed.
- Post-run tests: `10 / 10` passed.
- No tuning, threshold selection, checkpoint selection, extra variant, extra seed, rerun, or automatic extension occurred.

## Claim boundary

V65 provides a single-seed equal-fusion Softplus feasibility and performance signal. It does not establish superiority over ReLU, reliability fusion, other seeds, an independent test set, or an external dataset, and it does not authorize a manuscript comparison claim by itself. No further GPU experiment is currently authorized.
