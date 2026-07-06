# V40 Compute-Minimized Evidence Plan

## Why this addendum exists

The prior V39 core rerun consumed substantial compute. V40-v2 cannot reuse V39 checkpoints as V40 headline evidence because the accepted V40-v2 split moves 122 samples relative to V39; the V40-v2 validation partition therefore differs from the training/validation exposure of the existing V39 models.

This addendum reduces the required new training burden while preserving a defensible validation-only paper path. It supersedes the all-dropout-condition V40 core rerun requirement in Gate 2 of `docs/PRE_MANUSCRIPT_V40_MASTER_PLAN.md`.

## Fixed primary comparison

Do not run V40 p=0.00 or p=0.20 conditions.

Pre-specify the reliability-aware configuration with dropout `p=0.15` before any V40 result is viewed. Its choice is based only on archived prior development evidence and must not be presented as V40 optimization or as the best dropout probability.

Run exactly four V40-v2 core trainings after the experiment contract is ready:

1. matched early fusion, seed 0;
2. matched early fusion, seed 2;
3. reliability-aware fusion with p=0.15, seed 0;
4. reliability-aware fusion with p=0.15, seed 2.

Use the same frozen training/evaluation contract for all four runs. Report two-run mean and run range. Do not select a configuration from V40 results because p=0.15 is pre-specified.

The V40 paper claim must be limited to comparison of matched early fusion against one pre-specified reliability-aware configuration. Do not claim a V40 dropout sweep, a V40-optimal dropout rate, or superiority over p=0.00/p=0.20.

## Minimum non-training evidence after the four core runs

Before manuscript drafting, complete:

- synthetic channel-removal evaluation for the two early and two p=0.15 checkpoints;
- standardized efficiency comparison for early and p=0.15;
- image-level 2000-resample bootstrap for early versus p=0.15;
- deterministic non-cherry-picked qualitative package;
- reproducibility bundle, provenance/data-availability ledger, and documentation cleanup;
- final pre-manuscript readiness report.

These tasks do not require another full model-training matrix.

## Optional strengthening, not a hard blocker

A static-global-weight fusion control and trained single-modality detectors improve mechanism attribution and tri-modal interpretation, but they are not required for the compute-minimized validation-only path. They may be added before submission if resources permit, or reported later as limitations/future work.

Do not silently use inference-only channel removal as a replacement for trained single-modality baselines.

## Guardrails

- V40-v2 manifests only; never use V39 or guard manifests for V40 result reporting.
- Do not reuse V39 metrics as V40 metrics.
- Do not use DroneVehicle or other external data.
- Do not edit the manuscript before the final readiness report.
- Do not claim independent testing, leakage-free data, verified temporal metadata, physical sensor-failure robustness, or a V40 hyperparameter sweep.

## Next task

Complete the experiment contract first. After it reports `V40_EXPERIMENT_CONTRACT_READY`, create and execute a four-run V40-v2 core-rerun task matching this addendum.
