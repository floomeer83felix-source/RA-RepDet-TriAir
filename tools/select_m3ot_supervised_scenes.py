#!/usr/bin/env python3
"""Freeze three group-covering M3OT val scenes without using predictions."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from datasets.m3ot_dataset import M3OTExternalDataset


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def select(records: list[dict]) -> dict:
    chosen = {}
    for group in ("1", "2"):
        rows = [row for row in records if row["group"] == group and row["boxes_xywh"]]
        if not rows:
            raise ValueError(f"No annotated val frames in M3OT group {group}")
        median_count = statistics.median(len(row["boxes_xywh"]) for row in rows)
        midpoint = (len(rows) - 1) / 2
        index, row = min(enumerate(rows),
                         key=lambda item: (abs(len(item[1]["boxes_xywh"]) - median_count),
                                           abs(item[0] - midpoint), item[1]["sample_id"]))
        chosen[f"group{group}_typical"] = {"sample_id": row["sample_id"],
                                            "group": group,
                                            "gt_boxes": len(row["boxes_xywh"]),
                                            "group_median_gt_boxes": median_count,
                                            "frame_rank": index}
    excluded = {row["sample_id"] for row in chosen.values()}
    dense = min((row for row in records if row["sample_id"] not in excluded),
                key=lambda row: (-len(row["boxes_xywh"]), row["sample_id"]))
    chosen["dense"] = {"sample_id": dense["sample_id"],
                       "group": dense["group"], "gt_boxes": len(dense["boxes_xywh"])}
    return chosen


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error(f"Refusing to replace frozen scene selection: {args.output}")
    dataset = M3OTExternalDataset(args.manifest, model_type="early", expected_split="val")
    chosen = select(dataset.records)
    payload = {"selection_policy": "Per-group median GT-count frame nearest sequence midpoint; third scene maximizes GT count; sample ID breaks ties; no prediction used.",
               "prediction_independent": True, "source_split": "val",
               "manifest": str(args.manifest.resolve()),
               "manifest_sha256": sha256(args.manifest), "selected": chosen}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    for label, row in chosen.items():
        print(f"{label}: {row['sample_id']} GT={row['gt_boxes']}")
    print(args.output)


if __name__ == "__main__":
    main()
