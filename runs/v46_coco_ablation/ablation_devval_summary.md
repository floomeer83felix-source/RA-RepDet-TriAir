# V46 Development-Validation Causal Ablation Summary

Generated: 2026-07-10T22:28:48+08:00

Status: `V46_CAUSAL_ABLATION_SEED0_PARTIAL_COMPLETE`

All fresh ablation checkpoints were trained for 50 epochs on the frozen V40 training manifest and selected only by development-validation project-local AP50. The locked guard was not accessed for ablation training, selection, continuation, or reporting.

## Per-run evidence

| Run | Variant | Seed | Source | Dropout | AP50:95 | AP50 | AP75 | F1@0.50 |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| matched_early_seed0 | matched_early | 0 | source-locked existing checkpoint | 0.00 | 0.705307 | 0.941146 | 0.837787 | 0.902284 |
| matched_early_seed1 | matched_early | 1 | source-locked existing checkpoint | 0.00 | 0.663793 | 0.938505 | 0.791577 | 0.884676 |
| matched_early_seed2 | matched_early | 2 | source-locked existing checkpoint | 0.00 | 0.671666 | 0.932084 | 0.797733 | 0.886633 |
| reliability_p015_seed0 | ra_full_p015 | 0 | source-locked existing checkpoint | 0.15 | 0.727973 | 0.954003 | 0.891326 | 0.914921 |
| reliability_p015_seed1 | ra_full_p015 | 1 | source-locked existing checkpoint | 0.15 | 0.722895 | 0.951538 | 0.874275 | 0.902601 |
| reliability_p015_seed2 | ra_full_p015 | 2 | source-locked existing checkpoint | 0.15 | 0.695948 | 0.954695 | 0.853028 | 0.911643 |
| ra_no_moddrop_seed0 | ra_no_moddrop | 0 | V46 fresh seed0 training | 0.00 | 0.711245 | 0.947747 | 0.866164 | 0.903946 |
| early_moddrop_seed0 | early_moddrop | 0 | V46 fresh seed0 training | 0.15 | 0.672664 | 0.946924 | 0.813581 | 0.907029 |

## Seed0 controlled contrasts

| Contrast | Delta AP50:95 | Delta AP50 | Delta AP75 | Delta F1 | Scope |
| --- | ---: | ---: | ---: | ---: | --- |
| ra_full_p015_minus_ra_no_moddrop | 0.016728 | 0.006256 | 0.025162 | 0.010975 | Seed0 modality-dropout increment within the same reliability-stem and dynamic-gate architecture. |
| ra_no_moddrop_minus_matched_early | 0.005938 | 0.006601 | 0.028377 | 0.001662 | Seed0 combined increment of modality-specific stems plus dynamic softmax gating; it does not isolate the gate alone. |
| early_moddrop_minus_matched_early | -0.032643 | 0.005777 | -0.024206 | 0.004745 | Seed0 modality-dropout increment within the matched early-fusion architecture. |
| ra_full_p015_minus_early_moddrop | 0.055309 | 0.007080 | 0.077745 | 0.007892 | Seed0 architecture increment at matched modality-dropout probability; stems and dynamic gating remain bundled. |

## Variant completion

- `matched_early`: complete for existing fixed seeds 0,1,2.
- `ra_full_p015`: complete for existing fixed seeds 0,1,2.
- `ra_no_moddrop`: fresh V46 seed0 complete; seeds 1,2 deferred for GPU time.
- `early_moddrop`: fresh V46 seed0 complete; seeds 1,2 deferred for GPU time.
- `ra_static_equal`: skipped because it requires architecture/model-loading changes outside the allowed V46 file scope and protected training-core plumbing.
- `ra_stems_concat_or_project`: skipped because it requires architecture/model-loading changes outside the allowed V46 file scope and protected training-core plumbing.

## Boundary

The fresh contrasts contain one seed only and are descriptive. The available implementation isolates modality dropout within each architecture, but modality-specific stems and dynamic softmax gating remain bundled because static-equal and deterministic-projection variants would require out-of-scope protected model/training changes. No guard ablation evaluation was run.
