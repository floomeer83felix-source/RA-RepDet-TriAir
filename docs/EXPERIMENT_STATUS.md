# Experiment Status

Updated: 2026-07-20

## Active task

`V62_CONTROL_AND_POSITIVE_BIAS_BOTH_COLLAPSE`

## V62 outcome

V62 completed the clean paired 500+500 pilot from the exact historical V57 seed-0 initialization. The trace-only target mover accepted the actual V61 failing row `devval:00005919` without changing boxes or labels, while the historical optimization helper remained train-only. All 24 scheduled recovery snapshots were atomically written and round-trip verified; no recovery event was needed.

The selected frozen outcome is `V62_CONTROL_AND_POSITIVE_BIAS_BOTH_COLLAPSE`.

## Paired result

- Both variants were `GEOMETRY_AND_GRADIENT_PRESERVED` at steps 0, 1, and 2.
- Both variants first met strict `EARLY_BBOX_COLLAPSE` at step 20: zero valid boxes on the frozen 32-row train subset and zero bbox output-layer gradients on all four frozen probe rows.
- Control remained collapsed at every later trace through step 500.
- The `+0.01` intervention had five valid boxes at step 50 but zero probe gradients, so that trace was `NEITHER_PREREGISTERED_STATE`; it returned to strict collapse at step 100 and remained collapsed through step 500.
- At step 500, both variants produced `0 / 272,000` valid train boxes and `0 / 272,000` valid frozen-devval boxes.
- The exact `+0.01` four-element initial bbox-output bias did not prevent the early V57 geometry/gradient collapse.

## Budgets and safety

- Optimizer steps: control/intervention/total `500 / 500 / 1,000`.
- No-step diagnostic backward calls: `96 / 96`.
- Verified atomic recovery snapshots: `24`; recovery events: `0`.
- Frozen devval geometry rows: `32` per variant at step 500; full-devval rows: `0`.
- AP/AR, threshold selection, tuning, early stopping, and checkpoint selection: none.
- All losses, gradients, parameters, geometry summaries, and recovery checks were finite.
- Reliability scorer remained dormant and unchanged in both equal-fusion variants.
- V61 blocked evidence and the protected V40-V61/V51/production/manuscript/submission fingerprint remained unchanged.

## Local checkpoints

- Control SHA256: `644b26444f09707aa463658c2437585dc8664f237cd0dea006995312b77c097f`.
- `+0.01` SHA256: `8980901d2a4d8e137cb44d36f34139ef97ef4eba57b733f6e414448a41c100a4`.

Checkpoints and recovery snapshots remain local under `D:\MM-UAV_v62_local` and are not committed.

## Reproducibility limitation

PyTorch warned that CUDA affine-grid/grid-sampler backward and CuBLAS operations are not strictly deterministic under the current environment. V62 is therefore bounded single-run, single-seed engineering evidence. The clean pair used identical frozen order/configuration and passed all internal state-isolation checks, but bitwise reproduction on another CUDA run is not claimed.

## Authorization boundary

V62 does not authorize a bias sweep, another initialization intervention, activation/loss changes, a full 7,187-step run, AP/AR evaluation, reliability-fusion claims, or manuscript changes. Any next experiment requires a separately frozen task and explicit GPU authorization.
