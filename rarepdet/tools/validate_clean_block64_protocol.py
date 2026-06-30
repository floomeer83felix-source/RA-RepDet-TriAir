#!/usr/bin/env python
"""Validate and freeze the Phase 4A block64/guard16 split protocol."""

import argparse
import csv
import hashlib
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = PROJECT_ROOT / "runs"


def resolve_path(path):
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_list(path):
    return [line.strip().replace("\\", "/") for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def read_csv_rows(path):
    with Path(path).open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def get_candidate_row(summary_path, candidate):
    rows = read_csv_rows(summary_path)
    for row in rows:
        if row.get("candidate") == candidate:
            return row
    raise RuntimeError(f"Candidate {candidate} not found in {summary_path}")


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    parser = argparse.ArgumentParser(description="Validate block64_guard16_seed0 candidate split and write protocol.")
    parser.add_argument("--candidate", default="block64_guard16_seed0")
    parser.add_argument("--candidate-dir", default="runs/blocked_split_candidates")
    parser.add_argument("--summary", default="runs/blocked_split_proposal_summary.csv")
    parser.add_argument("--out", default="runs/clean_block64g16_protocol.md")
    args = parser.parse_args()

    candidate_dir = resolve_path(args.candidate_dir)
    train_path = candidate_dir / f"{args.candidate}_train.txt"
    val_path = candidate_dir / f"{args.candidate}_val.txt"
    guard_path = candidate_dir / f"{args.candidate}_guard.txt"
    summary_path = resolve_path(args.summary)
    out_path = resolve_path(args.out)

    for path in (train_path, val_path, guard_path, summary_path):
        require(path.exists(), f"Required file not found: {path}")

    train_entries = read_list(train_path)
    val_entries = read_list(val_path)
    guard_entries = read_list(guard_path)
    train_set = set(train_entries)
    val_set = set(val_entries)
    guard_set = set(guard_entries)

    require(len(train_entries) == 7439, f"Expected 7439 train entries, got {len(train_entries)}")
    require(len(val_entries) == 2213, f"Expected 2213 validation entries, got {len(val_entries)}")
    require(len(guard_entries) == 837, f"Expected 837 guard entries, got {len(guard_entries)}")
    require(not (train_set & val_set), "Train and validation lists overlap.")
    require(not (train_set & guard_set), "Train and guard lists overlap.")
    require(not (val_set & guard_set), "Validation and guard lists overlap.")

    row = get_candidate_row(summary_path, args.candidate)
    require(int(row["train_images"]) == 7439, f"Summary train count mismatch: {row['train_images']}")
    require(int(row["val_images"]) == 2213, f"Summary val count mismatch: {row['val_images']}")
    require(int(row["guard_images"]) == 837, f"Summary guard count mismatch: {row['guard_images']}")
    require(int(row["exact_rgb_matched_val_images"]) == 0, "Summary reports nonzero exact RGB matched val images.")
    require(int(row["exact_rgb_matched_train_images"]) == 0, "Summary reports nonzero exact RGB matched train images.")
    require(int(row["exact_rgb_group_count"]) == 0, "Summary reports nonzero exact RGB groups.")
    require(int(row["id_guard_violations"]) == 0, "Summary reports nonzero same-family guard violations.")

    train_sha = sha256_file(train_path)
    val_sha = sha256_file(val_path)
    guard_sha = sha256_file(guard_path)

    lines = [
        "# Clean Block64G16 Protocol",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Candidate",
        "",
        f"- Candidate: `{args.candidate}`",
        "- Source: `runs/blocked_split_proposal_summary.csv`",
        "- These files are used directly for Phase 4A clean-split training and validation.",
        "- Guard samples are excluded from both training and validation inputs.",
        "",
        "## Frozen List Files",
        "",
        "| Split | Path | Count | SHA256 |",
        "| --- | --- | --- | --- |",
        f"| train | `{train_path}` | {len(train_entries)} | `{train_sha}` |",
        f"| validation | `{val_path}` | {len(val_entries)} | `{val_sha}` |",
        f"| guard | `{guard_path}` | {len(guard_entries)} | `{guard_sha}` |",
        "",
        "## Integrity Checks",
        "",
        "| Check | Result |",
        "| --- | --- |",
        "| train count equals 7439 | pass |",
        "| validation count equals 2213 | pass |",
        "| guard count equals 837 | pass |",
        "| train/validation/guard list overlap | none |",
        "| exact RGB-content train/validation matches | 0 |",
        "| exact RGB-content group count | 0 |",
        "| same-family guard-band violations | 0 |",
        "",
        "## Candidate Summary Row",
        "",
        "| Metric | Value |",
        "| --- | --- |",
    ]
    for key in (
        "train_images",
        "val_images",
        "guard_images",
        "train_gt_boxes",
        "val_gt_boxes",
        "guard_gt_boxes",
        "val_share_all_images",
        "val_share_used_images",
        "nearest_signature_min",
        "nearest_signature_p50",
        "nearest_signature_p90",
        "fraction_signature_le4",
        "nearest_id_distance_min",
        "nearest_id_distance_p50",
    ):
        lines.append(f"| {key} | {row.get(key, 'NA')} |")
    lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Validated candidate: {args.candidate}")
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
