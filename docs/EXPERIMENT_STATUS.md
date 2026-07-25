# Experiment Status

Updated: 2026-07-25

## Active task

`V68_MMUAV_MANUSCRIPT_EVIDENCE_AUDIT_AUTHORIZED`

## V67 completion evidence

V67 completed successfully at commit `305a49f06483923eadf7c2a60048a2ca51e7743c` with `V67_TWO_SEED_RELIABILITY_FULLTRAIN_COMPLETE`.

- Seed 0 reliability AP: `0.0404763204`; matched reliability-minus-equal delta: `+0.0041719276`.
- Seed 1 reliability AP: `0.0025823958`; matched delta: `-0.0004533834`.
- Reliability AP mean/sample standard deviation: `0.0215293581 / 0.0267950511`.
- Equal-fusion AP mean/sample standard deviation: `0.0196700860 / 0.0235244622`.
- Mean matched AP delta: `+0.0018592721`.
- All 14,374 optimizer steps, 80 diagnostic backward calls, 38 recovery snapshots, 20 audits, two final-checkpoint-only full-devval evaluations, and 10/10 tests completed under the frozen contract.

The paired direction is mixed and the seed sensitivity is large. V67 therefore supports a descriptive matched devval comparison, not a stable superiority claim.

## V68 authorized work

V68 is a CPU/documentation-only evidence-readiness gate. It will verify V65-V67 evidence, generate an exact paper table and claim matrix, compare the MM-UAV and TriAir protocols, audit data rights/citation requirements, and decide whether the MM-UAV evidence belongs in an appendix, should remain internal, or is blocked by provenance/permission gaps.

No CUDA work, experiment rerun, additional seed/variant, tuning, threshold selection, checkpoint selection, or automatic manuscript performance claim is authorized.

`main.tex`, `submission/**`, production model behavior, and historical evidence remain protected. Appendix-ready text may be created only as a separate draft under `manuscript/v68_mmuav_extension_draft/**`.
