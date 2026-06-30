#!/usr/bin/env python
"""Audit exact RGB-content duplicates across the current train/val split."""

import argparse
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rarepdet.tools.split_audit_common import (  # noqa: E402
    RUNS_DIR,
    add_rgb_hashes,
    add_signatures,
    direct_rgb_mae,
    exact_cross_split_groups,
    fmt,
    hamming_distance,
    markdown_table,
    read_split_records,
    total_gt,
    value_quantiles,
    write_csv,
)


SUMMARY_HEADERS = ["Metric", "Value", "Notes"]
PAIR_HEADERS = [
    "rank",
    "rgb_sha256",
    "val_path",
    "train_path",
    "val_family",
    "train_family",
    "val_id",
    "train_id",
    "id_distance",
    "rgb_sha256_equal",
    "signature_distance",
    "direct_rgb_mae",
    "val_gt_boxes",
    "train_gt_boxes",
]
GROUP_HEADERS = [
    "rgb_sha256",
    "train_count",
    "val_count",
    "total_count",
    "train_gt_count_set",
    "val_gt_count_set",
    "gt_count_relation",
    "min_id_distance",
    "median_id_distance",
    "min_train_id",
    "max_train_id",
    "min_val_id",
    "max_val_id",
    "families",
]


def id_distance(train_record, val_record):
    if train_record["id"] is None or val_record["id"] is None:
        return None
    if train_record["family"] != val_record["family"]:
        return None
    return abs(int(train_record["id"]) - int(val_record["id"]))


def group_id_distances(train_records, val_records):
    distances = []
    for train in train_records:
        for val in val_records:
            distance = id_distance(train, val)
            if distance is not None:
                distances.append(distance)
    return distances


def representative_pairs(groups, max_pairs=5000):
    rows = []
    rank = 1
    selected = []
    for rgb_sha, train_records, val_records in sorted(
        groups,
        key=lambda item: (
            min(group_id_distances(item[1], item[2]) or [10**12]),
            -(len(item[1]) + len(item[2])),
        ),
    ):
        for val in val_records:
            candidates = []
            for train in train_records:
                distance = id_distance(train, val)
                candidates.append((10**12 if distance is None else distance, val, train))
            selected.append((rgb_sha,) + sorted(candidates, key=lambda item: (item[0], item[2]["rel_path"]))[0])

    seen = {(item[2]["rel_path"], item[3]["rel_path"]) for item in selected}
    for rgb_sha, train_records, val_records in groups:
        candidates = []
        for val in val_records:
            for train in train_records:
                distance = id_distance(train, val)
                candidates.append((10**12 if distance is None else distance, val, train))
        for _, val, train in sorted(candidates, key=lambda item: (item[0], item[1]["rel_path"], item[2]["rel_path"]))[:5]:
            key = (val["rel_path"], train["rel_path"])
            if key not in seen:
                selected.append((rgb_sha, 10**12 if id_distance(train, val) is None else id_distance(train, val), val, train))
                seen.add(key)

    for rgb_sha, _, val, train in selected[:max_pairs]:
        mae = direct_rgb_mae(val["path"], train["path"])
        sig_distance = hamming_distance(val["signature"], train["signature"])
        distance = id_distance(train, val)
        rows.append(
            {
                "rank": rank,
                "rgb_sha256": rgb_sha,
                "val_path": val["rel_path"],
                "train_path": train["rel_path"],
                "val_family": val["family"],
                "train_family": train["family"],
                "val_id": val["id"] if val["id"] is not None else "NA",
                "train_id": train["id"] if train["id"] is not None else "NA",
                "id_distance": distance if distance is not None else "NA",
                "rgb_sha256_equal": str(val["rgb_sha256"] == train["rgb_sha256"]),
                "signature_distance": sig_distance,
                "direct_rgb_mae": fmt(mae),
                "val_gt_boxes": val["gt_boxes"],
                "train_gt_boxes": train["gt_boxes"],
            }
        )
        rank += 1
    return rows


def build_group_rows(groups):
    rows = []
    for rgb_sha, train_records, val_records in groups:
        train_gt_set = sorted({int(record["gt_boxes"]) for record in train_records})
        val_gt_set = sorted({int(record["gt_boxes"]) for record in val_records})
        all_gt_set = sorted(set(train_gt_set) | set(val_gt_set))
        relation = "identical" if len(all_gt_set) == 1 else "different"
        distances = group_id_distances(train_records, val_records)
        q = value_quantiles(distances)
        train_ids = [record["id"] for record in train_records if record["id"] is not None]
        val_ids = [record["id"] for record in val_records if record["id"] is not None]
        families = sorted({record["family"] for record in train_records + val_records})
        rows.append(
            {
                "rgb_sha256": rgb_sha,
                "train_count": len(train_records),
                "val_count": len(val_records),
                "total_count": len(train_records) + len(val_records),
                "train_gt_count_set": ";".join(str(value) for value in train_gt_set),
                "val_gt_count_set": ";".join(str(value) for value in val_gt_set),
                "gt_count_relation": relation,
                "min_id_distance": fmt(q["min"], digits=0),
                "median_id_distance": fmt(q["p50"], digits=0),
                "min_train_id": min(train_ids) if train_ids else "NA",
                "max_train_id": max(train_ids) if train_ids else "NA",
                "min_val_id": min(val_ids) if val_ids else "NA",
                "max_val_id": max(val_ids) if val_ids else "NA",
                "families": ";".join(families),
            }
        )
    return rows


def build_summary(train_records, val_records, groups, group_rows, pair_rows):
    matched_train = {record["rel_path"] for _, train_group, _ in groups for record in train_group}
    matched_val = {record["rel_path"] for _, _, val_group in groups for record in val_group}
    group_sizes = [row["total_count"] for row in group_rows]
    group_val_sizes = [row["val_count"] for row in group_rows]
    id_distances = [row["id_distance"] for row in pair_rows if row["id_distance"] != "NA"]
    size_q = value_quantiles(group_sizes)
    val_size_q = value_quantiles(group_val_sizes)
    id_q = value_quantiles(id_distances)
    identical_groups = sum(1 for row in group_rows if row["gt_count_relation"] == "identical")
    different_groups = sum(1 for row in group_rows if row["gt_count_relation"] == "different")
    label = (
        "CONFIRMED RGB-CONTENT CROSS-SPLIT DUPLICATION"
        if matched_val
        else "NO EXACT RGB-CONTENT CROSS-SPLIT DUPLICATION"
    )

    rows = [
        {"Metric": "interpretation_label", "Value": label, "Notes": "Exact required Phase 3C label."},
        {"Metric": "train_images", "Value": len(train_records), "Notes": "Existing train split rows."},
        {"Metric": "val_images", "Value": len(val_records), "Notes": "Existing validation split rows."},
        {
            "Metric": "exact_rgb_matched_val_images",
            "Value": len(matched_val),
            "Notes": "Validation samples with at least one train sample sharing exact RGB content.",
        },
        {
            "Metric": "exact_rgb_matched_val_fraction",
            "Value": fmt(len(matched_val) / max(len(val_records), 1)),
            "Notes": "Matched validation fraction.",
        },
        {
            "Metric": "exact_rgb_matched_train_images",
            "Value": len(matched_train),
            "Notes": "Train samples with at least one validation sample sharing exact RGB content.",
        },
        {
            "Metric": "exact_rgb_matched_train_fraction",
            "Value": fmt(len(matched_train) / max(len(train_records), 1)),
            "Notes": "Matched train fraction.",
        },
        {"Metric": "cross_split_rgb_groups", "Value": len(groups), "Notes": "Distinct RGB-content hashes present in both splits."},
        {"Metric": "group_total_size_min", "Value": fmt(size_q["min"], digits=0), "Notes": "Train+val samples per matched group."},
        {"Metric": "group_total_size_p50", "Value": fmt(size_q["p50"], digits=0), "Notes": "Train+val samples per matched group."},
        {"Metric": "group_total_size_max", "Value": fmt(size_q["max"], digits=0), "Notes": "Train+val samples per matched group."},
        {"Metric": "group_val_size_p50", "Value": fmt(val_size_q["p50"], digits=0), "Notes": "Validation samples per matched group."},
        {"Metric": "groups_identical_gt_box_counts", "Value": identical_groups, "Notes": "All records in the RGB group have one GT-box count."},
        {"Metric": "groups_different_gt_box_counts", "Value": different_groups, "Notes": "RGB group contains more than one GT-box count."},
        {"Metric": "pair_id_distance_min", "Value": fmt(id_q["min"], digits=0), "Notes": "Representative exact RGB pairs, same filename family only."},
        {"Metric": "pair_id_distance_p50", "Value": fmt(id_q["p50"], digits=0), "Notes": "Representative exact RGB pairs, same filename family only."},
        {"Metric": "pair_id_distance_p90", "Value": fmt(id_q["p90"], digits=0), "Notes": "Representative exact RGB pairs, same filename family only."},
        {"Metric": "train_gt_boxes", "Value": total_gt(train_records), "Notes": "Non-empty label rows in train split."},
        {"Metric": "val_gt_boxes", "Value": total_gt(val_records), "Notes": "Non-empty label rows in validation split."},
        {
            "Metric": "full_multimodal_byte_duplication_claim",
            "Value": "not_claimed",
            "Notes": "This audit only hashes RGB channels; full 5-channel byte equality is not implied.",
        },
    ]
    return rows, label


def main():
    parser = argparse.ArgumentParser(description="Audit exact RGB-content duplicates across TriAir train/val split.")
    parser.add_argument("--data", default=r"D:\download\triair")
    parser.add_argument("--train-split", default=r"D:\download\triair\splits\train.txt")
    parser.add_argument("--val-split", default=r"D:\download\triair\splits\val.txt")
    parser.add_argument("--out", default="runs")
    args = parser.parse_args()

    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = PROJECT_ROOT / out_dir

    train_records = read_split_records(args.data, args.train_split, "train")
    val_records = read_split_records(args.data, args.val_split, "val")
    add_rgb_hashes(train_records, "train")
    add_rgb_hashes(val_records, "val")
    add_signatures(train_records, "train")
    add_signatures(val_records, "val")

    groups = exact_cross_split_groups(train_records, val_records, key="rgb_sha256")
    group_rows = build_group_rows(groups)
    pair_rows = representative_pairs(groups)
    summary_rows, label = build_summary(train_records, val_records, groups, group_rows, pair_rows)

    write_csv(out_dir / "rgb_cross_split_duplicate_summary.csv", SUMMARY_HEADERS, summary_rows)
    write_csv(out_dir / "rgb_cross_split_exact_pairs.csv", PAIR_HEADERS, pair_rows)
    write_csv(out_dir / "rgb_cross_split_group_stats.csv", GROUP_HEADERS, group_rows)

    lines = [
        "# RGB Cross-Split Duplicate Summary",
        "",
        f"Interpretation: **{label}**",
        "",
        "This audit hashes only the first three RGB channels from each `.npy` sample. It does not claim full five-channel multimodal byte duplication.",
        "",
        "## Metrics",
        "",
    ]
    lines.extend(markdown_table(SUMMARY_HEADERS, summary_rows))
    lines.extend(
        [
            "",
            "## Representative Exact RGB Pairs",
            "",
            "The CSV contains representative cross-split pairs from matched RGB-content groups, including direct RGB MAE and 256-bit signature distance checks.",
            "",
        ]
    )
    lines.extend(markdown_table(PAIR_HEADERS, pair_rows[:30]))
    lines.append("")
    (out_dir / "rgb_cross_split_duplicate_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(label)
    print(f"Saved outputs to: {out_dir}")


if __name__ == "__main__":
    main()
