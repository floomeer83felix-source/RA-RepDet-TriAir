#!/usr/bin/env python
"""Build a deterministic component-disjoint TriAir split."""

from __future__ import annotations

import argparse
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
    relative_to_data,
    rgb_content_sha256,
    write_csv,
)


SPLITS = ("train", "val", "guard")
MANIFEST_FIELDS = [
    "component_id",
    "allocated_split",
    "rel_path",
    "family",
    "numeric_id",
    "rgb_sha256",
    "gt_boxes",
    "component_size",
    "component_provenance",
]


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
    parser.add_argument("--data", required=True, help="TriAir data root.")
    parser.add_argument("--target-train", required=True, type=int)
    parser.add_argument("--target-val", required=True, type=int)
    parser.add_argument("--target-guard", required=True, type=int)
    parser.add_argument("--guard-distance", required=True, type=int)
    parser.add_argument("--output-dir", required=True)
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


def write_split(path: Path, entries: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(f"{entry}\n" for entry in entries), encoding="utf-8")


def build_records(data_root: Path) -> list[dict[str, object]]:
    paths = find_inventory(data_root)
    records: list[dict[str, object]] = []
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
            print(f"inventory: {idx}/{len(paths)} RGB hashes")
    return records


def build_components(records: list[dict[str, object]], guard_distance: int) -> list[dict[str, object]]:
    uf = UnionFind(len(records))
    by_rgb: dict[str, list[int]] = defaultdict(list)
    by_family: dict[str, list[dict[str, object]]] = defaultdict(list)
    provenance_by_index: dict[int, set[str]] = defaultdict(set)

    for record in records:
        idx = int(record["index"])
        by_rgb[str(record["rgb_sha256"])].append(idx)
        family = str(record["family"])
        numeric_id = record["numeric_id"]
        if family in {"frame", "nframe"} and numeric_id is not None:
            by_family[family].append(record)

    for group in by_rgb.values():
        if len(group) <= 1:
            continue
        first = group[0]
        for other in group[1:]:
            uf.union(first, other)
        for idx in group:
            provenance_by_index[idx].add("exact_rgb_sha256")

    for family, family_records in by_family.items():
        ordered = sorted(family_records, key=lambda row: (int(row["numeric_id"]), str(row["rel_path"])))
        for left, right in zip(ordered, ordered[1:]):
            if int(right["numeric_id"]) - int(left["numeric_id"]) <= guard_distance:
                left_idx = int(left["index"])
                right_idx = int(right["index"])
                uf.union(left_idx, right_idx)
                provenance_by_index[left_idx].add(f"{family}_distance_le_{guard_distance}")
                provenance_by_index[right_idx].add(f"{family}_distance_le_{guard_distance}")

    grouped: dict[int, list[dict[str, object]]] = defaultdict(list)
    for record in records:
        grouped[uf.find(int(record["index"]))].append(record)

    components = []
    for rows in grouped.values():
        rows = sorted(rows, key=lambda row: str(row["rel_path"]))
        provenance = set()
        for row in rows:
            provenance.update(provenance_by_index.get(int(row["index"]), set()))
        if not provenance:
            provenance.add("singleton")
        components.append(
            {
                "rows": rows,
                "size": len(rows),
                "min_rel_path": str(rows[0]["rel_path"]),
                "provenance": ";".join(sorted(provenance)),
                "gt_boxes": sum(int(row["gt_boxes"]) for row in rows),
            }
        )
    components.sort(key=lambda item: (-int(item["size"]), str(item["min_rel_path"])))
    for idx, component in enumerate(components, 1):
        component["component_id"] = f"C{idx:05d}"
    return components


def allocation_cost(counts: dict[str, int], targets: dict[str, int]) -> tuple[float, int]:
    total_target = max(sum(targets.values()), 1)
    normalized = sum(((counts[split] - targets[split]) / total_target) ** 2 for split in SPLITS)
    absolute = sum(abs(counts[split] - targets[split]) for split in SPLITS)
    return normalized, absolute


def allocate_components(components: list[dict[str, object]], targets: dict[str, int]) -> dict[str, str]:
    counts = {split: 0 for split in SPLITS}
    allocation: dict[str, str] = {}
    for component in components:
        component_id = str(component["component_id"])
        size = int(component["size"])
        choices = []
        for split in SPLITS:
            candidate = dict(counts)
            candidate[split] += size
            choices.append((allocation_cost(candidate, targets), candidate[split], split))
        _, _, best_split = min(choices, key=lambda item: (item[0], item[1], item[2]))
        allocation[component_id] = best_split
        counts[best_split] += size

    improved = True
    while improved:
        improved = False
        current_cost = allocation_cost(counts, targets)
        for component in components:
            component_id = str(component["component_id"])
            current_split = allocation[component_id]
            size = int(component["size"])
            best_move = None
            for split in SPLITS:
                if split == current_split:
                    continue
                candidate = dict(counts)
                candidate[current_split] -= size
                candidate[split] += size
                candidate_cost = allocation_cost(candidate, targets)
                if candidate_cost < current_cost:
                    best_move = (candidate_cost, split, candidate)
                    current_cost = candidate_cost
            if best_move:
                _, new_split, new_counts = best_move
                allocation[component_id] = new_split
                counts = new_counts
                improved = True
                break
    return allocation


def build_manifest_rows(
    components: list[dict[str, object]], allocation: dict[str, str]
) -> list[dict[str, object]]:
    rows = []
    for component in components:
        component_id = str(component["component_id"])
        split = allocation[component_id]
        for record in component["rows"]:
            rows.append(
                {
                    "component_id": component_id,
                    "allocated_split": split,
                    "rel_path": record["rel_path"],
                    "family": record["family"],
                    "numeric_id": record["numeric_id"] if record["numeric_id"] is not None else "NA",
                    "rgb_sha256": record["rgb_sha256"],
                    "gt_boxes": record["gt_boxes"],
                    "component_size": component["size"],
                    "component_provenance": component["provenance"],
                }
            )
    rows.sort(key=lambda row: (str(row["allocated_split"]), str(row["rel_path"])))
    return rows


def summary_rows(
    data_root: Path,
    components: list[dict[str, object]],
    manifest_rows: list[dict[str, object]],
    targets: dict[str, int],
    split_entries: dict[str, list[str]],
    rerun_consistent: bool,
    guard_distance: int,
) -> list[dict[str, object]]:
    counts = Counter(str(row["allocated_split"]) for row in manifest_rows)
    component_counts = Counter()
    for component in components:
        component_counts[split_entries_for_component(component, split_entries)] += 1
    rows = [
        {"metric": "data_root", "value": str(data_root), "notes": "Local inventory root."},
        {"metric": "inventory_count", "value": len(manifest_rows), "notes": "All discovered .npy image samples."},
        {"metric": "unique_paths", "value": len({row["rel_path"] for row in manifest_rows}), "notes": "Unique relative paths in inventory."},
        {"metric": "component_count", "value": len(components), "notes": "Transitive components after exact-RGB and same-family proximity edges."},
        {"metric": "largest_component_size", "value": max((int(component["size"]) for component in components), default=0), "notes": "Largest connected component size."},
        {"metric": "guard_distance", "value": guard_distance, "notes": "Same-family ID distance used for component edges."},
        {"metric": "target_train", "value": targets["train"], "notes": "Requested train count."},
        {"metric": "target_val", "value": targets["val"], "notes": "Requested validation count."},
        {"metric": "target_guard", "value": targets["guard"], "notes": "Requested guard count."},
    ]
    for split in SPLITS:
        rows.append({"metric": f"achieved_{split}", "value": counts.get(split, 0), "notes": "Whole-component allocation count."})
        rows.append({"metric": f"{split}_sha256", "value": split_sha256(split_entries[split]), "notes": "SHA256 of split text entries."})
    rows.append({"metric": "deterministic_rerun_consistency", "value": "pass" if rerun_consistent else "fail", "notes": "Second in-process build produced identical split entries."})
    return rows


def split_entries_for_component(component: dict[str, object], split_entries: dict[str, list[str]]) -> str:
    first = str(component["rows"][0]["rel_path"])
    for split, entries in split_entries.items():
        if first in set(entries):
            return split
    return "unknown"


def build_from_records(records: list[dict[str, object]], targets: dict[str, int], guard_distance: int) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, list[str]], dict[str, str]]:
    components = build_components(records, guard_distance)
    allocation = allocate_components(components, targets)
    manifest_rows = build_manifest_rows(components, allocation)
    split_entries = {
        split: sorted(str(row["rel_path"]) for row in manifest_rows if row["allocated_split"] == split)
        for split in SPLITS
    }
    split_hashes = {split: split_sha256(entries) for split, entries in split_entries.items()}
    return components, manifest_rows, split_entries, split_hashes


def write_reports(
    output_dir: Path,
    data_root: Path,
    components: list[dict[str, object]],
    manifest_rows: list[dict[str, object]],
    split_entries: dict[str, list[str]],
    split_hashes: dict[str, str],
    targets: dict[str, int],
    guard_distance: int,
    rerun_consistent: bool,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for split, entries in split_entries.items():
        write_split(output_dir / f"{split}.txt", entries)
    write_csv(output_dir / "split_manifest.csv", MANIFEST_FIELDS, manifest_rows)

    counts = Counter(str(row["allocated_split"]) for row in manifest_rows)
    component_allocation_rows = []
    for component in components:
        component_id = str(component["component_id"])
        split = next(
            str(row["allocated_split"])
            for row in manifest_rows
            if row["component_id"] == component_id
        )
        component_allocation_rows.append(
            {
                "component_id": component_id,
                "allocated_split": split,
                "component_size": component["size"],
                "gt_boxes": component["gt_boxes"],
                "min_rel_path": component["min_rel_path"],
                "component_provenance": component["provenance"],
            }
        )
    write_csv(
        output_dir / "component_allocation.csv",
        ["component_id", "allocated_split", "component_size", "gt_boxes", "min_rel_path", "component_provenance"],
        component_allocation_rows,
    )

    summary = summary_rows(
        data_root,
        components,
        manifest_rows,
        targets,
        split_entries,
        rerun_consistent,
        guard_distance,
    )
    write_csv(output_dir / "split_build_summary.csv", ["metric", "value", "notes"], summary)

    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "data_root": str(data_root),
        "targets": targets,
        "guard_distance": guard_distance,
        "inventory_count": len(manifest_rows),
        "component_count": len(components),
        "largest_component_size": max((int(component["size"]) for component in components), default=0),
        "achieved_counts": {split: counts.get(split, 0) for split in SPLITS},
        "split_sha256": split_hashes,
        "deterministic_rerun_consistency": rerun_consistent,
        "component_allocation": component_allocation_rows,
        "manifest_rows": manifest_rows,
    }
    (output_dir / "split_manifest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md_lines = [
        "# V40 Component-Disjoint Split Build",
        "",
        "This CPU-only build assigns complete transitive components to train, validation, or guard. Components are induced by exact RGB-content SHA256 identity and same-family numeric-ID distance less than or equal to the configured guard distance.",
        "",
        "## Summary",
        "",
    ]
    md_lines.extend(markdown_table(["metric", "value", "notes"], summary))
    md_lines.extend(
        [
            "",
            "## Component Allocation",
            "",
        ]
    )
    md_lines.extend(
        markdown_table(
            ["component_id", "allocated_split", "component_size", "gt_boxes", "min_rel_path", "component_provenance"],
            component_allocation_rows[:50],
        )
    )
    if len(component_allocation_rows) > 50:
        md_lines.append("")
        md_lines.append(f"Only the first 50 of {len(component_allocation_rows)} components are shown; see `component_allocation.csv`.")
    md_lines.append("")
    (output_dir / "split_build_report.md").write_text("\n".join(md_lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    data_root = Path(args.data).resolve()
    output_dir = (PROJECT_ROOT / args.output_dir).resolve() if not Path(args.output_dir).is_absolute() else Path(args.output_dir)
    targets = {"train": args.target_train, "val": args.target_val, "guard": args.target_guard}
    if sum(targets.values()) <= 0:
        raise SystemExit("ERROR: target counts must be positive in aggregate.")

    print("Reading inventory and RGB hashes...")
    records = build_records(data_root)
    print("Building primary V40 component split...")
    components, manifest_rows, split_entries, split_hashes = build_from_records(records, targets, args.guard_distance)
    print("Rebuilding allocation once from the same immutable inventory to verify deterministic split hashes...")
    _, _, rerun_entries, rerun_hashes = build_from_records(records, targets, args.guard_distance)
    rerun_consistent = split_entries == rerun_entries and split_hashes == rerun_hashes

    write_reports(
        output_dir,
        data_root,
        components,
        manifest_rows,
        split_entries,
        split_hashes,
        targets,
        args.guard_distance,
        rerun_consistent,
    )
    print(f"Saved V40 split outputs under: {output_dir}")
    for split in SPLITS:
        print(f"{split}: {len(split_entries[split])} rows sha256={split_hashes[split]}")
    print(f"components: {len(components)} largest={max((int(component['size']) for component in components), default=0)}")
    print(f"deterministic_rerun_consistency: {'PASS' if rerun_consistent else 'FAIL'}")
    return 0 if rerun_consistent else 1


if __name__ == "__main__":
    sys.exit(main())
