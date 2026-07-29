#!/usr/bin/env python
"""Run evaluator-only completion for nine retained V76 single-modality checkpoints.

This script never trains, tunes, replaces seeds, or accesses the guard partition.
It fails before evaluation unless all nine retained ``best.pt`` files and the
frozen component-disjoint validation manifest are present.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODES = ("rgb", "thermal", "event")
SEEDS = (0, 1, 2)
DEFAULT_CHECKPOINT_ROOT = PROJECT_ROOT / "runs" / "v76_triair_single_modality_ablation" / "training"
DEFAULT_OUT = PROJECT_ROOT / "runs" / "v79_single_modality_evaluator_completion"
VAL_SPLIT = PROJECT_ROOT / "reproducibility" / "v40_expanded_adjacency_component_split_v2" / "manifests" / "v40_expanded_adjacency_component_disjoint_val.txt"
EVAL_SCRIPT = PROJECT_ROOT / "rarepdet" / "tools" / "eval_v76_single_modality.py"
SUMMARY_SCRIPT = PROJECT_ROOT / "rarepdet" / "tools" / "build_v79_single_modality_evaluator_summary.py"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve(value: str | Path) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else PROJECT_ROOT / path


def run(command: list[str]) -> None:
    print(subprocess.list2cmdline(command), flush=True)
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=r"D:\download\triair")
    parser.add_argument("--checkpoint-root", default=str(DEFAULT_CHECKPOINT_ROOT))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--check-only", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    checkpoint_root = resolve(args.checkpoint_root)
    out = resolve(args.out)
    data = resolve(args.data)
    val_split = resolve(VAL_SPLIT)
    out.mkdir(parents=True, exist_ok=True)

    required = []
    missing = []
    for mode in MODES:
        for seed in SEEDS:
            run_id = f"{mode}_seed{seed}"
            checkpoint = checkpoint_root / run_id / "weights" / "best.pt"
            required.append({"run_id": run_id, "input_mode": mode, "seed": seed, "checkpoint": str(checkpoint)})
            if not checkpoint.is_file():
                missing.append(str(checkpoint))

    preflight = {
        "status": "READY" if not missing and val_split.is_file() and data.is_dir() else "BLOCKED",
        "task": "V79_SINGLE_MODALITY_EVALUATOR_ONLY_COMPLETION",
        "training_authorized": False,
        "guard_used": False,
        "data": str(data),
        "data_exists": data.is_dir(),
        "validation_split": str(val_split),
        "validation_split_exists": val_split.is_file(),
        "validation_split_sha256": sha256(val_split) if val_split.is_file() else None,
        "required_checkpoints": required,
        "missing_checkpoints": missing,
        "metrics": ["ap50_95", "ap50", "ap75", "ar1", "ar10", "ar100"],
        "score_threshold": 0.001,
        "nms_threshold": 0.6,
        "max_detections": 100,
        "selection_rule": "evaluate the already-retained best development-validation project-local AP50 checkpoint once",
    }
    (out / "preflight.json").write_text(json.dumps(preflight, indent=2) + "\n", encoding="utf-8")

    blockers = []
    if not data.is_dir():
        blockers.append(f"dataset directory missing: {data}")
    if not val_split.is_file():
        blockers.append(f"validation manifest missing: {val_split}")
    if missing:
        blockers.append(f"retained checkpoints missing: {len(missing)}/9")
    if blockers:
        raise SystemExit("V79 evaluator preflight blocked; " + "; ".join(blockers) + f". See {out / 'preflight.json'}")
    if args.check_only:
        print(f"V79 preflight passed: all nine checkpoints are present. {out / 'preflight.json'}")
        return

    raw = out / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    for item in required:
        result = raw / f"{item['run_id']}.json"
        checkpoint = Path(item["checkpoint"])
        if args.resume and result.is_file():
            record = json.loads(result.read_text(encoding="utf-8"))
            if (
                record.get("checkpoint_sha256") == sha256(checkpoint)
                and record.get("split_sha256") == sha256(val_split)
                and all(key in record for key in ("ap50_95", "ar1", "ar10", "ar100"))
            ):
                print(f"skip verified evaluator result: {item['run_id']}")
                continue
        run([
            sys.executable,
            str(EVAL_SCRIPT),
            "--input-mode", item["input_mode"],
            "--seed", str(item["seed"]),
            "--data", str(data),
            "--split-file", str(val_split),
            "--weights", str(checkpoint),
            "--out-json", str(result),
            "--img-size", "640",
            "--batch-size", str(args.batch_size),
            "--num-workers", str(args.num_workers),
            "--device", args.device,
        ])

    run([sys.executable, str(SUMMARY_SCRIPT), "--out", str(out)])


if __name__ == "__main__":
    main()
