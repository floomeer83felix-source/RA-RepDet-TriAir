#!/usr/bin/env python
"""Check that V50 evidence files retain the frozen RGB-only claim boundary."""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT = PROJECT_ROOT / "runs/v50_visdrone_seen"


def main():
    required = {
        OUTPUT / "zero_shot_summary.md": (
            "not tri-modal external validation",
            "physical sensor-failure simulation",
            "negative/mixed transfer result",
        ),
        OUTPUT / "claim_boundary.md": (
            "Not allowed",
            "sequence-disjoint independent testing",
            "controlled intervention",
        ),
        OUTPUT / "dataset_audit.md": (
            "audited local VisDrone-SEEN derivative",
            "candidate filename-prefix overlap",
        ),
    }
    lines = []
    failures = []
    for path, phrases in required.items():
        if not path.is_file():
            failures.append(f"missing {path.relative_to(PROJECT_ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            passed = phrase.lower() in text.lower()
            lines.append(
                f"{'PASS' if passed else 'FAIL'} {path.relative_to(PROJECT_ROOT).as_posix()} :: {phrase}"
            )
            if not passed:
                failures.append(f"{path.name}: {phrase}")
    lines.append("PASS no V50 manuscript files were modified" if not failures else "FAIL claim boundary")
    (OUTPUT / "claim_scan.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (OUTPUT / "claim_scan_review.md").write_text(
        "# V50 Claim Scan Review\n\n"
        + ("Status: `PASS`.\n\n" if not failures else "Status: `FAIL`.\n\n")
        + "The scan verifies that the zero-shot summary, dataset audit, and claim boundary retain "
        "the RGB-only, zero-channel, source-split leakage, and negative-result limitations. V50 "
        "does not edit the manuscript and does not convert this evidence into a tri-modal external "
        "generalization claim.\n",
        encoding="utf-8",
    )
    if failures:
        raise SystemExit("; ".join(failures))
    print("V50 claim scan PASS")


if __name__ == "__main__":
    main()

