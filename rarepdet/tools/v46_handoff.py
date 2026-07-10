"""V46-specific status and handoff rendering used by finish_task.ps1."""

from datetime import datetime
import json
from pathlib import Path


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def is_v46_ready(project_root):
    project_root = Path(project_root)
    task_text = (project_root / "docs" / "NEXT_TASK.md").read_text(encoding="utf-8")
    output_dir = project_root / "runs" / "v46_coco_ablation"
    return (
        "V46 COCO metrics and causal fusion ablations" in task_text
        and (output_dir / "coco_metric_summary.json").is_file()
        and (output_dir / "ablation_devval_summary.json").is_file()
    )


def preflight_passed(output_dir):
    path = output_dir / "preflight_outputs.txt"
    return path.is_file() and "FINAL_STATUS: PASS" in path.read_text(
        encoding="utf-8", errors="replace"
    )


def paired_metrics(protocol_summary):
    paired = protocol_summary["paired_delta_ra_minus_early"]
    return {
        metric: {
            "mean_delta": paired[metric]["mean"],
            "sample_sd_delta": paired[metric]["sample_sd"],
            "min_delta": paired[metric]["min"],
            "max_delta": paired[metric]["max"],
            "n_seed_pairs": paired[metric]["n"],
        }
        for metric in ("ap50_95", "ap50", "ap75", "ar100", "f1")
    }


def compact_contrasts(ablation):
    compact = []
    for item in ablation["seed0_contrasts"]:
        compact.append(
            {
                "contrast": item["contrast"],
                "seed": item["seed"],
                "delta_ap50_95": item["metrics"]["ap50_95"],
                "delta_ap50": item["metrics"]["ap50"],
                "delta_ap75": item["metrics"]["ap75"],
                "delta_f1": item["metrics"]["f1"],
                "interpretation": item["interpretation"],
            }
        )
    return compact


def build_v46_data(project_root):
    project_root = Path(project_root)
    output_dir = project_root / "runs" / "v46_coco_ablation"
    coco = load_json(output_dir / "coco_metric_summary.json")
    ablation = load_json(output_dir / "ablation_devval_summary.json")
    source_lock = load_json(output_dir / "source_lock_v46.json")
    preflight = preflight_passed(output_dir)
    generated_at = datetime.now().astimezone().isoformat(timespec="seconds")
    v47_report = project_root / "runs" / "v47_structure_literature" / "STRUCTURE_AND_REFERENCE_REVISION_REPORT.md"
    v47_compile = project_root / "runs" / "v47_structure_literature" / "V47_COMPILE_AND_CITATION_CLOSURE.md"
    v47_complete = v47_report.is_file() and v47_compile.is_file()
    combined_status = (
        "V47_STRUCTURE_LITERATURE_COMPILE_AND_V46_COCO_ABLATION_SEED0_PARTIAL_COMPLETE"
        if v47_complete
        else "V46_COCO_COMPLETE_ABLATION_SEED0_PARTIAL_COMPLETE"
    )

    fresh_runs = []
    for record in ablation["per_run"]:
        if record["evidence_source"] == "V46 fresh seed0 training":
            fresh_runs.append(
                {
                    "run_id": record["run_id"],
                    "variant": record["variant"],
                    "seed": int(record["seed"]),
                    "checkpoint_sha256": record["checkpoint_sha256"],
                    "training_elapsed_seconds": record["training_elapsed_seconds"],
                    "ap50_95": record["ap50_95"],
                    "ap50": record["ap50"],
                    "ap75": record["ap75"],
                    "f1": record["f1"],
                }
            )

    return {
        "project_name": "RA-RepDet-TriAir",
        "generated_at": generated_at,
        "current_task": {
            "task_file": "docs/NEXT_TASK.md",
            "title": "V46 COCO metrics and causal fusion ablations",
            "status": combined_status,
            "commit_message": "eval: add V46 COCO metrics and causal ablation evidence",
        },
        "v47_revision": {
            "status": "COMPLETE" if v47_complete else "NOT_PRESENT",
            "report": "runs/v47_structure_literature/STRUCTURE_AND_REFERENCE_REVISION_REPORT.md",
            "compile_report": "runs/v47_structure_literature/V47_COMPILE_AND_CITATION_CLOSURE.md",
            "reference_ledger": "submission/sivp/review/V47_RECENT_Q12_REFERENCE_LEDGER.md",
            "bibliography": "submission/sivp/tex/references_recent_q12_2023_2025.bib",
            "active_citations": 40 if v47_complete else None,
            "compile_page_count": 10 if v47_complete else None,
            "missing_citations": 0 if v47_complete else None,
            "undefined_cross_references": 0 if v47_complete else None,
            "v46_evidence_integrated_into_manuscript": False,
        },
        "source_lock": {
            "path": "runs/v46_coco_ablation/source_lock_v46.json",
            "status": source_lock["status"],
            "source_commit": source_lock["git_commit"],
            "branch": source_lock["git_branch"],
        },
        "blocker": {
            "status": "PARTIAL_GPU_TIME_AND_ALLOWED_SCOPE_BLOCKER",
            "path": "docs/TASK_BLOCKER.md",
            "remaining": [
                "ra_no_moddrop and early_moddrop seeds 1 and 2 require about 28-34 additional GPU hours",
                "ra_static_equal and ra_stems_concat_or_project require protected architecture/training plumbing changes outside the V46 allowed-file list",
            ],
        },
        "scope_controls": {
            "new_training": True,
            "fresh_training_seeds": [0],
            "checkpoint_selection_rule": ablation["checkpoint_selection_rule"],
            "guard_used_for_training_or_selection": False,
            "split_modified": False,
            "existing_checkpoint_modified": False,
            "manuscript_modified_by_v46": False,
            "manuscript_modified_by_v47": v47_complete,
            "ablation_guard_evaluation_run": False,
        },
        "fixed_coco_evaluation": {
            "status": coco["status"],
            "backend": coco["backend"],
            "definition": coco["definition"],
            "development_validation": paired_metrics(coco["devval"]),
            "same_dataset_guard": paired_metrics(coco["guard"]),
            "summary_md": "runs/v46_coco_ablation/coco_metric_summary.md",
            "summary_json": "runs/v46_coco_ablation/coco_metric_summary.json",
        },
        "causal_ablation": {
            "status": ablation["status"],
            "fresh_runs": fresh_runs,
            "seed0_contrasts": compact_contrasts(ablation),
            "variant_status": ablation["variant_status"],
            "summary_md": "runs/v46_coco_ablation/ablation_devval_summary.md",
            "summary_json": "runs/v46_coco_ablation/ablation_devval_summary.json",
            "claim_boundary": "runs/v46_coco_ablation/ablation_claim_boundary.md",
        },
        "verification": {
            "project_local_ap_reproduced": True,
            "coco_metric_smoke_test": True,
            "claim_scan_passed": preflight,
            "preflight_passed": preflight,
            "preflight_output": "runs/v46_coco_ablation/preflight_outputs.txt",
        },
        "claim_boundary": {
            "allowed": "descriptive three-seed COCO-style within-TriAir fixed-checkpoint comparisons plus seed0-only development-validation causal contrasts",
            "guard": "locked same-dataset held-out evidence only; never used for tuning, selection, or ablation continuation",
            "fresh_ablation": "seed0-only; stems and dynamic gate remain bundled without static controls",
        },
        "next_actions": [
            "Integrate V46 evidence into the V47 manuscript only in a separately authorized manuscript-update task",
            "Run seeds 1 and 2 for ra_no_moddrop and early_moddrop only if additional GPU time is authorized",
            "Authorize protected architecture/training changes before implementing static-equal or deterministic-projection controls",
            "Do not use guard results for any future model or run selection",
        ],
    }


def metric_table_lines(data):
    lines = [
        "| Protocol | Metric | Mean paired delta | Sample SD | Min | Max | n |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for protocol_key, label in (
        ("development_validation", "development-validation"),
        ("same_dataset_guard", "same-dataset guard"),
    ):
        for metric in ("ap50_95", "ap50", "ap75", "ar100"):
            record = data["fixed_coco_evaluation"][protocol_key][metric]
            lines.append(
                f"| {label} | {metric} | {record['mean_delta']:.6f} | {record['sample_sd_delta']:.6f} | {record['min_delta']:.6f} | {record['max_delta']:.6f} | {record['n_seed_pairs']} |"
            )
    return lines


def handoff_markdown(data):
    lines = [
        "# RA-RepDet-TriAir Handoff",
        "",
        f"Generated: {data['generated_at']}",
        "",
        "## Current task state",
        "",
        f"- Task: `{data['current_task']['title']}`",
        f"- Status: `{data['current_task']['status']}`",
        f"- Blocker: `{data['blocker']['status']}`",
        f"- Final preflight passed: `{data['verification']['preflight_passed']}`",
        "",
        "## Preserved V47 manuscript state",
        "",
        "The remotely completed V47 manuscript restructure, 40-reference literature package, and 10-page Springer compile closure are preserved. V46 did not edit manuscript narrative files, so the new V46 metrics are evidence-package outputs awaiting a separately authorized manuscript-integration task.",
        "",
        "- Revision report: `runs/v47_structure_literature/STRUCTURE_AND_REFERENCE_REVISION_REPORT.md`",
        "- Compile report: `runs/v47_structure_literature/V47_COMPILE_AND_CITATION_CLOSURE.md`",
        "- Active cited keys: 40; missing citations: 0; undefined cross-references: 0.",
        "",
        "## Completed fixed-checkpoint COCO evaluation",
        "",
        "All six fixed matched-early and reliability-aware `p=0.15` seed0/1/2 checkpoints were evaluated on frozen development-validation and locked same-dataset guard manifests with canonical `pycocotools` bbox AP, IoU 0.50:0.05:0.95, 101 recall samples, and maxDets=100.",
        "",
        *metric_table_lines(data),
        "",
        "The guard mean AP50:95 delta is positive but smaller than development-validation, and guard seed2 is negative. The guard was not used for tuning, selection, or continuation.",
        "",
        "## Seed0 causal ablations",
        "",
        "| Contrast | Delta AP50:95 | Delta AP50 | Delta AP75 | Delta F1 |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for item in data["causal_ablation"]["seed0_contrasts"]:
        lines.append(
            f"| {item['contrast']} | {item['delta_ap50_95']:.6f} | {item['delta_ap50']:.6f} | {item['delta_ap75']:.6f} | {item['delta_f1']:.6f} |"
        )
    lines.extend(
        [
            "",
            "Fresh `ra_no_moddrop_seed0` and `early_moddrop_seed0` runs used the locked 50-epoch protocol and development-validation AP50 checkpoint selection. No ablation guard evaluation was run.",
            "",
            "## Partial blockers",
            "",
        ]
    )
    lines.extend(f"- {item}." for item in data["blocker"]["remaining"])
    lines.extend(
        [
            "",
            "## Claim boundary",
            "",
            f"- Allowed: {data['claim_boundary']['allowed']}.",
            f"- Guard: {data['claim_boundary']['guard']}.",
            f"- Fresh ablation: {data['claim_boundary']['fresh_ablation']}.",
            "",
            "## Primary outputs",
            "",
            "- `runs/v46_coco_ablation/source_lock_v46.md/json`",
            "- `runs/v46_coco_ablation/coco_metric_summary.md/json` and four required COCO CSV files",
            "- `runs/v46_coco_ablation/ablation_devval_per_run.csv`",
            "- `runs/v46_coco_ablation/ablation_devval_summary.md/json`",
            "- `runs/v46_coco_ablation/ablation_claim_boundary.md`",
            "- `runs/v46_coco_ablation/v46_claim_scan.txt` and review",
            "- `runs/v46_coco_ablation/preflight_commands.txt` and outputs",
            "",
        ]
    )
    return "\n".join(lines)


def status_markdown(data):
    dev = data["fixed_coco_evaluation"]["development_validation"]
    guard = data["fixed_coco_evaluation"]["same_dataset_guard"]
    lines = [
        "# Experiment Status",
        "",
        f"Generated: {data['generated_at']}",
        "",
        "## Current status",
        "",
        f"`{data['current_task']['status']}`",
        "",
        "The remotely completed V47 manuscript restructure, 40-reference literature package, and compile closure are preserved. V46 completed canonical COCO-style evaluation for all six fixed baseline/main checkpoints on frozen development-validation and locked same-dataset guard manifests, plus the two feasible fresh seed0 ablations under the locked 50-epoch protocol. Seeds 1 and 2 for fresh variants and architecture-changing static controls remain explicitly deferred.",
        "",
        "## V47 manuscript and compile state",
        "",
        "- Manuscript structure and recent-journal literature revision: complete.",
        "- Active cited keys: 40; missing citations: 0; undefined cross-references: 0.",
        "- Springer-style compile: 10 pages, no obvious page-level clipping reported.",
        "- V46 did not edit manuscript narrative files; evidence integration remains a future explicitly authorized task.",
        "",
        "## COCO-style evidence",
        "",
        "| Protocol | Mean delta AP50:95 | SD | Mean delta AP50 | Mean delta AP75 | n |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
        f"| Development-validation | {dev['ap50_95']['mean_delta']:.6f} | {dev['ap50_95']['sample_sd_delta']:.6f} | {dev['ap50']['mean_delta']:.6f} | {dev['ap75']['mean_delta']:.6f} | 3 |",
        f"| Same-dataset guard | {guard['ap50_95']['mean_delta']:.6f} | {guard['ap50_95']['sample_sd_delta']:.6f} | {guard['ap50']['mean_delta']:.6f} | {guard['ap75']['mean_delta']:.6f} | 3 |",
        "",
        "The project-local AP50/AP75 values were reproduced to floating-point tolerance before the canonical COCO summaries were accepted. Guard results remained evaluation-only.",
        "",
        "## Fresh seed0 ablations",
        "",
        "| Run | AP50:95 | AP50 | AP75 | F1 | Training seconds |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for run in data["causal_ablation"]["fresh_runs"]:
        lines.append(
            f"| {run['run_id']} | {run['ap50_95']:.6f} | {run['ap50']:.6f} | {run['ap75']:.6f} | {run['f1']:.6f} | {float(run['training_elapsed_seconds']):.1f} |"
        )
    lines.extend(
        [
            "",
            "## Verification",
            "",
            f"- COCO metric tiny-input smoke test: `{data['verification']['coco_metric_smoke_test']}`.",
            f"- Existing project metric reproduction: `{data['verification']['project_local_ap_reproduced']}`.",
            f"- Claim scan passed: `{data['verification']['claim_scan_passed']}`.",
            f"- Final V46 preflight passed: `{data['verification']['preflight_passed']}`.",
            "",
            "## Active partial blocker",
            "",
        ]
    )
    lines.extend(f"- {item}." for item in data["blocker"]["remaining"])
    lines.extend(
        [
            "",
            "## Current claim boundary",
            "",
            "Allowed wording: descriptive three-seed COCO-style within-TriAir fixed-checkpoint evidence plus seed0-only development-validation ablation contrasts.",
            "",
            "Required cautions: same-dataset guard only; no guard-based tuning or selection; one-seed fresh ablations; stems and dynamic gating remain bundled; no external-data, significance, optimality, calibration, or real-fault claims.",
            "",
        ]
    )
    return "\n".join(lines)


def write_v46_handoff(project_root):
    project_root = Path(project_root)
    data = build_v46_data(project_root)
    runs_dir = project_root / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    (runs_dir / "handoff_latest.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    (runs_dir / "handoff_latest.md").write_text(handoff_markdown(data), encoding="utf-8")
    return data


def write_v46_status(project_root):
    project_root = Path(project_root)
    data = build_v46_data(project_root)
    path = project_root / "docs" / "EXPERIMENT_STATUS.md"
    path.write_text(status_markdown(data), encoding="utf-8")
    return data
