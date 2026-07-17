# Experiment Status

Updated: 2026-07-17

## Active task

`V60_BBOX_COLLAPSE_PROVENANCE_AUDIT_COMPLETE_CAUSE_UNRESOLVED`

## V60 outcome

V60 completed the authorized read-only provenance audit with zero optimizer constructions and zero optimizer steps. Exactly twenty no-step backward calls were used: four frozen train rows for each of five frozen states. Parameters, checkpoints, protected V40-V59 evidence, V51, production TriAir, manuscript, and submission files remained unchanged.

The primary classification is `V57_BBOX_COLLAPSE_PROVENANCE_UNRESOLVED`.

## Direct findings

- The V55 and V57 seed-0 initialization files were reconstructed exactly, including serialized SHA256 values `91fec577380f895c932ffeb090bba7d376abc1ea1d97d568ae46901a7bbcb983` and `846da59cc8d908dfeb429fca2acb4985e73ff5fda3915154f9f764c571977cb9`.
- Their initial FCOS bbox-regression weight and bias tensors are bit-identical. Construction-order RNG consumption therefore did not change the bbox initialization.
- On the frozen 32-row train subset, V55/V57 initial states produced `18,401 / 17,134` valid boxes of `272,000`; collapse was not present at initialization.
- V55 final produced `272,000 / 272,000` valid train boxes and `272,000 / 272,000` valid devval boxes.
- V57 equal and reliability final states each produced `0 / 272,000` valid train boxes and `0 / 272,000` valid devval boxes. All candidates were finite but degenerate.
- The four-row probes found exactly zero bbox weight and bias gradient norms for both final V57 states. V55 final retained nonzero bbox gradients on all four rows.
- Final V57 pre-ReLU output was not uniformly non-positive: equal retained material positive components and reliability retained sparse positive components. Therefore the frozen strict dead-ReLU criterion was not met even though no valid geometry and no bbox gradients remained.

## Historical evidence

All four committed V55/V57 logs contain 7,187 finite rows. V55 alignment-on ends with bbox loss `0.5031289458274841`; V57 equal and reliability end at exactly `1.0` and contain no observations strictly between zero and one. Historical logs do not contain bbox-output or bbox-parameter-gradient fields, so they cannot establish the exact first step at which usable geometry disappeared.

## Frozen contracts

- Train/devval rows: `7,187 / 1,845`.
- Train SHA256: `e81973b95dd6fd5ce2d3c5de526310a3bef083df49b8db584fdf39b78a34d67a`.
- Devval SHA256: `113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54`.
- V60 train subset seed/count/SHA256: `60 / 32 / d1d59950d62d7b7ed5bb54b54769d2e5af36c3084d933a65a88870a0abf7204c`.
- V60 gradient subset count/SHA256: `4 / bfb526aa632b916e61357e215d7ea2f77e2f55bed5db8f20d411703569561166`.
- Reused V59 devval subset seed/count/SHA256: `58 / 32 / d622f6712a9bfb2faa596daa053ed207dded1a9227e80b4a10dd3b48ae3d51ee`.

## Authorization boundary

V60 remains diagnostic only. It does not authorize checkpoint repair, positive bbox-bias initialization, activation or loss changes, retraining, tuning, extra evaluation, AP/AR computation, or manuscript claims. Any corrective experiment requires a separate task.
