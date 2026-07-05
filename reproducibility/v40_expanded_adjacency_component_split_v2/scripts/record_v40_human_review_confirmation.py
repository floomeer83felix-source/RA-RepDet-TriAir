#!/usr/bin/env python
"""Record the research-owner V40 filename-proximity review confirmation."""

from __future__ import annotations

import argparse
import csv
import hashlib
import shutil
from datetime import date
from pathlib import Path


ALLOWED_LABELS = {
    "exact_duplicate",
    "adjacent_or_near_identical",
    "same_scene_distinct_observation",
    "false_candidate",
    "uncertain",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write_rows(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record the V40 research-owner review confirmation.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument(
        "--review-csv",
        default="reproducibility/v39_filename_proximity_review_packet_v1/reviewer_forms/filename_proximity_author_review.csv",
        help="Author review CSV to update after preserving the blank template.",
    )
    parser.add_argument(
        "--cluster-manifest",
        default="reproducibility/v39_filename_proximity_review_packet_v1/manifests/cluster_manifest.csv",
        help="Cluster manifest used to verify the expected 70 cluster IDs.",
    )
    parser.add_argument(
        "--blank-template-copy",
        default="reproducibility/v40_expanded_adjacency_component_split_v2/source_lock/filename_proximity_author_review_blank_template_before_v40_confirmation.csv",
        help="Output copy of the blank review template before confirmation is recorded.",
    )
    parser.add_argument("--reviewed-by", default="research_owner", help="Reviewer label recorded from V40_NEXT_TASK.")
    parser.add_argument("--review-date", default=str(date.today()), help="Review date to record.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    review_csv = root / args.review_csv
    cluster_manifest = root / args.cluster_manifest
    blank_copy = root / args.blank_template_copy

    fieldnames, rows = read_rows(review_csv)
    _, cluster_rows = read_rows(cluster_manifest)
    cluster_ids = {row["cluster_id"] for row in cluster_rows}
    if len(rows) != 70 or len({row.get("cluster_id", "") for row in rows}) != 70 or len(cluster_ids) != 70:
        raise SystemExit("Expected exactly 70 review rows and 70 cluster-manifest IDs.")
    missing = sorted(cluster_ids - {row.get("cluster_id", "") for row in rows})
    if missing:
        raise SystemExit(f"Review CSV is missing cluster IDs: {missing}")

    blank_copy.parent.mkdir(parents=True, exist_ok=True)
    if not blank_copy.exists():
        shutil.copy2(review_csv, blank_copy)

    for row in rows:
        preliminary = row.get("preliminary_label", "").strip()
        if preliminary not in ALLOWED_LABELS:
            raise SystemExit(f"Invalid preliminary label for {row.get('cluster_id')}: {preliminary}")
        row["author_final_label"] = preliminary
        row["reviewed_by"] = args.reviewed_by
        row["review_date"] = args.review_date
        row["author_notes"] = (
            "Research owner confirmed agreement with the preliminary review for all 70 "
            "filename-proximity clusters in docs/V40_NEXT_TASK.md."
        )

    write_rows(review_csv, fieldnames, rows)
    print("V40 human-review confirmation recorded")
    print(f"blank_template_copy={blank_copy.relative_to(root).as_posix()}")
    print(f"updated_review_csv_sha256={sha256_file(review_csv)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
