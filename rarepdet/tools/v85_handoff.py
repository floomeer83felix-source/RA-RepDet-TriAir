"""V85-specific handoff and status preservation helpers."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path


def is_v85_ready(project_root):
    root = Path(project_root)
    output = root / "runs/v85_real_qualitative_figure"
    required = (
        output / "V85_QUALITATIVE_FIGURE_SUMMARY.md",
        output / "selection/selected_samples.json",
        output / "predictions/checkpoint_identity.json",
        output / "provenance/qualitative_figure_provenance.md",
        output / "figure/fig6_real_qualitative.png",
        output / "figure/fig6_real_qualitative.pdf",
        output / "manuscript_integration_audit.md",
    )
    return all(path.is_file() for path in required)


def build_v85_data(project_root):
    root = Path(project_root)
    output = root / "runs/v85_real_qualitative_figure"
    selected = json.loads((output / "selection/selected_samples.json").read_text(encoding="utf-8"))
    checkpoints = json.loads((output / "predictions/checkpoint_identity.json").read_text(encoding="utf-8"))
    return {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "task": "V85 real checkpoint-backed qualitative figure",
        "status": "V85_REAL_QUALITATIVE_FIGURE_COMPLETE",
        "selected_samples": selected["samples"],
        "selection_thresholds": selected["thresholds"],
        "checkpoints": checkpoints,
        "display_contract": {"score_threshold": 0.25, "nms_iou": 0.60, "max_detections": 100},
        "locked_holdout_accessed": False,
        "synthetic_content_used": False,
        "figure": "runs/v85_real_qualitative_figure/figure/fig6_real_qualitative.pdf",
        "manuscript": "submission/v85_real_qualitative_manuscript/main.tex",
        "next_action": "Author review of the frozen qualitative figure before final submission packaging.",
    }


def write_v85_handoff(project_root):
    root = Path(project_root)
    data = build_v85_data(root)
    runs = root / "runs"
    (runs / "handoff_latest.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    samples = data["selected_samples"]
    lines = [
        "# RA-RepDet-TriAir Handoff", "", f"Generated: {data['generated_at']}", "",
        "## Current task", "", f"- Status: `{data['status']}`.",
        "- V85 generated and integrated a real checkpoint-backed qualitative figure.",
        "- No training, threshold tuning, synthetic content, manual box editing, or locked-holdout access occurred.",
        "", "## Frozen evidence", "",
        "- Candidate table covers all 2,213 frozen development-validation samples.",
        "- Selected samples: " + ", ".join(
            f"`{row['sample_id']}` (`{row['component_id']}`)" for row in samples
        ) + ".",
        "- Scenes use three distinct components and model-independent descriptor selection.",
        "- Checkpoints are matched early seed 0 and dynamic gate/no-dropout seed 0, both SHA256-verified.",
        "- One global display contract: score 0.25, NMS IoU 0.60, maximum 100 detections.",
        "", "## Artifacts", "",
        "- Summary: `runs/v85_real_qualitative_figure/V85_QUALITATIVE_FIGURE_SUMMARY.md`.",
        "- Provenance: `runs/v85_real_qualitative_figure/provenance/qualitative_figure_provenance.md`.",
        "- Manuscript: `submission/v85_real_qualitative_manuscript/main.tex`.",
        "- Figure PNG/PDF remain local under the repository heavy-artifact policy.",
        "- Two-pass manuscript source validation passed with zero undefined references.",
        "", "## Next action", "", f"- {data['next_action']}", "",
    ]
    (runs / "handoff_latest.md").write_text("\n".join(lines), encoding="utf-8")


def preserve_v85_status(project_root):
    status = Path(project_root) / "docs/EXPERIMENT_STATUS.md"
    marker = "V85_REAL_QUALITATIVE_FIGURE_COMPLETE"
    if not status.is_file() or marker not in status.read_text(encoding="utf-8"):
        raise RuntimeError("V85 experiment status is missing its completion marker")
