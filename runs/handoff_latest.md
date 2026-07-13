# RA-RepDet-TriAir Handoff

Generated: 2026-07-13T14:43:49+08:00

## Current task

- Title: V48 complete three-seed causal ablations, static fusion controls, and efficiency profiling
- Status: `V48_CAUSAL_ABLATION_COMPLETE`
- Source lock: `runs/v48_complete_ablation/source_lock_v48.json` at `3d18bcc1ed402776c43b1a9aaa022ffeb3416952`.
- Fresh runs complete: `10/10`.
- Checkpoint selection: development-validation project-local AP50 only.
- Locked holdout: not accessed by V48 variants.

## Run state

- `ra_no_moddrop_seed1`: `COMPLETE`.
- `ra_no_moddrop_seed2`: `COMPLETE`.
- `early_moddrop_seed1`: `COMPLETE`.
- `early_moddrop_seed2`: `COMPLETE`.
- `ra_static_equal_seed0`: `COMPLETE`.
- `ra_static_equal_seed1`: `COMPLETE`.
- `ra_static_equal_seed2`: `COMPLETE`.
- `ra_stems_project_seed0`: `COMPLETE`.
- `ra_stems_project_seed1`: `COMPLETE`.
- `ra_stems_project_seed2`: `COMPLETE`.

## Preserved evidence

- V46 COCO and seed0 ablation package preserved: `True`.
- V47 manuscript/compile package preserved: `True`.
- V48 uses development-validation evidence only; causal language remains bounded by completed shared seeds and static-control design.

## Next actions

- Continue only the pending source-locked V48 queue entries.
- Regenerate summary, claim scan, preflight, and efficiency artifacts after each completed seed block.
- Do not read or generate a V48 locked-holdout artifact.
