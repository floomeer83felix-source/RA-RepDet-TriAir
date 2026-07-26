# Task Blocker

Status: `V72_IMMEDIATE_EXPERIMENT_AUTHORIZED_NO_PREFLIGHT_BLOCKER`

Generated: 2026-07-26

## Current state

V71 completed with `V71_BLOCKED_ADAPTER_OR_ONTOLOGY_CONTRACT` only because it required a defensible physically aligned parameter-free five-channel adapter.

The user has directed the project to run the MM-UAV external-domain experiment immediately. V72 therefore replaces the physical-registration requirement with one predeclared naive normalized-grid assumption.

## Authorized immediate path

V72 must:

1. use the exact frozen `1,845`-row devval manifest;
2. use the six V71-verified frozen TriAir checkpoints;
3. reuse V53 independent modality decoding and letterbox;
4. independently letterbox RGB, IR, and event to `640 x 640`;
5. concatenate RGB + IR grayscale + event grayscale;
6. use RGB annotation geometry;
7. run one fixed 8-row no-metric smoke pass;
8. immediately run all six full-devval evaluations;
9. compute AP/AR and matched three-seed comparisons;
10. stop without result-driven tuning or reruns.

No provider, release, rights, calibration, or official-test research is required before V72 execution.

## Explicit limitation

The adapter does not establish physical RGB/IR/event pixel correspondence. This is not a runtime blocker. It must be disclosed as the central limitation of the stress-test result.

## Actual fail-closed conditions

Stop only if:

- the frozen manifest or six checkpoints fail identity/strict-load verification;
- the fixed adapter implementation is non-deterministic or cannot produce finite five-channel tensors;
- inputs are missing, corrupt, unreadable, or non-finite;
- inference/decoding/evaluator values become non-finite;
- OOM or unrecoverable runtime failure prevents a complete checkpoint metric record;
- evaluator constants or metric outputs differ from the frozen contract;
- unauthorized training, adaptation, tuning, checkpoint substitution, seed/variant addition, or result-driven rerun occurs;
- protected paths drift or private/heavy artifacts enter Git.

Physical-registration uncertainty alone must not stop V72.

## Next action

Execute `docs/NEXT_TASK.md` now. After the fixed 8-row smoke pass, launch the six checkpoint evaluations without waiting for any additional scientific, provider, or documentation review.