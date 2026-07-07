#!/usr/bin/env python
"""Audit a three-way component-disjoint TriAir split."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from hashlib import sha256
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rarepdet.tools.split_audit_common import (  # noqa: E402
    count_gt_boxes,
    markdown_table,
    parse_family_and_id,
    read_split_entries,
    relative_to_data,
    resolve_data_path,
    rgb_content_sha256,
    write_csv,
)


SPLITS = ("train", "val", "guard")
PAIRINGS = (("train", "val"), ("train", "guard"), ("val", "guard"))
SUMMARY_FIELDS = ["metric", "value", "status", "notes"]


class UnionFind:
    def __init__(self, size: int) -> None:
        self.parent = list(range(size))
        self.rank = [0] * size

    def find(self, value: int) -> int:
        parent = self.parent[value]
        if parent != value:
            self.parent[value] = self.find(parent)
        return self.parent[value]

    def union(self, left: int, right: int) -> None:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root == right_root:
            return
        if self.rank[left_root] < self.rank[right_root]:
            left_root, right_root = right_root, left_root
        self.parent[right_root] = left_root
        if self.rank[left_root] == self.rank[right_root]:
            self.rank[left_root] += 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", required=True)
    parser.add_argument("--train-split", required=True)
    parser.add_argument("--val-split", required=True)
    parser.add_argument("--guard-split", required=True)
    parser.add_argument("--guard-distance", required=True, type=int)
    parser.add_argument("--output-prefix", required=True)
    return parser.parse_args()


def find_inventory(data_root: Path) -> list[Path]:
    preferred = data_root / "data" / "images"
    if preferred.exists():
        paths = sorted(preferred.rglob("*.npy"))
    else:
        paths = sorted(data_root.rglob("*.npy"))
    return [path.resolve() for path in paths]


def split_sha256(entries: list[str]) -> str:
    digest = sha256()
    for entry in entries:
        digest.update(entry.encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def output_paths(root: Path, output_prefix: str) -> tuple[Path, Path, Path]:
    prefix = Path(output_prefix)
    if not prefix.is_absolute():
        prefix = root / prefix
    return prefix.with_suffix(".md"), prefix.with_suffix(".csv"), prefix.with_suffix(".json")


def read_partition_records(data_root: Path, split_file: str, split: str) -> list[dict[str, object]]:
    rows = []
    for entry in read_split_entries(split_file):
        path = resolve_data_path(data_root, entry)
        family, numeric_id = parse_family_and_id(path)
        rows.append(
            {
                "split": split,
                "entry": entry.replace("\\", "/"),
                "path": path,
                "rel_path": relative_to_data(path, data_root),
                "family": family,
                "numeric_id": numeric_id,
                "rgb_sha256": rgb_content_sha256(path),
                "gt_boxes": count_gt_boxes(path),
            }
        )
    return rows


def read_all_partitions(data_root: Path, split_files: dict[str, str]) -> dict[str, list[dict[str, object]]]:
    partitions = {}
    for split, split_file in split_files.items():
        rows = read_partition_records(data_root, split_file, split)
        partitions[split] = rows
        print(f"{split}: loaded {len(rows)} rows")
    return partitions


def build_inventory_records(data_root: Path) -> list[dict[str, object]]:
    paths = find_inventory(data_root)
    records = []
    for idx, path in enumerate(paths, 1):
        family, numeric_id = parse_family_and_id(path)
        records.append(
            {
                "index": idx - 1,
                "path": path,
                "rel_path": relative_to_data(path, data_root),
                "family": family,
                "numeric_id": numeric_id,
                "rgb_sha256": rgb_content_sha256(path),
                "gt_boxes": count_gt_boxes(path),
            }
        )
        if idx % 500 == 0 or idx == len(paths):
            print(f"audit inventory: {idx}/{len(paths)} RGB hashes")
    return records


def build_components(records: list[dict[str, object]], guard_distance: int) -> dict[str, str]:
    uf = UnionFind(len(records))
    by_rgb: dict[str, list[int]] = defaultdict(list)
    by_family: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in records:
        idx = int(record["index"])
        by_rgb[str(record["rgb_sha256"])].append(idx)
        if record["family"] in {"frame", "nframe"} and record["numeric_id"] is not None:
            by_family[str(record["family"])].append(record)

    for group in by_rgb.values():
        if len(group) > 1:
            first = group[0]
            for other in group[1:]:
                uf.union(first, other)

    for family_records in by_family.values():
        ordered = sorted(family_records, key=lambda row: (int(row["numeric_id"]), str(row["rel_path"])))
        for left, right in zip(ordered, ordered[1:]):
            if int(right["numeric_id"]) - int(left["numeric_id"]) <= guard_distance:
                uf.union(int(left["index"]), int(right["index"]))

    root_to_rows: dict[int, list[dict[str, object]]] = defaultdict(list)
    for record in records:
        root_to_rows[uf.find(int(record["index"]))].append(record)
    ordered_components = sorted(
        root_to_rows.values(),
        key=lambda rows: (-len(rows), min(str(row["rel_path"]) for row in rows)),
    )
    component_by_path: dict[str, str] = {}
    for idx, rows in enumerate(ordered_components, 1):
        component_id = f"C{idx:05d}"
        for row in rows:
            component_by_path[str(row["rel_path"])] = component_id
    return component_by_path


def exact_rgb_overlap_groups(left: list[dict[str, object]], right: list[dict[str, object]]) -> int:
    left_hashes = {str(row["rgb_sha256"]) for row in left}
    right_hashes = {str(row["rgb_sha256"]) for row in right}
    return len(left_hashes & right_hashes)


def same_family_distance_stats(
    left: list[dict[str, object]], right: list[dict[str, object]], guard_distance: int
) -> tuple[int, int, str]:
    left_by_family: dict[str, list[int]] = defaultdict(list)
    right_by_family: dict[str, list[int]] = defaultdict(list)
    for row in left:
        if row["family"] in {"frame", "nframe"} and row["numeric_id"] is not None:
            left_by_family[str(row["family"])].append(int(row["numeric_id"]))
    for row in right:
        if row["family"] in {"frame", "nframe"} and row["numeric_id"] is not None:
            right_by_family[str(row["family"])].append(int(row["numeric_id"]))

    violation_pairs = 0
    violating_right_ids = set()
    min_distance = None
    for family in sorted(set(left_by_family) & set(right_by_family)):
        left_ids = sorted(left_by_family[family])
        right_ids = sorted(right_by_family[family])
        left_index = 0
        for right_id in right_ids:
            while left_index < len(left_ids) and left_ids[left_index] < right_id - guard_distance:
                left_index += 1
            scan = left_index
            nearest_candidates = []
            if left_index > 0:
                nearest_candidates.append(abs(left_ids[left_index - 1] - right_id))
            while scan < len(left_ids) and left_ids[scan] <= right_id + guard_distance:
                distance = abs(left_ids[scan] - right_id)
                nearest_candidates.append(distance)
                violation_pairs += 1
                violating_right_ids.add((family, right_id))
                scan += 1
            if scan < len(left_ids):
                nearest_candidates.append(abs(left_ids[scan] - right_id))
            if nearest_candidates:
                local_min = min(nearest_candidates)
                min_distance = local_min if min_distance is None else min(min_distance, local_min)
    return violation_pairs, len(violating_right_ids), "NA" if min_distance is None else str(min_distance)


def pairwise_checks(partitions: dict[str, list[dict[str, object]]], guard_distance: int) -> list[dict[str, object]]:
    rows = []
    for left_name, right_name in PAIRINGS:
        left = partitions[left_name]
        right = partitions[right_name]
        left_paths = {str(row["rel_path"]) for row in left}
        right_paths = {str(row["rel_path"]) for row in right}
        path_overlap = len(left_paths & right_paths)
        rgb_groups = exact_rgb_overlap_groups(left, right)
        pair_count, sample_count, min_distance = same_family_distance_stats(left, right, guard_distance)
        rows.extend(
            [
                {
                    "metric": f"{left_name}_{right_name}_path_overlap",
                    "value": path_overlap,
                    "status": "pass" if path_overlap == 0 else "fail",
                    "notes": "Identical relative paths across partitions.",
                },
                {
                    "metric": f"{left_name}_{right_name}_exact_rgb_overlap_groups",
                    "value": rgb_groups,
                    "status": "pass" if rgb_groups == 0 else "fail",
                    "notes": "Unique exact RGB-content SHA256 groups shared across partitions.",
                },
                {
                    "metric": f"{left_name}_{right_name}_same_family_distance_{guard_distance}_violation_pairs",
                    "value": pair_count,
                    "status": "pass" if pair_count == 0 else "fail",
                    "notes": "Cross-partition same-family ID pairs inside the guard distance.",
                },
                {
                    "metric": f"{left_name}_{right_name}_same_family_distance_{guard_distance}_violating_records",
                    "value": sample_count,
                    "status": "pass" if sample_count == 0 else "fail",
                    "notes": "Records in the second partition with at least one nearby record in the first partition.",
                },
                {
                    "metric": f"{left_name}_{right_name}_min_same_family_id_distance",
                    "value": min_distance,
                    "status": "pass" if min_distance == "NA" or int(min_distance) > guard_distance else "fail",
                    "notes": "Minimum cross-partition same-family numeric ID distance.",
                },
            ]
        )
    return rows


def component_crossing_rows(
    partitions: dict[str, list[dict[str, object]]], component_by_path: dict[str, str]
) -> tuple[list[dict[str, object]], int]:
    component_splits: dict[str, set[str]] = defaultdict(set)
    missing_component_paths = 0
    for split, rows in partitions.items():
        for row in rows:
            component_id = component_by_path.get(str(row["rel_path"]))
            if component_id is None:
                missing_component_paths += 1
                continue
            component_splits[component_id].add(split)
    crossing = [
        {
            "metric": f"component_crossing_{component_id}",
            "value": ",".join(sorted(splits)),
            "status": "fail",
            "notes": "One connected component appears in multiple partitions.",
        }
        for component_id, splits in sorted(component_splits.items())
        if len(splits) > 1
    ]
    if not crossing:
        crossing.append(
            {
                "metric": "component_crossing_count",
                "value": 0,
                "status": "pass",
                "notes": "No connected component crosses partitions.",
            }
        )
    return crossing, missing_component_paths


def label_inventory_rows(partitions: dict[str, list[dict[str, object]]]) -> list[dict[str, object]]:
    rows = []
    for split in SPLITS:
        records = partitions[split]
        gt_total = sum(int(row["gt_boxes"]) for row in records)
        rows.extend(
            [
                {"metric": f"{split}_rows", "value": len(records), "status": "info", "notes": "Split rows."},
                {"metric": f"{split}_gt_boxes", "value": gt_total, "status": "info", "notes": "Total label rows/boxes."},
                {
                    "metric": f"{split}_images_with_gt",
                    "value": sum(1 for row in records if int(row["gt_boxes"]) > 0),
                    "status": "info",
                    "notes": "Images with at least one label row.",
                },
                {
                    "metric": f"{split}_empty_target_images",
                    "value": sum(1 for row in records if int(row["gt_boxes"]) == 0),
                    "status": "info",
                    "notes": "Images with zero label rows, including missing label files.",
                },
            ]
        )
    return rows


def check_manifest_consistency(split_dir: Path, actual_hashes: dict[str, str]) -> tuple[str, str]:
    manifest_json = split_dir / "split_manifest.json"
    if not manifest_json.exists():
        return "warning", "split_manifest.json not found beside split files"
    try:
        payload = json.loads(manifest_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return "fail", f"split_manifest.json parse failed: {exc}"
    recorded = payload.get("split_sha256", {})
    deterministic = payload.get("deterministic_rerun_consistency")
    mismatches = [
        split for split in SPLITS if str(recorded.get(split)) != str(actual_hashes.get(split))
    ]
    if mismatches:
        return "fail", "manifest split SHA256 mismatch: " + ", ".join(mismatches)
    if deterministic is not True:
        return "fail", f"builder deterministic_rerun_consistency is {deterministic}"
    return "pass", "manifest hashes match actual split files and builder rerun consistency is true"


def main() -> int:
    args = parse_args()
    data_root = Path(args.data).resolve()
    split_files = {"train": args.train_split, "val": args.val_split, "guard": args.guard_split}
    md_path, csv_path, json_path = output_paths(PROJECT_ROOT, args.output_prefix)

    partitions = read_all_partitions(data_root, split_files)
    split_entries = {split: [str(row["entry"]) for row in rows] for split, rows in partitions.items()}
    actual_hashes = {split: split_sha256(entries) for split, entries in split_entries.items()}

    print("Rebuilding full component graph for audit...")
    inventory_records = build_inventory_records(data_root)
    component_by_path = build_components(inventory_records, args.guard_distance)
    inventory_paths = {str(row["rel_path"]) for row in inventory_records}
    assigned_paths = [str(row["rel_path"]) for rows in partitions.values() for row in rows]
    assigned_counts = Counter(assigned_paths)
    duplicate_assigned = sorted(path for path, count in assigned_counts.items() if count > 1)
    unknown_assigned = sorted(set(assigned_paths) - inventory_paths)
    missing_assigned = sorted(inventory_paths - set(assigned_paths))

    summary_rows = [
        {"metric": "complete_inventory_count", "value": len(inventory_records), "status": "info", "notes": "All discovered local .npy image samples."},
        {"metric": "unique_inventory_paths", "value": len(inventory_paths), "status": "pass" if len(inventory_paths) == len(inventory_records) else "fail", "notes": "Unique relative paths in local inventory."},
        {"metric": "assigned_total_rows", "value": len(assigned_paths), "status": "info", "notes": "Rows across train, validation, and guard split files."},
        {"metric": "assigned_unique_paths", "value": len(set(assigned_paths)), "status": "info", "notes": "Unique assigned relative paths."},
        {"metric": "missing_inventory_paths", "value": len(missing_assigned), "status": "pass" if not missing_assigned else "fail", "notes": "Local inventory paths absent from all split files."},
        {"metric": "unknown_assigned_paths", "value": len(unknown_assigned), "status": "pass" if not unknown_assigned else "fail", "notes": "Split rows not present in local inventory."},
        {"metric": "duplicate_assigned_paths", "value": len(duplicate_assigned), "status": "pass" if not duplicate_assigned else "fail", "notes": "Paths assigned more than once across all partitions."},
        {"metric": "component_count", "value": len(set(component_by_path.values())), "status": "info", "notes": "Transitive component count in full inventory."},
    ]
    component_sizes = Counter(component_by_path.values())
    summary_rows.append(
        {
            "metric": "largest_component_size",
            "value": max(component_sizes.values()) if component_sizes else 0,
            "status": "info",
            "notes": "Largest connected component size.",
        }
    )
    for split in SPLITS:
        summary_rows.append({"metric": f"{split}_sha256", "value": actual_hashes[split], "status": "info", "notes": "SHA256 of split text entries."})

    split_dir = Path(args.train_split).resolve().parent if Path(args.train_split).is_absolute() else (PROJECT_ROOT / args.train_split).resolve().parent
    manifest_status, manifest_note = check_manifest_consistency(split_dir, actual_hashes)
    summary_rows.append(
        {
            "metric": "deterministic_rerun_consistency",
            "value": manifest_status,
            "status": manifest_status,
            "notes": manifest_note,
        }
    )

    summary_rows.extend(label_inventory_rows(partitions))
    summary_rows.extend(pairwise_checks(partitions, args.guard_distance))
    crossing_rows, missing_component_paths = component_crossing_rows(partitions, component_by_path)
    summary_rows.append(
        {
            "metric": "assigned_paths_missing_component_id",
            "value": missing_component_paths,
            "status": "pass" if missing_component_paths == 0 else "fail",
            "notes": "Assigned paths that could not be mapped to a rebuilt component.",
        }
    )
    if crossing_rows and crossing_rows[0]["metric"] == "component_crossing_count":
        summary_rows.extend(crossing_rows)
    else:
        summary_rows.append(
            {
                "metric": "component_crossing_count",
                "value": len(crossing_rows),
                "status": "fail",
                "notes": "Connected components crossing train/validation/guard.",
            }
        )
        summary_rows.extend(crossing_rows[:50])

    fail_rows = [row for row in summary_rows if row["status"] == "fail"]
    final_status = "PASS" if not fail_rows else "FAIL"
    summary_rows.append(
        {
            "metric": "final_component_disjoint_gate",
            "value": final_status,
            "status": "pass" if final_status == "PASS" else "fail",
            "notes": "Hard continuation gate for V40 GPU work.",
        }
    )

    md_path.parent.mkdir(parents=True, exist_ok=True)
    write_csv(csv_path, SUMMARY_FIELDS, summary_rows)
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "data_root": str(data_root),
        "guard_distance": args.guard_distance,
        "split_files": split_files,
        "split_sha256": actual_hashes,
        "final_component_disjoint_gate": final_status,
        "failed_metrics": [row["metric"] for row in fail_rows],
        "missing_inventory_path_examples": missing_assigned[:20],
        "unknown_assigned_path_examples": unknown_assigned[:20],
        "duplicate_assigned_path_examples": duplicate_assigned[:20],
        "summary_rows": summary_rows,
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md_lines = [
        "# V40 Component-Disjoint Split Audit",
        "",
        f"Final component-disjoint gate: **{final_status}**",
        "",
        f"Data root: `{data_root}`",
        f"Guard distance: `{args.guard_distance}`",
        "",
        "## Summary Metrics",
        "",
    ]
    md_lines.extend(markdown_table(SUMMARY_FIELDS, summary_rows))
    md_lines.extend(
        [
            "",
            "## Gate Interpretation",
            "",
            "- PASS means all local samples are assigned exactly once, no path/exact-RGB/same-family guard-band leakage crosses partitions, components do not cross partitions, and deterministic builder hashes match the audited split files.",
            "- FAIL means V40 must stop before GPU training and report this blocked state.",
            "",
        ]
    )
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    print(f"Final component-disjoint gate: {final_status}")
    print(f"Saved: {md_path}")
    print(f"Saved: {csv_path}")
    print(f"Saved: {json_path}")
    return 0 if final_status == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
