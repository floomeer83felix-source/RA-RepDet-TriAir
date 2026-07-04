#!/usr/bin/env python
"""Report-only validation gate for author submission input responses."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


LEDGER_REQUIRED_COLUMNS = {
    "item_id",
    "category",
    "exact_required_input",
    "repository_destination",
    "current_state",
}

RESPONSE_REQUIRED_COLUMNS = {
    "item_id",
    "category",
    "exact_required_input",
    "current_status",
    "author_response",
    "confirmed_by",
    "confirmation_date",
    "source_of_confirmation",
    "repository_destination",
    "validation_rule",
    "notes",
}

RESPONSE_ONLY_FIELDS = [
    "author_response",
    "confirmed_by",
    "confirmation_date",
    "source_of_confirmation",
]

EXTERNAL_VERIFICATION_CATEGORIES = {
    "data_governance",
    "release_archive",
    "figure_asset",
    "environment",
    "compile_readiness",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--responses", required=True, help="Author response CSV path.")
    parser.add_argument("--ledger", required=True, help="Canonical ledger CSV path.")
    parser.add_argument("--output-prefix", required=True, help="Output prefix for validation reports.")
    return parser.parse_args()


def resolve_path(root: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def is_complete(row: dict[str, str]) -> bool:
    return (row.get("current_state") or "").strip().lower().startswith("complete")


def nonblank(row: dict[str, str], field: str) -> bool:
    return bool((row.get(field) or "").strip())


def blank_fields(row: dict[str, str], fields: list[str]) -> list[str]:
    return [field for field in fields if not nonblank(row, field)]


def valid_date(value: str) -> bool:
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return False
    return True


def contains_basic_email(value: str) -> bool:
    return bool(re.search(r"\b[^@\s]+@[^@\s]+\.[^@\s]+\b", value))


def contains_orcid_or_none(value: str) -> bool:
    lowered = value.lower()
    if any(token in lowered for token in ("none", "not supplied", "not available", "no orcid")):
        return True
    return bool(re.search(r"\b\d{4}-\d{4}-\d{4}-\d{3}[\dXx]\b", value))


def contains_doi_or_none(value: str) -> bool:
    lowered = value.lower()
    if any(token in lowered for token in ("none", "not applicable", "no doi", "no zenodo")):
        return True
    return bool(re.search(r"\b10\.\d{4,9}/\S+\b", value))


def contains_url_or_policy(value: str) -> bool:
    lowered = value.lower()
    if any(token in lowered for token in ("no-release", "no release", "private", "not released")):
        return True
    return bool(re.search(r"\bhttps?://[^\s,;]+", value))


def valid_release_tag(value: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/\-]{0,127}", value.strip()))


def contains_commit_hash(value: str) -> bool:
    return bool(re.search(r"\b[0-9a-fA-F]{7,40}\b", value))


def classify_row(row: dict[str, str]) -> tuple[str, list[str], list[str], str]:
    item_id = (row.get("item_id") or "").strip()
    category = (row.get("category") or "").strip()
    response = (row.get("author_response") or "").strip()
    missing = blank_fields(row, RESPONSE_ONLY_FIELDS)
    findings: list[str] = []
    external_note = "none"

    if not any(nonblank(row, field) for field in RESPONSE_ONLY_FIELDS):
        return (
            "pending_author_response",
            RESPONSE_ONLY_FIELDS.copy(),
            ["all response and confirmation fields are blank by design"],
            "none",
        )

    if not response and any(nonblank(row, field) for field in RESPONSE_ONLY_FIELDS[1:]):
        return (
            "invalid_or_incomplete",
            ["author_response"],
            ["confirmation metadata is present without an author response"],
            "none",
        )

    if missing:
        return (
            "response_present_needs_confirmation",
            missing,
            ["author response is present but confirmation metadata is incomplete"],
            "none",
        )

    confirmation_date = (row.get("confirmation_date") or "").strip()
    if not valid_date(confirmation_date):
        findings.append("confirmation_date must use YYYY-MM-DD")

    if item_id == "AUTH_004" and not contains_basic_email(response):
        findings.append("corresponding-author email response lacks a basic email shape")
    if item_id == "AUTH_003" and not contains_orcid_or_none(response):
        findings.append("ORCID response lacks ORCID-style shape or explicit none/not supplied wording")
    if item_id == "REL_001" and not contains_url_or_policy(response):
        findings.append("release URL response lacks URL shape or explicit no-release/private policy")
    if item_id == "REL_002" and not valid_release_tag(response):
        findings.append("release tag response contains whitespace or unsupported characters")
    if item_id == "REL_003" and not contains_commit_hash(response):
        findings.append("immutable source response lacks a basic 7-40 character hex commit hash")
    if item_id == "REL_004" and not valid_date(response):
        findings.append("archive date response must use YYYY-MM-DD")
    if item_id == "REL_006" and not contains_doi_or_none(response):
        findings.append("DOI response lacks DOI shape or explicit no-DOI wording")

    if findings:
        return ("invalid_or_incomplete", [], findings, "none")

    if category in EXTERNAL_VERIFICATION_CATEGORIES:
        external_note = (
            "format is structurally acceptable, but future application still needs external owner/provider/asset verification"
        )
        return ("external_verification_required", [], ["confirmation fields are present and basic format checks passed"], external_note)

    return ("structurally_ready_for_future_apply", [], ["confirmation fields are present and basic format checks passed"], "none")


def output_paths(root: Path, output_prefix: str) -> tuple[Path, Path, Path, Path]:
    prefix = resolve_path(root, output_prefix)
    if prefix.name.lower() == "author_response_validation":
        validation_base = prefix.with_name("AUTHOR_RESPONSE_VALIDATION")
    else:
        validation_base = prefix
    readiness_base = validation_base.parent / "METADATA_APPLICATION_READINESS_MAP"
    return (
        validation_base.with_suffix(".md"),
        validation_base.with_suffix(".csv"),
        readiness_base.with_suffix(".md"),
        readiness_base.with_suffix(".csv"),
    )


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def md_escape(value: object) -> str:
    return str(value).replace("|", "\\|")


def write_validation_md(
    path: Path,
    validation_rows: list[dict[str, str]],
    summary: dict[str, object],
    integrity_errors: list[str],
) -> None:
    state_counts = summary["state_counts"]
    category_state_counts = summary["category_state_counts"]
    lines = [
        "# Author Response Validation",
        "",
        "This report is a report-only validation gate. It does not modify or confirm any factual submission value.",
        "",
        "## Summary",
        "",
        f"- Ledger total: {summary['ledger_total']}",
        f"- Resolved ledger rows: {summary['resolved_count']}",
        f"- Unresolved ledger rows: {summary['unresolved_count']}",
        f"- Response-template rows: {summary['response_row_count']}",
        f"- Structural integrity errors: {len(integrity_errors)}",
        "- Readiness counts: "
        + (
            ", ".join(f"{key}={value}" for key, value in sorted(state_counts.items()))
            if state_counts
            else "none"
        ),
        "",
        "## Counts By Category And State",
        "",
        "| category | readiness_state | count |",
        "| --- | --- | --- |",
    ]
    for (category, state), count in sorted(category_state_counts.items()):
        lines.append(f"| {category} | {state} | {count} |")

    lines += [
        "",
        "## Structural Integrity Errors",
        "",
    ]
    if integrity_errors:
        lines.extend(f"- {error}" for error in integrity_errors)
    else:
        lines.append("- none")

    lines += [
        "",
        "## Item Validation",
        "",
        "| item_id | category | readiness_state | minimum_missing_fields | structural_findings | external_verification_note | repository_destination |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in validation_rows:
        lines.append(
            "| {item_id} | {category} | {readiness_state} | {minimum_missing_fields} | {structural_findings} | {external_verification_note} | {repository_destination} |".format(
                **{key: md_escape(value) for key, value in row.items()}
            )
        )
    lines += [
        "",
        "A structurally ready row is not externally verified. Future application tasks must still check author confirmation source, owner approval, and any provider/release/asset constraints before writing destination files.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_readiness_md(path: Path, readiness_rows: list[dict[str, str]], summary: dict[str, object]) -> None:
    lines = [
        "# Metadata Application Readiness Map",
        "",
        "This map identifies future destination files only. It does not copy, apply, approve, or verify any author-provided fact.",
        "",
        f"- Unresolved response rows reviewed: {summary['response_row_count']}",
        f"- Rows ready for immediate future application: {summary['state_counts'].get('structurally_ready_for_future_apply', 0)}",
        f"- Rows requiring external verification before future application: {summary['state_counts'].get('external_verification_required', 0)}",
        f"- Pending author responses: {summary['state_counts'].get('pending_author_response', 0)}",
        "",
        "| item_id | category | readiness_state | future_application_destination | application_gate | external_verification_required | apply_blocker | notes |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in readiness_rows:
        lines.append(
            "| {item_id} | {category} | {readiness_state} | {future_application_destination} | {application_gate} | {external_verification_required} | {apply_blocker} | {notes} |".format(
                **{key: md_escape(value) for key, value in row.items()}
            )
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    responses_path = resolve_path(root, args.responses)
    ledger_path = resolve_path(root, args.ledger)

    ledger_rows, ledger_columns = read_csv(ledger_path)
    response_rows, response_columns = read_csv(responses_path)
    integrity_errors: list[str] = []

    missing_ledger_columns = sorted(LEDGER_REQUIRED_COLUMNS - set(ledger_columns))
    missing_response_columns = sorted(RESPONSE_REQUIRED_COLUMNS - set(response_columns))
    if missing_ledger_columns:
        integrity_errors.append("ledger missing required columns: " + ", ".join(missing_ledger_columns))
    if missing_response_columns:
        integrity_errors.append("response CSV missing required columns: " + ", ".join(missing_response_columns))

    ledger_by_id: dict[str, dict[str, str]] = {}
    for row in ledger_rows:
        item_id = (row.get("item_id") or "").strip()
        if item_id in ledger_by_id:
            integrity_errors.append(f"duplicate ledger item_id: {item_id}")
        ledger_by_id[item_id] = row

    response_ids = [(row.get("item_id") or "").strip() for row in response_rows]
    response_counts = Counter(response_ids)
    duplicate_response_ids = sorted(item_id for item_id, count in response_counts.items() if count > 1)
    unknown_response_ids = sorted(item_id for item_id in response_counts if item_id not in ledger_by_id)
    if duplicate_response_ids:
        integrity_errors.append("duplicate response item_id values: " + ", ".join(duplicate_response_ids))
    if unknown_response_ids:
        integrity_errors.append("response item IDs absent from ledger: " + ", ".join(unknown_response_ids))

    unresolved_rows = [row for row in ledger_rows if not is_complete(row)]
    resolved_rows = [row for row in ledger_rows if is_complete(row)]
    unresolved_ids = {(row.get("item_id") or "").strip() for row in unresolved_rows}
    resolved_ids = {(row.get("item_id") or "").strip() for row in resolved_rows}
    missing_response_ids = sorted(unresolved_ids - set(response_ids))
    resolved_response_ids = sorted(resolved_ids & set(response_ids))
    if missing_response_ids:
        integrity_errors.append("unresolved ledger item IDs missing from response CSV: " + ", ".join(missing_response_ids))
    if resolved_response_ids:
        integrity_errors.append("resolved ledger item IDs should not appear in response CSV: " + ", ".join(resolved_response_ids))

    validation_rows: list[dict[str, str]] = []
    readiness_rows: list[dict[str, str]] = []
    for row in response_rows:
        item_id = (row.get("item_id") or "").strip()
        ledger_row = ledger_by_id.get(item_id, {})
        state, missing, findings, external_note = classify_row(row)
        missing_text = "; ".join(missing) if missing else "none"
        findings_text = "; ".join(findings) if findings else "none"
        destination = row.get("repository_destination") or ledger_row.get("repository_destination", "")
        category = row.get("category") or ledger_row.get("category", "")
        validation_rows.append(
            {
                "item_id": item_id,
                "category": category,
                "exact_required_input": row.get("exact_required_input") or ledger_row.get("exact_required_input", ""),
                "readiness_state": state,
                "minimum_missing_fields": missing_text,
                "structural_findings": findings_text,
                "external_verification_note": external_note,
                "repository_destination": destination,
                "current_status": row.get("current_status", ""),
            }
        )
        is_external = "yes" if category in EXTERNAL_VERIFICATION_CATEGORIES else "no"
        if state == "structurally_ready_for_future_apply":
            gate = "future application task may update destinations after final review of confirmation source"
            blocker = "none at structural gate"
        elif state == "external_verification_required":
            gate = "future application task must verify external owner/provider/asset evidence before writing destinations"
            blocker = "external verification remains required"
        else:
            gate = "future application task must not update destinations"
            blocker = missing_text if missing_text != "none" else findings_text
        readiness_rows.append(
            {
                "item_id": item_id,
                "category": category,
                "readiness_state": state,
                "future_application_destination": destination,
                "application_gate": gate,
                "external_verification_required": is_external,
                "apply_blocker": blocker,
                "notes": row.get("notes", ""),
            }
        )

    state_counts = Counter(row["readiness_state"] for row in validation_rows)
    category_state_counts = Counter((row["category"], row["readiness_state"]) for row in validation_rows)
    summary = {
        "ledger_total": len(ledger_rows),
        "resolved_count": len(resolved_rows),
        "unresolved_count": len(unresolved_rows),
        "response_row_count": len(response_rows),
        "state_counts": state_counts,
        "category_state_counts": category_state_counts,
    }

    validation_md, validation_csv, readiness_md, readiness_csv = output_paths(root, args.output_prefix)
    validation_fields = [
        "item_id",
        "category",
        "exact_required_input",
        "readiness_state",
        "minimum_missing_fields",
        "structural_findings",
        "external_verification_note",
        "repository_destination",
        "current_status",
    ]
    readiness_fields = [
        "item_id",
        "category",
        "readiness_state",
        "future_application_destination",
        "application_gate",
        "external_verification_required",
        "apply_blocker",
        "notes",
    ]
    write_csv(validation_csv, validation_rows, validation_fields)
    write_csv(readiness_csv, readiness_rows, readiness_fields)
    write_validation_md(validation_md, validation_rows, summary, integrity_errors)
    write_readiness_md(readiness_md, readiness_rows, summary)

    print(f"Saved: {validation_md}")
    print(f"Saved: {validation_csv}")
    print(f"Saved: {readiness_md}")
    print(f"Saved: {readiness_csv}")
    print(
        "Readiness counts: "
        + ", ".join(f"{key}={value}" for key, value in sorted(state_counts.items()))
    )
    if integrity_errors:
        for error in integrity_errors:
            print(f"ERROR: {error}")
        return 1
    print("Result: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
