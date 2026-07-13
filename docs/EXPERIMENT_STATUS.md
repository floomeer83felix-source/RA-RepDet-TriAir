# Experiment Status

Updated: 2026-07-13

## Active task

`V49_MANUSCRIPT_INTEGRATION_DRAFT_COMPLETE_COMPILE_PENDING`

V46 canonical COCO-style fixed-checkpoint metrics and V48 complete three-seed causal ablation and efficiency evidence have been integrated into the preserved V47 SIVP manuscript. No new training, prediction generation, checkpoint selection, split modification, or holdout access was performed during V49.

## Manuscript integration completed

- Updated the abstract in all three active entry files.
- Updated Introduction, contributions, Method, evaluation protocol, Results, Discussion, Limitations, and Conclusion.
- Added canonical COCO fixed-checkpoint evidence.
- Added complete three-seed causal ablation evidence.
- Added RTX 3090 efficiency evidence.
- Preserved the V47 40-reference literature set without adding or deleting citation keys.

## New manuscript tables

- `submission/sivp/tables/Table_10_coco_fixed_checkpoint_summary.tex`
- `submission/sivp/tables/Table_11_three_seed_causal_ablation.tex`
- `submission/sivp/tables/Table_12_efficiency_profile.tex`

## Fixed main comparison

Reliability-aware `p=0.15` minus matched early fusion, paired by seed:

| Protocol | AP50:95 mean delta | Sample SD | AP50 mean delta | AP75 mean delta | n |
| --- | ---: | ---: | ---: | ---: | ---: |
| Development-validation | +0.035350 | 0.020586 | +0.016167 | +0.063844 | 3 |
| Locked same-dataset holdout | +0.006195 | 0.018737 | +0.008534 | +0.003258 | 3 |

The locked-holdout AP50:95 result is mixed across seeds; seed2 is negative. AP50 is positive for all three locked-holdout seed pairs.

## Three-seed mechanism evidence

| Contrast | Mean delta AP50:95 | Sample SD |
| --- | ---: | ---: |
| `ra_no_moddrop - ra_static_equal` | +0.062055 | 0.018781 |
| `ra_no_moddrop - ra_stems_project` | +0.040376 | 0.007357 |
| `ra_full_p015 - ra_no_moddrop` | -0.009542 | 0.025797 |
| `early_moddrop - matched_early` | +0.003755 | 0.032160 |

The active manuscript now identifies dynamic sample-dependent gating as the strongest supported development-validation mechanism. Modality dropout is treated as architecture- and metric-dependent and is not claimed optimal.

## Efficiency evidence

RTX 3090, float32, batch one, `1x5x640x640`:

| Model | Parameters | GFLOPs | Mean latency | FPS | Peak allocated memory |
| --- | ---: | ---: | ---: | ---: | ---: |
| Matched early | 6,591,609 | 104.762 | 40.4046 ms | 24.7497 | 122.49 MiB |
| Full RA `p=0.15` | 6,593,293 | 105.392 | 40.6794 ms | 24.5825 | 236.40 MiB |

Parameter and latency overheads are small, but the measured peak allocated memory increases substantially.

## Claim boundary

Allowed:

- descriptive three-seed component-disjoint development-validation evidence;
- locked same-dataset fixed-checkpoint holdout evidence for matched early versus full RA `p=0.15`;
- bounded static-control and dynamic-gating contrasts on development-validation;
- hardware-specific efficiency measurements under the recorded procedure.

Disallowed:

- external-dataset or independent-benchmark generalization;
- statistical significance;
- universal causal proof;
- optimal modality dropout;
- calibrated physical sensor reliability;
- real sensor-fault robustness;
- V48 ablation holdout performance.

## Current blocker

The manuscript writing and table integration are complete. A fresh Springer `sn-jnl`/BibTeX compile and rendered-page inspection remain required before V49 can be marked submission-ready.

## Primary report

- `runs/v49_manuscript_integration/V49_MANUSCRIPT_INTEGRATION_REPORT.md`
