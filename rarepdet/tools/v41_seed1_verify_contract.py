#!/usr/bin/env python
"""Verify the V41 fresh paired seed1 development-validation contract."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path


EXPECTED = {
    "train_manifest": "f24117e3fec5833e06e20202f8ea05cbc2242b3977bcb791d95f2099c8b4133f",
    "val_manifest": "722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f",
    "rarepdet/eval_map.py": "94557cb80ae24b8663e9eb31955afe668b994058cd8e3e7618ae33e4c0017715",
    "rarepdet/metrics.py": "6ffa798647376594befc45f89ebb1aa1a5fbe3b50e5f484e7804c22bac13b081",
}

SOURCE_FILES = [
    "rarepdet/train_early_fusion.py",
    "rarepdet/eval_map.py",
    "rarepdet/metrics.py",
    "rarepdet/data.py",
    "datasets/triair_dataset.py",
    "rarepdet/models/early_fusion_fcos.py",
    "rarepdet/models/repvit_fpn_backbone.py",
]

READ_FIRST_FILES = [
    "AGENTS.md",
    "PROJECT_PROFILE.md",
    "docs/PROJECT_CONTEXT.md",
    "docs/V40_PUBLICATION_SNAPSHOT.md",
    "docs/REPRODUCIBILITY.md",
    "runs/handoff_latest.md",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--source-lock", required=True)
    parser.add_argument("--train-manifest", required=True)
    parser.add_argument("--val-manifest", required=True)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_commit(repo: Path) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    except Exception as exc:
        return f"unavailable: {exc}"


def package_version(name: str) -> str:
    try:
        module = __import__(name)
        return str(getattr(module, "__version__", "unknown"))
    except Exception as exc:
        return f"unavailable: {exc}"


def torch_environment() -> dict[str, object]:
    try:
        import torch
    except Exception as exc:
        return {"torch_import": f"failed: {exc}"}

    env = {
        "torch": torch.__version__,
        "torch_cuda": str(torch.version.cuda),
        "cuda_available": bool(torch.cuda.is_available()),
        "cuda_device_count": int(torch.cuda.device_count()) if torch.cuda.is_available() else 0,
    }
    if torch.cuda.is_available():
        current = torch.cuda.current_device()
        env.update(
            {
                "cuda_current_device": int(current),
                "gpu_name": torch.cuda.get_device_name(current),
                "gpu_total_memory_mib": int(torch.cuda.get_device_properties(current).total_memory // (1024 * 1024)),
            }
        )
    return env


def manifest_count(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def status_row(name: str, path: Path, expected: str | None = None) -> dict[str, object]:
    exists = path.exists()
    actual = sha256_file(path) if exists and path.is_file() else "NA"
    if not exists:
        status = "FAIL"
    elif expected is None:
        status = "RECORDED"
    else:
        status = "PASS" if actual == expected else "FAIL"
    return {
        "name": name,
        "path": str(path),
        "exists": exists,
        "sha256": actual,
        "expected_sha256": expected or "recorded_only",
        "status": status,
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["name", "path", "exists", "sha256", "expected_sha256", "status"]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).resolve()
    out_dir = (repo / args.out).resolve() if not Path(args.out).is_absolute() else Path(args.out).resolve()
    source_lock = (repo / args.source_lock).resolve()
    train_manifest = (repo / args.train_manifest).resolve()
    val_manifest = (repo / args.val_manifest).resolve()

    rows = [
        status_row("source_lock", source_lock, None),
        status_row("train_manifest", train_manifest, EXPECTED["train_manifest"]),
        status_row("val_manifest", val_manifest, EXPECTED["val_manifest"]),
    ]
    for rel in SOURCE_FILES:
        rows.append(status_row(rel, repo / rel, EXPECTED.get(rel)))

    read_first = []
    for rel in READ_FIRST_FILES:
        path = repo / rel
        read_first.append({"path": rel, "exists": path.exists(), "note": "missing file is recorded but not a frozen hash gate"})

    hard_failures = [row for row in rows if row["status"] == "FAIL"]
    env = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "repo": str(repo),
        "git_commit": git_commit(repo),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "packages": {
            "numpy": package_version("numpy"),
            "torchvision": package_version("torchvision"),
            "timm": package_version("timm"),
        },
        "torch": torch_environment(),
    }
    counts = {}
    for name, path in (("train_manifest", train_manifest), ("val_manifest", val_manifest)):
        counts[name] = manifest_count(path) if path.exists() else "NA"

    payload = {
        "status": "PASS" if not hard_failures else "FAIL",
        "hard_failures": hard_failures,
        "contract_rows": rows,
        "read_first_files": read_first,
        "manifest_counts": counts,
        "environment": env,
        "training_contract": {
            "seed": 1,
            "epochs": 50,
            "img_size": 640,
            "batch_size": 4,
            "lr": 1e-4,
            "num_workers": 0,
            "device": "cuda",
            "runs": [
                {"run_id": "matched_early_seed1", "model": "early", "modality_dropout": 0.0},
                {"run_id": "reliability_p015_seed1", "model": "reliability", "modality_dropout": 0.15},
            ],
        },
        "evaluation_contract": {
            "split": "V40 development-validation manifest only",
            "detector_score_thr": 0.001,
            "metric_score_thr": 0.50,
            "nms_thresh": 0.6,
            "detections_per_img": 100,
            "guard_access": "not permitted",
        },
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "contract_verification.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    write_csv(out_dir / "contract_verification.csv", rows)

    lines = [
        "# V41 Seed1 Contract Verification",
        "",
        f"Generated: `{payload['environment']['generated_at']}`",
        f"Status: **{payload['status']}**",
        f"Git commit: `{payload['environment']['git_commit']}`",
        "",
        "## Frozen Hash Checks",
        "",
        "| name | exists | sha256 | expected | status |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(f"| {row['name']} | {row['exists']} | `{row['sha256']}` | `{row['expected_sha256']}` | {row['status']} |")
    lines.extend(
        [
            "",
            "## Manifest Counts",
            "",
            f"- Train manifest rows: {counts['train_manifest']}",
            f"- Development-validation manifest rows: {counts['val_manifest']}",
            "",
            "## Environment",
            "",
            f"- Python: {env['python']}",
            f"- Platform: {env['platform']}",
            f"- PyTorch: {env['torch'].get('torch', 'NA')}",
            f"- Torch CUDA: {env['torch'].get('torch_cuda', 'NA')}",
            f"- CUDA available: {env['torch'].get('cuda_available', 'NA')}",
            f"- GPU: {env['torch'].get('gpu_name', 'NA')}",
            f"- GPU memory MiB: {env['torch'].get('gpu_total_memory_mib', 'NA')}",
            f"- torchvision: {env['packages']['torchvision']}",
            f"- timm: {env['packages']['timm']}",
            f"- numpy: {env['packages']['numpy']}",
            "",
            "## Read-First File Presence",
            "",
            "| path | exists | note |",
            "| --- | --- | --- |",
        ]
    )
    for row in read_first:
        lines.append(f"| {row['path']} | {row['exists']} | {row['note']} |")
    lines.append("")
    if hard_failures:
        lines.append("## Blocking Failures")
        lines.append("")
        for row in hard_failures:
            lines.append(f"- {row['name']}: expected `{row['expected_sha256']}`, got `{row['sha256']}`")
        lines.append("")
    (out_dir / "contract_verification.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Contract verification: {payload['status']}")
    print(f"Saved: {out_dir / 'contract_verification.md'}")
    print(f"Saved: {out_dir / 'contract_verification.json'}")
    return 0 if payload["status"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
