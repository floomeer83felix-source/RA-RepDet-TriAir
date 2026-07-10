#!/usr/bin/env python
"""Scan V46 reports for prohibited affirmative claim wording."""

from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "runs" / "v46_coco_ablation"

PHRASES = [
    "external generalization",
    "independent public benchmark",
    "statistical significance",
    "optimal dropout",
    "calibrated sensor reliability",
    "real sensor-fault robustness",
    "COCO proof",
]

NEGATION_MARKERS = [
    " not ",
    " no ",
    "do not",
    "does not",
    "cannot",
    "disallowed",
    "forbid",
    "prohibited",
    "required caution",
    "without claiming",
]

EXCLUDED_NAMES = {
    "v46_claim_scan.txt",
    "v46_claim_scan_review.md",
    "preflight_commands.txt",
    "preflight_outputs.txt",
}


def report_files():
    extensions = {".md", ".json", ".csv", ".txt"}
    for path in sorted(OUTPUT_DIR.iterdir()):
        if not path.is_file() or path.suffix.lower() not in extensions:
            continue
        if path.name in EXCLUDED_NAMES or "log" in path.name.lower():
            continue
        yield path


def is_guardrail(line):
    normalized = f" {line.lower()} "
    return any(marker in normalized for marker in NEGATION_MARKERS)


def main():
    matches = []
    scanned = list(report_files())
    for path in scanned:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        for line_number, line in enumerate(lines, start=1):
            lowered = line.lower()
            for phrase in PHRASES:
                if phrase.lower() in lowered:
                    matches.append(
                        {
                            "file": path.relative_to(PROJECT_ROOT).as_posix(),
                            "line": line_number,
                            "phrase": phrase,
                            "classification": "guardrail_or_negation" if is_guardrail(line) else "needs_review",
                            "context": line.strip(),
                        }
                    )

    scan_lines = [
        f"generated_at: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        f"files_scanned: {len(scanned)}",
        f"matches: {len(matches)}",
    ]
    if not matches:
        scan_lines.append("NO_MATCHES")
    for match in matches:
        scan_lines.append(
            f"{match['file']}:{match['line']} | {match['phrase']} | {match['classification']} | {match['context']}"
        )
    (OUTPUT_DIR / "v46_claim_scan.txt").write_text("\n".join(scan_lines) + "\n", encoding="utf-8")

    unresolved = [match for match in matches if match["classification"] == "needs_review"]
    review_lines = [
        "# V46 Claim Scan Review",
        "",
        f"Generated: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        "",
        f"Files scanned: {len(scanned)}",
        "",
        f"Phrase matches: {len(matches)}",
        "",
        f"Unresolved affirmative matches: {len(unresolved)}",
        "",
    ]
    if matches:
        review_lines.extend(
            [
                "| File | Line | Phrase | Classification | Context |",
                "| --- | ---: | --- | --- | --- |",
            ]
        )
        for match in matches:
            context = match["context"].replace("|", "\\|")
            review_lines.append(
                f"| `{match['file']}` | {match['line']} | {match['phrase']} | {match['classification']} | {context} |"
            )
        review_lines.append("")
    if unresolved:
        review_lines.append(
            "Result: `FAIL`. At least one prohibited phrase appears outside an explicit negation or guardrail context."
        )
    else:
        review_lines.append(
            "Result: `PASS`. Every match is an explicit denial, caution, limitation, or claim-boundary guardrail; no affirmative prohibited claim was found."
        )
    review_lines.append("")
    (OUTPUT_DIR / "v46_claim_scan_review.md").write_text(
        "\n".join(review_lines), encoding="utf-8"
    )

    print(f"files_scanned={len(scanned)} matches={len(matches)} unresolved={len(unresolved)}")
    if unresolved:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
