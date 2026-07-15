# RA-RepDet-TriAir Handoff

Generated: 2026-07-15

## Current task

- V53 outcome: `V53_CPU_PREFLIGHT_READY_FOR_SEPARATE_GPU_AUTHORIZATION`.
- Starting commit: `6cb8ba426432f0c590c937ac05dc017eb859582b`.
- RGB-supervised train/devval/total: 7,187 / 1,845 / 9,032.
- Excluded from RGB supervision: 106 IR-only and 35,898 `UNLABELED` rows.
- Manifest hashes are frozen in `runs/v53_mmuav_feature_alignment_preflight/manifest_hashes.json`.
- Adapter: `datasets/mmuav_feature_alignment_dataset.py`.
- Experimental alignment: `rarepdet/experimental/mmuav_feature_alignment.py`.
- Experimental scaffold: `rarepdet/experimental/mmuav_feature_alignment_model.py`.
- Mechanism: STN-inspired residual affine feature alignment with exact-identity zero-residual initialization.
- RGB is the reference feature grid; IR/event are aligned only in feature space.
- Alignment-off control and equal/reliability fusion interfaces are available.
- Equal/RA scaffold parameters: 52,220 / 53,309; estimated MACs: 342,835,584 / 342,838,752 at 320x320 branch inputs.
- Tests: 9/9 pass. Protected core, V52 evidence, and manuscript changes: none.
- Pilot locked; CUDA probe not performed; GPU optimizer steps: 0.

## Required action

Do not start GPU work without separate authorization. A future 200-step pilot should use the frozen V53 manifests, compare alignment-off/on under the registered ablation contract, monitor RTX 3090 memory, and retain the private-use/license boundary. V51 remains unchanged.
