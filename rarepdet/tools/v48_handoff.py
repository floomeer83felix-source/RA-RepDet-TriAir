"""V48-specific handoff and status rendering used by the task finalizer."""

from datetime import datetime
import json
from pathlib import Path


def is_v48_ready(project_root):
    root = Path(project_root)
    task = root / "docs" / "NEXT_TASK.md"
    output = root / "runs" / "v48_complete_ablation"
    return task.is_file() and "V48 complete three-seed causal ablations" in task.read_text(encoding="utf-8") and (output / "source_lock_v48.json").is_file() and (output / "causal_ablation_summary.json").is_file()


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_v48_data(project_root):
    root = Path(project_root)
    output = root / "runs" / "v48_complete_ablation"
    summary = load_json(output / "causal_ablation_summary.json")
    source_lock = load_json(output / "source_lock_v48.json")
    run_status = load_json(output / "run_status.json")
    efficiency_path = output / "efficiency_summary.json"
    efficiency = load_json(efficiency_path) if efficiency_path.is_file() else None
    return {
        "project_name": "RA-RepDet-TriAir",
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "current_task": {
            "title": "V48 complete three-seed causal ablations, static fusion controls, and efficiency profiling",
            "status": summary["status"],
            "commit_message": "eval: complete V48 causal ablations and efficiency profiling",
        },
        "source_lock": {"path": "runs/v48_complete_ablation/source_lock_v48.json", "git_commit": source_lock["git_commit"]},
        "execution": run_status,
        "efficiency": efficiency,
        "v46_preserved": (root / "runs" / "v46_coco_ablation" / "coco_metric_summary.json").is_file(),
        "v47_preserved": (root / "runs" / "v47_structure_literature" / "V47_COMPILE_AND_CITATION_CLOSURE.md").is_file(),
    }


def handoff_markdown(data):
    execution = data["execution"]
    lines = [
        "# RA-RepDet-TriAir Handoff",
        "",
        f"Generated: {data['generated_at']}",
        "",
        "## Current task",
        "",
        f"- Title: {data['current_task']['title']}",
        f"- Status: `{data['current_task']['status']}`",
        f"- Source lock: `{data['source_lock']['path']}` at `{data['source_lock']['git_commit']}`.",
        f"- Fresh runs complete: `{execution['completed_fresh_runs']}/{execution['required_fresh_runs']}`.",
        "- Checkpoint selection: development-validation project-local AP50 only.",
        "- Locked holdout: not accessed by V48 variants.",
        "",
        "## Run state",
        "",
    ]
    for record in execution["runs"]:
        lines.append(f"- `{record['run_id']}`: `{record.get('state', 'PENDING')}`.")
    lines.extend(
        [
            "",
            "## Preserved evidence",
            "",
            f"- V46 COCO and seed0 ablation package preserved: `{data['v46_preserved']}`.",
            f"- V47 manuscript/compile package preserved: `{data['v47_preserved']}`.",
            "- V48 uses development-validation evidence only; causal language remains bounded by completed shared seeds and static-control design.",
            "",
            "## Next actions",
            "",
            "- Continue only the pending source-locked V48 queue entries.",
            "- Regenerate summary, claim scan, preflight, and efficiency artifacts after each completed seed block.",
            "- Do not read or generate a V48 locked-holdout artifact.",
            "",
        ]
    )
    return "\n".join(lines)


def status_markdown(data):
    execution = data["execution"]
    lines = [
        "# Experiment Status",
        "",
        f"Updated: {data['generated_at']}",
        "",
        "## Active task",
        "",
        f"`{data['current_task']['status']}`",
        "",
        "V48 implements source-locked static fusion controls and completes the V46 replication queue under the frozen V40 component-disjoint development-validation protocol. The locked holdout remains prohibited for V48 training, selection, continuation, evaluation, and reporting.",
        "",
        "## Completion",
        "",
        f"- Fresh V48 runs: `{execution['completed_fresh_runs']}/{execution['required_fresh_runs']}` complete.",
        "- Inherited matched-early and full reliability-aware fixed checkpoints: three source-locked seeds each.",
        "- V46 seed0 `ra_no_moddrop` and `early_moddrop`: preserved immutable inputs.",
        "- V47 manuscript package: preserved and not edited by V48.",
        "",
        "## Evidence paths",
        "",
        "- `runs/v48_complete_ablation/source_lock_v48.md`",
        "- `runs/v48_complete_ablation/causal_ablation_summary.md`",
        "- `runs/v48_complete_ablation/efficiency_summary.md`",
        "- `runs/v48_complete_ablation/claim_boundary.md`",
        "",
        "## Fresh run state",
        "",
    ]
    lines.extend(f"- `{record['run_id']}`: `{record.get('state', 'PENDING')}`." for record in execution["runs"])
    lines.append("")
    return "\n".join(lines)


def write_v48_handoff(project_root):
    root = Path(project_root)
    data = build_v48_data(root)
    (root / "runs" / "handoff_latest.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    (root / "runs" / "handoff_latest.md").write_text(handoff_markdown(data), encoding="utf-8")
    return data


def write_v48_status(project_root):
    root = Path(project_root)
    data = build_v48_data(root)
    (root / "docs" / "EXPERIMENT_STATUS.md").write_text(status_markdown(data), encoding="utf-8")
    return data
