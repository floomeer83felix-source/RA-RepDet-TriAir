# Current Task

## Title
Phase 5 — Stress-Suite Readiness Audit

## Goal
Perform a read-first, no-training audit of the local RA-RepDet-TriAir repository so that the next task can implement a reproducible test-time multimodal stress suite without guessing about data formats, model interfaces, or evaluation behavior.

## Read First
1. `AGENTS.md` if it exists.
2. `docs/PROJECT_CONTEXT.md`
3. `docs/EXPERIMENT_STATUS.md`
4. `README.md`
5. `runs/clean_block64g16_protocol.md`
6. `runs/phase4b_report.md`
7. `rarepdet/train_early_fusion.py`
8. `rarepdet/eval_map.py`
9. `datasets/triair_dataset.py`
10. `rarepdet/tools/eval_missing_modality.py`
11. `rarepdet/tools/profile_model.py`

## Frozen Assets
- Remote branch: `research/ra-repdet-triair`.
- Manuscript protocol: `block64_guard16_seed0`.
- Train / validation / guard sample counts: `7439 / 2213 / 837`.
- Headline baseline: `R4 Reliability p=0.20` with controlled seeds `0` and `2`.
- Downstream architecture and standard training behavior: RepViT-M0.9 → FPN → FCOS.
- Existing E0–E6 and R0–R4 outputs, checkpoints, split files, and reports.

## Allowed Files To Modify
- `runs/phase5_stress_readiness.md`
- `runs/phase5_stress_readiness.json`
- `runs/handoff_latest.md`
- `runs/handoff_latest.json`
- `docs/TASK_BLOCKER.md` only if needed.

## Forbidden Files To Modify
- All training, model, dataset, loss, and primary evaluation source files.
- All existing configs, split manifests, checkpoints, weights, dataset files, `.npy` files, images, videos, and prior E0–E6/R0–R4 run outputs.
- Do not run a training job, inference sweep, or any GPU-heavy command.

## Required Commands
Run only safe inspection commands appropriate to the local repository, for example:

```text
git status --short
git branch --show-current
git log -1 --oneline
find . -maxdepth 3 -type f | sort
```

Then inspect the repository files named in **Read First**. Use a short CPU-only Python probe only if required to establish the shape, dtype, metadata fields, and temporal-neighbor availability of a small number of existing dataset samples. The probe must be read-only and must not open a GPU context.

## Required Outputs
Create `runs/phase5_stress_readiness.md` and `runs/phase5_stress_readiness.json` containing:

1. Exact file paths and callable entry points for:
   - dataset construction;
   - RGB / thermal / event loading;
   - model construction;
   - fusion/gating implementation;
   - missing-modality handling;
   - validation and AP/F1 computation;
   - logging and result serialization.
2. The exact sample dictionary / tuple schema returned by the validation dataset, including tensor shapes, dtypes, normalization behavior, filenames/IDs, labels, sequence IDs, timestamps, event-window IDs, and any modality masks when available.
3. A definitive answer, supported by code or a small read-only sample probe, to each question:
   - Does the dataset retain raw event streams, timestamps, event voxel bins, or only pre-aggregated event tensors?
   - Are preceding/following event windows addressable from a validation sample?
   - Are RGB, thermal, and event images stored separately or packed in a 5-channel `.npy` tensor?
   - Are sequence / frame identifiers sufficient to audit neighboring-frame leakage?
   - Does the model already expose fusion weights or modality masks during inference?
4. Feasibility status for each Phase 5 stress condition:
   - RGB brightness / exposure;
   - RGB motion blur;
   - thermal contrast compression;
   - event sparsity;
   - event temporal offset;
   - thermal spatial shift;
   - event spatial shift;
   - missing RGB / thermal / event;
   - future unseen combination stress tests.

For each condition, label it `ready`, `requires_adapter`, or `not_supported_with_current_data`, and state the least-invasive implementation location.

5. A proposed, minimal **next implementation task** that adds no training-code changes and preserves the blocked split. Include its exact allowed files, frozen assets, acceptance criteria, CPU/GPU expectations, and an explicit statement that it must not begin a model-training run.

6. A concise list of blockers or ambiguities. If an ambiguity cannot be resolved from repository code and local metadata, create `docs/TASK_BLOCKER.md` instead of guessing.

## Acceptance Criteria
- No changes outside **Allowed Files To Modify**.
- No GPU training, inference sweep, split rewrite, or dataset mutation.
- The report identifies all required code entry points and records actual findings rather than assumptions.
- The report makes a clear go/no-go recommendation for a test-time-only `stress_v1` implementation.
- `runs/handoff_latest.md` summarizes the work, changed paths, command outcomes, git commit SHA, no-training confirmation, and the recommended next task.
- `runs/handoff_latest.json` mirrors the key findings in structured form.
- Commit all allowed outputs with the commit message below and push the current branch.

## Commit Message
`docs: audit stress-suite readiness for R2-RepDet`

## Completion / Blocker Rule
After completing the audit, update the required handoff files, commit, and push. If a required fact cannot be verified safely, write `docs/TASK_BLOCKER.md`, commit that blocker with the partial report and handoff, push, and stop. Do not modify source code or improvise a training run.
