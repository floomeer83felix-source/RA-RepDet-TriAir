#!/usr/bin/env python
"""Archive V81 checkpoint identities and reconcile against supplied V80 rows."""

from __future__ import annotations

import csv
import hashlib
import importlib.metadata
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import torch
import torchvision


ROOT = Path(__file__).resolve().parents[2]
V79 = ROOT / "runs" / "v79_single_modality_evaluator_completion"
SUPPLIED = ROOT / "runs" / "v80_supplied_standardized_single_modality_metrics"
OUT = ROOT / "runs" / "v81_single_modality_retraining_reconciliation"
METRICS = ("ap50_95", "ap50", "ap75", "ar1", "ar10", "ar100")
MODE_MAP = {"RGB-only": "rgb", "Thermal-only": "thermal", "Event-only": "event"}


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def main() -> None:
    supplied = {}
    with (SUPPLIED / "per_run.csv").open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            supplied[(MODE_MAP[row["modality"]], int(row["seed"]))] = {
                metric: float(row[metric]) for metric in METRICS
            }

    results = [json.loads(path.read_text(encoding="utf-8")) for path in sorted((V79 / "raw").glob("*.json"))]
    if len(results) != 9:
        raise RuntimeError(f"Expected nine V79 results, found {len(results)}")

    rows = []
    for result in results:
        reference = supplied[(result["input_mode"], int(result["seed"]))]
        row = {
            "run_id": result["run_id"],
            "input_mode": result["input_mode"],
            "seed": result["seed"],
            "checkpoint_epoch": result["checkpoint_epoch"],
            "checkpoint_sha256": result["checkpoint_sha256"],
            "split_sha256": result["split_sha256"],
        }
        for metric in METRICS:
            row[f"v81_{metric}"] = result[metric]
            row[f"supplied_{metric}"] = reference[metric]
            row[f"delta_{metric}"] = result[metric] - reference[metric]
        rows.append(row)

    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "reconciliation_per_run.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    summary = {}
    for mode in ("rgb", "thermal", "event"):
        mode_rows = [row for row in rows if row["input_mode"] == mode]
        summary[mode] = {}
        for metric in METRICS:
            summary[mode][metric] = {
                "v81_mean": sum(row[f"v81_{metric}"] for row in mode_rows) / len(mode_rows),
                "supplied_mean": sum(row[f"supplied_{metric}"] for row in mode_rows) / len(mode_rows),
                "mean_delta": sum(row[f"delta_{metric}"] for row in mode_rows) / len(mode_rows),
                "max_abs_seed_delta": max(abs(row[f"delta_{metric}"]) for row in mode_rows),
            }

    manifest = [
        {key: result[key] for key in (
            "run_id", "input_mode", "seed", "checkpoint_epoch", "checkpoint_sha256",
            "split_sha256", "weights", "selection_rule",
        )}
        for result in results
    ]
    write_json(OUT / "checkpoint_manifest.json", {"count": len(manifest), "entries": manifest})

    evaluator = ROOT / "rarepdet" / "tools" / "eval_v76_single_modality.py"
    builder = ROOT / "rarepdet" / "tools" / "build_v79_single_modality_evaluator_summary.py"
    environment = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "python": platform.python_version(),
        "pytorch": torch.__version__,
        "torchvision": torchvision.__version__,
        "cuda_runtime": torch.version.cuda,
        "cuda_available": torch.cuda.is_available(),
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "pycocotools": importlib.metadata.version("pycocotools"),
        "evaluator_sha256": hashlib.sha256(evaluator.read_bytes()).hexdigest(),
        "summary_builder_sha256": hashlib.sha256(builder.read_bytes()).hexdigest(),
        "validation_split_sha256": results[0]["split_sha256"],
    }
    write_json(OUT / "runtime_environment.json", environment)

    decision = {
        "status": "V81_RETRAINING_AND_STANDARDIZED_EVALUATION_COMPLETE_MATERIAL_RECONCILIATION_DIFFERENCE",
        "training_runs_complete": 9,
        "standardized_evaluations_complete": 9,
        "checkpoint_hashes_present": all(bool(result["checkpoint_sha256"]) for result in results),
        "split_hash_consistent": len({result["split_sha256"] for result in results}) == 1,
        "guard_used": any(bool(result["guard_used"]) for result in results),
        "material_difference": True,
        "manuscript_action": "keep V78 authoritative; do not silently replace the supplied V80 table",
        "identity_interpretation": "V81 checkpoints are fresh retraining outputs, not recovered V77/V80 identities",
        "group_metric_comparison": summary,
    }
    write_json(OUT / "reconciliation_summary.json", decision)
    write_json(OUT / "final_decision.json", {key: decision[key] for key in (
        "status", "training_runs_complete", "standardized_evaluations_complete",
        "checkpoint_hashes_present", "split_hash_consistent", "guard_used",
        "material_difference", "manuscript_action", "identity_interpretation",
    )})

    labels = {"rgb": "RGB-only", "thermal": "Thermal-only", "event": "Event-only"}
    lines = [
        "# V81 single-modality retraining reconciliation", "",
        f"Status: `{decision['status']}`.", "",
        "Nine fresh V81 runs and nine standardized COCO evaluations completed. ",
        f"All records use split SHA256 `{results[0]['split_sha256']}`.", "",
        "## Mean comparison", "",
        "| Modality | Metric | V81 | Supplied V80 | Delta |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for mode in ("rgb", "thermal", "event"):
        for metric in METRICS:
            values = summary[mode][metric]
            lines.append(
                f"| {labels[mode]} | {metric} | {values['v81_mean']:.4f} | "
                f"{values['supplied_mean']:.4f} | {values['mean_delta']:+.4f} |"
            )
    lines.extend([
        "", "## Decision", "",
        "The differences are material and cannot be treated as display rounding. The V81 checkpoints are fresh retraining outputs, while the supplied V77/V80 rows have no checkpoint identity package. Both evidence sets are retained and neither is silently overwritten. V78 remains authoritative pending an explicit evidence-source decision.",
        "", "No guard access, tuning, seed replacement, selective rerun, or checkpoint substitution occurred. Large checkpoint files remain local.", "",
    ])
    (OUT / "reconciliation.md").write_text("\n".join(lines), encoding="utf-8")
    (OUT / "protocol.md").write_text(
        "# V81 reconciliation protocol\n\n"
        "- Training: nine fresh 50-epoch runs under frozen V40 component-disjoint train/devval manifests.\n"
        "- Evaluation: one COCO pass per retained `best.pt`; IoU 0.50:0.05:0.95, 101 recall points, maxDets 1/10/100, score threshold 0.001, NMS 0.6.\n"
        "- Comparison: seed-matched V81 minus supplied V80 across six AP/AR metrics.\n"
        "- Boundary: development-validation only; no independent-test or significance claim.\n",
        encoding="utf-8",
    )
    (OUT / "handoff.md").write_text(
        "# V81 handoff\n\nTraining and standardized evaluation are complete 9/9. "
        "Compact identity, runtime, metric, and reconciliation evidence is archived here and under "
        "`runs/v79_single_modality_evaluator_completion/`.\n\nMaterial differences from supplied V77/V80 rows remain. "
        "Keep V78 authoritative pending an explicit evidence-source decision. Large `.pt` files remain local.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
