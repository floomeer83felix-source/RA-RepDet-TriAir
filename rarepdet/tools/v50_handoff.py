"""V50-specific handoff, experiment status, and blocker rendering."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path


def is_v50_ready(project_root):
    root = Path(project_root)
    task = root / "docs/NEXT_TASK.md"
    output = root / "runs/v50_visdrone_seen"
    return (
        task.is_file()
        and "V50 audit and evaluate" in task.read_text(encoding="utf-8")
        and (output / "source_lock_v50.json").is_file()
    )


def load_json(path, default=None):
    path = Path(path)
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else default


def build_v50_data(project_root):
    root = Path(project_root)
    output = root / "runs/v50_visdrone_seen"
    status = load_json(output / "rgb_run_status.json", {"state": "NOT_STARTED", "runs": []})
    zero = load_json(output / "zero_shot_summary.json", {})
    rgb = load_json(output / "rgb_summary.json", {"status": "pending"})
    violation = load_json(output / "protocol_violation_evidence.json", {})
    return {
        "project_name": "RA-RepDet-TriAir",
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "current_task": {
            "title": "V50 audited VisDrone-SEEN external RGB evidence",
            "status": status.get("state", "UNKNOWN"),
            "commit_message": "eval: add V50 audited VisDrone-SEEN external RGB evidence",
        },
        "dataset": {
            "root": r"D:\datasets\visdrone_seen",
            "audit": "runs/v50_visdrone_seen/dataset_audit.json",
            "source_lock": "runs/v50_visdrone_seen/source_lock_v50.json",
            "identity": "audited local RGB-only VisDrone-SEEN derivative",
            "train_devval_candidate_prefix_overlaps": 24,
            "exact_cross_split_duplicates": 0,
        },
        "zero_shot": zero,
        "rgb": rgb,
        "execution": status,
        "protocol_violation": violation,
        "claim_boundary": "runs/v50_visdrone_seen/claim_boundary.md",
        "v49_compile_pending_separately": True,
    }


def handoff_markdown(data):
    runs = data["execution"].get("runs", [])
    violation = data.get("protocol_violation", {})
    lines = [
        "# RA-RepDet-TriAir Handoff",
        "",
        f"Generated: {data['generated_at']}",
        "",
        "## Current task",
        "",
        f"- Title: {data['current_task']['title']}",
        f"- Status: `{data['current_task']['status']}`.",
        f"- Dataset identity: {data['dataset']['identity']}.",
        f"- Dataset audit: `{data['dataset']['audit']}`.",
        f"- Source lock: `{data['dataset']['source_lock']}`.",
        (
            "- Zero-shot evaluation: devval completed, but test outputs are quarantined because they were generated before all three RGB checkpoints were frozen."
            if violation
            else "- Zero-shot evaluation: six frozen TriAir checkpoints on devval and test, using RGB plus exact zero thermal/event channels."
        ),
        f"- RGB baseline summary: `{data['rgb'].get('status', 'pending')}`.",
        "",
        "## RGB run state",
        "",
    ]
    if runs:
        lines.extend(
            f"- `rgb_seed{item['seed']}`: `{item.get('state', 'PENDING')}`"
            + (f", best SHA256 `{item['checkpoint_sha256']}`." if item.get("checkpoint_sha256") else ".")
            for item in runs
        )
    else:
        lines.append("- Queue not started.")
    if violation:
        lines.extend(
            [
                "",
                "## Blocking protocol violation",
                "",
                f"- Status: `{violation.get('status', 'UNKNOWN')}`.",
                "- The first zero-shot test result preceded RGB seed 0 training, while RGB seeds 1 and 2 were still pending.",
                "- The RGB queue was stopped immediately after detection; no RGB checkpoint was frozen.",
                "- Existing test metrics are retained only as violation evidence and are not accepted final V50 results.",
                "- Evidence: `runs/v50_visdrone_seen/protocol_violation_evidence.json`.",
            ]
        )
    lines.extend(
        [
            "",
            "## Scientific boundary",
            "",
            "- Evidence is RGB-only external domain-shift/missing-modality stress, not tri-modal external validation.",
            "- Zero-filled channels are a controlled intervention, not a physical sensor-failure simulation.",
            "- The source split has 24 candidate filename-prefix train/devval overlaps; do not claim sequence-disjoint independent testing.",
            (
                "- Negative, mixed, and near-zero outputs are preserved only as quarantined protocol evidence."
                if violation
                else "- Negative, mixed, and near-zero frozen-transfer results are retained."
            ),
            "- V49 Springer/BibTeX compile closure remains a separate pending item and was not altered by V50.",
            "",
        ]
    )
    return "\n".join(lines)


def status_markdown(data):
    test = data.get("zero_shot", {}).get("test", {})
    deltas = test.get("paired_deltas_ra_minus_early", {})
    ap_delta = deltas.get("ap50_95", {})
    violation = data.get("protocol_violation", {})
    lines = [
        "# Experiment Status",
        "",
        f"Updated: {data['generated_at']}",
        "",
        "## Active task",
        "",
        f"`V50_{data['current_task']['status']}`",
        "",
        "V50 audits the local RGB-only VisDrone-SEEN derivative and separates frozen TriAir-checkpoint stress evaluation from a dataset-specific true-RGB baseline.",
        "",
        "## Dataset gate",
        "",
        "- 8,629 RGB JPEG images with paired YOLO labels; linked original eight-column annotations restore ignored regions.",
        "- Local generator provenance validated with zero image and zero label mismatches.",
        "- Exact cross-split duplicates: 0; candidate filename-prefix train/devval overlaps: 24.",
        "- Four-wheel mapping: car, van, truck, and bus -> one vehicle class.",
        "",
        "## Frozen checkpoint stress result",
        "",
    ]
    if violation:
        lines.extend(
            [
                f"- Status: `{violation.get('status', 'UNKNOWN')}`.",
                "- Zero-shot devval outputs exist, but test outputs were generated before the three RGB checkpoints were frozen.",
                "- Test metrics are quarantined and are not accepted V50 final evidence.",
                "- RGB seed 0 was stopped during epoch 1; seeds 1 and 2 never started.",
            ]
        )
    elif ap_delta:
        lines.append(
            f"- Test RA-minus-early paired AP@[.50:.95] delta: `{ap_delta['mean']:.6f} +/- {ap_delta['sample_sd']:.6f}` (mean +/- sample SD, n=3)."
        )
    if not violation:
        lines.extend(
            [
                "- Absolute transfer scores are low and are reported as negative/mixed domain-shift evidence.",
                "- No threshold, NMS, mapping, adapter, or architecture setting was changed after devval inspection.",
            ]
        )
    lines.extend(
        [
            "",
            "## RGB baseline",
            "",
            f"- Queue state: `{data['execution'].get('state', 'NOT_STARTED')}`.",
        ]
    )
    for item in data["execution"].get("runs", []):
        lines.append(f"- seed {item['seed']}: `{item.get('state', 'PENDING')}`.")
    lines.extend(
        [
            "",
            "## Claim boundary",
            "",
            (
                "No final V50 performance claim is accepted while the test-order violation remains unresolved."
                if violation
                else "Allowed: audited RGB-only external evidence, controlled zero-channel stress, descriptive paired deltas, and separately trained RGB context."
            ),
            "",
            "Disallowed: tri-modal external generalization, physical sensor-fault robustness, calibrated reliability, sequence-disjoint independent testing, statistical significance, universal causality, or optimal dropout.",
            "",
            "## Evidence paths",
            "",
            "- `runs/v50_visdrone_seen/dataset_audit.md`",
            "- `runs/v50_visdrone_seen/source_lock_v50.md`",
            "- `runs/v50_visdrone_seen/zero_shot_summary.md`",
            "- `runs/v50_visdrone_seen/rgb_summary.json`",
            "- `runs/v50_visdrone_seen/protocol_violation_evidence.json`",
            "- `runs/v50_visdrone_seen/claim_boundary.md`",
            "",
        ]
    )
    return "\n".join(lines)


def blocker_markdown(data):
    state = data["execution"].get("state", "NOT_STARTED")
    violation = data.get("protocol_violation", {})
    if violation:
        status = violation.get("status", "V50_PROTOCOL_VIOLATION")
        body = (
            "The frozen V50 source lock required all three RGB checkpoints to be frozen before test access. "
            "All six zero-shot test evaluations were generated before RGB training began. The RGB queue was "
            "stopped during seed 0 epoch 1, and the test metrics are quarantined as protocol-violation evidence. "
            "See runs/v50_visdrone_seen/protocol_violation_evidence.json."
        )
    elif state == "COMPLETE":
        status = "V50_NONE"
        body = (
            "V50 has no remaining dataset, annotation, split, GPU, evaluation, or training blocker. "
            "The prior V49 Springer/BibTeX compile and rendered-page inspection remains a separate "
            "manuscript-closure item and was not changed by V50."
        )
    else:
        status = "V50_RGB_QUEUE_RUNNING"
        body = (
            "The V50 audit and six-checkpoint RGB-only stress evaluation are complete. The three-seed "
            "50-epoch pure-RGB queue is still running under the frozen source lock; this is an active "
            "execution state, not a failed task."
        )
    return (
        "# Task Blocker\n\n"
        f"Status: `{status}`\n\n"
        f"Generated: {data['generated_at']}\n\n"
        + body
        + "\n"
    )


def write_v50_handoff(project_root):
    root = Path(project_root)
    data = build_v50_data(root)
    (root / "runs/handoff_latest.json").write_text(
        json.dumps(data, indent=2) + "\n", encoding="utf-8"
    )
    (root / "runs/handoff_latest.md").write_text(handoff_markdown(data), encoding="utf-8")
    return data


def write_v50_status(project_root):
    root = Path(project_root)
    data = build_v50_data(root)
    (root / "docs/EXPERIMENT_STATUS.md").write_text(status_markdown(data), encoding="utf-8")
    return data


def write_v50_blocker(project_root):
    root = Path(project_root)
    data = build_v50_data(root)
    (root / "docs/TASK_BLOCKER.md").write_text(blocker_markdown(data), encoding="utf-8")
    return data
