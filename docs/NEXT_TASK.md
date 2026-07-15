# Current Task

## User Authorization (2026-07-15)

The user selected **Plan A** for continued MM-UAV research:

> native RGB/IR/event inputs, independent modality branches, learned feature-level alignment, and RGB-coordinate detection supervision.

All MM-UAV work is local, private research only. Do not ask the user to reconfirm this scope unless a later task proposes public redistribution, external sharing, commercial use, or a new manuscript/public benchmark claim.

This task authorizes CPU-only dataset preparation, architecture pre-registration, experimental module implementation, and tests. It does **not** authorize CUDA work, the 200-step pilot, epoch training, checkpoint production, AP evaluation, manuscript edits, or public release of data or derivatives.

## Title

V53 MM-UAV annotated-only feature-alignment preflight.

## Goal

Prepare a scientifically defensible, reproducible private MM-UAV research path that does not assume raw-grid alignment.

The V53 deliverable is a source-locked RGB-supervised dataset contract plus a minimal experimental learned feature-alignment scaffold that is ready for a separately authorized 200-step GPU pilot.

## Required Start

Run:

```powershell
git switch research/ra-repdet-triair
git pull --ff-only research research/ra-repdet-triair
git rev-parse HEAD
```

Record the starting commit SHA.

Read first:

- `AGENTS.md`
- `docs/PROJECT_CONTEXT.md`
- `docs/EXPERIMENT_STATUS.md`
- `docs/TASK_BLOCKER.md`
- `docs/NEXT_TASK.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`
- all contract and alignment evidence under `runs/v52_mmuav_audit/`
- the existing TriAir model builders, stems, fusion code, dataset adapters, trainer interfaces, and tests needed for compatibility review
- pinned official MM-UAV alignment evidence recorded by V52

Do not modify V40--V52 historical evidence except the current status, blocker, and handoff files explicitly listed below.

## Standing Private-Research Boundary

- Work only with locally available MM-UAV files.
- Do not copy raw images, event frames, annotations, or transformed media into Git.
- Do not publish or redistribute MM-UAV media, annotations, derivative labels, or converted datasets.
- Keep the unresolved dataset license visible in status and handoff records.
- The unresolved redistribution license is not a reason to repeatedly ask whether this local-only task is private; that scope is already frozen.
- Stop and request a new authorization only before public release, external sharing, commercial use, or manuscript/public benchmark claims.

## Frozen V52 Facts

Preserve the following unless a reproducible parser bug is found:

- local root: `E:\MM-UAV_extracted\MMMUAV\train`;
- 424 complete source-train sequences; incomplete sequence `0512` remains quarantined;
- sequence-disjoint split: 339 train / 85 development-validation sequences;
- frozen interval-20 source indices: `1, 21, 41, ...`;
- frozen interval-20 rows: 45,036;
- rows with any RGB or IR source GT: 9,138;
- rows with RGB GT: 9,032 total = 7,187 train + 1,845 development-validation;
- rows with IR GT: 9,007;
- rows with both RGB and IR GT: 8,901;
- RGB-only rows: 131;
- IR-only rows: 106;
- rows with no source GT: 35,898 and status `UNLABELED`;
- common-track RGB/IR rows: 8,883;
- native grids: RGB 640x360, IR 640x512, event 346x260;
- event frames have no independent detection boxes;
- direct raw RGB/IR/event channel concatenation is invalid;
- no official deterministic raw-grid RGB/IR/event transform was found;
- official evidence supports learned feature alignment rather than raw-grid registration;
- V51 remains separate and must not be changed by this task.

## Supervised Target Contract

Freeze RGB as the sole detection-output coordinate system for V53.

The formal supervised set contains exactly the 9,032 frozen interval-20 rows with at least one valid RGB source GT row:

- train: 7,187;
- development-validation: 1,845.

Rules:

- RGB boxes are the only detector targets.
- IR boxes are metadata for correspondence and alignment diagnostics only.
- Event has no detector target.
- The 106 IR-only rows must not enter RGB detection training or evaluation.
- The 35,898 no-GT rows must remain `UNLABELED`; never create empty targets from them.
- Do not interpolate, propagate, pseudo-label, nearest-frame transfer, or copy boxes across modalities.
- Preserve source sequence, split, frame index, paths, original interval-20 row ID, and source GT paths.
- Do not move sequences between train and development-validation.

Create:

```text
runs/v53_mmuav_feature_alignment_preflight/
runs/v53_mmuav_feature_alignment_preflight/manifests/train_rgb_supervised.txt
runs/v53_mmuav_feature_alignment_preflight/manifests/devval_rgb_supervised.txt
runs/v53_mmuav_feature_alignment_preflight/rgb_target_contract.md
runs/v53_mmuav_feature_alignment_preflight/rgb_target_contract.json
runs/v53_mmuav_feature_alignment_preflight/manifest_integrity.md
runs/v53_mmuav_feature_alignment_preflight/manifest_hashes.json
```

Fail closed if the exact 7,187 / 1,845 / 9,032 counts cannot be reproduced.

## Dataset Adapter

Implement a V53-specific adapter without changing the established TriAir dataset behavior.

Preferred location:

```text
datasets/mmuav_feature_alignment_dataset.py
```

Each sample must expose:

```text
rgb
ir
event
target_rgb
sequence_id
frame_index
split
original_row_id
rgb_gt_present
ir_gt_present
common_track_ids
modality_native_shapes
modality_transforms
```

Requirements:

- load RGB, IR, and event independently from their native files;
- validate exact synchronized source frame IDs;
- reject missing or mismatched media rather than substituting nearby frames;
- preserve independent modality geometry metadata;
- apply deterministic, explicitly recorded branch-specific preprocessing;
- transform detection boxes only through the RGB preprocessing path;
- never transform RGB boxes with the IR or event preprocessing transform;
- avoid loading complete sequences into memory;
- deterministic evaluation behavior;
- no raw-channel concatenation in the adapter;
- no CUDA operations.

A valid implementation may resize or letterbox modalities independently for their own stems, but must not describe that preprocessing as spatial registration.

## Experimental Feature-Alignment Scaffold

Implement a minimal experimental scaffold isolated from the production TriAir training path.

Preferred locations after repository inspection:

```text
rarepdet/experimental/mmuav_feature_alignment.py
rarepdet/experimental/mmuav_feature_alignment_model.py
```

Do not silently modify the default detector builder or current TriAir experiment configurations.

Required architecture contract:

```text
RGB native input   -> RGB stem -------------------------------> RGB reference features
IR native input    -> IR stem -> learned feature align to RGB -> aligned IR features
Event native input -> Event stem -> learned feature align ----> aligned event features
RGB reference + aligned IR + aligned event -> fusion interface -> detector interface
```

Requirements:

- three independent input branches;
- RGB features define the reference feature grid;
- IR and event are aligned only in feature space;
- no raw image/channel concatenation path;
- no claim of pixel-level calibration;
- expose an `alignment_enabled` switch;
- expose an identity/no-alignment control path for future ablation;
- initialize the learned alignment conservatively near identity where technically valid;
- document whether the implementation is STN-inspired, deformable-alignment-inspired, or another explicitly named mechanism;
- do not copy unexplained constants from provider code;
- do not fit alignment using development-validation GT;
- do not use detection metrics to choose alignment hyperparameters in V53;
- maintain a clean interface so a later task can compare alignment-off versus alignment-on under the same detector and data contract.

V53 may use synthetic tensors and CPU-loaded real samples for forward, shape, and gradient tests. It must not run CUDA or optimize on the dataset.

## Pre-Registration Outputs

Create:

```text
runs/v53_mmuav_feature_alignment_preflight/method_contract.md
runs/v53_mmuav_feature_alignment_preflight/method_contract.json
runs/v53_mmuav_feature_alignment_preflight/alignment_design.md
runs/v53_mmuav_feature_alignment_preflight/alignment_design.json
runs/v53_mmuav_feature_alignment_preflight/ablation_contract.md
runs/v53_mmuav_feature_alignment_preflight/compute_estimate.json
runs/v53_mmuav_feature_alignment_preflight/source_lock_v53.md
runs/v53_mmuav_feature_alignment_preflight/source_lock_v53.json
runs/v53_mmuav_feature_alignment_preflight/preflight_commands.txt
runs/v53_mmuav_feature_alignment_preflight/preflight_output.txt
runs/v53_mmuav_feature_alignment_preflight/pilot_gate.json
```

The future minimum ablation contract must be frozen as:

1. RGB-only detector;
2. three independent stems with alignment disabled;
3. learned feature alignment enabled with fixed/equal fusion;
4. learned feature alignment enabled with RA dynamic fusion.

Do not run these experiments in V53.

Record parameter counts and CPU-side shape-based compute estimates for the experimental alignment scaffold where practical. Clearly label estimates versus measured values.

## Pilot Gate

The V53 pilot gate must remain locked:

```json
{
  "locked": true,
  "gpu_optimizer_steps": 0,
  "reason": "V53_CPU_ONLY_PRE-REGISTRATION_AND_PREFLIGHT"
}
```

No CUDA availability probe, GPU forward/backward, 200-step pilot, checkpoint creation, epoch training, inference benchmark, AP evaluation, or multi-seed experiment is authorized.

A future task may unlock a 200-step pilot only after:

- manifests reproduce exact counts and hashes;
- adapter tests pass;
- no raw-concatenation path exists;
- feature-alignment interface and alignment-off control are frozen;
- source-lock files are complete;
- estimated RTX 3090 memory risk is documented;
- the user separately authorizes GPU work.

## Required Tests

Add V53-specific tests, preferably under:

```text
tests/test_v53_mmuav_feature_alignment.py
```

At minimum verify:

- exact train/devval/total RGB-supervised counts: 7,187 / 1,845 / 9,032;
- all 106 IR-only rows are excluded from RGB supervision;
- all 35,898 no-GT rows remain `UNLABELED` and excluded;
- train and development-validation sequences are disjoint;
- original interval-20 row IDs remain traceable;
- every manifest media path and RGB GT path exists;
- synchronized frame IDs match exactly across RGB/IR/event;
- RGB boxes are transformed only by the RGB transform;
- adapter returns native-shape and transform metadata;
- model has three independent branches;
- no raw-channel concatenation route is present;
- alignment-off and alignment-on CPU forward paths produce valid finite feature shapes;
- identity/near-identity initialization behaves as documented;
- a CPU synthetic backward test yields finite gradients in enabled alignment parameters;
- no development-validation GT fitting code path exists;
- no CUDA call or GPU optimizer step occurs;
- pilot gate remains locked;
- protected V40--V52 evidence and manuscript files are unchanged.

Save exact commands and full outputs.

## Allowed Changes

- `docs/NEXT_TASK.md`
- `docs/EXPERIMENT_STATUS.md`
- `docs/TASK_BLOCKER.md`
- `docs/PROJECT_CONTEXT.md`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`
- `runs/v53_mmuav_feature_alignment_preflight/**`
- V53-specific dataset adapter files under `datasets/**`
- isolated experimental alignment/model files under `rarepdet/experimental/**`
- V53-specific CPU tools under `rarepdet/tools/**`
- V53 tests under `tests/**`

## Forbidden Changes

- raw MM-UAV files or source annotations;
- public or redistributable MM-UAV derivative datasets;
- V40--V52 historical evidence other than current handoff/status pointers;
- V51 process evidence or status history;
- default TriAir dataset semantics;
- production detector/trainer defaults unless a later task explicitly approves integration;
- manuscript files;
- GPU run outputs, checkpoints, or metrics.

## Decision Output

At completion choose exactly one:

- `V53_CPU_PREFLIGHT_READY_FOR_SEPARATE_GPU_AUTHORIZATION`
- `V53_BLOCKED_RGB_SUPERVISED_MANIFEST_CONTRACT`
- `V53_BLOCKED_DATA_ADAPTER_OR_SYNCHRONIZATION`
- `V53_BLOCKED_FEATURE_ALIGNMENT_IMPLEMENTATION`
- `V53_BLOCKED_COMPUTE_OR_TEST_PREFLIGHT`

Update:

```text
docs/EXPERIMENT_STATUS.md
docs/TASK_BLOCKER.md
runs/handoff_latest.md
runs/handoff_latest.json
```

Do not mark the GPU pilot as authorized.

## Finish

Run:

```powershell
powershell -ExecutionPolicy Bypass -File rarepdet/tools/finish_task.ps1
```

Commit and push with a concise message such as:

```text
exp: prepare V53 MM-UAV feature-alignment preflight
```

The final report must state:

- starting and final commit SHA;
- exact RGB-supervised train/devval/total counts;
- excluded IR-only and `UNLABELED` counts;
- created manifest hashes;
- adapter and experimental module paths;
- selected alignment mechanism and initialization;
- alignment-off control availability;
- parameter/compute estimates;
- test results;
- protected-file verification;
- pilot-gate status;
- GPU optimizer steps;
- remaining blockers before a 200-step pilot.
