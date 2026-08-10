#!/usr/bin/env python
"""Fail-closed V84 repository, split, and checkpoint identity preflight."""

from __future__ import annotations

from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import torch


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runs/v84_jei_critical_closure/preflight"
TRAIN_SPLIT = ROOT / "reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_train.txt"
VAL_SPLIT = ROOT / "reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt"
EXPECTED_SPLITS = {
    "train": {"rows": 7439, "sha256": "f24117e3fec5833e06e20202f8ea05cbc2242b3977bcb791d95f2099c8b4133f"},
    "devval": {"rows": 2213, "sha256": "722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f"},
}
V48_VARIANTS = {"matched_early", "early_moddrop", "ra_no_moddrop", "ra_full_p015"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def repository_state() -> dict:
    status = subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True).splitlines()
    return {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "commit": git("rev-parse", "HEAD"),
        "branch": git("branch", "--show-current"),
        "remote": git("remote", "get-url", "research"),
        "working_tree_status": status,
        "holdout_accessed": False,
    }


def split_identity() -> dict:
    records = {}
    paths = {"train": TRAIN_SPLIT, "devval": VAL_SPLIT}
    for name, path in paths.items():
        expected = EXPECTED_SPLITS[name]
        record = {
            "path": str(path.relative_to(ROOT)),
            "exists": path.is_file(),
            "expected_rows": expected["rows"],
            "expected_sha256": expected["sha256"],
        }
        if path.is_file():
            record["rows"] = len(path.read_text(encoding="utf-8").splitlines())
            record["sha256"] = sha256(path)
        record["status"] = "PASS" if (
            record.get("rows") == expected["rows"] and record.get("sha256") == expected["sha256"]
        ) else "FAIL"
        records[name] = record
    return {"status": "PASS" if all(row["status"] == "PASS" for row in records.values()) else "FAIL", "splits": records, "holdout_accessed": False}


def check_checkpoint(path: Path, expected: dict, family: str) -> dict:
    result = {
        "family": family,
        "run_id": expected["run_id"],
        "variant": expected.get("variant", expected.get("input_mode")),
        "seed": expected["seed"],
        "checkpoint": str(path),
        "exists": path.is_file(),
        "expected_sha256": expected["checkpoint_sha256"],
    }
    if not path.is_file():
        result.update(status="FAIL", checks={"exists": False})
        return result
    actual_hash = sha256(path)
    checkpoint = torch.load(path, map_location="cpu", weights_only=False)
    cfg = checkpoint.get("model_cfg", {})
    train_args = checkpoint.get("train_args", {})
    expected_epoch = expected.get("selected_epoch", expected.get("checkpoint_epoch"))
    checks = {
        "exists": True,
        "sha256": actual_hash == expected["checkpoint_sha256"],
        "seed": train_args.get("seed") == expected["seed"],
        "epoch": checkpoint.get("epoch") == expected_epoch,
        "model_state": isinstance(checkpoint.get("model_state"), dict),
        "image_size": cfg.get("img_size") == 640,
        "num_classes": cfg.get("num_classes") == 2,
        "fpn_width": cfg.get("fpn_out_channels") == 128,
    }
    if family == "V48":
        checks["model_type"] = cfg.get("model_type") == expected["model"]
        checks["input_channels"] = cfg.get("in_chans") == 5
        checks["modality_dropout"] = float(train_args.get("modality_dropout", -1)) == float(expected["modality_dropout"])
    else:
        checks["input_mode"] = cfg.get("input_mode") == expected["input_mode"]
        checks["input_channels"] = cfg.get("in_chans") == {"rgb": 3, "thermal": 1, "event": 1}[expected["input_mode"]]
        checks["split_sha256"] = expected["split_sha256"] == EXPECTED_SPLITS["devval"]["sha256"]
    result.update(
        actual_sha256=actual_hash,
        epoch=checkpoint.get("epoch"),
        model_cfg=cfg,
        checks=checks,
        status="PASS" if all(checks.values()) else "FAIL",
    )
    return result


def checkpoint_inventory() -> dict:
    v48 = json.loads((ROOT / "runs/v48_complete_ablation/causal_ablation_summary.json").read_text(encoding="utf-8"))
    v48_rows = [row for row in v48["per_run"] if row["variant"] in V48_VARIANTS]
    v81 = json.loads((ROOT / "runs/v81_single_modality_retraining_reconciliation/checkpoint_manifest.json").read_text(encoding="utf-8"))
    records = []
    for row in v48_rows:
        records.append(check_checkpoint(Path(row["weights"]), row, "V48"))
    for row in v81["entries"]:
        path = Path(row["weights"])
        if not path.is_file():
            path = ROOT / "runs/v76_triair_single_modality_ablation/training" / row["run_id"] / "weights/best.pt"
        records.append(check_checkpoint(path, row, "V81"))
    observed_v48 = {(row["variant"], row["seed"]) for row in records if row["family"] == "V48"}
    expected_v48 = {(variant, seed) for variant in V48_VARIANTS for seed in (0, 1, 2)}
    observed_v81 = {row["run_id"] for row in records if row["family"] == "V81"}
    expected_v81 = {f"{mode}_seed{seed}" for mode in ("rgb", "thermal", "event") for seed in (0, 1, 2)}
    complete = (
        len(records) == 21
        and observed_v48 == expected_v48
        and observed_v81 == expected_v81
        and all(row["status"] == "PASS" for row in records)
    )
    return {
        "status": "PASS" if complete else "FAIL",
        "expected_count": 21,
        "verified_count": sum(row["status"] == "PASS" for row in records),
        "v48_required": 12,
        "v81_required": 9,
        "v81_registry_sha256": sha256(ROOT / "runs/v81_single_modality_retraining_reconciliation/checkpoint_manifest.json"),
        "records": records,
        "holdout_accessed": False,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    repo = repository_state()
    splits = split_identity()
    inventory = checkpoint_inventory()
    status = "PASS" if splits["status"] == inventory["status"] == "PASS" else "FAIL"
    write_json(OUT / "repository_state.json", repo)
    write_json(OUT / "split_identity.json", splits)
    write_json(OUT / "checkpoint_inventory.json", inventory)
    lines = [
        "# V84 Preflight Summary",
        "",
        f"Status: `{status}`",
        "",
        f"- Repository commit: `{repo['commit']}`; branch: `{repo['branch']}`.",
        f"- Frozen split identity: `{splits['status']}` (train 7,439; devval 2,213).",
        f"- Checkpoint identity: `{inventory['verified_count']}/{inventory['expected_count']} PASS` (V48 12 + V81 9).",
        "- Locked holdout accessed: `false`.",
        "",
        "Downstream V84 work is authorized only when this preflight status is PASS.",
    ]
    (OUT / "preflight_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "splits": splits["status"], "checkpoints": inventory["verified_count"]}, indent=2))
    if status != "PASS":
        raise SystemExit("V84 preflight failed closed")


if __name__ == "__main__":
    main()
