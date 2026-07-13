# V48 Causal Ablation Summary

Generated: 2026-07-13T14:43:34+08:00

Status: `V48_CAUSAL_ABLATION_COMPLETE`

All V48 comparisons are frozen development-validation evidence. Checkpoint selection is development-validation project-local AP50. No V48 variant accesses the locked holdout.

## Per-run evidence

| Run | Variant | Seed | Source | AP50:95 | AP50 | AP75 | F1 | Selected epoch | Runtime sec |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| early_moddrop_seed0 | early_moddrop | 0 | inherited V46 fresh seed0 training | 0.672664 | 0.946924 | 0.813581 | 0.907029 | 6 | NA |
| early_moddrop_seed1 | early_moddrop | 1 | V48 fresh training | 0.692124 | 0.942839 | 0.822447 | 0.905156 | 8 | 45611.4 |
| early_moddrop_seed2 | early_moddrop | 2 | V48 fresh training | 0.687241 | 0.941444 | 0.827335 | 0.892090 | 6 | 43950.1 |
| matched_early_seed0 | matched_early | 0 | inherited V46 source-locked checkpoint | 0.705307 | 0.941146 | 0.837787 | 0.902284 | 9 | NA |
| matched_early_seed1 | matched_early | 1 | inherited V46 source-locked checkpoint | 0.663793 | 0.938505 | 0.791577 | 0.884676 | 4 | NA |
| matched_early_seed2 | matched_early | 2 | inherited V46 source-locked checkpoint | 0.671666 | 0.932084 | 0.797733 | 0.886633 | 5 | NA |
| reliability_p015_seed0 | ra_full_p015 | 0 | inherited V46 source-locked checkpoint | 0.727973 | 0.954003 | 0.891326 | 0.914921 | 9 | NA |
| reliability_p015_seed1 | ra_full_p015 | 1 | inherited V46 source-locked checkpoint | 0.722895 | 0.951538 | 0.874275 | 0.902601 | 8 | NA |
| reliability_p015_seed2 | ra_full_p015 | 2 | inherited V46 source-locked checkpoint | 0.695948 | 0.954695 | 0.853028 | 0.911643 | 7 | NA |
| ra_no_moddrop_seed0 | ra_no_moddrop | 0 | inherited V46 fresh seed0 training | 0.711245 | 0.947747 | 0.866164 | 0.903946 | 5 | NA |
| ra_no_moddrop_seed1 | ra_no_moddrop | 1 | V48 fresh training | 0.733413 | 0.947670 | 0.882399 | 0.899133 | 5 | 45948.7 |
| ra_no_moddrop_seed2 | ra_no_moddrop | 2 | V48 fresh training | 0.730786 | 0.947223 | 0.873939 | 0.903913 | 6 | 43927.6 |
| ra_static_equal_seed0 | ra_static_equal | 0 | V48 fresh training | 0.670492 | 0.925747 | 0.811444 | 0.876437 | 5 | 43396.2 |
| ra_static_equal_seed1 | ra_static_equal | 1 | V48 fresh training | 0.657185 | 0.941306 | 0.810108 | 0.892181 | 4 | 46870.0 |
| ra_static_equal_seed2 | ra_static_equal | 2 | V48 fresh training | 0.661602 | 0.935266 | 0.794414 | 0.891566 | 4 | 47170.0 |
| ra_stems_project_seed0 | ra_stems_project | 0 | V48 fresh training | 0.675353 | 0.933150 | 0.826623 | 0.887032 | 5 | 43396.3 |
| ra_stems_project_seed1 | ra_stems_project | 1 | V48 fresh training | 0.684547 | 0.943020 | 0.830176 | 0.906831 | 5 | 46868.3 |
| ra_stems_project_seed2 | ra_stems_project | 2 | V48 fresh training | 0.694417 | 0.945413 | 0.845453 | 0.896787 | 6 | 47169.0 |

## Paired contrasts

| Contrast | Shared seeds | Mean delta AP50:95 | Sample SD | Scope |
| --- | --- | ---: | ---: | --- |
| ra_full_p015_minus_matched_early | [0, 1, 2] | 0.035350 | 0.020586 | Development-validation full reliability-aware fusion minus matched early fusion. |
| ra_no_moddrop_minus_matched_early | [0, 1, 2] | 0.044893 | 0.034142 | Development-validation combination of separate stems and dynamic gate minus matched early fusion. |
| ra_full_p015_minus_ra_no_moddrop | [0, 1, 2] | -0.009542 | 0.025797 | Development-validation modality-dropout increment within the reliability-aware architecture. |
| early_moddrop_minus_matched_early | [0, 1, 2] | 0.003755 | 0.032160 | Development-validation modality-dropout increment within early fusion. |
| ra_static_equal_minus_matched_early | [0, 1, 2] | -0.017162 | 0.015385 | Development-validation increment from separate stems with fixed equal feature fusion. |
| ra_no_moddrop_minus_ra_static_equal | [0, 1, 2] | 0.062055 | 0.018781 | Development-validation dynamic-gating increment beyond equal-weight stem fusion. |
| ra_stems_project_minus_matched_early | [0, 1, 2] | 0.004517 | 0.029869 | Development-validation learned deterministic fusion control minus matched early fusion. |
| ra_no_moddrop_minus_ra_stems_project | [0, 1, 2] | 0.040376 | 0.007357 | Development-validation dynamic-gating contrast against deterministic learned projection control. |

## Completion

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

## Boundary

Means and sample SDs are descriptive for only the shared completed seeds. No significance test is run or claimed. The deterministic-projection control is a learned fixed-order fusion control and does not isolate stems alone.
