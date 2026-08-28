# Project Context

Repository: `floomeer83felix-source/RA-RepDet-TriAir`

Local workspace: `D:\work\RepViT-main`

Remote branch: `research/ra-repdet-triair`

Primary TriAir dataset root: `D:\download\triair`

MM-UAV private research subset root: `E:\MM-UAV_extracted\MMMUAV\train`

## Standing User Instruction

All MM-UAV work in this repository is local, private research only. Do not repeatedly ask the user to reconfirm this scope. Reconfirmation is required only if a task proposes public dataset or derivative-data redistribution, external sharing, commercial use, or a new manuscript/public benchmark claim.

The unresolved MM-UAV dataset license must remain documented as a dissemination restriction. Do not publish or redistribute MM-UAV media, annotations, transformed copies, or derivative labels from this repository.

When the user accepts an explicitly proposed next experimental stage, says to proceed, or asks to write the task, immediately write the complete authorization into Git in the same turn. At minimum update `docs/NEXT_TASK.md`, `docs/EXPERIMENT_STATUS.md`, and `docs/TASK_BLOCKER.md`, then push to `research/ra-repdet-triair`. Do not wait for a separate reminder. This standing workflow rule authorizes task documentation only; experiment execution must remain within the newly written task boundary.

## Core Project

This project studies RepViT-based multimodal UAV vehicle detection on TriAir. The main experimental line compares:

- E0: Early Fusion RepViT-FCOS.
- E1: Reliability Fusion RepViT-FCOS.
- E2: Reliability Fusion RepViT-FCOS with modality dropout 0.15.

TriAir uses 5-channel `.npy` samples in RGB, thermal, and event order. Missing label txt files are treated as empty-target images. The detection label class `0` is shifted to torchvision label `1`, with background remaining `0`.

MM-UAV is a separate, method-expansion research line. Direct raw RGB/IR/event channel concatenation is invalid under the V52 audit. Any continued MM-UAV work must use independent modality branches and learned feature-level alignment, with RGB as the detection output coordinate system unless a later task explicitly changes the target contract.

Heavy artifacts must stay local: datasets, `.npy`, weights, checkpoints, prediction images, transformed MM-UAV media, and large visualizations are not part of the GitHub handoff.
