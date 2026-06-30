#!/usr/bin/env python
"""Preflight checks for the RA-RepDet SIVP submission source.

The strict mode intentionally fails when author-provided information, public
archive metadata, final figures, or non-placeholder declarations are absent.
Use --allow-placeholders only for draft/readiness audits.
"""

import argparse
import re
import sys
from pathlib import Path


REQUIRED_FILES = [
    "main.tex",
    "main_sivp_snjnl.tex",
    "references.bib",
    "REVISION_LOG_V18.md",
    "SUBMISSION_PRECHECK_V18.md",
    "archive_manifest.txt",
    "AUTHOR_FINAL_INPUTS_REQUIRED_V18.md",
    "metadata/submission_metadata.yaml",
    "metadata/submission_metadata.tex",
    "metadata/IMPLEMENTATION_DETAILS_TEMPLATE.md",
    "submission/sivp/tex/sn-jnl.cls",
]

STRICT_REQUIRED_FINAL_ASSETS = [
    "figures/Fig1_overall_architecture.pdf",
    "figures/Fig2_leakage_aware_protocol.pdf",
    "figures/Fig3_controlled_ablation.pdf",
    "figures/Fig4_missing_modality_robustness.pdf",
    "figures/Fig5_reliability_weight_audit.pdf",
    "figures/Fig6_qualitative_results.pdf",
]

PLACEHOLDER_PATTERNS = [
    r"\[[A-Z0-9 _/-]*(AUTHOR|AFFILIATION|EMAIL|FUNDING|ACKNOWLEDG|COMPETING|CONTRIBUTION|DATA AVAILABILITY)[A-Z0-9 _/-]*\]",
    r"AUTHOR_(REQUIRED|CONFIRMATION_REQUIRED|CONFIRMATION REQUIRED)",
    r"AUTHOR CONFIRMATION REQUIRED",
    r"TODO",
    r"UNKNOWN",
    r"NOT PROVIDED",
    r"NOT_RELEASED",
    r"DO NOT CLAIM",
    r"Final artwork pending",
    r"TABLE PLACEHOLDER",
    r"PLACEHOLDER",
]


def read_text(path):
    return path.read_text(encoding="utf-8", errors="replace")


def add_issue(issues, severity, message):
    issues.append((severity, message))


def parse_bib_keys(text):
    return set(re.findall(r"@\w+\s*\{\s*([^,\s]+)", text))


def parse_cite_keys(text):
    keys = set()
    for content in re.findall(r"\\cite(?:[tp])?(?:\[[^\]]*\])?(?:\[[^\]]*\])?\{([^}]+)\}", text):
        for key in content.split(","):
            key = key.strip()
            if key:
                keys.add(key)
    return keys


def check_tex_pair(root, issues):
    main = root / "main.tex"
    sn = root / "main_sivp_snjnl.tex"
    if not main.exists() or not sn.exists():
        return
    main_text = read_text(main)
    sn_text = read_text(sn)
    if main_text != sn_text:
        add_issue(issues, "FAIL", "main.tex and main_sivp_snjnl.tex differ; v18 requires simultaneous updates.")
    if "sn-jnl" not in sn_text or "iicol" not in sn_text:
        add_issue(issues, "FAIL", "main_sivp_snjnl.tex does not use the Springer sn-jnl two-column template.")


def check_citations(root, issues):
    bib_path = root / "references.bib"
    tex_paths = [root / "main.tex", root / "main_sivp_snjnl.tex", root / "submission/sivp/tex/ra_repdet_sivp.tex"]
    if not bib_path.exists():
        return
    bib_keys = parse_bib_keys(read_text(bib_path))
    cite_keys = set()
    for path in tex_paths:
        if path.exists():
            cite_keys.update(parse_cite_keys(read_text(path)))
    missing = sorted(cite_keys - bib_keys)
    if missing:
        add_issue(issues, "FAIL", "Unresolved citation keys: " + ", ".join(missing))


def check_claim_language(root, issues):
    for rel in ("main.tex", "main_sivp_snjnl.tex", "submission/sivp/tex/ra_repdet_sivp.tex"):
        path = root / rel
        if not path.exists():
            continue
        text = read_text(path).lower()
        if "test set" in text or "held-out test" in text:
            add_issue(
                issues,
                "FAIL",
                f"{rel} contains test-set wording; v18 requires validation wording unless independent frozen test results are provided.",
            )


def check_placeholders(root, allow_placeholders, issues):
    paths = [
        root / "main.tex",
        root / "main_sivp_snjnl.tex",
        root / "REVISION_LOG_V18.md",
        root / "SUBMISSION_PRECHECK_V18.md",
        root / "archive_manifest.txt",
        root / "AUTHOR_FINAL_INPUTS_REQUIRED_V18.md",
        root / "metadata/submission_metadata.yaml",
        root / "metadata/submission_metadata.tex",
        root / "metadata/IMPLEMENTATION_DETAILS_TEMPLATE.md",
        root / "submission/sivp/tex/ra_repdet_sivp.tex",
    ]
    combined = []
    for path in paths:
        if path.exists():
            combined.append((path, read_text(path)))
    for pattern in PLACEHOLDER_PATTERNS:
        regex = re.compile(pattern, re.IGNORECASE)
        for path, text in combined:
            if regex.search(text):
                severity = "WARN" if allow_placeholders else "FAIL"
                add_issue(issues, severity, f"Placeholder or unverified field remains in {path.relative_to(root)}: /{pattern}/")
                break


def check_final_assets(root, allow_placeholders, issues):
    missing = [rel for rel in STRICT_REQUIRED_FINAL_ASSETS if not (root / rel).exists()]
    if missing:
        severity = "WARN" if allow_placeholders else "FAIL"
        add_issue(issues, severity, "Missing final figure assets: " + ", ".join(missing))


def main():
    parser = argparse.ArgumentParser(description="RA-RepDet SIVP preflight submission checks.")
    parser.add_argument("--root", default=".", help="Project root.")
    parser.add_argument("--allow-placeholders", action="store_true", help="Permit draft placeholders and missing final assets.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    issues = []

    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            add_issue(issues, "FAIL", f"Missing required file: {rel}")

    check_tex_pair(root, issues)
    check_citations(root, issues)
    check_claim_language(root, issues)
    check_placeholders(root, args.allow_placeholders, issues)
    check_final_assets(root, args.allow_placeholders, issues)

    failures = [message for severity, message in issues if severity == "FAIL"]
    warnings = [message for severity, message in issues if severity == "WARN"]

    print("RA-RepDet SIVP preflight")
    print(f"root: {root}")
    print(f"allow_placeholders: {args.allow_placeholders}")
    for message in warnings:
        print(f"WARN: {message}")
    for message in failures:
        print(f"FAIL: {message}")

    if failures:
        print("RESULT: FAIL")
        return 1

    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
