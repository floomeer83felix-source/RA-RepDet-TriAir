# Task Blocker

Status: `V71_BLOCKED_ADAPTER_OR_ONTOLOGY_CONTRACT`

Generated: 2026-07-26

## Current state

V71 passed the frozen data and checkpoint gates but failed the required parameter-free adapter gate.

The exact 1,845-row exposed devval manifest is present and unchanged. All six authoritative TriAir manuscript checkpoints match frozen hashes and strictly load in the unchanged Early Fusion or reliability-aware architecture.

V52 records:

- temporal synchronization by matching frame index only;
- different native RGB, IR, and event dimensions;
- `pixel_alignment_established: false`;
- `deterministic_raw_grid_transform_found: false`;
- no complete provider calibration or executable raw-grid transform.

V53 records `raw_channel_concatenation: false` and uses independent modality branches with learned feature alignment. V71 prohibits that learned alignment path. Independent resizing or letterboxing cannot establish physical pixel correspondence and would place unrelated modality coordinates into a shared five-channel tensor.

No smoke pass, CUDA inference, predictions, or metrics were run.

## Error tail

The two corrected implementation-only preflight errors were:

```text
ModuleNotFoundError: No module named 'rarepdet'
RuntimeError: self.dim() cannot be 0 to view Long as Byte (different element sizes)
```

They were fixed by adding the repository root to `sys.path` and flattening scalar tensors before byte fingerprinting. The complete six-checkpoint CPU preflight then passed.

The V69 historical regression suite returned `8 / 9` because its final test recomputes a whole-worktree protected aggregate created during V69. A linked worktree checkout can have different working-tree byte representations, so that stale aggregate differs even though `git diff` confirms V52-V70 historical paths are unchanged. V71's focused protection check and direct Git path audit pass.

## Attempted fixes

1. Verified the V52 provider/alignment evidence for a deterministic calibration transform; none exists.
2. Verified the V53 fixed preprocessing path; it explicitly performs independent letterboxing without registration and forbids raw concatenation.
3. Considered learned V53 feature alignment; it is forbidden by V71 and incompatible with the frozen TriAir checkpoint architecture.
4. Did not invent, fit, or infer a transform from devval media or labels.

## Related files

- `runs/v52_mmuav_audit/alignment_source_audit.json`
- `runs/v52_mmuav_audit/official_alignment_verification.json`
- `runs/v52_mmuav_audit/synchronization_audit.json`
- `runs/v53_mmuav_feature_alignment_preflight/method_contract.json`
- `runs/v53_mmuav_feature_alignment_preflight/alignment_design.json`
- `runs/v71_mmuav_existing_devval_triair_zero_shot_external_domain_validation/handoff.md`

## Repair options

1. Obtain a provider-issued, executable deterministic RGB/IR/event calibration and registration transform, freeze it without devval fitting, and resume the unchanged six-checkpoint V71 protocol.
2. Authorize a scientifically different task using independent modality branches and the already established learned feature-alignment architecture. That would not be an evaluation of the six unchanged TriAir manuscript checkpoints and must be reported separately.

## Required start conditions

Before model inference, verify:

1. the worktree is clean and the current task commit is present;
2. the exact frozen 1,845-row MM-UAV devval manifest, row order, modality pairing, annotations, and evaluator are available;
3. the six authoritative frozen TriAir checkpoints can be located, hashed, and strictly loaded;
4. a deterministic parameter-free five-channel adapter can be frozen at `640 x 640`;
5. vehicle ontology, score threshold `0.001`, NMS `0.6`, maximum `100` detections, and COCO AP/AR semantics are fixed;
6. protected files and historical evidence match their frozen fingerprints.

## Authorized work

V71 may:

- use the existing frozen 1,845-row MM-UAV devval manifest;
- parse its annotations for the final frozen metric computation;
- run a fixed no-metric smoke pass;
- run each of six frozen TriAir checkpoints exactly once on the full devval set;
- compute AP, AP50, AP75, AR@1, AR@10, and AR@100;
- compute matched seed-wise RA-RepDet minus Early Fusion differences and descriptive three-seed summaries;
- commit compact hashes, contracts, metrics, tests, and conclusions.

V71 may not:

- call the dataset an independent or blind external test;
- train, fine-tune, adapt, calibrate, pseudo-label, or optimize on MM-UAV;
- use MM-UAV-trained V57/V63/V65-V67 weights, learned MM-UAV alignment, or the MM-UAV Softplus wrapper;
- tune preprocessing, ontology, thresholds, NMS, checkpoints, seeds, or variants using V71 results;
- rerun a checkpoint because its metric is poor;
- place raw media, labels, full predictions, tensors, checkpoints, local paths, or heavy/private artifacts in Git.

## Fail-closed conditions

Stop with the matching V71 blocked state if:

- any frozen TriAir checkpoint or model contract cannot be verified;
- the 1,845-row manifest or evaluator differs from frozen evidence;
- the five-channel adapter or ontology requires learned or result-informed choices;
- inference, decoded boxes, predictions, or metric inputs become non-finite;
- OOM, unreadable modalities, coordinate mismatch, evaluator mismatch, protected-file drift, or private/heavy Git artifacts occur;
- any unauthorized tuning, checkpoint substitution, seed addition, variant addition, or result-driven rerun is attempted.

## Next action

Choose and authorize one repair option. Do not launch the six-checkpoint GPU evaluation until a defensible input-coordinate contract exists.
