#!/usr/bin/env python
"""Report-only planner for future confirmed submission updates."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


PLAN_STATES = {
    "pending_author_response",
    "awaiting_confirmation_metadata",
    "awaiting_external_verification",
    "awaiting_figure_decision",
    "eligible_for_future_guarded_application",
    "not_applicable_in_current_phase",
}

LEDGER_REQUIRED_COLUMNS = {
    "item_id",
    "category",
    "exact_required_input",
    "repository_destination",
    "current_state",
    "action_to_close",
    "notes",
}

RESPONSE_REQUIRED_COLUMNS = {
    "item_id",
    "category",
    "exact_required_input",
    "author_response",
    "confirmed_by",
    "confirmation_date",
    "source_of_confirmation",
    "repository_destination",
    "validation_rule",
    "notes",
}

VALIDATION_REQUIRED_COLUMNS = {
    "item_id",
    "category",
    "readiness_state",
    "minimum_missing_fields",
    "structural_findings",
    "external_verification_note",
    "repository_destination",
}

FIGURE_DECISION_REQUIRED_COLUMNS = {
    "figure_id",
    "author_decision",
    "approval_date",
    "approver_identity",
    "final_asset_authorized",
}

FIGURE6_REQUIRED_COLUMNS = {
    "review_slot",
    "author_decision",
    "crop_or_redaction_needed",
    "approval_date",
    "approver_identity",
}

PLAN_FIELDS = [
    "item_id",
    "category",
    "validation_state",
    "plan_state",
    "author_confirmation_complete",
    "external_verification_required",
    "future_destination_files",
    "future_application_scope",
    "blocking_conditions",
    "required_evidence",
    "next_safe_action",
    "notes",
]

CHECK_FIELDS = ["check_id", "scope", "status", "value", "evidence", "notes"]

RESPONSE_CONFIRMATION_FIELDS = [
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

FIGURE_DESTINATIONS = {
    "FIG_001": "figures/Fig1_overall_architecture.pdf; submission/sivp/figures/FINAL_ASSET_INSERTION_MAP.md",
    "FIG_002": "figures/Fig2_leakage_aware_protocol.pdf; submission/sivp/figures/FINAL_ASSET_INSERTION_MAP.md",
    "FIG_003": "figures/Fig3_controlled_ablation.pdf; submission/sivp/figures/FINAL_ASSET_INSERTION_MAP.md",
    "FIG_004": "figures/Fig4_missing_modality_robustness.pdf; submission/sivp/figures/FINAL_ASSET_INSERTION_MAP.md",
    "FIG_005": "figures/Fig5_reliability_weight_audit.pdf; submission/sivp/figures/FINAL_ASSET_INSERTION_MAP.md",
    "FIG_006": "figures/Fig6_qualitative_results.pdf; submission/sivp/figures/FINAL_ASSET_INSERTION_MAP.md",
}

APPLICATION_SCOPE_BY_CATEGORY = {
    "author_metadata": "authorship and submission metadata placeholders after author confirmation",
    "declarations": "funding, acknowledgments, contributions, competing interests, AI-use disclosure, and submission-form declarations after author confirmation",
    "data_governance": "data availability, dataset citation, licence, access, redistribution, and metadata records after external provider/owner verification",
    "release_archive": "archive manifest, release/precheck metadata, release licence, immutable source identifier, archive date, and DOI state after release-owner verification",
    "figure_asset": "final figure-asset workflow and insertion-map closure after author approval and final asset evidence",
    "claim_scope": "validation-only wording or approved held-out-evidence claim scope after author decision",
    "environment": "environment and reproducibility metadata after a confirmed environment record is supplied",
    "compile_readiness": "strict preflight and Springer sn-jnl compile readiness only after all external blockers close",
}

REQUIRED_EVIDENCE_BY_CATEGORY = {
    "author_metadata": "author response plus confirmer, confirmation date, and source of confirmation",
    "declarations": "author-approved declaration wording plus confirmer, confirmation date, and source of confirmation",
    "data_governance": "author/data-owner response, confirmation metadata, and external provider/licence/access evidence",
    "release_archive": "release-owner response, confirmation metadata, immutable release/source evidence, licence, archive date, and DOI/no-DOI evidence",
    "figure_asset": "author figure decision, final asset authorization, approval metadata, and final approved figure asset evidence",
    "claim_scope": "author claim-scope decision and confirmation metadata; new held-out evidence only if stronger claims are requested",
    "environment": "completed environment record and research-owner confirmation metadata",
    "compile_readiness": "all strict-preflight blockers closed, local sn-jnl readiness recorded, and compile owner confirmation",
}

FUTURE_SEQUENCE = [
    "authorship/declarations",
    "data/release facts",
    "figure workflow",
    "claim scope",
    "environment",
    "strict preflight",
    "compile",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Repository root.")
    parser.add_argument("--responses", required=True, help="Author response CSV path.")
    parser.add_argument("--validation", required=True, help="Phase 7H validation CSV path.")
    parser.add_argument("--ledger", required=True, help="Canonical submission-input ledger CSV path.")
    parser.add_argument("--figure-decisions", required=True, help="Author figure decision CSV path.")
    parser.add_argument("--figure6-template", required=True, help="Fig. 6 panel review template CSV path.")
    parser.add_argument("--output-prefix", required=True, help="Output prefix for plan reports.")
    return parser.parse_args()


def resolve_path(root: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def md_escape(value: object) -> str:
    return str(value).replace("|", "\\|")


def is_complete(row: dict[str, str]) -> bool:
    return (row.get("current_state") or "").strip().lower().startswith("complete")


def nonblank(row: dict[str, str], field: str) -> bool:
    return bool((row.get(field) or "").strip())


def missing_confirmation_fields(row: dict[str, str]) -> list[str]:
    return [field for field in RESPONSE_CONFIRMATION_FIELDS if not nonblank(row, field)]


def rows_by_id(rows: list[dict[str, str]], id_field: str, label: str, errors: list[str]) -> dict[str, dict[str, str]]:
    grouped: dict[str, dict[str, str]] = {}
    counts = Counter((row.get(id_field) or "").strip() for row in rows)
    duplicates = sorted(item_id for item_id, count in counts.items() if count > 1)
    blanks = [label for item_id in counts if not item_id]
    if duplicates:
        errors.append(f"duplicate {label} IDs: " + ", ".join(duplicates))
    if blanks:
        errors.append(f"blank {label} ID found")
    for row in rows:
        item_id = (row.get(id_field) or "").strip()
        if item_id:
            grouped[item_id] = row
    return grouped


def add_missing_column_errors(label: str, columns: list[str], required: set[str], errors: list[str]) -> None:
    missing = sorted(required - set(columns))
    if missing:
        errors.append(f"{label} missing required columns: " + ", ".join(missing))


def output_paths(root: Path, output_prefix: str) -> tuple[Path, Path, Path, Path, Path]:
    prefix = resolve_path(root, output_prefix)
    base = prefix.with_name("CONFIRMED_UPDATE_PLAN")
    review_dir = root / "submission" / "sivp" / "review"
    check_base = review_dir / "CONFIRMED_UPDATE_PLAN_CHECK"
    return (
        base.with_suffix(".md"),
        base.with_suffix(".csv"),
        base.with_suffix(".json"),
        check_base.with_suffix(".md"),
        check_base.with_suffix(".csv"),
    )


def figure_id_for_item(item_id: str) -> str:
    if not item_id.startswith("FIG_"):
        return ""
    try:
        index = int(item_id.split("_", 1)[1])
    except (IndexError, ValueError):
        return ""
    return f"Fig. {index}"


def has_pending_text(*values: str) -> bool:
    text = " ".join(value.lower() for value in values if value)
    pending_tokens = ("pending", "required", "missing", "defer", "not final")
    return any(token in text for token in pending_tokens)


def figure_decision_complete(figure_id: str, decisions_by_id: dict[str, dict[str, str]]) -> bool:
    row = decisions_by_id.get(figure_id)
    if not row:
        return False
    required = ["author_decision", "approval_date", "approver_identity", "final_asset_authorized"]
    if any(not nonblank(row, field) for field in required):
        return False
    return not has_pending_text(row.get("author_decision", ""), row.get("final_asset_authorized", ""))


def figure6_template_complete(rows: list[dict[str, str]]) -> bool:
    if not rows:
        return False
    required = ["author_decision", "crop_or_redaction_needed", "approval_date", "approver_identity"]
    for row in rows:
        if any(not nonblank(row, field) for field in required):
            return False
        if has_pending_text(row.get("author_decision", ""), row.get("crop_or_redaction_needed", "")):
            return False
    return True


def external_evidence_recorded(response_row: dict[str, str], validation_row: dict[str, str]) -> bool:
    note = (validation_row.get("external_verification_note") or "").strip().lower()
    if not note or note == "none":
        return False
    if "required" in note or "needs" in note or "still" in note:
        return False
    return all(nonblank(response_row, field) for field in RESPONSE_CONFIRMATION_FIELDS)


def destination_for(row: dict[str, str]) -> str:
    item_id = (row.get("item_id") or "").strip()
    if item_id in FIGURE_DESTINATIONS:
        return FIGURE_DESTINATIONS[item_id]
    return row.get("repository_destination", "")


def classify_plan_row(
    ledger_row: dict[str, str],
    response_row: dict[str, str],
    validation_row: dict[str, str],
    figure_decisions_by_id: dict[str, dict[str, str]],
    figure6_complete: bool,
) -> dict[str, str]:
    item_id = (ledger_row.get("item_id") or "").strip()
    category = (ledger_row.get("category") or "").strip()
    validation_state = (validation_row.get("readiness_state") or "").strip()
    missing_fields = missing_confirmation_fields(response_row)
    author_confirmation_complete = (
        not missing_fields and validation_state == "structurally_ready_for_future_apply"
    )
    external_required = category in EXTERNAL_VERIFICATION_CATEGORIES
    blocking: list[str] = []
    notes: list[str] = []

    if missing_fields:
        blocking.append("missing " + ", ".join(missing_fields))
    if validation_state != "structurally_ready_for_future_apply":
        blocking.append(f"validation_state={validation_state}")

    plan_state = "pending_author_response"
    next_safe_action = "complete the author response row with confirmation metadata"

    if category == "figure_asset":
        figure_id = figure_id_for_item(item_id)
        decision_complete = figure6_complete if item_id == "FIG_006" else figure_decision_complete(
            figure_id, figure_decisions_by_id
        )
        if not decision_complete:
            plan_state = "awaiting_figure_decision"
            blocking.append("author figure decision or final asset authorization is pending")
            next_safe_action = "complete author figure decisions and final-asset approval metadata"
            if item_id == "FIG_006":
                notes.append("Fig. 6 planning uses only template completion state and exposes no local panel paths.")
        elif missing_fields:
            plan_state = "pending_author_response"
        elif validation_state != "structurally_ready_for_future_apply":
            plan_state = "awaiting_confirmation_metadata"
            next_safe_action = "rerun validation after confirmation metadata is corrected"
        elif not external_evidence_recorded(response_row, validation_row):
            plan_state = "awaiting_external_verification"
            blocking.append("final figure asset evidence is not externally verified")
            next_safe_action = "record external final-asset evidence before any figure application task"
        else:
            plan_state = "eligible_for_future_guarded_application"
            blocking = ["none at planning gate"]
            next_safe_action = "promote a guarded future figure-application task"
    elif missing_fields and not any(nonblank(response_row, field) for field in RESPONSE_CONFIRMATION_FIELDS):
        plan_state = "pending_author_response"
    elif missing_fields:
        plan_state = "awaiting_confirmation_metadata"
        next_safe_action = "complete missing confirmation metadata and rerun validation"
    elif validation_state != "structurally_ready_for_future_apply":
        plan_state = "awaiting_confirmation_metadata"
        next_safe_action = "correct validation findings and rerun the Phase 7H validator"
    elif external_required and not external_evidence_recorded(response_row, validation_row):
        plan_state = "awaiting_external_verification"
        blocking.append("external verification evidence is not recorded in response and validation data")
        next_safe_action = "record owner/provider/asset evidence before any future source update"
    elif author_confirmation_complete:
        plan_state = "eligible_for_future_guarded_application"
        blocking = ["none at planning gate"]
        next_safe_action = "promote a guarded future application task for this category"

    if plan_state not in PLAN_STATES:
        raise ValueError(f"unknown plan state computed for {item_id}: {plan_state}")

    if not blocking:
        blocking = ["none at planning gate"]
    if ledger_row.get("notes"):
        notes.append(ledger_row["notes"])

    return {
        "item_id": item_id,
        "category": category,
        "validation_state": validation_state,
        "plan_state": plan_state,
        "author_confirmation_complete": "yes" if author_confirmation_complete else "no",
        "external_verification_required": "yes" if external_required else "no",
        "future_destination_files": destination_for(ledger_row),
        "future_application_scope": APPLICATION_SCOPE_BY_CATEGORY.get(category, "not applicable in current phase"),
        "blocking_conditions": "; ".join(dict.fromkeys(blocking)),
        "required_evidence": REQUIRED_EVIDENCE_BY_CATEGORY.get(category, "author-confirmed evidence"),
        "next_safe_action": next_safe_action,
        "notes": "; ".join(note for note in notes if note) or "report-only planning row; no destination edited",
    }


def build_destination_groups(plan_rows: list[dict[str, str]]) -> dict[str, list[str]]:
    groups: dict[str, set[str]] = {}
    for row in plan_rows:
        groups.setdefault(row["category"], set())
        for item in row["future_destination_files"].split(";"):
            clean = item.strip()
            if clean:
                groups[row["category"]].add(clean)
    return {category: sorted(values) for category, values in sorted(groups.items())}


def check_no_fig6_exposure(plan_rows: list[dict[str, str]]) -> bool:
    fig6_rows = [row for row in plan_rows if row["item_id"] == "FIG_006"]
    forbidden_tokens = ("review_slot", "sample_identifier", "image_index_", "manifest_row_id", "crop path")
    text = " ".join(" ".join(row.values()) for row in fig6_rows).lower()
    return not any(token in text for token in forbidden_tokens)


def build_checks(
    ledger_rows: list[dict[str, str]],
    unresolved_rows: list[dict[str, str]],
    response_rows: list[dict[str, str]],
    validation_rows: list[dict[str, str]],
    plan_rows: list[dict[str, str]],
    structural_errors: list[str],
) -> list[dict[str, str]]:
    ledger_by_id = {(row.get("item_id") or "").strip(): row for row in ledger_rows}
    tab_state = ledger_by_id.get("TAB_001", {}).get("current_state", "missing")
    eligible_count = sum(1 for row in plan_rows if row["plan_state"] == "eligible_for_future_guarded_application")
    duplicate_or_unknown = [error for error in structural_errors if "duplicate" in error or "absent" in error or "unknown" in error]
    checks = [
        {
            "check_id": "PLAN_001",
            "scope": "canonical ledger row count",
            "status": "pass" if len(ledger_rows) == 30 else "fail",
            "value": str(len(ledger_rows)),
            "evidence": "submission/sivp/review/FINAL_SUBMISSION_INPUT_LEDGER.csv",
            "notes": "Expected 30 canonical ledger rows.",
        },
        {
            "check_id": "PLAN_002",
            "scope": "TAB_001 resolved state",
            "status": "pass" if tab_state.lower().startswith("complete") else "fail",
            "value": tab_state,
            "evidence": "FINAL_SUBMISSION_INPUT_LEDGER.csv",
            "notes": "Resolved table row remains absent from unresolved planning work.",
        },
        {
            "check_id": "PLAN_003",
            "scope": "response, validation, and plan row counts",
            "status": "pass" if len(response_rows) == len(validation_rows) == len(plan_rows) == len(unresolved_rows) == 29 else "fail",
            "value": f"responses={len(response_rows)}; validation={len(validation_rows)}; plan={len(plan_rows)}; unresolved={len(unresolved_rows)}",
            "evidence": "AUTHOR_SUBMISSION_INPUT_RESPONSES.csv; AUTHOR_RESPONSE_VALIDATION.csv; CONFIRMED_UPDATE_PLAN.csv",
            "notes": "One row is expected for each unresolved non-table ledger item.",
        },
        {
            "check_id": "PLAN_004",
            "scope": "one-to-one ID linkage",
            "status": "pass" if not duplicate_or_unknown else "fail",
            "value": "0 linkage errors" if not duplicate_or_unknown else "; ".join(duplicate_or_unknown),
            "evidence": "planner structural checks",
            "notes": "Every unresolved ledger item must link to exactly one response and one validation row.",
        },
        {
            "check_id": "PLAN_005",
            "scope": "eligible rows in current blank template",
            "status": "pass" if eligible_count == 0 else "fail",
            "value": str(eligible_count),
            "evidence": "CONFIRMED_UPDATE_PLAN.csv",
            "notes": "Current Phase 7G response template is blank, so no row may be eligible.",
        },
        {
            "check_id": "PLAN_006",
            "scope": "response-template edits",
            "status": "pass",
            "value": "0 edits by planner",
            "evidence": "planner output allowlist",
            "notes": "The planner writes only plan and check reports.",
        },
        {
            "check_id": "PLAN_007",
            "scope": "TeX, metadata destination, figure, and release-manifest edits",
            "status": "pass",
            "value": "0 edits by planner",
            "evidence": "planner output allowlist",
            "notes": "Destination files are listed for future guarded tasks only.",
        },
        {
            "check_id": "PLAN_008",
            "scope": "figure decision inference",
            "status": "pass",
            "value": "0 inferred approvals",
            "evidence": "AUTHOR_FIGURE_REVIEW_DECISIONS.csv; FIGURE6_PANEL_REVIEW_TEMPLATE.csv",
            "notes": "Pending author-review rows remain blocked.",
        },
        {
            "check_id": "PLAN_009",
            "scope": "Fig. 6 local path exposure",
            "status": "pass" if check_no_fig6_exposure(plan_rows) else "fail",
            "value": "no local panel path or filename exposed",
            "evidence": "CONFIRMED_UPDATE_PLAN.csv",
            "notes": "Fig. 6 uses only decision-template completion state.",
        },
        {
            "check_id": "PLAN_010",
            "scope": "strict preflight expected state",
            "status": "warning",
            "value": "expected FAIL",
            "evidence": "python scripts/preflight_submission.py --root .",
            "notes": "External facts and final approved figure assets remain absent.",
        },
    ]
    return checks


def write_plan_md(
    path: Path,
    summary: dict[str, object],
    destination_groups: dict[str, list[str]],
    plan_rows: list[dict[str, str]],
) -> None:
    lines = [
        "# Confirmed Update Plan",
        "",
        "This is a future update plan only. It does not apply, confirm, approve, or copy any author response into TeX, metadata, release, reference, or figure destinations.",
        "",
        "## Summary",
        "",
        f"- Canonical ledger rows: {summary['ledger_total']}",
        f"- Resolved ledger rows: {summary['resolved_count']}",
        f"- Unresolved ledger rows: {summary['unresolved_count']}",
        f"- Plan rows: {summary['plan_rows']}",
        f"- Eligible for future guarded application: {summary['eligible_rows']}",
        f"- Formal submission readiness: no",
        "",
        "## Plan Counts By Category",
        "",
        "| category | plan_state | count |",
        "| --- | --- | --- |",
    ]
    for key, count in summary["category_plan_state_counts"]:
        category, plan_state = key
        lines.append(f"| {category} | {plan_state} | {count} |")

    lines += [
        "",
        "## Destination Groups",
        "",
        "These files are listed as future destinations only; no listed destination was edited.",
        "",
        "| category | future destination files |",
        "| --- | --- |",
    ]
    for category, destinations in destination_groups.items():
        lines.append(f"| {category} | {md_escape('; '.join(destinations))} |")

    lines += [
        "",
        "## Future Application Sequence",
        "",
    ]
    for index, step in enumerate(FUTURE_SEQUENCE, start=1):
        lines.append(f"{index}. {step}")

    lines += [
        "",
        "## Plan Rows",
        "",
        "| item_id | category | validation_state | plan_state | author_confirmation_complete | external_verification_required | future_destination_files | future_application_scope | blocking_conditions | required_evidence | next_safe_action | notes |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in plan_rows:
        lines.append(
            "| "
            + " | ".join(md_escape(row[field]) for field in PLAN_FIELDS)
            + " |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_check_md(path: Path, checks: list[dict[str, str]]) -> None:
    lines = [
        "# Confirmed Update Plan Check",
        "",
        "This review confirms that Phase 7I produced a report-only update plan and did not apply submission facts or assets.",
        "",
        "| check_id | scope | status | value | evidence | notes |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in checks:
        lines.append(
            "| "
            + " | ".join(md_escape(row[field]) for field in CHECK_FIELDS)
            + " |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    responses_path = resolve_path(root, args.responses)
    validation_path = resolve_path(root, args.validation)
    ledger_path = resolve_path(root, args.ledger)
    figure_decisions_path = resolve_path(root, args.figure_decisions)
    figure6_template_path = resolve_path(root, args.figure6_template)
    plan_md, plan_csv, plan_json, check_md, check_csv = output_paths(root, args.output_prefix)

    structural_errors: list[str] = []
    ledger_rows, ledger_columns = read_csv(ledger_path)
    response_rows, response_columns = read_csv(responses_path)
    validation_rows, validation_columns = read_csv(validation_path)
    figure_decision_rows, figure_decision_columns = read_csv(figure_decisions_path)
    figure6_rows, figure6_columns = read_csv(figure6_template_path)

    add_missing_column_errors("ledger", ledger_columns, LEDGER_REQUIRED_COLUMNS, structural_errors)
    add_missing_column_errors("responses", response_columns, RESPONSE_REQUIRED_COLUMNS, structural_errors)
    add_missing_column_errors("validation", validation_columns, VALIDATION_REQUIRED_COLUMNS, structural_errors)
    add_missing_column_errors("figure decisions", figure_decision_columns, FIGURE_DECISION_REQUIRED_COLUMNS, structural_errors)
    add_missing_column_errors("Fig. 6 template", figure6_columns, FIGURE6_REQUIRED_COLUMNS, structural_errors)

    ledger_by_id = rows_by_id(ledger_rows, "item_id", "ledger item", structural_errors)
    responses_by_id = rows_by_id(response_rows, "item_id", "response item", structural_errors)
    validation_by_id = rows_by_id(validation_rows, "item_id", "validation item", structural_errors)
    figure_decisions_by_id = rows_by_id(figure_decision_rows, "figure_id", "figure decision", structural_errors)

    unresolved_rows = [row for row in ledger_rows if not is_complete(row)]
    resolved_rows = [row for row in ledger_rows if is_complete(row)]
    unresolved_ids = {(row.get("item_id") or "").strip() for row in unresolved_rows}
    resolved_ids = {(row.get("item_id") or "").strip() for row in resolved_rows}
    response_ids = set(responses_by_id)
    validation_ids = set(validation_by_id)

    missing_response = sorted(unresolved_ids - response_ids)
    missing_validation = sorted(unresolved_ids - validation_ids)
    extra_response = sorted(response_ids - unresolved_ids)
    extra_validation = sorted(validation_ids - unresolved_ids)
    resolved_in_response = sorted(resolved_ids & response_ids)
    resolved_in_validation = sorted(resolved_ids & validation_ids)

    if missing_response:
        structural_errors.append("unresolved ledger item IDs absent from response data: " + ", ".join(missing_response))
    if missing_validation:
        structural_errors.append("unresolved ledger item IDs absent from validation data: " + ", ".join(missing_validation))
    if extra_response:
        structural_errors.append("response item IDs absent from unresolved ledger data: " + ", ".join(extra_response))
    if extra_validation:
        structural_errors.append("validation item IDs absent from unresolved ledger data: " + ", ".join(extra_validation))
    if resolved_in_response:
        structural_errors.append("resolved ledger item IDs present in response data: " + ", ".join(resolved_in_response))
    if resolved_in_validation:
        structural_errors.append("resolved ledger item IDs present in validation data: " + ", ".join(resolved_in_validation))
    if len(response_rows) != len(unresolved_rows):
        structural_errors.append(f"response/unresolved count mismatch: responses={len(response_rows)} unresolved={len(unresolved_rows)}")
    if len(validation_rows) != len(unresolved_rows):
        structural_errors.append(f"validation/unresolved count mismatch: validation={len(validation_rows)} unresolved={len(unresolved_rows)}")

    figure6_complete = figure6_template_complete(figure6_rows)
    plan_rows: list[dict[str, str]] = []
    if not structural_errors:
        for ledger_row in unresolved_rows:
            item_id = (ledger_row.get("item_id") or "").strip()
            plan_rows.append(
                classify_plan_row(
                    ledger_row,
                    responses_by_id[item_id],
                    validation_by_id[item_id],
                    figure_decisions_by_id,
                    figure6_complete,
                )
            )
    else:
        for ledger_row in unresolved_rows:
            item_id = (ledger_row.get("item_id") or "").strip()
            if item_id in responses_by_id and item_id in validation_by_id:
                plan_rows.append(
                    classify_plan_row(
                        ledger_row,
                        responses_by_id[item_id],
                        validation_by_id[item_id],
                        figure_decisions_by_id,
                        figure6_complete,
                    )
                )

    if len(plan_rows) != len(unresolved_rows):
        structural_errors.append(f"plan/unresolved count mismatch: plan={len(plan_rows)} unresolved={len(unresolved_rows)}")

    plan_state_counts = Counter(row["plan_state"] for row in plan_rows)
    category_plan_state_counts = Counter((row["category"], row["plan_state"]) for row in plan_rows)
    eligible_rows = plan_state_counts.get("eligible_for_future_guarded_application", 0)
    destination_groups = build_destination_groups(plan_rows)
    checks = build_checks(ledger_rows, unresolved_rows, response_rows, validation_rows, plan_rows, structural_errors)

    summary = {
        "ledger_total": len(ledger_rows),
        "resolved_count": len(resolved_rows),
        "unresolved_count": len(unresolved_rows),
        "response_rows": len(response_rows),
        "validation_rows": len(validation_rows),
        "plan_rows": len(plan_rows),
        "eligible_rows": eligible_rows,
        "plan_state_counts": dict(sorted(plan_state_counts.items())),
        "category_plan_state_counts": sorted(category_plan_state_counts.items()),
        "external_verification_categories": sorted(EXTERNAL_VERIFICATION_CATEGORIES),
        "future_application_sequence": FUTURE_SEQUENCE,
    }
    json_payload = {
        "phase": "Phase 7I",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "formal_submission_readiness": False,
        "report_only": True,
        "planner": {
            "script": "submission/sivp/metadata/plan_confirmed_submission_updates.py",
            "mode": "cpu-only report-only",
            "accepted_arguments": [
                "--root",
                "--responses",
                "--validation",
                "--ledger",
                "--figure-decisions",
                "--figure6-template",
                "--output-prefix",
            ],
            "outcome": "PASS" if not structural_errors else "FAIL",
        },
        "counts": {
            "ledger_total": len(ledger_rows),
            "resolved_count": len(resolved_rows),
            "unresolved_count": len(unresolved_rows),
            "response_rows": len(response_rows),
            "validation_rows": len(validation_rows),
            "plan_rows": len(plan_rows),
            "eligible_rows": eligible_rows,
            "plan_state_counts": dict(sorted(plan_state_counts.items())),
            "plan_state_counts_by_category": {
                f"{category}:{state}": count
                for (category, state), count in sorted(category_plan_state_counts.items())
            },
        },
        "structural_errors": structural_errors,
        "destination_groups": destination_groups,
        "future_application_sequence": FUTURE_SEQUENCE,
        "plan_rows": plan_rows,
        "checks": checks,
        "no_destination_application_confirmation": True,
    }

    write_csv(plan_csv, plan_rows, PLAN_FIELDS)
    write_plan_md(plan_md, summary, destination_groups, plan_rows)
    write_json(plan_json, json_payload)
    write_csv(check_csv, checks, CHECK_FIELDS)
    write_check_md(check_md, checks)

    print(f"Saved: {plan_md}")
    print(f"Saved: {plan_csv}")
    print(f"Saved: {plan_json}")
    print(f"Saved: {check_md}")
    print(f"Saved: {check_csv}")
    print(
        "Plan counts: "
        + ", ".join(f"{key}={value}" for key, value in sorted(plan_state_counts.items()))
    )
    print(f"Eligible rows: {eligible_rows}")
    if structural_errors:
        for error in structural_errors:
            print(f"ERROR: {error}")
        print("Result: FAIL")
        return 1
    print("Result: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
