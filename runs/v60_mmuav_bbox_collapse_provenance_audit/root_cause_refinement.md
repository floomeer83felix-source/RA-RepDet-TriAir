# V60 Root-Cause Refinement

Completion state: `V60_BBOX_COLLAPSE_PROVENANCE_AUDIT_COMPLETE_CAUSE_UNRESOLVED`.

Primary classification: `V57_BBOX_COLLAPSE_PROVENANCE_UNRESOLVED`.

## Established directly

- Exact historical V55 and V57 seed-0 initializations were reconstructed, and their bbox-regression weight/bias tensors are bit-identical.
- Both initial states have usable bbox geometry on the frozen train subset: V55 `18,401 / 272,000` valid and V57 `17,134 / 272,000` valid.
- V55 final has `272,000 / 272,000` valid boxes on both train and devval probes.
- V57 equal and reliability finals each have `0 / 272,000` valid boxes on both train and devval probes; all candidates are finite and degenerate.
- Both final V57 states have zero bbox weight and bias gradient norms on all four frozen no-step gradient rows. V55 final has nonzero bbox gradients on all four rows.
- Equal and reliability V57 checkpoints therefore share the same observed geometry-and-gradient failure outcome.

## Why the strict dead-ReLU label is not selected

V57 equal final retains post-ReLU positive component fractions of approximately `0.1722 / 0.1679 / 0.1519 / 0.0807` across the four FPN levels. V57 reliability final retains sparse positive fractions of approximately `0.000050 / 0.000068 / 0.000645 / 0.002656`. These positive components never combine into positive-area decoded boxes, and bbox gradients remain zero, but the frozen V60 definition requires non-positive pre-ReLU distances and zero post-ReLU distances together with absent gradients. That full condition is not observed.

## Historical limitation

The four 7,187-row logs are finite and contain bbox loss, total loss, learning rate, and global gradient norm. They do not contain bbox-head outputs or bbox-parameter gradients. V57 equal/reliability bbox losses end at exactly `1.0`, with no observations strictly between zero and one, while V55 alignment-on ends at `0.5031289458274841`. This establishes a divergent historical loss trajectory but cannot locate the exact geometry-collapse step or uniquely identify the initiating update.

No repair, retraining, threshold selection, AP/AR evaluation, or manuscript claim is authorized by V60.
