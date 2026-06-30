#!/usr/bin/env python
"""Propose leakage-aware blocked TriAir splits without changing the dataset."""

import argparse
import bisect
import random
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rarepdet.tools.split_audit_common import (  # noqa: E402
    RUNS_DIR,
    add_rgb_hashes,
    add_signatures,
    count_id_guard_violations,
    exact_cross_split_groups,
    fmt,
    markdown_table,
    nearest_signature_pairs,
    read_split_records,
    total_gt,
    value_quantiles,
    write_csv,
)


SUMMARY_HEADERS = [
    "candidate",
    "block_size",
    "guard_band",
    "train_images",
    "val_images",
    "guard_images",
    "train_gt_boxes",
    "val_gt_boxes",
    "guard_gt_boxes",
    "val_share_all_images",
    "val_share_used_images",
    "exact_rgb_matched_val_images",
    "exact_rgb_matched_train_images",
    "exact_rgb_group_count",
    "id_guard_violations",
    "nearest_signature_min",
    "nearest_signature_p50",
    "nearest_signature_p90",
    "fraction_signature_le4",
    "nearest_id_distance_min",
    "nearest_id_distance_p50",
    "recommended",
]


def load_all_records(data_root, train_split, val_split):
    train_records = read_split_records(data_root, train_split, "source_train")
    val_records = read_split_records(data_root, val_split, "source_val")
    by_path = {}
    for record in train_records + val_records:
        by_path[record["rel_path"]] = record
    records = list(by_path.values())
    records.sort(key=lambda item: (item["family"], item["id"] if item["id"] is not None else -1, item["rel_path"]))
    return records


def block_key(record, block_size):
    if record["id"] is None:
        return (record["family"], "unknown", record["rel_path"])
    return (record["family"], int(record["id"]) // int(block_size))


def select_validation_blocks(blocks_by_family, target_ratio, seed):
    rng = random.Random(seed)
    selected = set()
    for family, family_blocks in sorted(blocks_by_family.items()):
        total = sum(len(records) for _, records in family_blocks)
        target = int(round(total * target_ratio))
        order = family_blocks[:]
        rng.shuffle(order)
        current = 0
        chosen = []
        for key, records in order:
            if current >= target and chosen:
                break
            chosen.append(key)
            current += len(records)
        selected.update(chosen)
    return selected


def assign_candidate(records, block_size, guard_band, val_ratio, seed):
    blocks_by_family = {}
    for record in records:
        key = block_key(record, block_size)
        blocks_by_family.setdefault(record["family"], {}).setdefault(key, []).append(record)
    blocks_by_family = {
        family: sorted(blocks.items(), key=lambda item: str(item[0]))
        for family, blocks in blocks_by_family.items()
    }
    val_blocks = select_validation_blocks(blocks_by_family, val_ratio, seed)

    val_records = [record for record in records if block_key(record, block_size) in val_blocks]
    val_rel_paths = {record["rel_path"] for record in val_records}
    val_ids_by_family = {}
    for record in val_records:
        if record["id"] is not None:
            val_ids_by_family.setdefault(record["family"], []).append(int(record["id"]))
    for family in val_ids_by_family:
        val_ids_by_family[family] = sorted(val_ids_by_family[family])

    train_records = []
    guard_records = []
    for record in records:
        if record["rel_path"] in val_rel_paths:
            continue
        ids = val_ids_by_family.get(record["family"], [])
        nearest = nearest_distance(ids, record["id"])
        if nearest is not None and nearest <= guard_band:
            guard_records.append(record)
        else:
            train_records.append(record)
    return train_records, val_records, guard_records


def nearest_distance(sorted_ids, query_id):
    if query_id is None or not sorted_ids:
        return None
    pos = bisect.bisect_left(sorted_ids, int(query_id))
    candidates = []
    if pos < len(sorted_ids):
        candidates.append(abs(sorted_ids[pos] - int(query_id)))
    if pos > 0:
        candidates.append(abs(sorted_ids[pos - 1] - int(query_id)))
    return min(candidates) if candidates else None


def write_candidate_lists(out_dir, candidate, train_records, val_records, guard_records):
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, records in (("train", train_records), ("val", val_records), ("guard", guard_records)):
        path = out_dir / f"{candidate}_{name}.txt"
        path.write_text("\n".join(record["rel_path"] for record in records) + "\n", encoding="utf-8")


def diagnostic_row(candidate, block_size, guard_band, train_records, val_records, guard_records):
    groups = exact_cross_split_groups(train_records, val_records, key="rgb_sha256")
    matched_val = {record["rel_path"] for _, _, val_group in groups for record in val_group}
    matched_train = {record["rel_path"] for _, train_group, _ in groups for record in train_group}
    id_violations, id_distances = count_id_guard_violations(train_records, val_records, guard_band)

    nearest = nearest_signature_pairs(train_records, val_records) if train_records and val_records else []
    sig_distances = [distance for _, _, distance in nearest]
    sig_q = value_quantiles(sig_distances)
    id_q = value_quantiles(id_distances)
    fraction_le4 = sum(1 for value in sig_distances if value <= 4) / max(len(sig_distances), 1)
    used_images = len(train_records) + len(val_records)
    all_images = used_images + len(guard_records)

    return {
        "candidate": candidate,
        "block_size": block_size,
        "guard_band": guard_band,
        "train_images": len(train_records),
        "val_images": len(val_records),
        "guard_images": len(guard_records),
        "train_gt_boxes": total_gt(train_records),
        "val_gt_boxes": total_gt(val_records),
        "guard_gt_boxes": total_gt(guard_records),
        "val_share_all_images": fmt(len(val_records) / max(all_images, 1)),
        "val_share_used_images": fmt(len(val_records) / max(used_images, 1)),
        "exact_rgb_matched_val_images": len(matched_val),
        "exact_rgb_matched_train_images": len(matched_train),
        "exact_rgb_group_count": len(groups),
        "id_guard_violations": id_violations,
        "nearest_signature_min": fmt(sig_q["min"], digits=0),
        "nearest_signature_p50": fmt(sig_q["p50"], digits=0),
        "nearest_signature_p90": fmt(sig_q["p90"], digits=0),
        "fraction_signature_le4": fmt(fraction_le4),
        "nearest_id_distance_min": fmt(id_q["min"], digits=0),
        "nearest_id_distance_p50": fmt(id_q["p50"], digits=0),
        "recommended": "no",
    }


def choose_recommended(rows):
    viable = []
    for row in rows:
        if int(row["exact_rgb_matched_val_images"]) != 0:
            continue
        if int(row["exact_rgb_matched_train_images"]) != 0:
            continue
        if int(row["id_guard_violations"]) != 0:
            continue
        if int(row["val_gt_boxes"]) <= 0:
            continue
        val_share = float(row["val_share_all_images"])
        guard_images = int(row["guard_images"])
        viable.append((abs(val_share - 0.20), guard_images, -int(row["val_gt_boxes"]), row))
    if not viable:
        return None
    viable.sort(key=lambda item: item[:3])
    return viable[0][3]


def main():
    parser = argparse.ArgumentParser(description="Propose blocked TriAir split candidates.")
    parser.add_argument("--data", default=r"D:\download\triair")
    parser.add_argument("--train-split", default=r"D:\download\triair\splits\train.txt")
    parser.add_argument("--val-split", default=r"D:\download\triair\splits\val.txt")
    parser.add_argument("--out", default="runs")
    parser.add_argument("--seed", default=0, type=int)
    parser.add_argument("--val-ratio", default=0.2, type=float)
    args = parser.parse_args()

    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = PROJECT_ROOT / out_dir
    candidate_dir = out_dir / "blocked_split_candidates"

    records = load_all_records(args.data, args.train_split, args.val_split)
    add_rgb_hashes(records, "all")
    add_signatures(records, "all")

    rows = []
    candidate_payloads = []
    for block_size, guard_band in ((64, 16), (128, 32), (256, 64)):
        candidate = f"block{block_size}_guard{guard_band}_seed{args.seed}"
        print(f"Building candidate: {candidate}")
        train_records, val_records, guard_records = assign_candidate(
            records,
            block_size=block_size,
            guard_band=guard_band,
            val_ratio=args.val_ratio,
            seed=args.seed,
        )
        write_candidate_lists(candidate_dir, candidate, train_records, val_records, guard_records)
        row = diagnostic_row(candidate, block_size, guard_band, train_records, val_records, guard_records)
        rows.append(row)
        candidate_payloads.append((row, train_records, val_records, guard_records))

    recommended = choose_recommended(rows)
    if recommended:
        for row in rows:
            row["recommended"] = "yes" if row["candidate"] == recommended["candidate"] else "no"

    write_csv(out_dir / "blocked_split_proposal_summary.csv", SUMMARY_HEADERS, rows)

    lines = [
        "# Blocked Split Proposal Summary",
        "",
        "These are diagnostic candidate lists only. They do not replace `D:\\download\\triair\\splits\\train.txt` or `val.txt`.",
        "",
    ]
    if recommended:
        lines.extend(
            [
                "## Recommendation",
                "",
                f"Recommended candidate: **{recommended['candidate']}**.",
                "",
                "It is selected because it has zero exact RGB-content train/val matches, zero same-family guard-band id violations, and the closest validation share among viable candidates.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "## Recommendation",
                "",
                "No candidate met the zero exact RGB-content match criterion. Use a larger contiguous grouping or family-level holdout before retraining.",
                "",
            ]
        )
    lines.extend(["## Candidate Metrics", ""])
    lines.extend(markdown_table(SUMMARY_HEADERS, rows))
    lines.extend(
        [
            "",
            "## Local Candidate Lists",
            "",
            f"- Directory: `{candidate_dir}`",
            "- Each candidate writes train, val, and guard text files using dataset-relative image paths.",
            "- Guard samples are excluded from training for that candidate.",
            "",
        ]
    )
    (out_dir / "blocked_split_proposal_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved blocked split proposal to: {out_dir}")


if __name__ == "__main__":
    main()
