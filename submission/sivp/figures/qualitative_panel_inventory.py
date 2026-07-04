#!/usr/bin/env python
"""Inventory local Fig. 6 qualitative panels without exposing local paths."""

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


MANIFEST_REL = Path("runs/clean_qualitative_manifest.csv")
LOCAL_OUTPUT_ROOT = Path("runs/local_candidate_figures")
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}


def is_relative_to(path, base):
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False


def relpath(root, path):
    return Path(path).resolve().relative_to(root).as_posix()


def git_ignored(root, path):
    rel = relpath(root, path)
    result = subprocess.run(
        ["git", "check-ignore", "-q", "--", rel],
        cwd=root,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def validate_output_path(root, output):
    output_path = Path(output)
    resolved = (root / output_path).resolve() if not output_path.is_absolute() else output_path.resolve()
    local_root = (root / LOCAL_OUTPUT_ROOT).resolve()
    if not is_relative_to(resolved, local_root):
        raise RuntimeError("output path must resolve under runs/local_candidate_figures/")
    if not git_ignored(root, resolved):
        raise RuntimeError("output path is not ignored by Git")
    return resolved


def read_manifest(root):
    path = root / MANIFEST_REL
    data = path.read_bytes()
    text = data.decode("utf-8-sig")
    reader = csv.DictReader(text.splitlines())
    rows = list(reader)
    return path, reader.fieldnames or [], rows, hashlib.sha256(data).hexdigest()


def discover_path_column(headers, rows):
    header_scores = []
    for header in headers:
        lower = header.lower()
        score = 0
        if "panel" in lower:
            score += 4
        if "path" in lower:
            score += 3
        if "file" in lower:
            score += 1
        image_like_values = 0
        nonempty_values = 0
        for row in rows:
            value = (row.get(header) or "").strip()
            if value:
                nonempty_values += 1
                if Path(value).suffix.lower() in IMAGE_SUFFIXES:
                    image_like_values += 1
        if image_like_values:
            score += 2
        if nonempty_values:
            score += 1
        if score:
            header_scores.append((score, image_like_values, nonempty_values, header))

    if not header_scores:
        return None
    header_scores.sort(key=lambda item: (-item[0], -item[1], -item[2], item[3].lower()))
    return header_scores[0][3]


def safe_identifier(row, fallback):
    for key in ("Image Index", "image_index", "index", "Index", "sample_id", "Sample ID"):
        value = (row.get(key) or "").strip()
        if value:
            return f"image_index_{value}" if "index" in key.lower() else f"sample_{value}"
    return f"manifest_row_{fallback}"


def inventory_rows(rows, path_column):
    results = []
    with_path = 0
    existing = 0
    missing = 0
    for index, row in enumerate(rows, start=1):
        raw_path = (row.get(path_column) or "").strip() if path_column else ""
        has_path = bool(raw_path)
        exists = False
        diagnostic = "no path metadata"
        if has_path:
            with_path += 1
            panel_path = Path(raw_path).expanduser()
            exists = panel_path.exists() and panel_path.is_file()
            diagnostic = "exists" if exists else "missing or not a file"
            if exists:
                existing += 1
            else:
                missing += 1
        else:
            missing += 1
        results.append(
            {
                "manifest_row_id": index,
                "safe_sample_identifier": safe_identifier(row, index),
                "panel_path": raw_path,
                "has_path_metadata": has_path,
                "exists": exists,
                "diagnostic": diagnostic,
            }
        )
    return results, with_path, existing, missing


def write_json_atomic(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(path)
    finally:
        if tmp.exists():
            tmp.unlink()


def main(argv=None):
    parser = argparse.ArgumentParser(description="Local-only Fig. 6 qualitative panel inventory.")
    parser.add_argument("--dry-run", action="store_true", required=True, help="Required mode; never writes images.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--output", required=True, help="Ignored local JSON path under runs/local_candidate_figures/.")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    try:
        output_path = validate_output_path(root, args.output)
        manifest_path, headers, rows, manifest_sha256 = read_manifest(root)
        path_column = discover_path_column(headers, rows)
        row_results, with_path, existing, missing = inventory_rows(rows, path_column)
        payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "mode": "dry-run",
            "manifest": {
                "path": str(manifest_path),
                "relative_path": MANIFEST_REL.as_posix(),
                "sha256": manifest_sha256,
                "headers": headers,
                "row_count": len(rows),
                "discovered_panel_path_column": path_column,
            },
            "summary": {
                "manifest_row_count": len(rows),
                "rows_with_path_metadata": with_path,
                "locally_existing_panel_files": existing,
                "missing_or_unverifiable": missing,
                "image_content_opened": False,
                "images_or_figures_written": False,
            },
            "rows": row_results,
        }
        write_json_atomic(output_path, payload)
    except (OSError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print("RA-RepDet Fig. 6 local panel inventory")
    print(f"manifest rows: {len(rows)}")
    print(f"rows with candidate path metadata: {with_path}")
    print(f"existing local panel files: {existing}")
    print(f"missing or unverifiable: {missing}")
    print(f"output: {relpath(root, output_path)}")
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
