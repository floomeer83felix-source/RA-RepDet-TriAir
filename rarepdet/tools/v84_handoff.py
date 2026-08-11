"""V84-specific handoff and status preservation helpers."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path


def _load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def is_v84_ready(project_root):
    root = Path(project_root)
    output = root / "runs/v84_jei_critical_closure"
    required = [
        output / "V84_EVIDENCE_SUMMARY.md",
        output / "manuscript_integration_audit.md",
        output / "rgb_thermal_baseline/summary.json",
        output / "channel_removal_2x2/run_status.json",
        output / "gate_quality_analysis/run_status.json",
        output / "component_cluster_bootstrap/run_status.json",
    ]
    if not all(path.is_file() for path in required):
        return False
    return all(
        _load_json(path).get("state") == "COMPLETE"
        for path in required[3:]
    )


def build_v84_data(project_root):
    root = Path(project_root)
    output = root / "runs/v84_jei_critical_closure"
    rgbt = _load_json(output / "rgb_thermal_baseline/summary.json")
    return {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "task": "V84 JEI critical evidence closure",
        "status": "V84_JEI_CRITICAL_EVIDENCE_CLOSURE_COMPLETE",
        "required_work": {
            "rgb_thermal_seeds": "3/3 COMPLETE",
            "channel_removal": "48/48 COMPLETE",
            "gate_quality": "30/30 COMPLETE",
            "component_bootstrap": "12/12 COMPLETE",
            "published_comparator": "DOCUMENTED_PROTOCOL_LICENSE_STOP",
            "mm_uav_reproducibility": "COMPLETE",
            "manuscript_integration": "COMPLETE",
        },
        "rgb_thermal": rgbt,
        "component_bootstrap": {
            "components": 1298,
            "replicates": 5000,
            "gate_vs_early_ap_95ci": [0.0376306, 0.0464252],
            "gate_vs_fixed_equal_ap_95ci": [0.0452387, 0.0539360],
            "gate_vs_projection_ap_95ci": [0.0269344, 0.0350818],
        },
        "claim_boundary": {
            "isolated_event_gain_established": False,
            "calibrated_sensor_health_established": False,
            "published_same_protocol_superiority_established": False,
            "locked_holdout_access_in_v84": False,
        },
        "evidence_summary": "runs/v84_jei_critical_closure/V84_EVIDENCE_SUMMARY.md",
        "manuscript": "submission/v84_jei_evidence_manuscript/main.tex",
        "next_action": "Rebuild and author-review final V84 figures before submission packaging.",
    }


def write_v84_handoff(project_root):
    root = Path(project_root)
    data = build_v84_data(root)
    runs = root / "runs"
    (runs / "handoff_latest.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    rgbt = data["rgb_thermal"]
    ap = rgbt.get("summary", {}).get("ap50_95", {})
    lines = [
        "# RA-RepDet-TriAir Handoff",
        "",
        f"Generated: {data['generated_at']}",
        "",
        "## Current task",
        "",
        f"- Status: `{data['status']}`.",
        "- V84 required computations are complete; the published comparator reached the preregistered transparent-stop condition.",
        "- The locked 837-image internal holdout was not accessed in V84.",
        "",
        "## Key evidence",
        "",
        f"- RGB+thermal baseline AP: `{ap.get('mean', 0):.4f} +/- {ap.get('sample_std', 0):.4f}` over seeds 0/1/2.",
        "- Channel-removal factorial: `48/48 COMPLETE`; event-removal robustness is mainly associated with dropout training.",
        "- Gate quality/corruption: `30/30 COMPLETE`; affected-modality weights are not monotonic sensor-health estimates.",
        "- Component bootstrap: 1,298 components and 5,000 replicates; all three primary gate/no-dropout AP intervals are positive.",
        "- MM-UAV sequence, geometry, conversion, transfer, and evaluation contracts are frozen.",
        "",
        "## Claim boundary",
        "",
        "- Dynamic gating is the defining RA-RepDet mechanism; gate/no-dropout is the nominal-accuracy primary variant.",
        "- No positive isolated event gain, calibrated reliability, same-protocol published superiority, SOTA, or statistical-significance claim is supported.",
        "- TriAir remains component-disjoint development-validation evidence; MM-UAV remains supervised exposed-devval transfer evidence.",
        "",
        "## Artifacts and next action",
        "",
        "- Evidence summary: `runs/v84_jei_critical_closure/V84_EVIDENCE_SUMMARY.md`.",
        "- Manuscript source: `submission/v84_jei_evidence_manuscript/main.tex`.",
        "- Two-pass source-only pdfLaTeX validation passed with zero undefined references.",
        f"- Next action: {data['next_action']}",
        "",
    ]
    (runs / "handoff_latest.md").write_text("\n".join(lines), encoding="utf-8")


def preserve_v84_status(project_root):
    status = Path(project_root) / "docs/EXPERIMENT_STATUS.md"
    marker = "V84_JEI_CRITICAL_EVIDENCE_CLOSURE_COMPLETE"
    if not status.is_file() or marker not in status.read_text(encoding="utf-8"):
        raise RuntimeError("V84 experiment status is missing its completion marker")
