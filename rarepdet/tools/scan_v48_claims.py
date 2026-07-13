#!/usr/bin/env python
"""Scan V48 artifacts for prohibited affirmative claim language."""

from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "runs" / "v48_complete_ablation"
PHRASES = (
    "external generalization",
    "independent benchmark",
    "statistical significance",
    "proves causality",
    "optimal dropout",
    "calibrated reliability",
    "sensor health probability",
    "real sensor-fault robustness",
    "guard-selected",
    "holdout-selected",
)
NEGATION_MARKERS = (" not ", " no ", "do not", "does not", "cannot", "must not", "without", "forbid", "prohibit")
EXCLUDED = {"claim_scan.txt", "claim_scan_review.md", "preflight_commands.txt", "preflight_outputs.txt"}


def is_guardrail(line):
    normalized = f" {line.lower()} "
    return any(marker in normalized for marker in NEGATION_MARKERS)


def main():
    matches = []
    files = [
        path for path in sorted(OUTPUT_DIR.rglob("*"))
        if path.is_file() and path.suffix.lower() in {".md", ".json", ".csv", ".txt"} and path.name not in EXCLUDED and "log" not in path.name.lower()
    ]
    for path in files:
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            for phrase in PHRASES:
                if phrase in line.lower():
                    matches.append({
                        "file": path.relative_to(PROJECT_ROOT).as_posix(),
                        "line": number,
                        "phrase": phrase,
                        "classification": "guardrail_or_negation" if is_guardrail(line) else "needs_review",
                        "context": line.strip(),
                    })
    unresolved = [item for item in matches if item["classification"] == "needs_review"]
    scan = [
        f"generated_at: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        f"files_scanned: {len(files)}",
        f"matches: {len(matches)}",
    ]
    scan.extend(f"{item['file']}:{item['line']} | {item['phrase']} | {item['classification']} | {item['context']}" for item in matches)
    (OUTPUT_DIR / "claim_scan.txt").write_text("\n".join(scan) + "\n", encoding="utf-8")
    review = [
        "# V48 Claim Scan Review",
        "",
        f"Generated: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        "",
        f"Files scanned: {len(files)}",
        f"Phrase matches: {len(matches)}",
        f"Unresolved affirmative matches: {len(unresolved)}",
        "",
        "Result: `PASS`. No prohibited affirmative claim wording was found." if not unresolved else "Result: `FAIL`. Prohibited wording requires review.",
        "",
    ]
    (OUTPUT_DIR / "claim_scan_review.md").write_text("\n".join(review), encoding="utf-8")
    print(f"files_scanned={len(files)} matches={len(matches)} unresolved={len(unresolved)}")
    if unresolved:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
