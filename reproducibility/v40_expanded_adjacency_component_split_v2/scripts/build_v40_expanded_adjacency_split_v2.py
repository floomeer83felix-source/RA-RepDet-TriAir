#!/usr/bin/env python
"""Build the V40 expanded-adjacency component-disjoint split."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path


ALLOWED_LABELS = {
    "exact_duplicate",
    "adjacent_or_near_identical",
    "same_scene_distinct_observation",
    "false_candidate",
    "uncertain",
}
ADJACENCY_LABELS = {"exact_duplicate", "adjacent_or_near_identical"}


INPUTS = {
    "v39_train_manifest": "runs/component_disjoint_candidates/candidate_component_disjoint_v1_train.txt",
    "v39_validation_manifest": "runs/component_disjoint_candidates/candidate_component_disjoint_v1_val.txt",
    "v39_guard_manifest_archival": "runs/component_disjoint_candidates/candidate_component_disjoint_v1_guard_unchanged.txt",
    "original_graph_nodes": "reproducibility/v39_filename_proximity_review_packet_v1/input_snapshot/original_candidate_graph_component_nodes__component_nodes.csv",
    "original_graph_edges": "reproducibility/v39_filename_proximity_review_packet_v1/input_snapshot/original_candidate_graph_component_edges__component_edges.csv",
    "original_graph_components": "reproducibility/v39_filename_proximity_review_packet_v1/input_snapshot/original_candidate_graph_components__components.csv",
    "reviewed_41_assignment": "reproducibility/v39_filename_proximity_review_packet_v1/input_snapshot/reviewed_41_component_assignment__reviewed_41_component_assignment.csv",
    "filename_cluster_manifest": "reproducibility/v39_filename_proximity_review_packet_v1/manifests/cluster_manifest.csv",
    "filename_all_pair_manifest": "reproducibility/v39_filename_proximity_review_packet_v1/manifests/all_pair_manifest.csv",
    "filename_selected_pair_manifest": "reproducibility/v39_filename_proximity_review_packet_v1/manifests/selected_pair_manifest.csv",
    "completed_author_review_csv": "reproducibility/v39_filename_proximity_review_packet_v1/reviewer_forms/filename_proximity_author_review.csv",
    "blank_author_review_template_copy": "reproducibility/v40_expanded_adjacency_component_split_v2/source_lock/filename_proximity_author_review_blank_template_before_v40_confirmation.csv",
    "v39_audit_scope_resolution": "reproducibility/v39_audit_scope_resolution/V39_AUDIT_SCOPE_RESOLUTION.md",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_commit(root: Path) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    except Exception:
        return "UNKNOWN"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sample_id_from_relpath(rel_path: str) -> str:
    return Path(rel_path).stem


class DSU:
    def __init__(self, nodes: list[str]):
        self.parent = {node: node for node in nodes}

    def find(self, node: str) -> str:
        parent = self.parent[node]
        if parent != node:
            self.parent[node] = self.find(parent)
        return self.parent[node]

    def union(self, a: str, b: str) -> None:
        if a not in self.parent or b not in self.parent:
            return
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if ra < rb:
            self.parent[rb] = ra
        else:
            self.parent[ra] = rb


def rel_label_path(image_rel_path: str) -> str:
    return image_rel_path.replace("/images/", "/labels/").replace("\\images\\", "\\labels\\").replace(".npy", ".txt")


def gt_box_count(dataset_root: Path, image_rel_path: str) -> int:
    label_path = dataset_root / rel_label_path(image_rel_path)
    if not label_path.exists():
        return 0
    return sum(1 for line in label_path.read_text(encoding="utf-8", errors="ignore").splitlines() if line.strip())


def bool_text(value: bool) -> str:
    return "yes" if value else "no"


def int_distance(value: str) -> int:
    if value in {"", "NA", "nan", "None", None}:  # type: ignore[comparison-overlap]
        return 10**9
    return int(float(value))


def load_manifests(root: Path) -> tuple[dict[str, dict[str, object]], list[str], list[str], list[str]]:
    train_rels = [line.strip() for line in (root / INPUTS["v39_train_manifest"]).read_text().splitlines() if line.strip()]
    val_rels = [line.strip() for line in (root / INPUTS["v39_validation_manifest"]).read_text().splitlines() if line.strip()]
    guard_rels = [line.strip() for line in (root / INPUTS["v39_guard_manifest_archival"]).read_text().splitlines() if line.strip()]
    samples: dict[str, dict[str, object]] = {}
    for partition, rels in [("TRAIN", train_rels), ("VALIDATION", val_rels)]:
        for rel in rels:
            sid = sample_id_from_relpath(rel)
            if sid in samples:
                raise SystemExit(f"Duplicate sample ID in V39 universe: {sid}")
            samples[sid] = {"sample_id": sid, "relative_path": rel, "v39_partition": partition}
    return samples, train_rels, val_rels, guard_rels


def verify_author_review(root: Path) -> tuple[list[dict[str, str]], dict[str, str]]:
    rows = read_csv(root / INPUTS["completed_author_review_csv"])
    cluster_rows = read_csv(root / INPUTS["filename_cluster_manifest"])
    cluster_ids = {row["cluster_id"] for row in cluster_rows}
    ids = [row.get("cluster_id", "") for row in rows]
    issues = []
    if len(rows) != 70 or len(set(ids)) != 70 or len(cluster_ids) != 70:
        issues.append("expected exactly 70 review rows and 70 cluster-manifest IDs")
    if set(ids) != cluster_ids:
        issues.append("author review cluster IDs do not match cluster manifest IDs")
    for row in rows:
        label = row.get("author_final_label", "").strip()
        if not label:
            issues.append(f"{row.get('cluster_id')}: missing author_final_label")
        elif label not in ALLOWED_LABELS:
            issues.append(f"{row.get('cluster_id')}: invalid author_final_label={label}")
        if not row.get("reviewed_by", "").strip():
            issues.append(f"{row.get('cluster_id')}: missing reviewed_by")
        if not row.get("review_date", "").strip():
            issues.append(f"{row.get('cluster_id')}: missing review_date")
    if issues:
        raise SystemExit("V40_HUMAN_REVIEW_GATE_BLOCKED\n" + "\n".join(issues[:20]))
    return rows, {row["cluster_id"]: row["author_final_label"].strip() for row in rows}


def load_original_edges(root: Path, samples: dict[str, dict[str, object]]) -> dict[tuple[str, str], dict[str, object]]:
    edges: dict[tuple[str, str], dict[str, object]] = {}
    for row in read_csv(root / INPUTS["original_graph_edges"]):
        a, b = row["sample_id_a"], row["sample_id_b"]
        if a not in samples or b not in samples:
            continue
        exact = row.get("exact_pixel_match", "").strip().lower() == "true"
        phash_le4 = int_distance(row.get("phash_distance", "")) <= 4
        dhash_le4 = int_distance(row.get("dhash_distance", "")) <= 4
        if not (exact or phash_le4 or dhash_le4):
            continue
        key = tuple(sorted((a, b)))
        rec = edges.setdefault(
            key,
            {
                "sample_id_a": key[0],
                "sample_id_b": key[1],
                "original_exact_match": False,
                "original_phash_le4": False,
                "original_dhash_le4": False,
                "source_rows": 0,
            },
        )
        rec["original_exact_match"] = bool(rec["original_exact_match"] or exact)
        rec["original_phash_le4"] = bool(rec["original_phash_le4"] or phash_le4)
        rec["original_dhash_le4"] = bool(rec["original_dhash_le4"] or dhash_le4)
        rec["source_rows"] = int(rec["source_rows"]) + 1
    return edges


def source_type_for_original(edge: dict[str, object]) -> str:
    if edge["original_exact_match"]:
        return "original_exact"
    if edge["original_phash_le4"]:
        return "original_phash"
    return "original_dhash"


def load_human_edges(root: Path, samples: dict[str, dict[str, object]], label_by_cluster: dict[str, str]) -> dict[tuple[str, str, str], dict[str, object]]:
    edges: dict[tuple[str, str, str], dict[str, object]] = {}
    for row in read_csv(root / INPUTS["filename_all_pair_manifest"]):
        cluster_id = row["cluster_id"]
        label = label_by_cluster.get(cluster_id, "")
        if label not in ADJACENCY_LABELS:
            continue
        val_id = row["validation_sample_id"]
        train_id = row["nearest_train_sample_id"]
        if val_id not in samples or train_id not in samples:
            raise SystemExit(f"Human-adjudicated pair endpoint missing from V40 universe: {row.get('pair_id')}")
        a, b = sorted((val_id, train_id))
        key = (a, b, row["pair_id"])
        edges[key] = {
            "sample_id_a": a,
            "sample_id_b": b,
            "pair_id": row["pair_id"],
            "cluster_id": cluster_id,
            "human_final_label": label,
            "family": row.get("family", ""),
            "id_distance": row.get("id_distance", ""),
        }
    return edges


def assign_original_component_ids_from_edges(
    samples: dict[str, dict[str, object]],
    original_edges: dict[tuple[str, str], dict[str, object]],
) -> None:
    dsu = DSU(sorted(samples))
    for a, b in original_edges:
        dsu.union(a, b)
    groups: dict[str, list[str]] = defaultdict(list)
    for sid in sorted(samples):
        groups[dsu.find(sid)].append(sid)
    for index, members in enumerate(sorted(groups.values(), key=lambda item: (item[0], len(item))), start=1):
        if len(members) == 1:
            cid = f"orig_singleton_{members[0]}"
        else:
            cid = f"orig_rule_{index:05d}"
        for sid in members:
            samples[sid]["original_component_id"] = cid


def build_components(samples: dict[str, dict[str, object]], original_edges: dict[tuple[str, str], dict[str, object]], human_edges: dict[tuple[str, str, str], dict[str, object]]) -> tuple[dict[str, str], dict[str, list[str]]]:
    dsu = DSU(sorted(samples))
    for a, b in original_edges:
        dsu.union(a, b)
    for _, edge in human_edges.items():
        dsu.union(str(edge["sample_id_a"]), str(edge["sample_id_b"]))
    groups: dict[str, list[str]] = defaultdict(list)
    for sid in sorted(samples):
        groups[dsu.find(sid)].append(sid)
    sorted_groups = sorted(groups.values(), key=lambda members: (members[0], len(members)))
    component_by_sample: dict[str, str] = {}
    members_by_component: dict[str, list[str]] = {}
    for index, members in enumerate(sorted_groups, start=1):
        cid = f"v40c_{index:05d}"
        members_by_component[cid] = members
        for sid in members:
            component_by_sample[sid] = cid
    return component_by_sample, members_by_component


def component_stats(
    component_id: str,
    members: list[str],
    samples: dict[str, dict[str, object]],
    original_edges_by_component: dict[str, list[dict[str, object]]],
    human_edges_by_component: dict[str, list[dict[str, object]]],
) -> dict[str, object]:
    train_members = [sid for sid in members if samples[sid]["v39_partition"] == "TRAIN"]
    val_members = [sid for sid in members if samples[sid]["v39_partition"] == "VALIDATION"]
    original_list = original_edges_by_component.get(component_id, [])
    human_list = human_edges_by_component.get(component_id, [])
    return {
        "component_id": component_id,
        "size": len(members),
        "v39_train_count": len(train_members),
        "v39_validation_count": len(val_members),
        "gt_box_count": sum(int(samples[sid]["gt_box_count"]) for sid in members),
        "member_sample_ids": "|".join(members),
        "v39_train_sample_ids": "|".join(train_members),
        "v39_validation_sample_ids": "|".join(val_members),
        "original_edge_count": len(original_list),
        "original_exact_edge_count": sum(1 for edge in original_list if edge["original_exact_match"] == "yes"),
        "original_phash_edge_count": sum(1 for edge in original_list if edge["original_phash_le4"] == "yes"),
        "original_dhash_edge_count": sum(1 for edge in original_list if edge["original_dhash_le4"] == "yes"),
        "human_adjudicated_edge_count": len(human_list),
        "contains_human_adjudicated_adjacency_edge": bool_text(bool(human_list)),
        "human_cluster_ids": "|".join(sorted({str(edge.get("source_cluster_id", "")) for edge in human_list if edge.get("source_cluster_id")})),
    }


def write_source_lock(root: Path, out_root: Path, script_paths: list[Path]) -> list[dict[str, object]]:
    rows = []
    for role, rel in INPUTS.items():
        path = root / rel
        rows.append(
            {
                "role": role,
                "path": rel,
                "exists": bool_text(path.exists()),
                "bytes": path.stat().st_size if path.exists() else "",
                "sha256": sha256_file(path) if path.exists() else "",
            }
        )
    for script_path in script_paths:
        rel = script_path.relative_to(root).as_posix()
        rows.append(
            {
                "role": script_path.stem,
                "path": rel,
                "exists": "yes",
                "bytes": script_path.stat().st_size,
                "sha256": sha256_file(script_path),
            }
        )
    write_csv(out_root / "source_lock/input_lock_manifest.csv", rows, ["role", "path", "exists", "bytes", "sha256"])
    lines = [
        "# V40 Source Lock",
        "",
        f"- Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"- Git commit: `{git_commit(root)}`",
        f"- Environment: Python {sys.version.split()[0]} on {platform.platform()}",
        "- Stage status: `passed`",
        "",
        "| Role | Path | Exists | Bytes | SHA-256 |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for row in rows:
        lines.append(f"| {row['role']} | `{row['path']}` | {row['exists']} | {row['bytes']} | `{row['sha256']}` |")
    (out_root / "source_lock/input_lock.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return rows


def write_human_summary(root: Path, out_root: Path, author_rows: list[dict[str, str]]) -> dict[str, object]:
    counts = {label: 0 for label in sorted(ALLOWED_LABELS)}
    adjacency_clusters = []
    non_adjacency_clusters: dict[str, list[str]] = {label: [] for label in sorted(ALLOWED_LABELS - ADJACENCY_LABELS)}
    for row in author_rows:
        label = row["author_final_label"].strip()
        counts[label] += 1
        if label in ADJACENCY_LABELS:
            adjacency_clusters.append(row["cluster_id"])
        else:
            non_adjacency_clusters[label].append(row["cluster_id"])

    summary_rows = []
    for row in author_rows:
        summary_rows.append(
            {
                "cluster_id": row["cluster_id"],
                "preliminary_label": row.get("preliminary_label", ""),
                "author_final_label": row.get("author_final_label", ""),
                "reviewed_by": row.get("reviewed_by", ""),
                "review_date": row.get("review_date", ""),
                "creates_v40_adjacency_edges": bool_text(row.get("author_final_label", "") in ADJACENCY_LABELS),
                "representative_pair_ids": row.get("representative_pair_ids", ""),
                "pair_count": row.get("pair_count", ""),
                "minimum_id_distance": row.get("minimum_id_distance", ""),
                "author_notes": row.get("author_notes", ""),
            }
        )
    write_csv(
        out_root / "human_review_summary/final_filename_proximity_human_review.csv",
        summary_rows,
        [
            "cluster_id",
            "preliminary_label",
            "author_final_label",
            "reviewed_by",
            "review_date",
            "creates_v40_adjacency_edges",
            "representative_pair_ids",
            "pair_count",
            "minimum_id_distance",
            "author_notes",
        ],
    )
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "git_commit": git_commit(root),
        "status": "PASS",
        "total_clusters": len(author_rows),
        "final_label_counts": counts,
        "adjacency_edge_cluster_count": len(adjacency_clusters),
        "adjacency_edge_cluster_ids": sorted(adjacency_clusters),
        "non_adjacency_cluster_ids_by_label": non_adjacency_clusters,
        "required_phrase": "human-adjudicated adjacent-or-near-identical component",
    }
    write_json(out_root / "human_review_summary/final_filename_proximity_human_review_summary.json", payload)
    lines = [
        "# V40 Final Filename-Proximity Human Review Summary",
        "",
        f"- Generated: {payload['generated_at']}",
        f"- Git commit: `{payload['git_commit']}`",
        "- Status: `PASS`",
        "- Required wording: human-adjudicated adjacent-or-near-identical component",
        "",
        "## Final Label Counts",
        "",
    ]
    for label in sorted(counts):
        lines.append(f"- `{label}`: {counts[label]}")
    lines.extend(
        [
            "",
            "## Clusters Creating V40 Adjacency Edges",
            "",
            "| Cluster ID | Final label |",
            "| --- | --- |",
        ]
    )
    for cluster_id in sorted(adjacency_clusters):
        lines.append(f"| `{cluster_id}` | `adjacent_or_near_identical` |")
    (out_root / "human_review_summary/final_filename_proximity_human_review_summary.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    return payload


def optimize_assignment(
    component_rows: list[dict[str, object]],
    frozen_val_count: int,
    frozen_val_gt: int,
) -> tuple[dict[str, str], dict[str, object]]:
    components = sorted(component_rows, key=lambda row: str(row["component_id"]))
    pure_train = [row for row in components if int(row["v39_train_count"]) and not int(row["v39_validation_count"])]
    pure_val = [row for row in components if int(row["v39_validation_count"]) and not int(row["v39_train_count"])]
    mixed = [row for row in components if int(row["v39_train_count"]) and int(row["v39_validation_count"])]

    pure_val_base_count = sum(int(row["size"]) for row in pure_val)
    pure_val_base_gt = sum(int(row["gt_box_count"]) for row in pure_val)
    mixed_target = frozen_val_count - pure_val_base_count

    mixed_states: dict[int, tuple[int, dict[int, str]]] = {0: (0, {0: ""})}
    for row in mixed:
        size = int(row["size"])
        train_count = int(row["v39_train_count"])
        val_count = int(row["v39_validation_count"])
        gt_count = int(row["gt_box_count"])
        new_states: dict[int, tuple[int, dict[int, str]]] = {}
        for count, (moved, gt_bits) in mixed_states.items():
            candidates = [
                (count, moved + val_count, 0, "0"),
                (count + size, moved + train_count, gt_count, "1"),
            ]
            for new_count, new_moved, add_gt, bit in candidates:
                if new_count not in new_states or new_moved < new_states[new_count][0]:
                    new_states[new_count] = (new_moved, {})
                if new_moved == new_states[new_count][0]:
                    bucket = new_states[new_count][1]
                    for gt, bits in gt_bits.items():
                        new_gt = gt + add_gt
                        new_bits = bits + bit
                        if new_gt not in bucket or new_bits < bucket[new_gt]:
                            bucket[new_gt] = new_bits
        mixed_states = new_states

    def pure_options(rows: list[dict[str, object]], need: int, selected_bit: str) -> list[tuple[int, int, str, set[str]]]:
        if need == 0:
            return [(0, 0, "", set())]
        states: dict[int, tuple[int, dict[int, tuple[str, set[str]]]]] = {0: (0, {0: ("", set())})}
        for row in rows:
            cid = str(row["component_id"])
            size = int(row["size"])
            gt_count = int(row["gt_box_count"])
            new_states: dict[int, tuple[int, dict[int, tuple[str, set[str]]]]] = {}
            for count, (moved, gt_payloads) in states.items():
                for take in [False, True]:
                    new_count = count + (size if take else 0)
                    if new_count > need:
                        continue
                    new_moved = moved + (size if take else 0)
                    bit = selected_bit if take else ("0" if selected_bit == "1" else "1")
                    if new_count not in new_states or new_moved < new_states[new_count][0]:
                        new_states[new_count] = (new_moved, {})
                    if new_moved == new_states[new_count][0]:
                        bucket = new_states[new_count][1]
                        for gt, (bits, selected) in gt_payloads.items():
                            new_gt = gt + (gt_count if take else 0)
                            new_bits = bits + bit
                            new_selected = set(selected)
                            if take:
                                new_selected.add(cid)
                            if new_gt not in bucket or new_bits < bucket[new_gt][0]:
                                bucket[new_gt] = (new_bits, new_selected)
            states = new_states
        if need not in states:
            return []
        moved, payloads = states[need]
        return [(moved, gt, bits, selected) for gt, (bits, selected) in payloads.items()]

    lower_best = None
    candidate_counts = []
    for mixed_count, (mixed_moved, _) in mixed_states.items():
        diff = mixed_target - mixed_count
        lower = mixed_moved + abs(diff)
        if lower_best is None or lower < lower_best:
            lower_best = lower
            candidate_counts = [mixed_count]
        elif lower == lower_best:
            candidate_counts.append(mixed_count)

    best_tuple: tuple[int, int, int, str] | None = None
    best_assignment: dict[str, str] | None = None
    best_detail: dict[str, object] | None = None

    mixed_by_id = [str(row["component_id"]) for row in mixed]
    pure_train_ids = [str(row["component_id"]) for row in pure_train]
    pure_val_ids = [str(row["component_id"]) for row in pure_val]

    for mixed_count in sorted(candidate_counts):
        mixed_moved, mixed_gt_bits = mixed_states[mixed_count]
        diff = mixed_target - mixed_count
        if diff > 0:
            correction_options = pure_options(pure_train, diff, "1")
            correction_gt_sign = 1
            correction_side = "pure_train_to_validation"
        elif diff < 0:
            correction_options = pure_options(pure_val, -diff, "0")
            correction_gt_sign = -1
            correction_side = "pure_validation_to_train"
        else:
            correction_options = [(0, 0, "", set())]
            correction_gt_sign = 0
            correction_side = "none"
        for correction_moved, correction_gt, _correction_bits, selected_corrections in correction_options:
            total_moved = mixed_moved + correction_moved
            for mixed_gt, mixed_bits in mixed_gt_bits.items():
                assignment = {}
                for row in pure_train:
                    cid = str(row["component_id"])
                    assignment[cid] = "VALIDATION" if cid in selected_corrections else "TRAIN"
                for row in pure_val:
                    cid = str(row["component_id"])
                    assignment[cid] = "TRAIN" if cid in selected_corrections else "VALIDATION"
                for cid, bit in zip(mixed_by_id, mixed_bits):
                    assignment[cid] = "VALIDATION" if bit == "1" else "TRAIN"
                bitstring = "".join("1" if assignment[str(row["component_id"])] == "VALIDATION" else "0" for row in components)
                signed_correction_gt = correction_gt * correction_gt_sign
                final_val_gt = pure_val_base_gt + mixed_gt + signed_correction_gt
                objective = (0, total_moved, abs(final_val_gt - frozen_val_gt), bitstring)
                if best_tuple is None or objective < best_tuple:
                    best_tuple = objective
                    best_assignment = assignment
                    best_detail = {
                        "pure_val_base_count": pure_val_base_count,
                        "pure_val_base_gt_box_count": pure_val_base_gt,
                        "mixed_target_validation_count": mixed_target,
                        "mixed_component_count": len(mixed),
                        "pure_train_component_count": len(pure_train),
                        "pure_validation_component_count": len(pure_val),
                        "selected_mixed_validation_count": mixed_count,
                        "selected_mixed_gt_box_count": mixed_gt,
                        "selected_mixed_moved_samples": mixed_moved,
                        "pure_correction_side": correction_side,
                        "pure_correction_component_ids": sorted(selected_corrections),
                        "pure_correction_moved_samples": correction_moved,
                        "pure_correction_gt_box_count": correction_gt,
                        "pure_correction_gt_box_signed_delta": signed_correction_gt,
                        "validation_count_abs_diff": 0,
                        "moved_samples": total_moved,
                        "validation_gt_box_abs_diff": abs(final_val_gt - frozen_val_gt),
                        "assignment_bitstring": bitstring,
                    }

    if best_assignment is None or best_detail is None:
        raise SystemExit("No deterministic V40 assignment found.")
    return best_assignment, best_detail


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build V40 expanded-adjacency graph, split assignment, and manifests.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--dataset-root", default="D:/download/triair", help="TriAir dataset root used only for GT box counts.")
    parser.add_argument(
        "--out-root",
        default="reproducibility/v40_expanded_adjacency_component_split_v2",
        help="V40 output root.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    out_root = (root / args.out_root).resolve()
    dataset_root = Path(args.dataset_root)
    out_root.mkdir(parents=True, exist_ok=True)

    samples, train_rels, val_rels, guard_rels = load_manifests(root)
    if len(train_rels) != 7439 or len(val_rels) != 2213 or len(samples) != 9652:
        raise SystemExit("Unexpected V39 universe size for V40.")
    author_rows, label_by_cluster = verify_author_review(root)
    for sid, sample in samples.items():
        sample["gt_box_count"] = gt_box_count(dataset_root, str(sample["relative_path"]))

    original_edges = load_original_edges(root, samples)
    assign_original_component_ids_from_edges(samples, original_edges)
    human_edges = load_human_edges(root, samples, label_by_cluster)
    component_by_sample, members_by_component = build_components(samples, original_edges, human_edges)
    for sid, cid in component_by_sample.items():
        samples[sid]["v40_component_id"] = cid

    extended_edge_rows = []
    original_edges_by_component: dict[str, list[dict[str, object]]] = defaultdict(list)
    human_edges_by_component: dict[str, list[dict[str, object]]] = defaultdict(list)
    edge_index = 1
    for key, edge in sorted(original_edges.items()):
        a, b = key
        cid = component_by_sample[a]
        row = {
            "edge_id": f"orig_{edge_index:06d}",
            "source_type": source_type_for_original(edge),
            "source_cluster_id": "",
            "source_pair_id": "",
            "human_final_label": "",
            "sample_id_a": a,
            "sample_id_b": b,
            "partition_a": samples[a]["v39_partition"],
            "partition_b": samples[b]["v39_partition"],
            "cross_partition_in_v39": bool_text(samples[a]["v39_partition"] != samples[b]["v39_partition"]),
            "v40_component_id": cid,
            "original_exact_match": bool_text(bool(edge["original_exact_match"])),
            "original_phash_le4": bool_text(bool(edge["original_phash_le4"])),
            "original_dhash_le4": bool_text(bool(edge["original_dhash_le4"])),
            "human_id_distance": "",
        }
        extended_edge_rows.append(row)
        original_edges_by_component[cid].append(row)
        edge_index += 1
    human_index = 1
    for key, edge in sorted(human_edges.items()):
        a = str(edge["sample_id_a"])
        b = str(edge["sample_id_b"])
        cid = component_by_sample[a]
        row = {
            "edge_id": f"hafp_{human_index:06d}",
            "source_type": "human_adjudicated_filename_proximity",
            "source_cluster_id": edge["cluster_id"],
            "source_pair_id": edge["pair_id"],
            "human_final_label": edge["human_final_label"],
            "sample_id_a": a,
            "sample_id_b": b,
            "partition_a": samples[a]["v39_partition"],
            "partition_b": samples[b]["v39_partition"],
            "cross_partition_in_v39": bool_text(samples[a]["v39_partition"] != samples[b]["v39_partition"]),
            "v40_component_id": cid,
            "original_exact_match": "no",
            "original_phash_le4": "no",
            "original_dhash_le4": "no",
            "human_id_distance": edge["id_distance"],
        }
        extended_edge_rows.append(row)
        human_edges_by_component[cid].append(row)
        human_index += 1

    node_rows = []
    for sid in sorted(samples):
        sample = samples[sid]
        node_rows.append(
            {
                "sample_id": sid,
                "relative_path": sample["relative_path"],
                "v39_partition": sample["v39_partition"],
                "gt_box_count": sample["gt_box_count"],
                "original_component_id": sample["original_component_id"],
                "v40_component_id": sample["v40_component_id"],
            }
        )

    component_rows = []
    membership_rows = []
    for cid, members in sorted(members_by_component.items()):
        stats = component_stats(cid, members, samples, original_edges_by_component, human_edges_by_component)
        component_rows.append(stats)
        for order, sid in enumerate(members, start=1):
            membership_rows.append(
                {
                    "component_id": cid,
                    "member_order": order,
                    "sample_id": sid,
                    "relative_path": samples[sid]["relative_path"],
                    "v39_partition": samples[sid]["v39_partition"],
                    "gt_box_count": samples[sid]["gt_box_count"],
                    "original_component_id": samples[sid]["original_component_id"],
                }
            )

    frozen_val_gt = sum(int(samples[sample_id_from_relpath(rel)]["gt_box_count"]) for rel in val_rels)
    component_assignment, objective = optimize_assignment(component_rows, 2213, frozen_val_gt)

    assignment_rows = []
    moved_rows = []
    new_train_rels = []
    new_val_rels = []
    for sid in sorted(samples):
        sample = samples[sid]
        cid = str(sample["v40_component_id"])
        v40_partition = component_assignment[cid]
        moved = str(sample["v39_partition"]) != v40_partition
        row = {
            "sample_id": sid,
            "relative_path": sample["relative_path"],
            "v39_partition": sample["v39_partition"],
            "v40_partition": v40_partition,
            "moved_relative_to_v39": bool_text(moved),
            "gt_box_count": sample["gt_box_count"],
            "v40_component_id": cid,
            "original_component_id": sample["original_component_id"],
        }
        assignment_rows.append(row)
        if moved:
            moved_rows.append(row)
        if v40_partition == "TRAIN":
            new_train_rels.append(str(sample["relative_path"]))
        else:
            new_val_rels.append(str(sample["relative_path"]))

    component_assignment_rows = []
    for row in component_rows:
        cid = str(row["component_id"])
        assignment = component_assignment[cid]
        component_assignment_rows.append(
            {
                **row,
                "v40_assignment": assignment,
                "moved_train_to_validation": sum(
                    1
                    for sid in str(row["member_sample_ids"]).split("|")
                    if samples[sid]["v39_partition"] == "TRAIN" and assignment == "VALIDATION"
                ),
                "moved_validation_to_train": sum(
                    1
                    for sid in str(row["member_sample_ids"]).split("|")
                    if samples[sid]["v39_partition"] == "VALIDATION" and assignment == "TRAIN"
                ),
            }
        )

    write_csv(
        out_root / "extended_graph/extended_nodes.csv",
        node_rows,
        ["sample_id", "relative_path", "v39_partition", "gt_box_count", "original_component_id", "v40_component_id"],
    )
    edge_fields = [
        "edge_id",
        "source_type",
        "source_cluster_id",
        "source_pair_id",
        "human_final_label",
        "sample_id_a",
        "sample_id_b",
        "partition_a",
        "partition_b",
        "cross_partition_in_v39",
        "v40_component_id",
        "original_exact_match",
        "original_phash_le4",
        "original_dhash_le4",
        "human_id_distance",
    ]
    write_csv(out_root / "extended_graph/extended_edges.csv", extended_edge_rows, edge_fields)
    component_fields = [
        "component_id",
        "size",
        "v39_train_count",
        "v39_validation_count",
        "gt_box_count",
        "member_sample_ids",
        "v39_train_sample_ids",
        "v39_validation_sample_ids",
        "original_edge_count",
        "original_exact_edge_count",
        "original_phash_edge_count",
        "original_dhash_edge_count",
        "human_adjudicated_edge_count",
        "contains_human_adjudicated_adjacency_edge",
        "human_cluster_ids",
    ]
    write_csv(out_root / "extended_graph/extended_components.csv", component_rows, component_fields)
    write_csv(
        out_root / "extended_graph/component_membership.csv",
        membership_rows,
        ["component_id", "member_order", "sample_id", "relative_path", "v39_partition", "gt_box_count", "original_component_id"],
    )
    provenance_rows = [
        {"metric": "universe_samples", "value": len(samples)},
        {"metric": "original_unique_edges", "value": len(original_edges)},
        {"metric": "human_adjudicated_edges", "value": len(human_edges)},
        {"metric": "extended_edge_rows", "value": len(extended_edge_rows)},
        {"metric": "extended_components", "value": len(component_rows)},
        {"metric": "components_with_human_adjudicated_edges", "value": sum(1 for row in component_rows if row["contains_human_adjudicated_adjacency_edge"] == "yes")},
        {"metric": "required_phrase", "value": "human-adjudicated adjacent-or-near-identical component"},
    ]
    write_csv(out_root / "extended_graph/component_provenance_summary.csv", provenance_rows, ["metric", "value"])

    assignment_fields = [
        "sample_id",
        "relative_path",
        "v39_partition",
        "v40_partition",
        "moved_relative_to_v39",
        "gt_box_count",
        "v40_component_id",
        "original_component_id",
    ]
    write_csv(out_root / "split_build/v40_assignment.csv", assignment_rows, assignment_fields)
    write_csv(out_root / "split_build/v40_moved_samples.csv", moved_rows, assignment_fields)
    write_csv(
        out_root / "split_build/v40_component_assignment.csv",
        component_assignment_rows,
        component_fields + ["v40_assignment", "moved_train_to_validation", "moved_validation_to_train"],
    )

    (out_root / "manifests").mkdir(parents=True, exist_ok=True)
    (out_root / "manifests/v40_expanded_adjacency_component_disjoint_train.txt").write_text(
        "\n".join(new_train_rels) + "\n", encoding="utf-8"
    )
    (out_root / "manifests/v40_expanded_adjacency_component_disjoint_val.txt").write_text(
        "\n".join(new_val_rels) + "\n", encoding="utf-8"
    )
    (out_root / "manifests/v40_guard_unchanged_archival.txt").write_text(
        "\n".join(guard_rels) + "\n", encoding="utf-8"
    )

    objective_payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "git_commit": git_commit(root),
        "status": "PASS",
        "algorithm": "deterministic dynamic programming over extended components",
        "objective_order": [
            "minimize absolute validation-count difference from 2213",
            "minimize moved samples relative to frozen V39 assignment",
            "minimize absolute validation GT-box-count difference from frozen V39 validation GT boxes",
            "select lexicographically smallest component-assignment bitstring with TRAIN=0 and VALIDATION=1",
        ],
        "train_count": len(new_train_rels),
        "validation_count": len(new_val_rels),
        "validation_gt_box_count": sum(int(row["gt_box_count"]) for row in assignment_rows if row["v40_partition"] == "VALIDATION"),
        "frozen_v39_validation_gt_box_count": frozen_val_gt,
        "moved_samples": len(moved_rows),
        **objective,
    }
    write_json(out_root / "split_build/v40_assignment_rationale.json", objective_payload)
    rationale = [
        "# V40 Assignment Rationale",
        "",
        f"- Generated: {objective_payload['generated_at']}",
        f"- Git commit: `{objective_payload['git_commit']}`",
        "- Status: `PASS`",
        "- Algorithm: deterministic dynamic programming over extended components.",
        "",
        "## Objective Result",
        "",
        f"- Validation count: {objective_payload['validation_count']}",
        f"- Train count: {objective_payload['train_count']}",
        f"- Validation GT boxes: {objective_payload['validation_gt_box_count']}",
        f"- Frozen V39 validation GT boxes: {frozen_val_gt}",
        f"- Moved samples relative to V39: {len(moved_rows)}",
        f"- Validation-count absolute difference: {objective_payload['validation_count_abs_diff']}",
        f"- Validation-GT absolute difference: {objective_payload['validation_gt_box_abs_diff']}",
        "",
        "No model output, AP, F1, loss, prediction, confidence, checkpoint, qualitative result, or external data was used.",
    ]
    (out_root / "split_build/v40_assignment_rationale.md").write_text("\n".join(rationale) + "\n", encoding="utf-8")

    graph_payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "git_commit": git_commit(root),
        "status": "PASS",
        "universe_samples": len(samples),
        "v39_train_count": len(train_rels),
        "v39_validation_count": len(val_rels),
        "v39_guard_count_archival": len(guard_rels),
        "original_unique_edges": len(original_edges),
        "human_adjudicated_edges": len(human_edges),
        "extended_edge_rows": len(extended_edge_rows),
        "extended_components": len(component_rows),
        "components_with_human_adjudicated_edges": sum(1 for row in component_rows if row["contains_human_adjudicated_adjacency_edge"] == "yes"),
        "required_phrase": "human-adjudicated adjacent-or-near-identical component",
    }
    write_json(out_root / "extended_graph/extended_graph_build_report.json", graph_payload)
    graph_lines = [
        "# V40 Extended Graph Build Report",
        "",
        f"- Generated: {graph_payload['generated_at']}",
        f"- Git commit: `{graph_payload['git_commit']}`",
        "- Status: `PASS`",
        "- Required wording: human-adjudicated adjacent-or-near-identical component",
        "",
        "## Counts",
        "",
        f"- Universe samples: {graph_payload['universe_samples']}",
        f"- Original unique edges: {graph_payload['original_unique_edges']}",
        f"- Human-adjudicated edges: {graph_payload['human_adjudicated_edges']}",
        f"- Extended components: {graph_payload['extended_components']}",
        f"- Components with human-adjudicated edges: {graph_payload['components_with_human_adjudicated_edges']}",
        "",
        "The V39 guard manifest was copied only as unchanged archival reference and is excluded from the V40 train/validation universe.",
    ]
    (out_root / "extended_graph/extended_graph_build_report.md").write_text("\n".join(graph_lines) + "\n", encoding="utf-8")

    script_dir = out_root / "scripts"
    script_paths = [
        script_dir / "record_v40_human_review_confirmation.py",
        script_dir / "build_v40_expanded_adjacency_split_v2.py",
        script_dir / "audit_v40_expanded_adjacency_split_v2.py",
    ]
    write_source_lock(root, out_root, [path for path in script_paths if path.exists()])
    write_human_summary(root, out_root, author_rows)

    print(json.dumps({**graph_payload, "train_count": len(new_train_rels), "validation_count": len(new_val_rels), "moved_samples": len(moved_rows)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
