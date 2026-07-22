# Task Blocker

Status: `V65_FULLTRAIN_SOFTPLUS_AUTHORIZED_NO_ACTIVE_PREFLIGHT_BLOCKER`

Generated: 2026-07-22

## Current state

V64 completed successfully with `V64_SEED1_RELU_CONTROL_COLLAPSE_NOT_REPRODUCED_WITHIN_200_STEPS`.

The seed-1 ReLU and Softplus variants were both geometry-and-gradient preserved through step 200. This means the V63 seed-0 ReLU collapse was not independently reproduced and the bounded mechanism is initialization-sensitive. This is a scientific result, not an engineering blocker.

V65 is now authorized as the fastest paper-relevant next gate: one seed-0 equal-fusion Softplus model trained for the complete frozen 7,187-row order, followed by one full 1,845-row devval evaluation using only the final checkpoint.

## Authorized boundary

V65 may:

- verify V63/V64 and all earlier evidence without mutation;
- reconstruct the exact frozen seed-0 common initialization;
- train one equal-fusion, alignment-on, dormant-scorer Softplus model for exactly 7,187 optimizer steps;
- consume the complete frozen historical order exactly once;
- perform the ten registered geometry/gradient audits and at most 40 no-step diagnostic backward calls;
- save and verify local recovery snapshots;
- evaluate the final step-7,187 checkpoint once on all 1,845 frozen devval rows;
- report fixed COCO-style AP/AR and prediction-safety metrics;
- commit compact source, tests, hashes, logs, statistics, and conclusions.

V65 may not:

- initialize from any trained V55-V64 checkpoint;
- run a ReLU full-training control;
- activate or train the reliability scorer;
- modify loss, target, matching, anchors, scale, clipping, decode, threshold, NMS, preprocessing, detector, evaluator, alignment, or equal-fusion behavior;
- tune thresholds, select checkpoints, stop based on devval metrics, run extra seeds/variants, rerun after observing results, or automatically extend the budget;
- modify production TriAir defaults, historical evidence, V51, manuscript, submission, raw data, or annotations;
- put checkpoints, optimizer states, recovery snapshots, raw predictions, tensors, images, feature maps, or other heavy artifacts in Git.

## Fail-closed blockers

Stop with the matching V65 blocked state on:

1. prior evidence, source, manifest, order, subset, initialization, evaluator, or protected-file mismatch;
2. incorrect Softplus parameters, source location, call count, or train/inference asymmetry;
3. any forbidden model, loss, matching, decode, evaluator, alignment, fusion, or scorer difference;
4. repeated, substituted, replayed, or skipped training rows or optimizer steps;
5. more than 7,187 optimizer steps or more than 40 diagnostic backward calls;
6. invalid recovery snapshots or diagnostic mutation of persistent state;
7. OOM or non-finite training, geometry, prediction, metric, or recovery value;
8. full-devval evaluation before the final checkpoint;
9. tuning, checkpoint selection, extra variant/seed, rerun, reliability-fusion training, or automatic extension;
10. protected-file or heavy-artifact Git violation.

## Next action

Execute V65 exactly as written in `docs/NEXT_TASK.md`. First complete all CPU source-lock, seed-0 initialization, full-order, recovery, and evaluator-contract tests. Then run the exact 7,187-step Softplus training pass and evaluate only the final checkpoint on full devval.
