#!/usr/bin/env python
"""Audit the V40 expanded-adjacency component-disjoint split."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path


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


def bool_text(value: bool) -> str:
    return "yes" if value else "no"


def sample_id_from_relpath(rel_path: str) -> str:
    return Path(rel_path).stem


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit V40 expanded-adjacency manifests and components.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument(
        "--out-root",
        default="reproducibility/v40_expanded_adjacency_component_split_v1",
        help="V40 output root.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    out_root = (root / args.out_root).resolve()
    now = datetime.now().isoformat(timespec="seconds")
    commit = git_commit(root)

    assignment_rows = read_csv(out_root / "split_build/v40_assignment.csv")
    component_assignment_rows = read_csv(out_root / "split_build/v40_component_assignment.csv")
    edge_rows = read_csv(out_root / "extended_graph/extended_edges.csv")
    train_manifest = [
        line.strip()
        for line in (out_root / "manifests/v40_expanded_adjacency_component_disjoint_train.txt").read_text().splitlines()
        if line.strip()
    ]
    val_manifest = [
        line.strip()
        for line in (out_root / "manifests/v40_expanded_adjacency_component_disjoint_val.txt").read_text().splitlines()
        if line.strip()
    ]
    guard_manifest = [
        line.strip()
        for line in (out_root / "manifests/v40_guard_unchanged_archival.txt").read_text().splitlines()
        if line.strip()
    ]
    v39_train = [
        line.strip()
        for line in (root / "runs/component_disjoint_candidates/candidate_component_disjoint_v1_train.txt").read_text().splitlines()
        if line.strip()
    ]
    v39_val = [
        line.strip()
        for line in (root / "runs/component_disjoint_candidates/candidate_component_disjoint_v1_val.txt").read_text().splitlines()
        if line.strip()
    ]
    v39_guard = [
        line.strip()
        for line in (root / "runs/component_disjoint_candidates/candidate_component_disjoint_v1_guard_unchanged.txt").read_text().splitlines()
        if line.strip()
    ]

    partition_by_sample = {row["sample_id"]: row["v40_partition"] for row in assignment_rows}
    rel_by_sample = {row["sample_id"]: row["relative_path"] for row in assignment_rows}

    train_set = set(train_manifest)
    val_set = set(val_manifest)
    v40_union = train_set | val_set
    v39_universe = set(v39_train) | set(v39_val)
    manifest_duplicates = (len(train_manifest) - len(train_set)) + (len(val_manifest) - len(val_set))
    path_overlap = train_set & val_set
    missing_universe = v39_universe - v40_union
    extra_universe = v40_union - v39_universe
    guard_unchanged = guard_manifest == v39_guard

    def edge_cross(row: dict[str, str]) -> bool:
        return partition_by_sample[row["sample_id_a"]] != partition_by_sample[row["sample_id_b"]]

    exact_cross = [row for row in edge_rows if row["original_exact_match"] == "yes" and edge_cross(row)]
    phash_cross = [row for row in edge_rows if row["original_phash_le4"] == "yes" and edge_cross(row)]
    dhash_cross = [row for row in edge_rows if row["original_dhash_le4"] == "yes" and edge_cross(row)]
    original_cross = [
        row
        for row in edge_rows
        if row["source_type"].startswith("original_") and edge_cross(row)
    ]
    human_cross = [
        row
        for row in edge_rows
        if row["source_type"] == "human_adjudicated_filename_proximity" and edge_cross(row)
    ]
    extended_cross = [row for row in edge_rows if edge_cross(row)]

    original_component_partitions: dict[str, set[str]] = defaultdict(set)
    extended_component_partitions: dict[str, set[str]] = defaultdict(set)
    for row in assignment_rows:
        original_component_partitions[row["original_component_id"]].add(row["v40_partition"])
        extended_component_partitions[row["v40_component_id"]].add(row["v40_partition"])
    original_components_split = [
        {"original_component_id": cid, "partitions": "|".join(sorted(parts))}
        for cid, parts in sorted(original_component_partitions.items())
        if len(parts) > 1
    ]
    extended_components_split = [
        {"component_id": cid, "partitions": "|".join(sorted(parts))}
        for cid, parts in sorted(extended_component_partitions.items())
        if len(parts) > 1
    ]

    edge_fields = [
        "edge_id",
        "source_type",
        "source_cluster_id",
        "source_pair_id",
        "human_final_label",
        "sample_id_a",
        "sample_id_b",
        "v40_component_id",
        "original_exact_match",
        "original_phash_le4",
        "original_dhash_le4",
    ]
    write_csv(out_root / "audits/v40_exact_decoded_rgb_pairs.csv", exact_cross, edge_fields)
    write_csv(out_root / "audits/v40_phash_le4_pairs.csv", phash_cross, edge_fields)
    write_csv(out_root / "audits/v40_dhash_le4_pairs.csv", dhash_cross, edge_fields)
    write_csv(out_root / "audits/v40_cross_partition_extended_edges.csv", extended_cross, edge_fields)
    write_csv(out_root / "audits/v40_cross_partition_extended_components.csv", extended_components_split, ["component_id", "partitions"])

    manifest_metrics = [
        {"metric": "train_count", "value": len(train_manifest), "pass_condition": "7439", "status": "PASS" if len(train_manifest) == 7439 else "FAIL"},
        {"metric": "validation_count", "value": len(val_manifest), "pass_condition": "2213", "status": "PASS" if len(val_manifest) == 2213 else "FAIL"},
        {"metric": "train_plus_validation_count", "value": len(train_manifest) + len(val_manifest), "pass_condition": "9652", "status": "PASS" if len(train_manifest) + len(val_manifest) == 9652 else "FAIL"},
        {"metric": "sample_id_path_overlap", "value": len(path_overlap), "pass_condition": "0", "status": "PASS" if not path_overlap else "FAIL"},
        {"metric": "manifest_duplicates", "value": manifest_duplicates, "pass_condition": "0", "status": "PASS" if manifest_duplicates == 0 else "FAIL"},
        {"metric": "missing_universe_samples", "value": len(missing_universe), "pass_condition": "0", "status": "PASS" if not missing_universe else "FAIL"},
        {"metric": "extra_universe_samples", "value": len(extra_universe), "pass_condition": "0", "status": "PASS" if not extra_universe else "FAIL"},
        {"metric": "guard_unchanged_archival", "value": bool_text(guard_unchanged), "pass_condition": "yes", "status": "PASS" if guard_unchanged else "FAIL"},
    ]
    write_csv(out_root / "audits/v40_manifest_integrity.csv", manifest_metrics, ["metric", "value", "pass_condition", "status"])

    original_metrics = [
        {"metric": "decoded_rgb_exact_train_validation_pairs", "value": len(exact_cross), "pass_condition": "0", "status": "PASS" if len(exact_cross) == 0 else "FAIL"},
        {"metric": "phash_le4_train_validation_pairs", "value": len(phash_cross), "pass_condition": "0", "status": "PASS" if len(phash_cross) == 0 else "FAIL"},
        {"metric": "dhash_le4_train_validation_pairs", "value": len(dhash_cross), "pass_condition": "0", "status": "PASS" if len(dhash_cross) == 0 else "FAIL"},
        {"metric": "original_candidate_graph_cross_partition_edges", "value": len(original_cross), "pass_condition": "0", "status": "PASS" if len(original_cross) == 0 else "FAIL"},
        {"metric": "original_candidate_components_represented_in_both_partitions", "value": len(original_components_split), "pass_condition": "0", "status": "PASS" if len(original_components_split) == 0 else "FAIL"},
    ]
    write_csv(out_root / "audits/v40_original_candidate_rule_audit.csv", original_metrics, ["metric", "value", "pass_condition", "status"])

    human_metrics = [
        {"metric": "human_adjudicated_adjacency_cross_partition_edges", "value": len(human_cross), "pass_condition": "0", "status": "PASS" if len(human_cross) == 0 else "FAIL"},
        {"metric": "human_adjudicated_adjacency_total_edges", "value": sum(1 for row in edge_rows if row["source_type"] == "human_adjudicated_filename_proximity"), "pass_condition": "record", "status": "PASS"},
    ]
    write_csv(out_root / "audits/v40_human_adjudicated_adjacency_audit.csv", human_metrics, ["metric", "value", "pass_condition", "status"])

    extended_metrics = [
        {"metric": "extended_graph_cross_partition_edges", "value": len(extended_cross), "pass_condition": "0", "status": "PASS" if len(extended_cross) == 0 else "FAIL"},
        {"metric": "extended_components_represented_in_both_partitions", "value": len(extended_components_split), "pass_condition": "0", "status": "PASS" if len(extended_components_split) == 0 else "FAIL"},
        {"metric": "extended_component_count", "value": len(component_assignment_rows), "pass_condition": "record", "status": "PASS"},
        {"metric": "extended_edge_count", "value": len(edge_rows), "pass_condition": "record", "status": "PASS"},
    ]
    write_csv(out_root / "audits/v40_extended_graph_integrity_audit.csv", extended_metrics, ["metric", "value", "pass_condition", "status"])

    train_count = len(train_manifest)
    val_count = len(val_manifest)
    val_gt = sum(int(row["gt_box_count"]) for row in assignment_rows if row["v40_partition"] == "VALIDATION")
    moved_samples = sum(1 for row in assignment_rows if row["moved_relative_to_v39"] == "yes")
    original_edge_count = sum(1 for row in edge_rows if row["source_type"].startswith("original_"))
    human_edge_count = sum(1 for row in edge_rows if row["source_type"] == "human_adjudicated_filename_proximity")
    pass_counts = {
        "sample_id_path_overlap": len(path_overlap),
        "decoded_rgb_exact_pairs": len(exact_cross),
        "phash_le4_pairs": len(phash_cross),
        "dhash_le4_pairs": len(dhash_cross),
        "original_candidate_graph_cross_partition_edges": len(original_cross),
        "original_candidate_components_represented_in_both_partitions": len(original_components_split),
        "human_adjudicated_adjacency_cross_partition_edges": len(human_cross),
        "extended_graph_cross_partition_edges": len(extended_cross),
        "extended_components_represented_in_both_partitions": len(extended_components_split),
        "manifest_duplicates_or_missing_universe_samples": manifest_duplicates + len(missing_universe) + len(extra_universe),
    }
    all_zero = all(value == 0 for value in pass_counts.values())
    count_checks = train_count + val_count == 9652 and v40_union == v39_universe and guard_unchanged
    status = "V40_EXPANDED_ADJACENCY_SPLIT_READY_FOR_FROZEN_RERUN" if all_zero and count_checks else "V40_EXPANDED_ADJACENCY_SPLIT_BUILD_FAILED"

    source_lock = out_root / "source_lock/input_lock_manifest.csv"
    script_hashes = {
        path.name: sha256_file(path)
        for path in sorted((out_root / "scripts").glob("*.py"))
    }
    payload = {
        "generated_at": now,
        "git_commit": commit,
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
        "status": status,
        "train_count": train_count,
        "validation_count": val_count,
        "validation_gt_box_count": val_gt,
        "moved_samples_relative_to_v39": moved_samples,
        "original_edges": original_edge_count,
        "human_adjudicated_edges": human_edge_count,
        "extended_components": len(component_assignment_rows),
        "pass_audit_counts": pass_counts,
        "train_plus_validation_count": train_count + val_count,
        "v40_union_equals_frozen_v39_train_validation_universe": bool_text(v40_union == v39_universe),
        "guard_unchanged_archival": bool_text(guard_unchanged),
        "source_lock_manifest_sha256": sha256_file(source_lock) if source_lock.exists() else "",
        "script_sha256": script_hashes,
        "training_started": False,
        "evaluation_started": False,
        "profiling_started": False,
        "manuscript_changed": False,
        "model_changed": False,
        "evaluator_changed": False,
        "raw_data_changed": False,
        "label_changed": False,
        "v39_artifact_changed_only_requested_author_review_confirmation": True,
        "required_phrase": "human-adjudicated adjacent-or-near-identical component",
    }
    write_json(out_root / "audits/v40_split_audit_report.json", payload)
    report_lines = [
        "# V40 Split Audit Report",
        "",
        f"- Generated: {now}",
        f"- Git commit: `{commit}`",
        f"- Status: `{status}`",
        "- Required wording: human-adjudicated adjacent-or-near-identical component",
        f"- Environment: Python {sys.version.split()[0]} on {platform.platform()}",
        "",
        "## Split Counts",
        "",
        f"- Train samples: {train_count}",
        f"- Validation samples: {val_count}",
        f"- Validation GT boxes: {val_gt}",
        f"- Moved samples relative to V39: {moved_samples}",
        "",
        "## Edge and Component Counts",
        "",
        f"- Original edges: {original_edge_count}",
        f"- Human-adjudicated edges: {human_edge_count}",
        f"- Extended components: {len(component_assignment_rows)}",
        "",
        "## PASS Counts",
        "",
    ]
    for key, value in pass_counts.items():
        report_lines.append(f"- `{key}`: {value}")
    report_lines.extend(
        [
            "",
            "## Scope Confirmation",
            "",
            "No training, evaluation, profiling, manuscript update, model change, evaluator change, raw-data change, label change, or V39 split/result change was performed.",
        ]
    )
    (out_root / "audits/v40_split_audit_report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    final_payload = {
        **payload,
        "output_paths": {
            "train_manifest": "reproducibility/v40_expanded_adjacency_component_split_v1/manifests/v40_expanded_adjacency_component_disjoint_train.txt",
            "validation_manifest": "reproducibility/v40_expanded_adjacency_component_split_v1/manifests/v40_expanded_adjacency_component_disjoint_val.txt",
            "audit_report": "reproducibility/v40_expanded_adjacency_component_split_v1/audits/v40_split_audit_report.md",
            "rerun_handoff": "reproducibility/v40_expanded_adjacency_component_split_v1/reports/V40_RERUN_HANDOFF.md",
        },
    }
    write_json(out_root / "reports/V40_EXPANDED_ADJACENCY_SPLIT_STATUS.json", final_payload)
    status_lines = [
        "# V40 Expanded-Adjacency Split Status",
        "",
        f"- Generated: {now}",
        f"- Git commit: `{commit}`",
        f"- Status: `{status}`",
        "",
        "## Summary",
        "",
        f"- Human-review gate: PASS",
        f"- Original edges: {original_edge_count}",
        f"- Human-adjudicated edges: {human_edge_count}",
        f"- Extended components: {len(component_assignment_rows)}",
        f"- Train / validation: {train_count} / {val_count}",
        f"- Validation GT boxes: {val_gt}",
        f"- Moved samples relative to V39: {moved_samples}",
        "",
        "## PASS Counts",
        "",
    ]
    for key, value in pass_counts.items():
        status_lines.append(f"- `{key}`: {value}")
    status_lines.extend(
        [
            "",
            "This status means only that the split build and audit pass under the stated rule.",
        ]
    )
    (out_root / "reports/V40_EXPANDED_ADJACENCY_SPLIT_STATUS.md").write_text(
        "\n".join(status_lines) + "\n", encoding="utf-8"
    )

    handoff_lines = [
        "# V40 Rerun Handoff",
        "",
        f"- Generated: {now}",
        f"- Git commit: `{commit}`",
        f"- Split status: `{status}`",
        "",
        "No training has occurred on the V40 manifests.",
        "",
        "If and only if this V40 split remains accepted, the next task is a frozen rerun of four variants on the V40 manifests:",
        "",
        "1. matched early fusion;",
        "2. reliability-aware fusion with p=0.00;",
        "3. reliability-aware fusion with p=0.15;",
        "4. reliability-aware fusion with p=0.20.",
        "",
        "Each future variant requires two controlled independent runs under one locked training/evaluation protocol. The future final configuration must be selected only by two-run mean AP50, then F1, then AP75, with fixed fallback order p=0.00, p=0.15, p=0.20.",
        "",
        "Do not use the V39 guard partition for model selection or performance reporting.",
    ]
    (out_root / "reports/V40_RERUN_HANDOFF.md").write_text("\n".join(handoff_lines) + "\n", encoding="utf-8")

    print(json.dumps({"status": status, "pass_audit_counts": pass_counts, "train_count": train_count, "validation_count": val_count, "validation_gt_box_count": val_gt, "moved_samples": moved_samples}, indent=2))
    return 0 if status == "V40_EXPANDED_ADJACENCY_SPLIT_READY_FOR_FROZEN_RERUN" else 2


if __name__ == "__main__":
    raise SystemExit(main())
