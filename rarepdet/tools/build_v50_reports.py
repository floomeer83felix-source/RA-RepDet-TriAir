#!/usr/bin/env python
"""Aggregate V50 zero-shot and RGB-baseline result records."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import json
from pathlib import Path
from statistics import mean, stdev


PROJECT_ROOT = Path(__file__).resolve().parents[2]
METRICS = (
    "ap50_95",
    "ap50",
    "ap75",
    "ar100",
    "ap_small",
    "ap_medium",
    "ap_large",
)
ROW_FIELDS = (
    "run_id",
    "protocol",
    "variant",
    "model",
    "seed",
    "images",
    "gt_boxes",
    "ignored_regions",
    "detections",
    *METRICS,
    "fps",
    "checkpoint_sha256",
    "manifest_sha256",
    "annotations_sha256",
    "adapter",
    "weights",
    "command",
)


def load_results(directory):
    return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(directory.glob("*.json"))]


def write_csv(path, rows, fields=ROW_FIELDS):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def describe(values):
    return {
        "mean": mean(values),
        "sample_sd": stdev(values) if len(values) > 1 else 0.0,
        "values": values,
    }


def group_summary(rows):
    output = {}
    for variant in sorted({row["variant"] for row in rows}):
        selected = [row for row in rows if row["variant"] == variant]
        output[variant] = {
            metric: describe([float(row[metric]) for row in selected]) for metric in METRICS
        }
    return output


def paired_rows(protocol, rows):
    by_seed = {(row["variant"], int(row["seed"])): row for row in rows}
    output = []
    for seed in (0, 1, 2):
        early = by_seed[("matched_early", seed)]
        reliability = by_seed[("ra_full_p015", seed)]
        row = {"protocol": protocol, "seed": seed}
        for metric in METRICS:
            row[f"early_{metric}"] = float(early[metric])
            row[f"ra_{metric}"] = float(reliability[metric])
            row[f"delta_{metric}"] = float(reliability[metric]) - float(early[metric])
        output.append(row)
    return output


def paired_summary(rows):
    return {
        metric: describe([float(row[f"delta_{metric}"]) for row in rows]) for metric in METRICS
    }


def metric_table(rows):
    lines = [
        "| run | seed | AP@[.50:.95] | AP50 | AP75 | AR100 | APs | APm | APl |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in sorted(rows, key=lambda item: (item["variant"], int(item["seed"]))):
        lines.append(
            f"| {row['run_id']} | {row['seed']} | {row['ap50_95']:.6f} | "
            f"{row['ap50']:.6f} | {row['ap75']:.6f} | {row['ar100']:.6f} | "
            f"{row['ap_small']:.6f} | {row['ap_medium']:.6f} | {row['ap_large']:.6f} |"
        )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", default="runs/v50_visdrone_seen")
    args = parser.parse_args()
    run_dir = Path(args.run_dir)
    if not run_dir.is_absolute():
        run_dir = PROJECT_ROOT / run_dir
    generated_at = datetime.now().astimezone().isoformat(timespec="seconds")

    zero = {}
    paired = []
    for protocol in ("devval", "test"):
        rows = load_results(run_dir / "raw/zero_shot" / protocol)
        if len(rows) != 6:
            raise RuntimeError(f"expected six zero-shot {protocol} results, found {len(rows)}")
        zero[protocol] = rows
        write_csv(run_dir / f"zero_shot_{protocol}_per_run.csv", rows)
        paired.extend(paired_rows(protocol, rows))

    paired_fields = ["protocol", "seed"]
    for metric in METRICS:
        paired_fields.extend((f"early_{metric}", f"ra_{metric}", f"delta_{metric}"))
    write_csv(run_dir / "zero_shot_paired_deltas.csv", paired, paired_fields)

    summary = {
        "generated_at": generated_at,
        "boundary": (
            "RGB-only missing-modality/domain-shift stress with thermal=event=0.0; not external "
            "tri-modal validation or physical sensor-failure evidence"
        ),
        "devval": {
            "groups": group_summary(zero["devval"]),
            "paired_deltas_ra_minus_early": paired_summary(
                [row for row in paired if row["protocol"] == "devval"]
            ),
        },
        "test": {
            "groups": group_summary(zero["test"]),
            "paired_deltas_ra_minus_early": paired_summary(
                [row for row in paired if row["protocol"] == "test"]
            ),
        },
    }
    (run_dir / "zero_shot_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    test_delta = summary["test"]["paired_deltas_ra_minus_early"]
    (run_dir / "zero_shot_summary.md").write_text(
        "# V50 Frozen-Checkpoint RGB-Only Stress Summary\n\n"
        "This is an RGB-only domain-shift and controlled missing-modality stress test. RGB is "
        "scaled to `[0,1]`; thermal and event are appended as exact `0.0` channels. It is not "
        "tri-modal external validation or a physical sensor-failure simulation.\n\n"
        "## Devval\n\n"
        + metric_table(zero["devval"])
        + "\n\n## Test\n\n"
        + metric_table(zero["test"])
        + "\n\n## Paired Test Deltas\n\n"
        + f"Across the three frozen seed pairs, RA minus matched early was "
        f"`{test_delta['ap50_95']['mean']:.6f} +/- {test_delta['ap50_95']['sample_sd']:.6f}` "
        f"for AP@[.50:.95], `{test_delta['ap50']['mean']:.6f} +/- "
        f"{test_delta['ap50']['sample_sd']:.6f}` for AP50, and "
        f"`{test_delta['ap75']['mean']:.6f} +/- {test_delta['ap75']['sample_sd']:.6f}` "
        "for AP75 (mean +/- sample SD). These descriptive differences are small in absolute "
        "terms and do not establish statistical significance.\n\n"
        "The low absolute scores are retained as a negative/mixed transfer result and must not "
        "be hidden or reframed as broad external generalization.\n",
        encoding="utf-8",
    )

    rgb_complete = True
    rgb_summary = {"generated_at": generated_at, "status": "pending"}
    for protocol in ("devval", "test"):
        directory = run_dir / "raw/rgb" / protocol
        rows = load_results(directory) if directory.is_dir() else []
        if len(rows) != 3:
            rgb_complete = False
            continue
        write_csv(run_dir / f"rgb_{protocol}_per_run.csv", rows)
        rgb_summary[protocol] = group_summary(rows)
    if rgb_complete:
        rgb_summary["status"] = "complete"
        (run_dir / "rgb_summary.json").write_text(
            json.dumps(rgb_summary, indent=2) + "\n", encoding="utf-8"
        )
        rgb_test = load_results(run_dir / "raw/rgb/test")
        (run_dir / "rgb_summary.md").write_text(
            "# V50 Dataset-Specific RGB Baseline\n\n"
            "True three-channel RGB RepViT-M0.9-FPN-FCOS, trained for 50 epochs on the frozen "
            "train split and selected only by devval canonical AP50. Test was accessed after all "
            "three checkpoints were frozen.\n\n"
            + metric_table(rgb_test)
            + "\n\nThis contextual baseline is not modality-matched to RA-RepDet training.\n",
            encoding="utf-8",
        )
    else:
        (run_dir / "rgb_summary.json").write_text(
            json.dumps(rgb_summary, indent=2) + "\n", encoding="utf-8"
        )

    (run_dir / "claim_boundary.md").write_text(
        "# V50 Claim Boundary\n\n"
        "Allowed after completion: audited external RGB-only aerial four-wheel vehicle evidence; "
        "frozen-checkpoint zero-filled missing-modality/domain-shift stress; descriptive paired "
        "three-seed differences; and a separately trained true-RGB contextual baseline.\n\n"
        "Not allowed: full RGB-thermal-event external validation, thermal/event generalization, "
        "physical sensor-failure robustness, calibrated reliability, sequence-disjoint independent "
        "testing, statistical significance, universal causality, or optimal-dropout claims.\n\n"
        "The zero channels are a controlled intervention after RGB scaling, not fabricated sensor "
        "measurements. The audited local derivative has 24 candidate filename-prefix overlaps "
        "between train and devval, so leakage-aware limitations remain explicit.\n",
        encoding="utf-8",
    )
    print(json.dumps({"zero_shot": "complete", "rgb": rgb_summary["status"]}, indent=2))


if __name__ == "__main__":
    main()
