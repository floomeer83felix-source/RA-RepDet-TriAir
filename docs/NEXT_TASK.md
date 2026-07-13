# Current Task

## Title

V49 integrate COCO metrics, causal ablations, and efficiency evidence into the SIVP manuscript.

## Goal

Update the preserved V47 manuscript so that its abstract, methods, evaluation protocol, results, discussion, limitations, and conclusion accurately reflect the completed V46 canonical COCO-style evaluation and V48 three-seed causal ablation and efficiency packages.

This is a manuscript-integration and compile task. Do not train models, regenerate predictions, modify checkpoints, alter manifests, or access the locked holdout beyond reading the frozen V46 summary files.

## Read First

1. `AGENTS.md`
2. `docs/PROJECT_CONTEXT.md`
3. `docs/EXPERIMENT_STATUS.md`
4. `runs/handoff_latest.md`
5. `runs/v46_coco_ablation/coco_metric_summary.md`
6. `runs/v46_coco_ablation/source_lock_v46.md`
7. `runs/v48_complete_ablation/causal_ablation_summary.md`
8. `runs/v48_complete_ablation/efficiency_summary.md`
9. `runs/v48_complete_ablation/claim_boundary.md`
10. `submission/sivp/tex/ra_repdet_sivp.tex`
11. `submission/sivp/tex/main.tex`
12. `submission/sivp/tables/Table_2_implementation_and_reproducibility.tex`

## Frozen Evidence and Interpretation

- The main fixed-checkpoint comparison remains matched early fusion versus reliability-aware fusion with modality dropout `p=0.15`, seeds 0/1/2.
- Canonical COCO-style bbox evaluation uses `pycocotools`, IoU 0.50:0.05:0.95, 101 recall samples, area=all, and maxDets=100.
- Development-validation mean paired delta for full RA `p=0.15` minus matched early is `+0.035350 ± 0.020586` AP50:95.
- Locked same-dataset holdout mean paired delta is `+0.006195 ± 0.018737` AP50:95; seed2 is negative, so the holdout result is mixed rather than uniformly positive.
- V48 ablations are development-validation only. No V48 ablation accessed the locked holdout.
- The cleanest available dynamic-gating contrasts are:
  - `ra_no_moddrop - ra_static_equal = +0.062055 ± 0.018781` AP50:95;
  - `ra_no_moddrop - ra_stems_project = +0.040376 ± 0.007357` AP50:95.
- The modality-dropout increment within the RA architecture is `ra_full_p015 - ra_no_moddrop = -0.009542 ± 0.025797` AP50:95. Do not claim that `p=0.15` is optimal or universally beneficial.
- Efficiency on RTX 3090, batch one, float32, `1x5x640x640`:
  - matched early: 6,591,609 parameters, 104.762 GFLOPs, 40.4046 ms mean latency, 24.7497 FPS, 122.49 MiB peak allocated memory;
  - full RA: 6,593,293 parameters, 105.392 GFLOPs, 40.6794 ms mean latency, 24.5825 FPS, 236.40 MiB peak allocated memory.

## Required Manuscript Changes

1. Update the abstract in:
   - `submission/sivp/tex/main.tex`;
   - root `main.tex`;
   - root `main_sivp_snjnl.tex`.
2. Update `submission/sivp/tex/ra_repdet_sivp.tex`:
   - replace the obsolete statement that COCO AP50:95 is unavailable;
   - describe the static-equal and deterministic-projection controls;
   - add canonical COCO fixed-checkpoint results;
   - add the complete three-seed causal ablation results;
   - add efficiency results;
   - revise Discussion, Limitations, and Conclusion to identify dynamic gating as the strongest supported mechanism while treating modality dropout cautiously.
3. Update `submission/sivp/tables/Table_2_implementation_and_reproducibility.tex`.
4. Create source-linked tables:
   - `submission/sivp/tables/Table_10_coco_fixed_checkpoint_summary.tex`;
   - `submission/sivp/tables/Table_11_three_seed_causal_ablation.tex`;
   - `submission/sivp/tables/Table_12_efficiency_profile.tex`.
5. Preserve the existing 40-reference citation closure unless a new citation is strictly necessary.
6. Compile with the Springer `sn-jnl` source package, run BibTeX, render all pages, and check citations, cross-references, clipping, tables, and bibliography.

## Claim Boundary

Allowed:

- descriptive three-seed component-disjoint development-validation comparisons;
- locked same-dataset fixed-checkpoint holdout evidence for the original matched-early versus full-RA `p=0.15` comparison;
- descriptive causal contrasts supported by the implemented static controls;
- hardware-specific efficiency measurements under the recorded RTX 3090 procedure.

Disallowed:

- external-dataset or independent-benchmark generalization;
- statistical significance;
- proof of universal causality;
- optimal or universally beneficial modality dropout;
- calibrated physical sensor reliability or sensor-health probabilities;
- real sensor-fault robustness;
- V48 ablation holdout performance.

## Required Outputs

- Updated manuscript entry files and body.
- Tables 10-12.
- `runs/v49_manuscript_integration/V49_MANUSCRIPT_INTEGRATION_REPORT.md`.
- `runs/v49_manuscript_integration/V49_COMPILE_AND_RENDER_REPORT.md` if compilation succeeds.
- Updated `docs/EXPERIMENT_STATUS.md`.
- Updated `docs/TASK_BLOCKER.md`.
- Updated `runs/handoff_latest.md/json`.

## Acceptance Criteria

- The abstract reports canonical AP50:95 and the bounded ablation interpretation.
- The manuscript no longer says COCO AP50:95 or causal ablations are future work.
- The manuscript does not describe `p=0.15` as optimal.
- The dynamic-gating conclusion is supported by both static-equal and deterministic-projection controls.
- The locked holdout is not used for V48 ablation claims.
- Efficiency claims include the memory increase as well as small parameter/latency overhead.
- All cited numerical values match the frozen V46/V48 summaries.
- The Springer/BibTeX build closes without undefined citations or cross-references, or an exact blocker is recorded.

## Commit Message

`paper: integrate V46 V48 evidence into SIVP manuscript`
