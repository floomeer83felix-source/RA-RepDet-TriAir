#!/usr/bin/env python
"""Write the V51 GPU-authorization status and handoff."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "runs/v51_visdrone_recovery"


def now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def write(path, text):
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def main():
    timestamp = now()
    fold_manifest = json.loads((OUTPUT / "fold_manifest.json").read_text(encoding="utf-8"))
    source_lock = json.loads((OUTPUT / "source_lock_v51.json").read_text(encoding="utf-8"))
    status = json.loads((OUTPUT / "cv_run_status.json").read_text(encoding="utf-8"))
    folds = [
        {
            "fold": item["fold"],
            "train_images": item["train_images"],
            "val_images": item["val_images"],
            "train_groups": item["train_groups"],
            "val_groups": item["val_groups"],
        }
        for item in fold_manifest["folds"]
    ]

    experiment_status = f"""# Experiment Status

Updated: {timestamp}

## Active task

`V51_AWAITING_GPU_AUTHORIZATION`

V51 preserves the quarantined V50 evidence and uses a pre-registered Route-B group-disjoint cross-validation recovery protocol.

## Recovery audit

- Starting commit: `{source_lock['starting_commit']}`.
- All 29 V51 frozen artifact hashes and all V50 immutable evidence checks match.
- No V50 queue or RGB training process remains alive.
- Route A rejected: the local DET train/val/test-dev images all occur in V50; `seen_strict` is a subset, and the other VisDrone-named directories are derivatives/reference data.
- Selected route: `B_GROUP_DISJOINT_CROSS_VALIDATION`; no blind or independent-test claim is allowed.

## Frozen folds

- Fold 0: 5,761 train / 2,868 validation images; 212 / 109 groups.
- Fold 1: 5,677 train / 2,952 validation images; 215 / 106 groups.
- Fold 2: 5,820 train / 2,809 validation images; 215 / 106 groups.
- The 321 filename-sequence groups are disjoint within every fold and each image appears in validation exactly once.

## GPU gate

- Queue state: `{status['state']}`.
- Full frozen design: 3 folds x seeds 0/1/2 = 9 from-scratch 50-epoch runs, followed by 18 frozen-checkpoint fold evaluations.
- Estimated wall time on the local RTX 3090: 65-75 hours.
- No V51 training or result-producing inference has started.

## Claim boundary

V51 Route B is RGB-only cross-validation evidence, not an independent test or tri-modal external validation. V50 test metrics remain quarantined and are excluded from V51 selection and reporting.
"""
    write(ROOT / "docs/EXPERIMENT_STATUS.md", experiment_status)

    blocker = f"""# Task Blocker

Status: `V51_AWAITING_GPU_AUTHORIZATION`

Generated: {timestamp}

## Exact blocker

The non-GPU V51 recovery audit, Route-B decision, three immutable group-disjoint folds, evaluator, queue, reports, and source lock are complete. The next command starts a large GPU experiment, and the user requested an explicit decision before GPU work.

The source-locked full design requires:

- 9 fresh RGB trainings: 3 folds x seeds 0, 1, and 2;
- 50 epochs per run at RGB 640, batch 4;
- 18 frozen TriAir-checkpoint fold evaluations after baseline training;
- no resume from the interrupted V50 run.

## Time estimate

- V50 observed training throughput: 1,618 iterations in approximately 409 seconds (`0.253 s/iteration`).
- V51 fold training size: approximately 1,420-1,455 iterations per epoch.
- V50 frozen-checkpoint inference throughput: approximately 22 images/second.
- Expected full-design wall time on the RTX 3090: 65-75 hours, including per-epoch fold validation and final evaluations.

## Validation completed

- V50 immutable/source-lock checks: all match.
- V51 source-lock hashes: 29/29 match.
- V51 tests: 4/4 pass.
- Fold validation sizes: 2,868 / 2,952 / 2,809 images.
- No group leakage and no GPU process started.

## Decision options

1. Authorize the full frozen design: 9 training runs, estimated 65-75 hours. This preserves the current source lock and strongest Route-B evidence.
2. Authorize a reduced design: one seed per fold (seeds 0/1/2 assigned across the three folds), estimated 22-26 hours. This requires a pre-training source-lock amendment and yields weaker evidence without within-fold seed replication.

No training will start until one option is explicitly authorized.

## Related files

- `runs/v51_visdrone_recovery/recovery_audit.md`
- `runs/v51_visdrone_recovery/route_decision.md`
- `runs/v51_visdrone_recovery/fold_integrity.md`
- `runs/v51_visdrone_recovery/source_lock_v51.md`
- `runs/v51_visdrone_recovery/cv_run_status.json`
- `runs/v50_visdrone_seen/protocol_violation_evidence.json`
"""
    write(ROOT / "docs/TASK_BLOCKER.md", blocker)

    handoff = f"""# RA-RepDet-TriAir Handoff

Generated: {timestamp}

## Current task

- Task: V51 clean VisDrone evidence recovery.
- Status: `V51_AWAITING_GPU_AUTHORIZATION`.
- Starting commit: `{source_lock['starting_commit']}`.
- Selected route: Route B, pre-registered group-disjoint cross-validation.
- Route A rejected because all local source DET partitions overlap V50; remaining VisDrone-named data are derivatives/reference data.

## Frozen protocol

- Three folds over 8,629 images and 321 filename-sequence groups.
- Validation fold sizes: 2,868 / 2,952 / 2,809.
- Full design: 9 fresh RGB 50-epoch runs plus 18 frozen-checkpoint evaluations.
- Queue requires explicit `--confirm-gpu-authorized` and has not started.
- Estimated full-design wall time: 65-75 hours on the local RTX 3090.

## Integrity

- V51 tests: 4/4 pass.
- Frozen hashes: 29/29 match.
- V50 protocol-violation evidence remains immutable and quarantined.
- No V50 or V51 training process is alive.

## Claim boundary

Route B is cross-validation only, not an independent/blind test. RGB-only and zero-channel evidence cannot validate external thermal/event fusion or physical sensor failure.
"""
    write(ROOT / "runs/handoff_latest.md", handoff)
    payload = {
        "generated_at": timestamp,
        "task": "V51 clean VisDrone evidence recovery",
        "status": "V51_AWAITING_GPU_AUTHORIZATION",
        "starting_commit": source_lock["starting_commit"],
        "route": "B_GROUP_DISJOINT_CROSS_VALIDATION",
        "folds": folds,
        "source_lock_hash_count": len(source_lock["frozen_hashes"]),
        "tests": {"passed": 4, "failed": 0},
        "gpu": {
            "started": False,
            "full_training_runs": 9,
            "zero_shot_evaluations": 18,
            "estimated_hours": [65, 75],
            "authorization_required": True,
        },
        "claim_boundary": {
            "blind_or_independent_test": False,
            "tri_modal_external_validation": False,
            "v50_test_metrics_quarantined": True,
        },
    }
    (ROOT / "runs/handoff_latest.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
