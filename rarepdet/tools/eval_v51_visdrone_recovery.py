#!/usr/bin/env python
"""Evaluate one frozen V51 validation fold with traceable outputs."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rarepdet.tools.eval_v50_visdrone_seen import evaluate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--fold", required=True, type=int, choices=(0, 1, 2))
    parser.add_argument("--variant", required=True)
    parser.add_argument("--model", required=True, choices=("early", "reliability", "rgb"))
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--data", default=r"D:\datasets\visdrone_seen")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--annotations", required=True)
    parser.add_argument("--weights", required=True)
    parser.add_argument("--img-size", type=int, default=640)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--detector-score-thr", type=float, default=0.001)
    parser.add_argument("--nms-thresh", type=float, default=0.6)
    parser.add_argument("--detections-per-img", type=int, default=100)
    parser.add_argument("--out-json", required=True)
    args = parser.parse_args()
    args.protocol = f"cv_fold_{args.fold}"
    result = evaluate(args)
    result["v51_route"] = "B_GROUP_DISJOINT_CROSS_VALIDATION"
    result["fold"] = args.fold
    result["claim_boundary"] = "cross-validation only; not an independent or blind test"

    output = Path(args.out_json)
    if not output.is_absolute():
        output = PROJECT_ROOT / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    excluded = {"environment", "coco_summary"}
    row = {key: value for key, value in result.items() if key not in excluded}
    for key, value in result["environment"].items():
        row[f"env_{key}"] = value
    with output.with_suffix(".csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row))
        writer.writeheader()
        writer.writerow(row)
    output.with_suffix(".txt").write_text(
        "V51 Route-B frozen-fold evaluation\n"
        f"run_id: {result['run_id']}\nfold: {args.fold}\n"
        f"AP50_95: {result['ap50_95']:.6f}\nAP50: {result['ap50']:.6f}\n"
        f"AP75: {result['ap75']:.6f}\nAR100: {result['ar100']:.6f}\n"
        f"checkpoint_sha256: {result['checkpoint_sha256']}\n"
        f"manifest_sha256: {result['manifest_sha256']}\n"
        f"annotations_sha256: {result['annotations_sha256']}\n"
        f"command: {result['command']}\n\n{result['coco_summary']}",
        encoding="utf-8",
    )
    print(json.dumps({key: result[key] for key in ("run_id", "fold", "ap50_95", "ap50")}, indent=2))


if __name__ == "__main__":
    main()
