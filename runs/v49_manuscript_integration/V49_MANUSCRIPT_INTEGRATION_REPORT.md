# V49 Manuscript Evidence Integration Report

Generated: 2026-07-13

## Status

`V49_MANUSCRIPT_INTEGRATION_DRAFT_COMPLETE_COMPILE_PENDING`

The V46 canonical COCO-style fixed-checkpoint evidence and the V48 complete three-seed causal ablation and efficiency evidence have been integrated into the preserved V47 SIVP manuscript structure. No training, prediction generation, checkpoint selection, split modification, or new holdout access was performed.

## Files updated

- `docs/NEXT_TASK.md`
- `submission/sivp/tex/main.tex`
- root `main.tex`
- root `main_sivp_snjnl.tex`
- `submission/sivp/tex/ra_repdet_sivp.tex`
- `submission/sivp/tables/Table_2_implementation_and_reproducibility.tex`

## New evidence tables

- `submission/sivp/tables/Table_10_coco_fixed_checkpoint_summary.tex`
- `submission/sivp/tables/Table_11_three_seed_causal_ablation.tex`
- `submission/sivp/tables/Table_12_efficiency_profile.tex`

## Integrated fixed-checkpoint evidence

Full reliability-aware `p=0.15` minus matched early fusion:

| Protocol | AP50:95 mean delta | Sample SD | AP50 mean delta | AP75 mean delta |
| --- | ---: | ---: | ---: | ---: |
| Development-validation | +0.035350 | 0.020586 | +0.016167 | +0.063844 |
| Locked same-dataset holdout | +0.006195 | 0.018737 | +0.008534 | +0.003258 |

The manuscript explicitly records that holdout AP50:95 is mixed across seeds and that seed2 is negative. AP50 remains positive for all three locked-holdout seed pairs.

## Integrated causal interpretation

The manuscript now identifies dynamic softmax weighting as the strongest supported development-validation mechanism, bounded by the implemented controls:

- `ra_no_moddrop - ra_static_equal`: `+0.062055 ± 0.018781` AP50:95;
- `ra_no_moddrop - ra_stems_project`: `+0.040376 ± 0.007357` AP50:95;
- `ra_full_p015 - ra_no_moddrop`: `-0.009542 ± 0.025797` AP50:95;
- `early_moddrop - matched_early`: `+0.003755 ± 0.032160` AP50:95.

The text no longer presents modality dropout `p=0.15` as optimal or universally beneficial. The preselected `p=0.15` model remains the fixed main configuration with locked-holdout evidence, while the later ablations remain development-validation only.

## Integrated efficiency interpretation

On the recorded RTX 3090 batch-one float32 procedure:

- matched early: 6,591,609 parameters, 104.762 GFLOPs, 40.4046 ms, 24.7497 FPS, 122.49 MiB;
- full RA `p=0.15`: 6,593,293 parameters, 105.392 GFLOPs, 40.6794 ms, 24.5825 FPS, 236.40 MiB.

The manuscript states that parameter, FLOP, and latency overheads are small, while peak allocated memory increases substantially.

## Narrative changes

- Abstract now reports canonical AP50:95, the mixed holdout result, dynamic-gating contrasts, cautious dropout interpretation, and efficiency overhead.
- Contributions now include canonical evaluation, three-seed controls, and efficiency profiling.
- Method now defines static equal and deterministic learned-projection controls.
- Evaluation protocol now distinguishes historical project-local metrics from canonical `pycocotools` metrics.
- Results now include dedicated COCO, ablation, and efficiency subsections.
- Discussion identifies dynamic gating as the strongest supported component and treats dropout as metric- and architecture-dependent.
- Limitations now cover holdout seed heterogeneity, incomplete factor isolation, single-GPU profiling, event provenance, graph completeness, and external validation.
- Conclusion no longer lists COCO metrics, causal ablations, or efficiency measurements as future work.

## Claim boundary preserved

The manuscript does not claim:

- external-dataset generalization;
- independent-benchmark validation;
- statistical significance;
- universal causal proof;
- optimal modality dropout;
- calibrated sensor reliability or sensor-health probabilities;
- real sensor-fault robustness;
- V48 ablation performance on the locked holdout.

## Citation state

No citation keys were added or removed from the preserved V47 body literature set. The intended 40-reference closure is therefore unchanged, subject to a fresh BibTeX compile.

## Compile status

A fresh V49 Springer/BibTeX compile has not yet been completed in the connected repository editing environment. The manuscript and tables require local `sn-jnl` compilation, citation closure, and rendered-page inspection before the task can be marked submission-ready.
