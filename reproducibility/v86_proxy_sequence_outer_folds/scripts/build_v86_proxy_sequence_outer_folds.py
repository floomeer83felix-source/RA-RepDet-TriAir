#!/usr/bin/env python3
"""Build deterministic V86 proxy-sequence groups and five outer folds."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


FAMILY_RE = re.compile(r"^(n?frame)_(\d+)$")
GUARD_DISTANCE = 16
FOLD_COUNT = 5


class DisjointSet:
    def __init__(self, members: list[str]) -> None:
        self.parent = {member: member for member in members}

    def find(self, member: str) -> str:
        parent = self.parent[member]
        if parent != member:
            self.parent[member] = self.find(parent)
        return self.parent[member]

    def union(self, left: str, right: str) -> None:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root != right_root:
            self.parent[right_root] = left_root


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def family_number(sample_id: str) -> tuple[str, int]:
    match = FAMILY_RE.fullmatch(sample_id)
    if not match:
        raise ValueError(f"Unexpected TriAir sample ID: {sample_id}")
    return match.group(1), int(match.group(2))


def sample_sort_key(sample_id: str) -> tuple[int, int, str]:
    family, number = family_number(sample_id)
    return (0 if family == "frame" else 1, number, sample_id)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def count_boxes(label_path: Path) -> int:
    if not label_path.exists():
        return 0
    count = 0
    for line_number, line in enumerate(label_path.read_text(encoding="utf-8-sig").splitlines(), 1):
        stripped = line.strip()
        if not stripped:
            continue
        fields = stripped.split()
        if len(fields) != 5:
            raise ValueError(f"Malformed annotation row: {label_path}:{line_number}")
        values = [float(value) for value in fields]
        if values[0] != 0 or not all(value == value for value in values):
            raise ValueError(f"Unexpected annotation row: {label_path}:{line_number}")
        count += 1
    return count


def git_commit(repo_root: Path) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True
    ).strip()


def build_edges(
    sample_ids: list[str], hash_rows: list[dict[str, str]], graph_rows: list[dict[str, str]]
) -> tuple[dict[tuple[str, str], set[str]], dict[tuple[str, str], set[str]]]:
    sample_set = set(sample_ids)
    near_duplicate_edges: dict[tuple[str, str], set[str]] = defaultdict(set)
    adjacency_edges: dict[tuple[str, str], set[str]] = defaultdict(set)

    by_family: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for sample_id in sample_ids:
        family, number = family_number(sample_id)
        by_family[family].append((number, sample_id))
    for family_records in by_family.values():
        family_records.sort()
        for (left_number, left), (right_number, right) in zip(
            family_records, family_records[1:]
        ):
            if right_number - left_number <= GUARD_DISTANCE:
                adjacency_edges[tuple(sorted((left, right)))].add(
                    f"same_family_consecutive_id_gap_le_{GUARD_DISTANCE}"
                )

    by_pixel_hash: dict[str, list[str]] = defaultdict(list)
    for row in hash_rows:
        sample_id = row["sample_id"]
        if sample_id in sample_set:
            by_pixel_hash[row["rgb_pixel_sha256"]].append(sample_id)
    for members in by_pixel_hash.values():
        members.sort(key=sample_sort_key)
        if len(members) > 1:
            anchor = members[0]
            for member in members[1:]:
                near_duplicate_edges[tuple(sorted((anchor, member)))].add(
                    "exact_decoded_rgb_sha256"
                )

    for row in graph_rows:
        if row["source_type"] != "human_adjudicated_filename_proximity":
            continue
        left, right = row["sample_id_a"], row["sample_id_b"]
        if left not in sample_set or right not in sample_set:
            raise ValueError(f"Human adjacency edge outside dataset: {left}, {right}")
        source = "human_adjudicated_adjacent_or_near_identical"
        adjacency_edges[tuple(sorted((left, right)))].add(source)

    return near_duplicate_edges, adjacency_edges


def assign_folds(groups: list[dict[str, object]]) -> dict[str, int]:
    loads = [dict(images=0, boxes=0, zero=0, groups=0) for _ in range(FOLD_COUNT)]
    assignment: dict[str, int] = {}
    ordered = sorted(
        groups,
        key=lambda group: (
            -int(group["number_of_images"]),
            -int(group["number_of_gt_boxes"]),
            str(group["proxy_group_id"]),
        ),
    )
    for group in ordered:
        fold = min(
            range(FOLD_COUNT),
            key=lambda index: (
                loads[index]["images"] + int(group["number_of_images"]),
                loads[index]["boxes"] + int(group["number_of_gt_boxes"]),
                loads[index]["zero"] + int(group["zero_target_images"]),
                loads[index]["groups"] + 1,
                index,
            ),
        )
        assignment[str(group["proxy_group_id"])] = fold
        loads[fold]["images"] += int(group["number_of_images"])
        loads[fold]["boxes"] += int(group["number_of_gt_boxes"])
        loads[fold]["zero"] += int(group["zero_target_images"])
        loads[fold]["groups"] += 1
    return assignment


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    dataset_root = args.dataset_root.resolve()
    output_root = args.output_root.resolve()
    images_dir = dataset_root / "data" / "images"
    labels_dir = dataset_root / "data" / "labels"
    hash_path = repo_root / (
        "reproducibility/v39_filename_proximity_review_packet_v1/input_snapshot/"
        "locked_rgb_hashes__rgb_hashes__rgb_hashes.csv"
    )
    graph_path = repo_root / (
        "reproducibility/v40_expanded_adjacency_component_split_v2/extended_graph/"
        "extended_edges.csv"
    )

    image_paths = sorted(images_dir.glob("*.npy"), key=lambda path: sample_sort_key(path.stem))
    sample_ids = [path.stem for path in image_paths]
    if len(sample_ids) != len(set(sample_ids)):
        raise ValueError("Duplicate image sample IDs")
    box_counts = {sample_id: count_boxes(labels_dir / f"{sample_id}.txt") for sample_id in sample_ids}

    hash_rows = read_csv(hash_path)
    if {row["sample_id"] for row in hash_rows} != set(sample_ids):
        raise ValueError("Locked RGB hash inventory does not exactly match dataset images")
    graph_rows = read_csv(graph_path)
    near_edges, adjacency_edges = build_edges(sample_ids, hash_rows, graph_rows)

    dsu = DisjointSet(sample_ids)
    for left, right in sorted(set(near_edges) | set(adjacency_edges)):
        dsu.union(left, right)
    components: dict[str, list[str]] = defaultdict(list)
    for sample_id in sample_ids:
        components[dsu.find(sample_id)].append(sample_id)
    component_members = sorted(
        (sorted(members, key=sample_sort_key) for members in components.values()),
        key=lambda members: sample_sort_key(members[0]),
    )

    group_rows: list[dict[str, object]] = []
    sample_to_group: dict[str, str] = {}
    for index, members in enumerate(component_members, 1):
        group_id = f"V86PG{index:04d}"
        family_counts = Counter(family_number(member)[0] for member in members)
        row = {
            "proxy_group_id": group_id,
            "number_of_images": len(members),
            "number_of_gt_boxes": sum(box_counts[member] for member in members),
            "zero_target_images": sum(box_counts[member] == 0 for member in members),
            "frame_images": family_counts["frame"],
            "nframe_images": family_counts["nframe"],
            "first_sample_id": members[0],
            "last_sample_id": members[-1],
        }
        group_rows.append(row)
        for member in members:
            sample_to_group[member] = group_id

    group_to_fold = assign_folds(group_rows)
    sample_to_fold = {
        sample_id: group_to_fold[group_id] for sample_id, group_id in sample_to_group.items()
    }

    output_root.mkdir(parents=True, exist_ok=True)
    manifests_dir = output_root / "manifests"
    manifests_dir.mkdir(exist_ok=True)
    for fold in range(FOLD_COUNT):
        members = [sample_id for sample_id in sample_ids if sample_to_fold[sample_id] == fold]
        manifest = manifests_dir / f"v86_outer_fold_{fold}.txt"
        manifest.write_text(
            "".join(f"data/images/{sample_id}.npy\n" for sample_id in members),
            encoding="utf-8",
        )
        train_members = [
            sample_id for sample_id in sample_ids if sample_to_fold[sample_id] != fold
        ]
        train_manifest = manifests_dir / f"v86_outer_fold_{fold}_train_complement.txt"
        train_manifest.write_text(
            "".join(f"data/images/{sample_id}.npy\n" for sample_id in train_members),
            encoding="utf-8",
        )

    membership_rows = [
        {
            "sample_id": sample_id,
            "proxy_group_id": sample_to_group[sample_id],
            "outer_fold": sample_to_fold[sample_id],
            "family": family_number(sample_id)[0],
            "numeric_id": family_number(sample_id)[1],
            "gt_boxes": box_counts[sample_id],
            "zero_target": int(box_counts[sample_id] == 0),
        }
        for sample_id in sample_ids
    ]
    write_csv(
        output_root / "proxy_group_membership.csv",
        list(membership_rows[0]),
        membership_rows,
    )

    for row in group_rows:
        row["outer_fold"] = group_to_fold[str(row["proxy_group_id"])]
    write_csv(output_root / "proxy_group_summary.csv", list(group_rows[0]), group_rows)

    near_rows = [
        {
            "sample_id_a": left,
            "sample_id_b": right,
            "sources": ";".join(sorted(sources)),
            "proxy_group_id": sample_to_group[left],
            "outer_fold": sample_to_fold[left],
        }
        for (left, right), sources in sorted(near_edges.items())
    ]
    adjacency_rows = [
        {
            "sample_id_a": left,
            "sample_id_b": right,
            "sources": ";".join(sorted(sources)),
            "proxy_group_id": sample_to_group[left],
            "outer_fold": sample_to_fold[left],
        }
        for (left, right), sources in sorted(adjacency_edges.items())
    ]
    write_csv(output_root / "known_near_duplicate_edges.csv", list(near_rows[0]), near_rows)
    write_csv(output_root / "known_adjacency_edges.csv", list(adjacency_rows[0]), adjacency_rows)

    fold_rows: list[dict[str, object]] = []
    fold_samples: dict[int, set[str]] = {}
    fold_groups: dict[int, set[str]] = {}
    for fold in range(FOLD_COUNT):
        members = {sample_id for sample_id in sample_ids if sample_to_fold[sample_id] == fold}
        groups = {sample_to_group[sample_id] for sample_id in members}
        fold_samples[fold] = members
        fold_groups[fold] = groups
        boxes = sum(box_counts[sample_id] for sample_id in members)
        family_counts = Counter(family_number(sample_id)[0] for sample_id in members)
        fold_rows.append(
            {
                "outer_fold": fold,
                "number_of_groups": len(groups),
                "number_of_images": len(members),
                "number_of_gt_boxes": boxes,
                "zero_target_images": sum(box_counts[sample_id] == 0 for sample_id in members),
                "boxes_per_image": f"{boxes / len(members):.6f}",
                "largest_group_size": max(
                    int(row["number_of_images"])
                    for row in group_rows
                    if row["proxy_group_id"] in groups
                ),
                "frame_family_images": family_counts["frame"],
                "nframe_family_images": family_counts["nframe"],
                "manifest": f"manifests/v86_outer_fold_{fold}.txt",
            }
        )
    write_csv(output_root / "fold_summary.csv", list(fold_rows[0]), fold_rows)

    pairwise_rows: list[dict[str, object]] = []
    for left_fold in range(FOLD_COUNT):
        for right_fold in range(left_fold + 1, FOLD_COUNT):
            crossing_near = sum(
                {sample_to_fold[left], sample_to_fold[right]} == {left_fold, right_fold}
                for left, right in near_edges
            )
            crossing_adjacency = sum(
                {sample_to_fold[left], sample_to_fold[right]} == {left_fold, right_fold}
                for left, right in adjacency_edges
            )
            pairwise_rows.append(
                {
                    "fold_a": left_fold,
                    "fold_b": right_fold,
                    "shared_image_ids": len(fold_samples[left_fold] & fold_samples[right_fold]),
                    "shared_proxy_groups": len(fold_groups[left_fold] & fold_groups[right_fold]),
                    "known_near_duplicate_edges": crossing_near,
                    "known_adjacency_edges": crossing_adjacency,
                }
            )
    write_csv(output_root / "pairwise_fold_audit.csv", list(pairwise_rows[0]), pairwise_rows)

    if sum(int(row["number_of_images"]) for row in fold_rows) != len(sample_ids):
        raise AssertionError("Fold image coverage failure")
    if set().union(*fold_samples.values()) != set(sample_ids):
        raise AssertionError("Fold image identity coverage failure")
    if any(
        int(row[key]) != 0
        for row in pairwise_rows
        for key in (
            "shared_image_ids",
            "shared_proxy_groups",
            "known_near_duplicate_edges",
            "known_adjacency_edges",
        )
    ):
        raise AssertionError("Pairwise isolation audit failed")

    source_lock = {
        "git_commit": git_commit(repo_root),
        "python": sys.version,
        "platform": platform.platform(),
        "dataset_root": str(dataset_root),
        "image_count": len(sample_ids),
        "gt_box_count": sum(box_counts.values()),
        "zero_target_images": sum(count == 0 for count in box_counts.values()),
        "guard_distance": GUARD_DISTANCE,
        "proxy_group_count": len(group_rows),
        "known_near_duplicate_edge_count": len(near_edges),
        "known_adjacency_edge_count": len(adjacency_edges),
        "inputs": {
            str(hash_path.relative_to(repo_root)).replace("\\", "/"): sha256(hash_path),
            str(graph_path.relative_to(repo_root)).replace("\\", "/"): sha256(graph_path),
        },
        "builder_script": {
            str(Path(__file__).resolve().relative_to(repo_root)).replace("\\", "/"): sha256(
                Path(__file__).resolve()
            )
        },
        "manifests": {
            f"manifests/{name}": sha256(manifests_dir / name)
            for fold in range(FOLD_COUNT)
            for name in (
                f"v86_outer_fold_{fold}.txt",
                f"v86_outer_fold_{fold}_train_complement.txt",
            )
        },
        "near_duplicate_definition": "exact decoded-RGB SHA256 identity",
        "adjacency_definition": (
            "same-family consecutive numeric IDs with gap <=16, plus frozen "
            "human-adjudicated adjacent-or-near-identical edges"
        ),
        "excluded_from_known_edges": (
            "pHash/dHash threshold matches remain candidate graph edges and are not "
            "treated as confirmed near-duplicate relationships"
        ),
    }
    (output_root / "source_lock.json").write_text(
        json.dumps(source_lock, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    summary = {
        "status": "PASS",
        "source_lock": source_lock,
        "folds": fold_rows,
        "pairwise_fold_audit": pairwise_rows,
    }
    (output_root / "v86_outer_fold_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    report_lines = [
        "# V86 Proxy-Sequence Outer-Fold Report",
        "",
        "Status: **PASS**",
        "",
        "The five manifests are held-out outer folds. For outer fold `k`, its training",
        "complement is the union of the other four manifests.",
        "",
        "## Frozen proxy-group rule",
        "",
        f"- Same-family consecutive numeric IDs with gap <= {GUARD_DISTANCE} are joined transitively.",
        "- Exact decoded-RGB SHA256 identities are joined.",
        "- Frozen human-adjudicated adjacent-or-near-identical edges are joined.",
        "- pHash/dHash threshold matches remain candidates, not confirmed near-duplicate edges.",
        "- No image pixels, annotations, predictions, checkpoints, or model metrics are used.",
        "",
        "## Fold statistics",
        "",
        "| Fold | Groups | Images | GT boxes | Zero-target | Boxes/image | Largest group | frame | nframe |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in fold_rows:
        report_lines.append(
            f"| {row['outer_fold']} | {row['number_of_groups']} | {row['number_of_images']} | "
            f"{row['number_of_gt_boxes']} | {row['zero_target_images']} | {row['boxes_per_image']} | "
            f"{row['largest_group_size']} | {row['frame_family_images']} | "
            f"{row['nframe_family_images']} |"
        )
    report_lines.extend(
        [
            "",
            "## Pairwise isolation audit",
            "",
            "| Fold A | Fold B | Shared images | Shared groups | Known near-duplicate edges | Known adjacency edges |",
            "|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in pairwise_rows:
        report_lines.append(
            f"| {row['fold_a']} | {row['fold_b']} | {row['shared_image_ids']} | "
            f"{row['shared_proxy_groups']} | {row['known_near_duplicate_edges']} | "
            f"{row['known_adjacency_edges']} |"
        )
    report_lines.extend(
        [
            "",
            "## Global checks",
            "",
            f"- Images covered exactly once: {len(sample_ids):,}",
            f"- GT boxes: {sum(box_counts.values()):,}",
            f"- Zero-target images: {sum(count == 0 for count in box_counts.values()):,}",
            f"- Proxy groups: {len(group_rows)}",
            f"- Known exact-RGB near-duplicate edges: {len(near_edges)}",
            f"- Known adjacency edges: {len(adjacency_edges)}",
            "- All 10 fold pairs pass all four zero-crossing requirements.",
            "",
            "The filename numeric ID is used only as a proxy grouping key. It is not claimed",
            "to be verified sequence, flight, timestamp, or acquisition-session metadata.",
            "",
        ]
    )
    (output_root / "V86_PROXY_SEQUENCE_OUTER_FOLD_REPORT.md").write_text(
        "\n".join(report_lines), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
