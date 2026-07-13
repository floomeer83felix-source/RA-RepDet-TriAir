# RA-RepDet-TriAir Handoff

Generated: 2026-07-13

## Current task

- Title: V49 integrate COCO metrics, causal ablations, and efficiency evidence into the SIVP manuscript
- Status: `V49_MANUSCRIPT_INTEGRATION_DRAFT_COMPLETE_COMPILE_PENDING`
- Training/evaluation performed in V49: `False`
- New holdout access in V49: `False`
- Active blocker: fresh Springer/BibTeX compile and rendered-page inspection

## Preserved evidence

- V46 canonical COCO fixed-checkpoint package: preserved.
- V47 structure and 40-reference package: preserved.
- V48 complete three-seed causal ablation and efficiency package: preserved.

## Manuscript files updated

- `submission/sivp/tex/main.tex`
- root `main.tex`
- root `main_sivp_snjnl.tex`
- `submission/sivp/tex/ra_repdet_sivp.tex`
- `submission/sivp/tables/Table_2_implementation_and_reproducibility.tex`

## New tables

- `submission/sivp/tables/Table_10_coco_fixed_checkpoint_summary.tex`
- `submission/sivp/tables/Table_11_three_seed_causal_ablation.tex`
- `submission/sivp/tables/Table_12_efficiency_profile.tex`

## Integrated scientific interpretation

- Fixed full RA `p=0.15` versus matched early:
  - development-validation AP50:95 delta: `+0.035350 ± 0.020586`;
  - locked same-dataset holdout AP50:95 delta: `+0.006195 ± 0.018737`, mixed across seeds;
  - locked-holdout AP50 delta remains positive for all three seeds.
- Cleanest dynamic-gating contrasts on development-validation:
  - versus static equal stems: `+0.062055 ± 0.018781` AP50:95;
  - versus deterministic learned projection: `+0.040376 ± 0.007357` AP50:95.
- Modality dropout increment within RA:
  - `-0.009542 ± 0.025797` AP50:95;
  - manuscript no longer claims optimal or universally beneficial dropout.
- Efficiency:
  - +1684 parameters;
  - +0.630 GFLOPs;
  - +0.2748 ms mean latency on RTX 3090;
  - peak allocated memory increases from 122.49 to 236.40 MiB.

## Claim boundary

The manuscript remains descriptive and within TriAir. It does not claim external generalization, statistical significance, universal causal proof, calibrated sensor reliability, real sensor-fault robustness, or V48 ablation holdout performance.

## Reports

- `runs/v49_manuscript_integration/V49_MANUSCRIPT_INTEGRATION_REPORT.md`
- `docs/TASK_BLOCKER.md`

## Next action

Compile `submission/sivp/tex/main.tex` with the Springer `sn-jnl` package and BibTeX, render every page, resolve any table/layout issues, confirm all 40 citations, and add `runs/v49_manuscript_integration/V49_COMPILE_AND_RENDER_REPORT.md`.
