#!/usr/bin/env python
"""Write the explicit V46 partial-completion blocker report."""

from datetime import datetime
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "runs" / "v46_coco_ablation"
BLOCKER_PATH = PROJECT_ROOT / "docs" / "TASK_BLOCKER.md"


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def hours(seconds):
    return float(seconds) / 3600.0


def pending_command(model, dropout, seed, run_id):
    python = r"C:\Users\xinnan\.conda\envs\pytorch\python.exe"
    return (
        f"{python} rarepdet/train_early_fusion.py --model {model} --data D:\\download\\triair "
        "--train-split reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_train.txt "
        "--val-split reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt "
        f"--epochs 50 --batch-size 4 --img-size 640 --device cuda --lr 1e-4 --num-workers 0 --modality-dropout {dropout:.2f} --seed {seed} "
        f"--out runs/v46_coco_ablation/local_training/{run_id}"
    )


def error_tail():
    lines = []
    for name in ("ablation_runner_stderr.log", "early_moddrop_parallel_stderr.log"):
        path = OUTPUT_DIR / name
        if path.is_file():
            content = path.read_text(encoding="utf-8", errors="replace").splitlines()
            lines.extend(f"[{name}] {line}" for line in content[-50:])
    return lines[-50:]


def main():
    execution = load_json(OUTPUT_DIR / "ablation_execution_status.json")
    summary = load_json(OUTPUT_DIR / "ablation_devval_summary.json")
    if execution["status"] != "SEED0_FEASIBLE_ABLATIONS_COMPLETE":
        raise RuntimeError("cannot write partial-completion blocker before seed0 runs complete")

    fresh = {
        record["run_id"]: record
        for record in summary["per_run"]
        if record["evidence_source"] == "V46 fresh seed0 training"
    }
    ra_hours = hours(fresh["ra_no_moddrop_seed0"]["training_elapsed_seconds"])
    early_hours = hours(fresh["early_moddrop_seed0"]["training_elapsed_seconds"])
    errors = error_tail()
    error_block = "\n".join(errors) if errors else "No error lines. Both feasible seed0 runs and evaluations completed successfully."

    pending_commands = [
        pending_command("reliability", 0.00, 1, "ra_no_moddrop_seed1"),
        pending_command("reliability", 0.00, 2, "ra_no_moddrop_seed2"),
        pending_command("early", 0.15, 1, "early_moddrop_seed1"),
        pending_command("early", 0.15, 2, "early_moddrop_seed2"),
    ]
    lines = [
        "# Task Blocker",
        "",
        "Status: `V46_PARTIAL_COMPLETION_GPU_TIME_AND_ALLOWED_SCOPE_BLOCKER`",
        "",
        f"Generated: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        "",
        "This is an accepted V46 partial-completion state, not a fabricated full completion. The fixed-checkpoint COCO package is complete, and the two feasible fresh seed0 ablations are complete. Remaining seed replication and architecture-changing controls are blocked as described below.",
        "",
        "## Completed before the blocker",
        "",
        "- Six fixed matched-early / reliability-aware `p=0.15` checkpoints were evaluated on both frozen development-validation and locked same-dataset guard manifests with canonical COCO-style AP.",
        "- Fresh `ra_no_moddrop_seed0` completed 50 epochs, dev-val AP50 checkpoint selection, and COCO-style dev-val evaluation.",
        "- Fresh `early_moddrop_seed0` completed 50 epochs, dev-val AP50 checkpoint selection, and COCO-style dev-val evaluation.",
        f"- Measured training runtime: `ra_no_moddrop_seed0={ra_hours:.3f} h`; `early_moddrop_seed0={early_hours:.3f} h`.",
        "- No ablation guard evaluation was run.",
        "",
        "## Blocker 1: remaining fresh seeds",
        "",
        "Seeds 1 and 2 remain unrun for `ra_no_moddrop` and `early_moddrop`. Based on the measured seed0 runtime, four additional 50-epoch jobs require substantial additional GPU time. `docs/NEXT_TASK.md` explicitly authorizes seed0-first partial completion when GPU/time is insufficient.",
        "",
        "Exact pending training commands:",
        "",
    ]
    for command in pending_commands:
        lines.extend(["```powershell", command, "```", ""])
    lines.extend(
        [
            "Minimal action needed: explicitly authorize another long GPU window, then run the four commands one seed pair at a time and evaluate only on development-validation before considering any optional guard check.",
            "",
            "## Blocker 2: static fusion controls",
            "",
            "`ra_static_equal` and `ra_stems_concat_or_project` require a new model architecture and checkpoint-loading path. The V46 allowed-file list permits reporting/evaluation scripts, metric helpers, and configs, but it does not permit edits to the protected training/model core required to add these variants. Implementing them inside a reporting script would be risky architecture duplication.",
            "",
            "Minimal action needed: explicitly expand the allowed file scope to a dedicated ablation model module plus training/evaluation plumbing, then source-lock that implementation before training.",
            "",
            "## Attempted alternatives",
            "",
            "1. Searched local run configs for checkpoints trained with the exact frozen V40 manifests and matching `reliability p=0.00` or `early p=0.15` settings; none existed, so incompatible older E-run checkpoints were not reused.",
            "2. Assessed static-equal and deterministic-projection implementation against the protected/allowed file lists; both require architecture plumbing outside the authorized scope and were skipped rather than producing unreviewable duplicate model code.",
            "3. Ran the two feasible seed0 jobs concurrently after verifying aggregate GPU memory headroom; each retained an independent process, deterministic seed state, output directory, and development-validation selection rule.",
            "",
            "## Last 50 error lines",
            "",
            "```text",
            error_block,
            "```",
            "",
            "## Related files",
            "",
            "- `runs/v46_coco_ablation/ablation_train_commands.txt`",
            "- `runs/v46_coco_ablation/ablation_execution_status.json`",
            "- `runs/v46_coco_ablation/ablation_devval_per_run.csv`",
            "- `runs/v46_coco_ablation/ablation_devval_summary.md/json`",
            "- `runs/v46_coco_ablation/ablation_claim_boundary.md`",
            "- `rarepdet/train_early_fusion.py` (executed, not modified)",
            "- `rarepdet/models/repvit_fpn_backbone.py` (source-locked, not modified)",
            "- `rarepdet/models/early_fusion_fcos.py` (source-locked, not modified)",
            "",
            "## Repair options",
            "",
            "1. GPU-replication option: retain the current architecture scope and run only the four pending seed1/2 jobs, then regenerate the descriptive summaries.",
            "2. Architecture-expansion option: authorize a dedicated V47-style ablation architecture module for static-equal and deterministic-projection controls, source-lock it, and run seed0 first before any further seeds.",
            "",
        ]
    )
    BLOCKER_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"saved: {BLOCKER_PATH}")


if __name__ == "__main__":
    main()
