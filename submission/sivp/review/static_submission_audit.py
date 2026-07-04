#!/usr/bin/env python
"""Static source audit for the SIVP submission package.

The audit is intentionally read-only for source TeX, BibTeX, traceability CSVs,
tables, and figures. It writes only the requested Markdown and CSV audit reports.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path


EXPECTED_TABLE_COUNT = 7
EXPECTED_FIGURE_COUNT = 6
CANONICAL_STEM = "STATIC_SUBMISSION_SOURCE_AUDIT"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument(
        "--output-prefix",
        required=True,
        help="Output prefix for the Markdown and CSV audit reports.",
    )
    return parser.parse_args()


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def add_row(rows: list[dict[str, str]], check_id: str, scope: str, status: str, severity: str, details: str) -> None:
    rows.append(
        {
            "check_id": check_id,
            "scope": scope,
            "status": status,
            "severity": severity,
            "details": " ".join(details.split()),
        }
    )


def extract_bib_keys(text: str) -> set[str]:
    return set(re.findall(r"@\w+\s*\{\s*([^,\s]+)", text))


def extract_cite_keys(text: str) -> list[str]:
    keys: list[str] = []
    for match in re.finditer(r"\\cite\w*(?:\[[^\]]*\]){0,2}\{([^}]+)\}", text):
        keys.extend(key.strip() for key in match.group(1).split(",") if key.strip())
    return keys


def resolve_latex_input(body_path: Path, input_value: str) -> Path:
    candidate = Path(input_value)
    if not candidate.suffix:
        candidate = candidate.with_suffix(".tex")
    if candidate.is_absolute():
        return candidate
    return (body_path.parent / candidate).resolve()


def table_labels_and_inputs(body_text: str) -> list[tuple[str, str]]:
    pattern = re.compile(
        r"\\begin\{table\*?\}.*?\\label\{([^}]+)\}.*?\\input\{([^}]+)\}.*?\\end\{table\*?\}",
        re.DOTALL,
    )
    return [(label, input_path) for label, input_path in pattern.findall(body_text)]


def output_paths(root: Path, output_prefix: str) -> tuple[Path, Path]:
    prefix = Path(output_prefix)
    if not prefix.is_absolute():
        prefix = root / prefix
    stem = CANONICAL_STEM if prefix.name.lower() == "static_submission_source_audit" else prefix.name
    base = prefix.with_name(stem)
    return base.with_suffix(".md"), base.with_suffix(".csv")


def write_reports(rows: list[dict[str, str]], md_path: Path, csv_path: Path, root: Path, exit_code: int) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["check_id", "scope", "status", "severity", "details"]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    blockers = [row for row in rows if row["status"] == "blocker"]
    warnings = [row for row in rows if row["status"] == "warning"]
    md_lines = [
        "# Static Submission Source Audit",
        "",
        f"Repository root: `{root}`",
        f"Result: {'PASS' if exit_code == 0 else 'FAIL'}",
        f"Blockers: {len(blockers)}",
        f"Warnings: {len(warnings)}",
        "",
        "| check_id | scope | status | severity | details |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        details = row["details"].replace("|", "\\|")
        md_lines.append(
            f"| {row['check_id']} | {row['scope']} | {row['status']} | {row['severity']} | {details} |"
        )
    md_lines.extend(
        [
            "",
            "Placeholder-mode preflight can pass structural checks while final submission readiness remains blocked by external author facts and final approved figure assets.",
            "This audit does not modify TeX, BibTeX, table fragments, figure assets, source CSVs, model code, or experiment outputs.",
            "",
        ]
    )
    md_path.write_text("\n".join(md_lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    rows: list[dict[str, str]] = []

    required_files = [
        root / "main.tex",
        root / "main_sivp_snjnl.tex",
        root / "references.bib",
        root / "submission" / "sivp" / "tex" / "main.tex",
        root / "submission" / "sivp" / "tex" / "ra_repdet_sivp.tex",
        root / "submission" / "sivp" / "tex" / "references.bib",
    ]
    missing_required = [path for path in required_files if not path.exists()]
    if missing_required:
        add_row(
            rows,
            "SRC_001",
            "required source entries",
            "blocker",
            "error",
            "Missing required files: " + ", ".join(rel(path, root) for path in missing_required),
        )
    else:
        add_row(
            rows,
            "SRC_001",
            "required source entries",
            "pass",
            "info",
            "All required source-entry files exist: " + ", ".join(rel(path, root) for path in required_files),
        )

    body_path = root / "submission" / "sivp" / "tex" / "ra_repdet_sivp.tex"
    body_text = read_text(body_path) if body_path.exists() else ""

    table_pairs = table_labels_and_inputs(body_text)
    table_inputs = [input_path for _, input_path in table_pairs]
    broken_inputs = [
        input_path
        for input_path in table_inputs
        if not resolve_latex_input(body_path, input_path).exists()
    ]
    if len(table_inputs) != EXPECTED_TABLE_COUNT or broken_inputs:
        detail_parts = [f"Found {len(table_inputs)} table inputs; expected {EXPECTED_TABLE_COUNT}."]
        if broken_inputs:
            detail_parts.append("Broken inputs: " + ", ".join(broken_inputs))
        add_row(rows, "TEX_001", "table inputs", "blocker", "error", " ".join(detail_parts))
    else:
        resolved = [rel(resolve_latex_input(body_path, input_path), root) for input_path in table_inputs]
        add_row(
            rows,
            "TEX_001",
            "table inputs",
            "pass",
            "info",
            f"All {EXPECTED_TABLE_COUNT} table inputs resolve: " + ", ".join(resolved),
        )

    table_placeholder_count = body_text.count("TABLE PLACEHOLDER")
    figure_placeholder_boxes = len(re.findall(r"Final artwork pending:", body_text))
    figure_pending_literal_count = body_text.count("Final artwork pending")
    if table_placeholder_count != 0 or figure_placeholder_boxes != EXPECTED_FIGURE_COUNT:
        add_row(
            rows,
            "TEX_002",
            "placeholder strings",
            "blocker",
            "error",
            f"TABLE PLACEHOLDER count={table_placeholder_count}; figure placeholder boxes={figure_placeholder_boxes}; expected boxes={EXPECTED_FIGURE_COUNT}.",
        )
    else:
        add_row(
            rows,
            "TEX_002",
            "placeholder strings",
            "pass",
            "info",
            f"TABLE PLACEHOLDER count=0; figure placeholder boxes={figure_placeholder_boxes}; literal Final artwork pending occurrences including captions={figure_pending_literal_count}.",
        )

    labels = re.findall(r"\\label\{([^}]+)\}", body_text)
    duplicate_labels = sorted(label for label in set(labels) if labels.count(label) > 1)
    if duplicate_labels:
        add_row(
            rows,
            "TEX_003",
            "labels",
            "blocker",
            "error",
            "Duplicate labels: " + ", ".join(duplicate_labels),
        )
    else:
        add_row(rows, "TEX_003", "labels", "pass", "info", f"All {len(labels)} body labels are unique.")

    bib_path = root / "references.bib"
    bib_keys = extract_bib_keys(read_text(bib_path)) if bib_path.exists() else set()
    cite_keys = extract_cite_keys(body_text)
    missing_cites = sorted(set(cite_keys) - bib_keys)
    if missing_cites:
        add_row(
            rows,
            "BIB_001",
            "citation keys",
            "blocker",
            "error",
            "Missing BibTeX keys for body citations: " + ", ".join(missing_cites),
        )
    else:
        add_row(rows, "BIB_001", "citation keys", "pass", "info", f"All {len(set(cite_keys))} cited keys exist in references.bib.")
    unused_keys = sorted(bib_keys - set(cite_keys))
    if unused_keys:
        add_row(
            rows,
            "BIB_002",
            "unused BibTeX keys",
            "warning",
            "warning",
            f"{len(unused_keys)} BibTeX keys are not cited in the SIVP body: " + ", ".join(unused_keys[:20]),
        )
    else:
        add_row(rows, "BIB_002", "unused BibTeX keys", "pass", "info", "No unused BibTeX keys in root references.bib.")

    table_trace_path = root / "submission" / "sivp" / "tables" / "TABLE_SOURCE_TRACEABILITY.csv"
    table_trace_rows = read_csv(table_trace_path)
    traced_fragments = {row.get("fragment", "").replace("\\", "/") for row in table_trace_rows}
    body_fragments = {rel(resolve_latex_input(body_path, input_path), root) for input_path in table_inputs}
    missing_trace_fragments = sorted(body_fragments - traced_fragments)
    table_labels = [label for label, _ in table_pairs]
    if len(table_trace_rows) != EXPECTED_TABLE_COUNT or missing_trace_fragments:
        add_row(
            rows,
            "TRACE_001",
            "table traceability",
            "blocker",
            "error",
            f"Trace rows={len(table_trace_rows)}; missing fragment rows: {', '.join(missing_trace_fragments) or 'none'}.",
        )
    else:
        add_row(
            rows,
            "TRACE_001",
            "table traceability",
            "pass",
            "info",
            f"All {len(table_labels)} table labels map through body inputs to {len(table_trace_rows)} table traceability rows.",
        )

    figure_trace_path = root / "submission" / "sivp" / "figures" / "FIGURE_SOURCE_TRACEABILITY.csv"
    figure_trace_rows = read_csv(figure_trace_path)
    figure_labels = [label for label in labels if label.startswith("fig:")]
    figure_ids = {row.get("figure_id", "") for row in figure_trace_rows}
    expected_figure_ids = {f"Fig. {idx}" for idx in range(1, EXPECTED_FIGURE_COUNT + 1)}
    if len(figure_labels) != EXPECTED_FIGURE_COUNT or not expected_figure_ids.issubset(figure_ids):
        add_row(
            rows,
            "TRACE_002",
            "figure traceability",
            "blocker",
            "error",
            f"Figure labels={len(figure_labels)}; traceability rows={len(figure_trace_rows)}; expected ids missing={', '.join(sorted(expected_figure_ids - figure_ids)) or 'none'}.",
        )
    else:
        add_row(
            rows,
            "TRACE_002",
            "figure traceability",
            "pass",
            "info",
            f"All {len(figure_labels)} figure labels have corresponding Fig. 1-6 traceability rows.",
        )

    add_row(
        rows,
        "READY_001",
        "readiness interpretation",
        "warning",
        "warning",
        "Placeholder-mode preflight PASS remains structural only and is not formal submission readiness.",
    )
    add_row(
        rows,
        "WRITE_001",
        "source modification guard",
        "pass",
        "info",
        "Audit writes only Markdown/CSV reports and does not open source TeX, BibTeX, traceability CSVs, tables, or figures for writing.",
    )

    hard_blockers = [row for row in rows if row["status"] == "blocker"]
    exit_code = 1 if hard_blockers else 0
    md_path, csv_path = output_paths(root, args.output_prefix)
    write_reports(rows, md_path, csv_path, root, exit_code)
    print(f"Saved: {md_path}")
    print(f"Saved: {csv_path}")
    print(f"Result: {'PASS' if exit_code == 0 else 'FAIL'}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
