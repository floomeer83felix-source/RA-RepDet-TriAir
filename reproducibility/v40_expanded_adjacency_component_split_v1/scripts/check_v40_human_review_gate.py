#!/usr/bin/env python
"""Check the V40 human-review gate before expanded graph construction.

This script is intentionally read-only with respect to source inputs. It writes
only source-lock and blocked-status reports under the V40 output root.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ALLOWED_FINAL_LABELS = {
    "exact_duplicate",
    "adjacent_or_near_identical",
    "same_scene_distinct_observation",
    "false_candidate",
    "uncertain",
}

ROOT_REL_INPUTS = [
    "runs/component_disjoint_candidates/candidate_component_disjoint_v1_train.txt",
    "runs/component_disjoint_candidates/candidate_component_disjoint_v1_val.txt",
    "runs/component_disjoint_candidates/candidate_component_disjoint_v1_guard_unchanged.txt",
    "reproducibility/v39_audit_scope_resolution/original_candidate_rule/exact_decoded_rgb_train_validation_pairs.csv",
    "reproducibility/v39_audit_scope_resolution/original_candidate_rule/phash_le4_train_validation_pairs.csv",
    "reproducibility/v39_audit_scope_resolution/original_candidate_rule/dhash_le4_train_validation_pairs.csv",
    "reproducibility/v39_audit_scope_resolution/original_candidate_rule/candidate_graph_cross_split_edges.csv",
    "reproducibility/v39_audit_scope_resolution/original_candidate_rule/candidate_component_partition_audit.csv",
    "reproducibility/v39_audit_scope_resolution/original_candidate_rule/reviewed_41_component_assignment.csv",
    "reproducibility/v39_filename_proximity_review_packet_v1/input_snapshot/original_candidate_graph_component_nodes__component_nodes.csv",
    "reproducibility/v39_filename_proximity_review_packet_v1/input_snapshot/original_candidate_graph_component_edges__component_edges.csv",
    "reproducibility/v39_filename_proximity_review_packet_v1/input_snapshot/original_candidate_graph_components__components.csv",
    "reproducibility/v39_filename_proximity_review_packet_v1/input_snapshot/reviewed_41_component_assignment__reviewed_41_component_assignment.csv",
    "reproducibility/v39_filename_proximity_review_packet_v1/manifests/cluster_manifest.csv",
    "reproducibility/v39_filename_proximity_review_packet_v1/manifests/all_pair_manifest.csv",
    "reproducibility/v39_filename_proximity_review_packet_v1/manifests/selected_pair_manifest.csv",
    "reproducibility/v39_filename_proximity_review_packet_v1/reviewer_forms/filename_proximity_author_review.csv",
    "reproducibility/v39_audit_scope_resolution/V39_AUDIT_SCOPE_RESOLUTION.md",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_commit(root: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=str(root),
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "UNKNOWN"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def nonempty(value: object) -> bool:
    return bool(str(value or "").strip())


def validate_gate(root: Path) -> tuple[dict[str, object], list[dict[str, object]]]:
    author_csv = root / "reproducibility/v39_filename_proximity_review_packet_v1/reviewer_forms/filename_proximity_author_review.csv"
    cluster_manifest = root / "reproducibility/v39_filename_proximity_review_packet_v1/manifests/cluster_manifest.csv"
    author_rows = read_csv(author_csv)
    cluster_rows = read_csv(cluster_manifest)

    cluster_ids = {row.get("cluster_id", "").strip() for row in cluster_rows}
    author_ids = [row.get("cluster_id", "").strip() for row in author_rows]
    unique_author_ids = set(author_ids)

    missing_or_invalid: list[dict[str, object]] = []
    label_counts = {label: 0 for label in sorted(ALLOWED_FINAL_LABELS)}
    for index, row in enumerate(author_rows, start=1):
        cluster_id = row.get("cluster_id", "").strip()
        label = row.get("author_final_label", "").strip()
        reviewed_by = row.get("reviewed_by", "").strip()
        review_date = row.get("review_date", "").strip()
        issues: list[str] = []
        if not cluster_id:
            issues.append("missing_cluster_id")
        if cluster_id and cluster_id not in cluster_ids:
            issues.append("cluster_id_not_in_cluster_manifest")
        if not label:
            issues.append("missing_author_final_label")
        elif label not in ALLOWED_FINAL_LABELS:
            issues.append("invalid_author_final_label")
        else:
            label_counts[label] += 1
        if not reviewed_by:
            issues.append("missing_reviewed_by")
        if not review_date:
            issues.append("missing_review_date")
        if issues:
            missing_or_invalid.append(
                {
                    "row_number": index,
                    "cluster_id": cluster_id,
                    "issues": "|".join(issues),
                    "author_final_label": label,
                    "reviewed_by": reviewed_by,
                    "review_date": review_date,
                    "requires_human_confirmation": row.get("requires_human_confirmation", "").strip(),
                }
            )

    duplicate_ids = sorted({cid for cid in author_ids if author_ids.count(cid) > 1})
    missing_cluster_ids = sorted(cluster_ids - unique_author_ids)
    unexpected_cluster_ids = sorted(unique_author_ids - cluster_ids)

    summary = {
        "status": "V40_HUMAN_REVIEW_GATE_BLOCKED" if missing_or_invalid or duplicate_ids or missing_cluster_ids or unexpected_cluster_ids else "PASS",
        "expected_cluster_count": 70,
        "author_review_row_count": len(author_rows),
        "author_review_unique_cluster_count": len(unique_author_ids),
        "cluster_manifest_count": len(cluster_ids),
        "missing_or_invalid_row_count": len(missing_or_invalid),
        "duplicate_cluster_ids": duplicate_ids,
        "missing_cluster_ids_from_author_review": missing_cluster_ids,
        "unexpected_author_review_cluster_ids": unexpected_cluster_ids,
        "final_label_counts": label_counts,
        "adjacency_edge_authorized_labels": ["exact_duplicate", "adjacent_or_near_identical"],
        "adjacency_edge_cluster_ids": sorted(
            row.get("cluster_id", "").strip()
            for row in author_rows
            if row.get("author_final_label", "").strip() in {"exact_duplicate", "adjacent_or_near_identical"}
        ),
    }
    if len(author_rows) != 70:
        summary["status"] = "V40_HUMAN_REVIEW_GATE_BLOCKED"
    if len(unique_author_ids) != 70:
        summary["status"] = "V40_HUMAN_REVIEW_GATE_BLOCKED"
    if len(cluster_ids) != 70:
        summary["status"] = "V40_HUMAN_REVIEW_GATE_BLOCKED"
    return summary, missing_or_invalid


def build_source_lock(root: Path, out_root: Path, script_path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for rel in ROOT_REL_INPUTS:
        path = root / rel
        rows.append(
            {
                "input_role": Path(rel).stem,
                "path": rel,
                "exists": "yes" if path.exists() else "no",
                "bytes": path.stat().st_size if path.exists() else "",
                "sha256": sha256_file(path) if path.exists() else "",
            }
        )
    rel_script = script_path.relative_to(root).as_posix()
    rows.append(
        {
            "input_role": "v40_human_review_gate_script",
            "path": rel_script,
            "exists": "yes",
            "bytes": script_path.stat().st_size,
            "sha256": sha256_file(script_path),
        }
    )
    write_csv(
        out_root / "source_lock/input_lock_manifest.csv",
        rows,
        ["input_role", "path", "exists", "bytes", "sha256"],
    )
    return rows


def write_reports(root: Path, out_root: Path, summary: dict[str, object], missing_rows: list[dict[str, object]], lock_rows: list[dict[str, object]]) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    commit = git_commit(root)
    env = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "cwd": str(root),
    }
    payload = {
        "generated_at": now,
        "git_commit": commit,
        "environment": env,
        **summary,
        "stage_a_status": "blocked" if summary["status"] == "V40_HUMAN_REVIEW_GATE_BLOCKED" else "passed",
        "graph_construction_started": False,
        "training_started": False,
        "evaluation_started": False,
        "profiling_started": False,
        "manuscript_changed": False,
        "model_changed": False,
        "evaluator_changed": False,
        "data_changed": False,
        "label_changed": False,
        "v39_artifact_changed": False,
    }
    write_json(out_root / "human_review_summary/final_filename_proximity_human_review_summary.json", payload)
    write_json(out_root / "reports/V40_EXPANDED_ADJACENCY_SPLIT_STATUS.json", payload)

    missing_fields = [
        "row_number",
        "cluster_id",
        "issues",
        "author_final_label",
        "reviewed_by",
        "review_date",
        "requires_human_confirmation",
    ]
    write_csv(out_root / "human_review_summary/human_review_gate_missing_or_invalid_rows.csv", missing_rows, missing_fields)

    author_csv = root / "reproducibility/v39_filename_proximity_review_packet_v1/reviewer_forms/filename_proximity_author_review.csv"
    author_rows = read_csv(author_csv)
    output_rows = []
    for row in author_rows:
        output_rows.append(
            {
                "cluster_id": row.get("cluster_id", ""),
                "author_final_label": row.get("author_final_label", ""),
                "reviewed_by": row.get("reviewed_by", ""),
                "review_date": row.get("review_date", ""),
                "preliminary_label": row.get("preliminary_label", ""),
                "requires_human_confirmation": row.get("requires_human_confirmation", ""),
                "gate_status": payload["status"],
            }
        )
    write_csv(
        out_root / "human_review_summary/final_filename_proximity_human_review.csv",
        output_rows,
        [
            "cluster_id",
            "author_final_label",
            "reviewed_by",
            "review_date",
            "preliminary_label",
            "requires_human_confirmation",
            "gate_status",
        ],
    )

    lock_md = [
        "# V40 Source Lock",
        "",
        f"- Generated: {now}",
        f"- Git commit: `{commit}`",
        f"- Stage status: `{payload['stage_a_status']}`",
        f"- Gate status: `{payload['status']}`",
        f"- Environment: Python {env['python']} on {env['platform']}",
        "",
        "## Locked Inputs",
        "",
        "| Role | Path | Exists | Bytes | SHA-256 |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for row in lock_rows:
        lock_md.append(
            f"| {row['input_role']} | `{row['path']}` | {row['exists']} | {row['bytes']} | `{row['sha256']}` |"
        )
    (out_root / "source_lock/input_lock.md").write_text("\n".join(lock_md) + "\n", encoding="utf-8")

    counts = payload["final_label_counts"]
    summary_md = [
        "# V40 Filename-Proximity Human Review Summary",
        "",
        f"- Generated: {now}",
        f"- Git commit: `{commit}`",
        f"- Status: `{payload['status']}`",
        f"- Stage: `Stage A - human-review gate`",
        "",
        "## Gate Result",
        "",
        "`V40_HUMAN_REVIEW_GATE_BLOCKED`",
        "",
        "The V40 expanded adjacency graph was not constructed because the completed author-review record is incomplete.",
        "Codex did not populate, change, infer, or backfill `author_final_label`, `reviewed_by`, or `review_date`.",
        "",
        "## Counts",
        "",
        f"- Expected clusters: {payload['expected_cluster_count']}",
        f"- Author-review rows: {payload['author_review_row_count']}",
        f"- Unique author-review cluster IDs: {payload['author_review_unique_cluster_count']}",
        f"- Cluster-manifest IDs: {payload['cluster_manifest_count']}",
        f"- Missing or invalid rows: {payload['missing_or_invalid_row_count']}",
        "",
        "## Final Label Counts",
        "",
    ]
    for label in sorted(counts):
        summary_md.append(f"- `{label}`: {counts[label]}")
    summary_md.extend(
        [
            "",
            "## Authorized V40 Adjacency Clusters",
            "",
            "No cluster is authorized for V40 human-adjudicated adjacency edges until the author-review CSV has completed final labels and reviewer/date fields.",
            "",
            "## Stop Condition",
            "",
            "Graph construction, split assignment, split audits, training, evaluation, profiling, and manuscript updates were not run.",
        ]
    )
    (out_root / "human_review_summary/final_filename_proximity_human_review_summary.md").write_text(
        "\n".join(summary_md) + "\n", encoding="utf-8"
    )

    status_md = [
        "# V40 Expanded-Adjacency Split Status",
        "",
        f"- Generated: {now}",
        f"- Git commit: `{commit}`",
        f"- Status: `{payload['status']}`",
        "",
        "## Human-Review Gate",
        "",
        f"- Final label counts: {json.dumps(counts, sort_keys=True)}",
        f"- Missing or invalid rows: {payload['missing_or_invalid_row_count']}",
        "",
        "## Construction Status",
        "",
        "- Original edges: not constructed; blocked before graph construction.",
        "- Human-adjudicated edges: 0 authorized because no completed author-final rows are available.",
        "- Extended components: not constructed.",
        "- V40 train/validation manifests: not created.",
        "- V40 audits: not run.",
        "",
        "## Confirmation",
        "",
        "No training, evaluation, profiling, manuscript update, model change, evaluator change, raw-data change, label change, V39 manifest change, or V39 result change occurred.",
    ]
    (out_root / "reports/V40_EXPANDED_ADJACENCY_SPLIT_STATUS.md").write_text(
        "\n".join(status_md) + "\n", encoding="utf-8"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check the V40 human-review gate and write blocked-status reports.")
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
    script_path = Path(__file__).resolve()
    out_root.mkdir(parents=True, exist_ok=True)
    summary, missing_rows = validate_gate(root)
    lock_rows = build_source_lock(root, out_root, script_path)
    write_reports(root, out_root, summary, missing_rows, lock_rows)
    if summary["status"] == "V40_HUMAN_REVIEW_GATE_BLOCKED":
        print("V40_HUMAN_REVIEW_GATE_BLOCKED")
        print(f"missing_or_invalid_row_count={summary['missing_or_invalid_row_count']}")
        return 2
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
