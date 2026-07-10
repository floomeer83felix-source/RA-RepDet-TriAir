#!/usr/bin/env python
"""Validate and summarize the twelve fixed-checkpoint V46 COCO results."""

import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path
from statistics import mean, stdev


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "runs" / "v46_coco_ablation"

RUNS = [
    ("matched_early_seed0", "matched_early", 0),
    ("matched_early_seed1", "matched_early", 1),
    ("matched_early_seed2", "matched_early", 2),
    ("reliability_p015_seed0", "ra_full_p015", 0),
    ("reliability_p015_seed1", "ra_full_p015", 1),
    ("reliability_p015_seed2", "ra_full_p015", 2),
]

METRICS = ["precision", "recall", "f1", "ap50_95", "ap50", "ap75", "ar100"]
IOU_KEYS = [f"{0.50 + 0.05 * index:.2f}" for index in range(10)]

CSV_FIELDS = [
    "protocol",
    "run_id",
    "variant",
    "model",
    "seed",
    "modality_dropout",
    "images",
    "gt_boxes",
    "detections",
    *METRICS,
    *[f"ap_iou_{key.replace('.', '')}" for key in IOU_KEYS],
    "project_ap50",
    "project_ap75",
    "inference_seconds",
    "metric_seconds",
    "fps",
    "checkpoint_sha256",
    "split_sha256",
    "weights",
    "split_file",
    "command",
]


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_protocol(protocol, source_lock):
    expected_split_hash = source_lock["manifests"][protocol]["sha256"]
    expected_checkpoints = {
        record["run_id"]: record["sha256"] for record in source_lock["fixed_checkpoints"]
    }
    records = []
    for run_id, variant, seed in RUNS:
        path = OUTPUT_DIR / "raw" / "coco" / protocol / f"{run_id}.json"
        if not path.is_file():
            raise FileNotFoundError(path)
        record = json.loads(path.read_text(encoding="utf-8"))
        if record["protocol"] != protocol:
            raise RuntimeError(f"protocol mismatch in {path}")
        if record["variant"] != variant or int(record["seed"]) != seed:
            raise RuntimeError(f"run identity mismatch in {path}")
        if record["checkpoint_sha256"] != expected_checkpoints[run_id]:
            raise RuntimeError(f"checkpoint hash mismatch in {path}")
        if record["split_sha256"] != expected_split_hash:
            raise RuntimeError(f"split hash mismatch in {path}")
        if record["coco_backend"] != "pycocotools.cocoeval.COCOeval":
            raise RuntimeError(f"unexpected metric backend in {path}")
        records.append(record)
    return records


def csv_row(record):
    row = {field: record.get(field, "") for field in CSV_FIELDS}
    for key in IOU_KEYS:
        row[f"ap_iou_{key.replace('.', '')}"] = record["ap_by_iou"][key]
    return row


def write_csv(path, rows, fieldnames):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def paired_rows(records):
    by_key = {(record["variant"], int(record["seed"])): record for record in records}
    rows = []
    fields = ["protocol", "seed"]
    for metric in METRICS:
        fields.extend([f"matched_early_{metric}", f"ra_full_p015_{metric}", f"delta_{metric}"])
    for key in IOU_KEYS:
        fields.append(f"delta_ap_iou_{key.replace('.', '')}")

    for seed in (0, 1, 2):
        early = by_key[("matched_early", seed)]
        reliability = by_key[("ra_full_p015", seed)]
        row = {"protocol": early["protocol"], "seed": seed}
        for metric in METRICS:
            row[f"matched_early_{metric}"] = early[metric]
            row[f"ra_full_p015_{metric}"] = reliability[metric]
            row[f"delta_{metric}"] = reliability[metric] - early[metric]
        for key in IOU_KEYS:
            row[f"delta_ap_iou_{key.replace('.', '')}"] = (
                reliability["ap_by_iou"][key] - early["ap_by_iou"][key]
            )
        rows.append(row)
    return rows, fields


def descriptive(values):
    return {
        "mean": mean(values),
        "sample_sd": stdev(values) if len(values) > 1 else None,
        "min": min(values),
        "max": max(values),
        "n": len(values),
    }


def summarize_protocol(records, pairs):
    groups = {}
    for variant in ("matched_early", "ra_full_p015"):
        variant_records = [record for record in records if record["variant"] == variant]
        groups[variant] = {
            metric: descriptive([float(record[metric]) for record in variant_records])
            for metric in METRICS
        }
    paired = {
        metric: descriptive([float(row[f"delta_{metric}"]) for row in pairs])
        for metric in METRICS
    }
    paired["ap_by_iou"] = {
        key: descriptive([float(row[f"delta_ap_iou_{key.replace('.', '')}"]) for row in pairs])
        for key in IOU_KEYS
    }
    return {"groups": groups, "paired_delta_ra_minus_early": paired}


def format_value(value):
    return f"{float(value):.6f}"


def append_protocol_markdown(lines, title, records, pairs, summary):
    lines.extend(
        [
            f"## {title}",
            "",
            "| Run | Variant | Seed | AP50:95 | AP50 | AP75 | AR100 | Precision@0.50 | Recall@0.50 | F1@0.50 |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for record in records:
        lines.append(
            f"| {record['run_id']} | {record['variant']} | {record['seed']} | {format_value(record['ap50_95'])} | {format_value(record['ap50'])} | {format_value(record['ap75'])} | {format_value(record['ar100'])} | {format_value(record['precision'])} | {format_value(record['recall'])} | {format_value(record['f1'])} |"
        )
    lines.extend(
        [
            "",
            "Paired deltas are reliability-aware `p=0.15` minus matched early fusion for the same seed.",
            "",
            "| Seed | Delta AP50:95 | Delta AP50 | Delta AP75 | Delta AR100 |",
            "| ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in pairs:
        lines.append(
            f"| {row['seed']} | {format_value(row['delta_ap50_95'])} | {format_value(row['delta_ap50'])} | {format_value(row['delta_ap75'])} | {format_value(row['delta_ar100'])} |"
        )
    lines.extend(
        [
            "",
            "| Metric | Mean paired delta | Sample SD | Min | Max | n |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for metric in ("ap50_95", "ap50", "ap75", "ar100"):
        stats = summary["paired_delta_ra_minus_early"][metric]
        lines.append(
            f"| {metric} | {format_value(stats['mean'])} | {format_value(stats['sample_sd'])} | {format_value(stats['min'])} | {format_value(stats['max'])} | {stats['n']} |"
        )
    lines.append("")


def main():
    source_lock_path = OUTPUT_DIR / "source_lock_v46.json"
    source_lock = json.loads(source_lock_path.read_text(encoding="utf-8"))
    generated_at = datetime.now().astimezone().isoformat(timespec="seconds")

    all_records = {}
    all_pairs = {}
    summaries = {}
    for protocol in ("devval", "guard"):
        records = load_protocol(protocol, source_lock)
        pairs, pair_fields = paired_rows(records)
        write_csv(
            OUTPUT_DIR / f"coco_{protocol}_per_run.csv",
            [csv_row(record) for record in records],
            CSV_FIELDS,
        )
        write_csv(OUTPUT_DIR / f"coco_{protocol}_paired_deltas.csv", pairs, pair_fields)
        all_records[protocol] = records
        all_pairs[protocol] = pairs
        summaries[protocol] = summarize_protocol(records, pairs)

    summary = {
        "status": "V46_FIXED_COCO_EVALUATION_COMPLETE",
        "generated_at": generated_at,
        "source_lock_sha256": sha256(source_lock_path),
        "backend": "pycocotools.cocoeval.COCOeval",
        "definition": {
            "metric": "single-class COCO bbox AP",
            "iou_thresholds": IOU_KEYS,
            "recall_samples": 101,
            "area": "all",
            "max_detections": 100,
            "detector_score_threshold": 0.001,
        },
        "devval": {
            "manifest": source_lock["manifests"]["devval"],
            "per_run": all_records["devval"],
            **summaries["devval"],
        },
        "guard": {
            "manifest": source_lock["manifests"]["guard"],
            "per_run": all_records["guard"],
            **summaries["guard"],
        },
        "guard_policy": source_lock["guard_policy"],
        "claim_boundary": "These are descriptive three-seed within-TriAir results. The guard is same-dataset held-out evidence and was not used for tuning or selection.",
    }
    (OUTPUT_DIR / "coco_metric_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# V46 COCO-style Metric Summary",
        "",
        f"Generated: {generated_at}",
        "",
        "Status: `V46_FIXED_COCO_EVALUATION_COMPLETE`",
        "",
        "The six fixed matched-early and reliability-aware `p=0.15` checkpoints were evaluated with canonical `pycocotools` bbox evaluation at IoU 0.50:0.05:0.95, 101 recall samples, area=all, and maxDets=100. The detector candidate threshold remained 0.001.",
        "",
        "COCO 101-point AP50/AP75 can differ slightly from the repository's prior all-point project-local AP50/AP75 even when predictions are identical.",
        "",
    ]
    append_protocol_markdown(
        lines,
        "Frozen V40 development-validation",
        all_records["devval"],
        all_pairs["devval"],
        summaries["devval"],
    )
    append_protocol_markdown(
        lines,
        "Locked same-dataset guard",
        all_records["guard"],
        all_pairs["guard"],
        summaries["guard"],
    )
    lines.extend(
        [
            "## Interpretation boundary",
            "",
            "These are descriptive three-seed within-TriAir comparisons. The guard is a locked same-dataset held-out partition, not external data. It was not used for training, tuning, threshold selection, dropout selection, checkpoint selection, ablation selection, or run continuation decisions.",
            "",
        ]
    )
    (OUTPUT_DIR / "coco_metric_summary.md").write_text("\n".join(lines), encoding="utf-8")

    print(
        json.dumps(
            {
                "status": summary["status"],
                "devval_mean_delta_ap50_95": summaries["devval"]["paired_delta_ra_minus_early"]["ap50_95"]["mean"],
                "guard_mean_delta_ap50_95": summaries["guard"]["paired_delta_ra_minus_early"]["ap50_95"]["mean"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
