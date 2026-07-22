# Experiment Status

Updated: 2026-07-22

## Active task

`V65_MMUAV_SEED0_SOFTPLUS_FULLTRAIN_DEVVAL_FEASIBILITY_AUTHORIZED`

## User authorization

The user reported that V64 completed, was pushed, and the completion-state audit was executed. Under the standing automatic task-handoff workflow, V65 is authorized as the next bounded stage: one complete seed-0 equal-fusion Softplus training pass followed by one final-checkpoint-only full-devval evaluation.

The standing local/private-research instruction remains frozen and must not be repeatedly reconfirmed.

## Frozen V63/V64 evidence

- V63 completion commit: `83bb9351a5d0a6115d81047482e23fef5eed26bb`.
- V63 outcome: `V63_RELU_COLLAPSE_REPRODUCED_SOFTPLUS_PRESERVES_THROUGH_STEP200`.
- V64 completion commit: `402eabb23896f7908b6a3eccd4d394d3ce41d487`.
- V64 outcome: `V64_SEED1_RELU_CONTROL_COLLAPSE_NOT_REPRODUCED_WITHIN_200_STEPS`.
- V64 seed-1 ReLU and Softplus were both geometry-and-gradient preserved at all thirteen traces through step 200.
- V64 therefore establishes bounded initialization sensitivity, not independent confirmation of a universal ReLU-collapse contrast.
- V63 and V64 both showed exact Softplus remained preserved through step 200.
- V64 completed 400/400 optimizer steps, 104/104 diagnostic backward calls, 26 verified recovery snapshots, and 10/10 post-run tests.

## V65 authorized run

Run exactly one variant:

`v65_seed0_equal_softplus_b1_t20_fulltrain`

Frozen configuration:

- exact historical seed-0 initialization SHA256 `846da59cc8d908dfeb429fca2acb4985e73ff5fda3915154f9f764c571977cb9`;
- exact historical 7,187-row V57 order, consumed once without reshuffle or repetition;
- alignment enabled;
- exact equal fusion `[1/3, 1/3, 1/3]`;
- reliability scorer dormant;
- exact parameter-free `softplus(beta=1.0, threshold=20.0)` in the shared training/inference bbox-distance path;
- FP32 AdamW, LR `1e-4`, weight decay `1e-4`;
- exactly 7,187 optimizer steps;
- compact geometry/gradient audits at steps `0, 15, 50, 200, 500, 1000, 2000, 4000, 6000, 7187`;
- maximum 40 diagnostic backward calls;
- one full 1,845-row devval evaluation using only the final step-7,187 checkpoint.

## Evidence and safety boundary

V65 may compute final COCO-style AP/AR metrics only after all training steps complete. It may not tune thresholds, select checkpoints, run extra variants or seeds, rerun after observing metrics, train the ReLU control, activate reliability fusion, or modify model/loss/matching/decode/evaluator semantics.

A successful V65 result is a single-seed equal-fusion feasibility and performance signal. It does not establish superiority, generalization, a final paper comparison, or an independent-test result.

## Allowed completion states

- `V65_FULLTRAIN_COMPLETE_NONZERO_AP`
- `V65_FULLTRAIN_COMPLETE_ZERO_AP`
- `V65_FULLTRAIN_BBOX_COLLAPSE`
- `V65_BLOCKED_SOURCE_INITIALIZATION_OR_EVALUATOR_CONTRACT`
- `V65_BLOCKED_TRAINING_TRACE_OR_RECOVERY_INCOMPLETE`
- `V65_BLOCKED_OOM_OR_NUMERICAL_INSTABILITY`
- `V65_BLOCKED_FULL_DEVVAL_EVALUATION`
- `V65_BLOCKED_TEST_OR_PROTECTED_FILE_VIOLATION`
