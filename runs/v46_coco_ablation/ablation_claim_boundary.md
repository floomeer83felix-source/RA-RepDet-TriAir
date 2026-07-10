# V46 Causal Ablation Claim Boundary

## Allowed statements

- The V46 package reports canonical COCO-style bbox AP for six fixed baseline/main checkpoints on frozen development-validation and locked same-dataset guard manifests.
- The fresh causal-ablation evidence is a seed0-only development-validation comparison under the locked 50-epoch protocol.
- `ra_full_p015 - ra_no_moddrop` is a seed0 estimate of the modality-dropout increment within the reliability architecture.
- `early_moddrop - matched_early` is a seed0 estimate of the modality-dropout increment within early fusion.
- `ra_no_moddrop - matched_early` bundles modality-specific stems and dynamic gating and cannot be attributed to the gate alone.

## Required cautions

- The new ablation contrasts have one seed and do not establish statistical significance.
- The held-out guard is same-dataset evidence and is not an independent public benchmark or external generalization test.
- No result establishes optimal dropout, calibrated sensor reliability, or real sensor-fault robustness.
- COCO-style metric reporting is an evaluation convention, not COCO proof of generalization or robustness.
- Static-equal and deterministic-projection controls were not implemented because the task's allowed-file scope forbids the required protected model/training plumbing changes.
- Seeds 1 and 2 for the two fresh feasible variants remain deferred because of the measured GPU runtime.
