# Experiment Status

Updated: 2026-07-25

## Active state

`V68_BLOCKED_DATA_RIGHTS_OR_CITATION_INCOMPLETE`

## V68 evidence audit

V68 completed the CPU/documentation-only MM-UAV manuscript-evidence audit. No CUDA, training, evaluation, tuning, checkpoint selection, new seed, or new variant was run.

- V65-V67 frozen file hashes, decisions, safety records, and final metrics matched exactly.
- The matched metric table was reproduced from immutable source files.
- Means and sample standard deviations matched through both Python `statistics` and an independent high-precision Decimal calculation.
- V68 tests passed `9 / 9`.
- Production, V40-V67 historical evidence, active manuscript, and submission fingerprints remained unchanged.
- No draft was created under `manuscript/v68_mmuav_extension_draft/`.

## Scientific result

The MM-UAV evidence is internally valid but weak and protocol-divergent:

- seed-0 reliability-minus-equal AP: `+0.0041719276`;
- seed-1 reliability-minus-equal AP: `-0.0004533834`;
- mean matched AP delta: `+0.0018592721`;
- equal AP mean/sample standard deviation: `0.0196700860 / 0.0235244622`;
- reliability AP mean/sample standard deviation: `0.0215293581 / 0.0267950511`.

The paired direction is mixed and initialization sensitivity is large. The scorer learned non-uniform model weights, but these are not calibrated physical sensor-reliability measurements.

## Protocol boundary

V65-V67 used 320 x 320 inputs, one ordered pass, learned IR/event feature alignment to RGB, no modality dropout, a Softplus bbox-distance path, and source-train-derived devval. The active TriAir manuscript uses a 640 x 640, 50-epoch headline protocol and a different input/method/evaluation contract. MM-UAV is therefore not an external replication or independent-test validation of the TriAir headline configuration.

## Manuscript gate

The current records do not establish MM-UAV provider/release authority, canonical dataset citation, version, dataset license, research-use permission, or permission to report aggregate derived metrics. Code and paper licenses are not dataset grants.

Recommendation: exclude MM-UAV evidence from the current manuscript and keep it internal until provider-verifiable rights and citation records are supplied. No additional GPU work is implied or authorized.
