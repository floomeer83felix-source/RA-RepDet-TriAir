#!/usr/bin/env python
"""Generate a lightweight handoff report for the RA-RepDet TriAir workspace."""

import csv
import json
import subprocess
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = PROJECT_ROOT / "runs"
DOCS_DIR = PROJECT_ROOT / "docs"
NEXT_TASK_PATH = DOCS_DIR / "NEXT_TASK.md"

PUBLICATION_HEADLINE = {
    "model": "R4 Reliability p=0.20",
    "protocol": "block64_guard16_seed0",
    "seeds": ["0", "2"],
    "decision": "SELECT R4 AS CLEAN-SPLIT MAIN VARIANT",
    "means": {
        "F1@0.50": "0.920861",
        "AP50": "0.962495",
        "AP75": "0.891266",
        "w/o RGB AP50": "0.916051",
        "w/o Thermal AP50": "0.718277",
        "w/o Event AP50": "0.961577",
    },
    "scope": "official clean blocked-split manuscript headline",
    "legacy_note": "Former E0-E6 random-split results are historical/exploratory diagnostics only.",
}

PHASE7B_LEDGER_MD = PROJECT_ROOT / "submission" / "sivp" / "metadata" / "FINAL_SUBMISSION_INPUT_LEDGER.md"
PHASE7B_LEDGER_CSV = PROJECT_ROOT / "submission" / "sivp" / "review" / "FINAL_SUBMISSION_INPUT_LEDGER.csv"
PHASE7B_REPORT_MD = RUNS_DIR / "phase7b_publication_state_reconciliation.md"
PHASE7B_REPORT_JSON = RUNS_DIR / "phase7b_publication_state_reconciliation.json"
PHASE7C_REPORT_MD = RUNS_DIR / "phase7c_table_insertion_report.md"
PHASE7C_REPORT_JSON = RUNS_DIR / "phase7c_table_insertion_report.json"
PHASE7C_RENDER_CHECK_MD = PROJECT_ROOT / "submission" / "sivp" / "review" / "TABLE_RENDERING_CHECK.md"
PHASE7C_TRACEABILITY_MD = PROJECT_ROOT / "submission" / "sivp" / "tables" / "TABLE_SOURCE_TRACEABILITY.md"
PHASE7D_REPORT_MD = RUNS_DIR / "phase7d_figure_source_lock_report.md"
PHASE7D_REPORT_JSON = RUNS_DIR / "phase7d_figure_source_lock_report.json"
PHASE7D_TRACEABILITY_MD = PROJECT_ROOT / "submission" / "sivp" / "figures" / "FIGURE_SOURCE_TRACEABILITY.md"
PHASE7D_TRACEABILITY_CSV = PROJECT_ROOT / "submission" / "sivp" / "figures" / "FIGURE_SOURCE_TRACEABILITY.csv"
PHASE7D_BUILD_SPEC_MD = PROJECT_ROOT / "submission" / "sivp" / "figures" / "FIGURE_BUILD_SPEC.md"
PHASE7D_REVIEW_CHECK_MD = PROJECT_ROOT / "submission" / "sivp" / "review" / "FIGURE_CANDIDATE_CHECK.md"
PHASE7D_REVIEW_CHECK_CSV = PROJECT_ROOT / "submission" / "sivp" / "review" / "FIGURE_CANDIDATE_CHECK.csv"
PHASE7E_REPORT_MD = RUNS_DIR / "phase7e_candidate_render_report.md"
PHASE7E_REPORT_JSON = RUNS_DIR / "phase7e_candidate_render_report.json"
PHASE7E_MANIFEST_MD = PROJECT_ROOT / "submission" / "sivp" / "figures" / "FIGURE_CANDIDATE_RENDER_MANIFEST.md"
PHASE7E_MANIFEST_CSV = PROJECT_ROOT / "submission" / "sivp" / "figures" / "FIGURE_CANDIDATE_RENDER_MANIFEST.csv"
PHASE7E_RENDER_CHECK_MD = PROJECT_ROOT / "submission" / "sivp" / "review" / "FIGURE_CANDIDATE_RENDER_CHECK.md"
PHASE7E_RENDER_CHECK_CSV = PROJECT_ROOT / "submission" / "sivp" / "review" / "FIGURE_CANDIDATE_RENDER_CHECK.csv"
PHASE7F_REPORT_MD = RUNS_DIR / "phase7f_author_review_intake_report.md"
PHASE7F_REPORT_JSON = RUNS_DIR / "phase7f_author_review_intake_report.json"
PHASE7F_PACKET_MD = PROJECT_ROOT / "submission" / "sivp" / "review" / "AUTHOR_FIGURE_REVIEW_PACKET.md"
PHASE7F_DECISIONS_CSV = PROJECT_ROOT / "submission" / "sivp" / "review" / "AUTHOR_FIGURE_REVIEW_DECISIONS.csv"
PHASE7F_PANEL_TEMPLATE_MD = PROJECT_ROOT / "submission" / "sivp" / "review" / "FIGURE6_PANEL_REVIEW_TEMPLATE.md"
PHASE7F_PANEL_TEMPLATE_CSV = PROJECT_ROOT / "submission" / "sivp" / "review" / "FIGURE6_PANEL_REVIEW_TEMPLATE.csv"
PHASE7F_PANEL_CHECK_MD = PROJECT_ROOT / "submission" / "sivp" / "review" / "FIGURE6_PANEL_INVENTORY_CHECK.md"
PHASE7F_PANEL_CHECK_CSV = PROJECT_ROOT / "submission" / "sivp" / "review" / "FIGURE6_PANEL_INVENTORY_CHECK.csv"
PHASE7G_REPORT_MD = RUNS_DIR / "phase7g_submission_intake_report.md"
PHASE7G_REPORT_JSON = RUNS_DIR / "phase7g_submission_intake_report.json"
PHASE7G_AUTHOR_PACKET_MD = PROJECT_ROOT / "submission" / "sivp" / "metadata" / "AUTHOR_SUBMISSION_INPUT_PACKET.md"
PHASE7G_AUTHOR_RESPONSES_CSV = PROJECT_ROOT / "submission" / "sivp" / "metadata" / "AUTHOR_SUBMISSION_INPUT_RESPONSES.csv"
PHASE7G_ENV_TEMPLATE_MD = PROJECT_ROOT / "submission" / "sivp" / "metadata" / "ENVIRONMENT_RECORD_TEMPLATE.md"
PHASE7G_ROADMAP_MD = PROJECT_ROOT / "submission" / "sivp" / "metadata" / "SUBMISSION_CLOSURE_ROADMAP.md"
PHASE7G_COMPLETENESS_MD = PROJECT_ROOT / "submission" / "sivp" / "review" / "SUBMISSION_INPUT_COMPLETENESS_CHECK.md"
PHASE7G_COMPLETENESS_CSV = PROJECT_ROOT / "submission" / "sivp" / "review" / "SUBMISSION_INPUT_COMPLETENESS_CHECK.csv"
PHASE7G_STATIC_AUDIT_MD = PROJECT_ROOT / "submission" / "sivp" / "review" / "STATIC_SUBMISSION_SOURCE_AUDIT.md"
PHASE7G_STATIC_AUDIT_CSV = PROJECT_ROOT / "submission" / "sivp" / "review" / "STATIC_SUBMISSION_SOURCE_AUDIT.csv"
PHASE7G_CROSSWALK_MD = PROJECT_ROOT / "submission" / "sivp" / "review" / "FIGURE_TABLE_CROSSWALK.md"
PHASE7G_CROSSWALK_CSV = PROJECT_ROOT / "submission" / "sivp" / "review" / "FIGURE_TABLE_CROSSWALK.csv"
PHASE7G_REPRO_AUDIT_MD = PROJECT_ROOT / "submission" / "sivp" / "review" / "REPRODUCIBILITY_CLOSURE_AUDIT.md"
PHASE7G_REPRO_AUDIT_CSV = PROJECT_ROOT / "submission" / "sivp" / "review" / "REPRODUCIBILITY_CLOSURE_AUDIT.csv"
PHASE7H_REPORT_MD = RUNS_DIR / "phase7h_author_response_validation_report.md"
PHASE7H_REPORT_JSON = RUNS_DIR / "phase7h_author_response_validation_report.json"
PHASE7H_VALIDATOR = PROJECT_ROOT / "submission" / "sivp" / "metadata" / "validate_author_submission_inputs.py"
PHASE7H_VALIDATION_MD = PROJECT_ROOT / "submission" / "sivp" / "metadata" / "AUTHOR_RESPONSE_VALIDATION.md"
PHASE7H_VALIDATION_CSV = PROJECT_ROOT / "submission" / "sivp" / "metadata" / "AUTHOR_RESPONSE_VALIDATION.csv"
PHASE7H_READINESS_MD = PROJECT_ROOT / "submission" / "sivp" / "metadata" / "METADATA_APPLICATION_READINESS_MAP.md"
PHASE7H_READINESS_CSV = PROJECT_ROOT / "submission" / "sivp" / "metadata" / "METADATA_APPLICATION_READINESS_MAP.csv"
PHASE7H_GATE_CHECK_MD = PROJECT_ROOT / "submission" / "sivp" / "review" / "AUTHOR_RESPONSE_GATE_CHECK.md"
PHASE7H_GATE_CHECK_CSV = PROJECT_ROOT / "submission" / "sivp" / "review" / "AUTHOR_RESPONSE_GATE_CHECK.csv"
PHASE7I_REPORT_MD = RUNS_DIR / "phase7i_update_planning_report.md"
PHASE7I_REPORT_JSON = RUNS_DIR / "phase7i_update_planning_report.json"
PHASE7I_PLANNER = PROJECT_ROOT / "submission" / "sivp" / "metadata" / "plan_confirmed_submission_updates.py"
PHASE7I_PLAN_MD = PROJECT_ROOT / "submission" / "sivp" / "metadata" / "CONFIRMED_UPDATE_PLAN.md"
PHASE7I_PLAN_CSV = PROJECT_ROOT / "submission" / "sivp" / "metadata" / "CONFIRMED_UPDATE_PLAN.csv"
PHASE7I_PLAN_JSON = PROJECT_ROOT / "submission" / "sivp" / "metadata" / "CONFIRMED_UPDATE_PLAN.json"
PHASE7I_CHECK_MD = PROJECT_ROOT / "submission" / "sivp" / "review" / "CONFIRMED_UPDATE_PLAN_CHECK.md"
PHASE7I_CHECK_CSV = PROJECT_ROOT / "submission" / "sivp" / "review" / "CONFIRMED_UPDATE_PLAN_CHECK.csv"
V40_REPORT_MD = RUNS_DIR / "phase_v40_component_disjoint_report.md"
V40_REPORT_JSON = RUNS_DIR / "phase_v40_component_disjoint_report.json"
V40_SPLIT_BUILD_SUMMARY = RUNS_DIR / "component_disjoint_v40" / "split_build_summary.csv"
V40_AUDIT_CSV = RUNS_DIR / "v40_component_disjoint" / "split_audit.csv"


EXPERIMENTS = [
    {
        "id": "E0",
        "method": "Early Fusion",
        "dir": RUNS_DIR / "E0_early_repvit_fcos_e50",
    },
    {
        "id": "E1",
        "method": "Reliability Fusion",
        "dir": RUNS_DIR / "E1_reliability_repvit_fcos_e50",
    },
    {
        "id": "E2",
        "method": "Reliability + Dropout 0.15",
        "dir": RUNS_DIR / "E2_reliability_dropout015_repvit_fcos_e50",
    },
    {
        "id": "E3",
        "method": "Reliability + Dropout 0.10",
        "dir": RUNS_DIR / "E3_reliability_dropout010_repvit_fcos_e50",
        "eval_subdir": "eval_thr050",
    },
    {
        "id": "E4",
        "method": "Reliability + Dropout 0.20",
        "dir": RUNS_DIR / "E4_reliability_dropout020_repvit_fcos_e50",
        "eval_subdir": "eval_thr050",
    },
    {
        "id": "E5",
        "method": "ACRF + Dropout 0.15",
        "dir": RUNS_DIR / "E5_acrf_dropout015_repvit_fcos_e50",
        "eval_subdir": "eval_thr050",
    },
    {
        "id": "E6",
        "method": "MSCD + Dropout 0.15",
        "dir": RUNS_DIR / "E6_mscd_dropout015_repvit_fcos_e50",
        "eval_subdir": "eval_thr050",
    },
]


def read_pipe_table(path):
    if not path.exists():
        return []
    rows = []
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        return rows
    headers = [part.strip() for part in lines[0].split("|")]
    for line in lines[2:]:
        values = [part.strip() for part in line.split("|")]
        if len(values) == len(headers):
            rows.append(dict(zip(headers, values)))
    return rows


def read_csv(path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path):
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def read_text(path):
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def parse_sections(path):
    sections = {}
    current = None
    for raw_line in read_text(path).splitlines():
        line = raw_line.strip()
        if line.startswith("#"):
            current = line.lstrip("#").strip()
            sections[current] = []
        elif current:
            sections[current].append(raw_line.rstrip())
    return {key: "\n".join(value).strip() for key, value in sections.items()}


def first_paragraph(text):
    for block in text.split("\n\n"):
        block = block.strip()
        if block:
            return " ".join(line.strip() for line in block.splitlines() if line.strip())
    return "NA"


def collect_current_task():
    sections = parse_sections(NEXT_TASK_PATH)
    title = first_paragraph(sections.get("Title", ""))
    current_task = first_paragraph(sections.get("Current Task", ""))
    if current_task == "NA" and title != "NA":
        current_task = title
    return {
        "task_file": "docs/NEXT_TASK.md",
        "current_task": current_task,
        "goal": first_paragraph(sections.get("Goal", "")),
        "commit_message": first_paragraph(sections.get("Commit Message", "")),
    }


def count_csv_rows(path):
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        next(reader, None)
        return sum(1 for _ in reader)


def read_key_value_file(path):
    if not path.exists():
        return {}
    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def git_lines(args):
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=PROJECT_ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except Exception as exc:
        return [f"git unavailable: {exc}"]
    output = (result.stdout or result.stderr).strip()
    return output.splitlines() if output else []


def collect_eval_results():
    results = []
    for exp in EXPERIMENTS:
        eval_subdir = exp.get("eval_subdir", "eval")
        row = read_key_value_file(exp["dir"] / eval_subdir / "eval_results.txt")
        results.append(
            {
                "id": exp["id"],
                "method": exp["method"],
                "precision": row.get("Precision"),
                "recall": row.get("Recall"),
                "ap50": row.get("AP50"),
                "ap75": row.get("AP75"),
                "gt_boxes": row.get("GT boxes"),
                "predictions": row.get("Predictions"),
                "mean_confidence": row.get("Mean Confidence"),
            }
        )
    return results


def collect_missing_modality():
    summary = read_csv(RUNS_DIR / "missing_modality_summary.csv")
    summary_ap75 = read_csv(RUNS_DIR / "missing_modality_summary_ap75.csv")
    return {"ap50": summary, "ap75": summary_ap75}


def collect_profile():
    return read_csv(RUNS_DIR / "profile_summary.csv")


def collect_phase2a():
    return {
        "main_results": read_csv(RUNS_DIR / "phase2a_main_results.csv"),
        "profile_e0": read_csv(RUNS_DIR / "phase2a_profile_e0" / "profile_results.csv"),
        "profile_e2": read_csv(RUNS_DIR / "phase2a_profile_e2" / "profile_results.csv"),
        "brightness_proxy": read_csv(RUNS_DIR / "phase2a_brightness_proxy" / "brightness_proxy_results.csv"),
        "alpha_modes": read_csv(RUNS_DIR / "phase2a_alpha" / "alpha_mode_summary.csv"),
        "report": str(RUNS_DIR / "phase2a_report.md") if (RUNS_DIR / "phase2a_report.md").exists() else None,
    }


def collect_phase2b():
    return {
        "evidence_summary": read_csv(RUNS_DIR / "acrf_evidence_summary.csv"),
        "evidence_report": str(RUNS_DIR / "acrf_evidence_report.md") if (RUNS_DIR / "acrf_evidence_report.md").exists() else None,
        "smoke_test": str(RUNS_DIR / "acrf_smoke_test.md") if (RUNS_DIR / "acrf_smoke_test.md").exists() else None,
        "e5_missing_modality": read_csv(
            RUNS_DIR / "E5_acrf_dropout015_repvit_fcos_e50" / "missing_modality" / "missing_modality_results.csv"
        ),
        "e5_alpha_modes": read_csv(
            RUNS_DIR / "E5_acrf_dropout015_repvit_fcos_e50" / "alpha_modes" / "alpha_mode_summary.csv"
        ),
    }


def collect_phase2c():
    return {
        "evidence_summary": read_csv(RUNS_DIR / "mscd_evidence_summary.csv"),
        "evidence_report": str(RUNS_DIR / "mscd_evidence_report.md") if (RUNS_DIR / "mscd_evidence_report.md").exists() else None,
        "phase2c_report": str(RUNS_DIR / "phase2c_report.md") if (RUNS_DIR / "phase2c_report.md").exists() else None,
        "smoke_test": str(RUNS_DIR / "mscd_smoke_test.md") if (RUNS_DIR / "mscd_smoke_test.md").exists() else None,
        "e6_missing_modality": read_csv(
            RUNS_DIR / "E6_mscd_dropout015_repvit_fcos_e50" / "missing_modality" / "missing_modality_results.csv"
        ),
    }


def collect_phase3a():
    return {
        "dropout_ablation": read_csv(RUNS_DIR / "dropout_ablation_summary.csv"),
        "dropout_report": str(RUNS_DIR / "dropout_ablation_summary.md") if (RUNS_DIR / "dropout_ablation_summary.md").exists() else None,
        "qualitative_manifest": read_csv(RUNS_DIR / "qualitative_cases_manifest.csv"),
        "qualitative_report": str(RUNS_DIR / "qualitative_cases_summary.md") if (RUNS_DIR / "qualitative_cases_summary.md").exists() else None,
        "phase3a_report": str(RUNS_DIR / "phase3a_report.md") if (RUNS_DIR / "phase3a_report.md").exists() else None,
    }


def collect_phase3b():
    return {
        "split_summary": read_csv(RUNS_DIR / "split_integrity_summary.csv"),
        "nearest_pair_count": count_csv_rows(RUNS_DIR / "split_integrity_nearest_pairs.csv"),
        "manual_review_count": count_csv_rows(RUNS_DIR / "split_integrity_manual_review.csv"),
        "exact_duplicate_count": count_csv_rows(RUNS_DIR / "split_integrity_exact_duplicates.csv"),
        "split_report": str(RUNS_DIR / "split_integrity_summary.md") if (RUNS_DIR / "split_integrity_summary.md").exists() else None,
        "selection_note": str(RUNS_DIR / "dropout_ratio_selection_note.md") if (RUNS_DIR / "dropout_ratio_selection_note.md").exists() else None,
        "phase3b_report": str(RUNS_DIR / "phase3b_report.md") if (RUNS_DIR / "phase3b_report.md").exists() else None,
    }


def collect_phase3c():
    return {
        "rgb_duplicate_summary": read_csv(RUNS_DIR / "rgb_cross_split_duplicate_summary.csv"),
        "rgb_exact_pair_count": count_csv_rows(RUNS_DIR / "rgb_cross_split_exact_pairs.csv"),
        "rgb_group_count": count_csv_rows(RUNS_DIR / "rgb_cross_split_group_stats.csv"),
        "blocked_split_summary": read_csv(RUNS_DIR / "blocked_split_proposal_summary.csv"),
        "strata_summary": read_csv(RUNS_DIR / "rgb_separation_strata_summary.csv"),
        "rgb_duplicate_report": str(RUNS_DIR / "rgb_cross_split_duplicate_summary.md")
        if (RUNS_DIR / "rgb_cross_split_duplicate_summary.md").exists()
        else None,
        "blocked_split_report": str(RUNS_DIR / "blocked_split_proposal_summary.md")
        if (RUNS_DIR / "blocked_split_proposal_summary.md").exists()
        else None,
        "strata_report": str(RUNS_DIR / "rgb_separation_strata_summary.md")
        if (RUNS_DIR / "rgb_separation_strata_summary.md").exists()
        else None,
        "phase3c_report": str(RUNS_DIR / "phase3c_report.md") if (RUNS_DIR / "phase3c_report.md").exists() else None,
    }


def collect_phase4a():
    return {
        "clean_protocol": str(RUNS_DIR / "clean_block64g16_protocol.md")
        if (RUNS_DIR / "clean_block64g16_protocol.md").exists()
        else None,
        "clean_summary": read_csv(RUNS_DIR / "clean_block64g16_summary.csv"),
        "clean_summary_report": str(RUNS_DIR / "clean_block64g16_summary.md")
        if (RUNS_DIR / "clean_block64g16_summary.md").exists()
        else None,
        "phase4a_report": str(RUNS_DIR / "phase4a_report.md") if (RUNS_DIR / "phase4a_report.md").exists() else None,
        "b0_eval": read_key_value_file(RUNS_DIR / "B0_early_block64g16_e50" / "eval_thr050" / "eval_results.txt"),
        "b1_eval": read_key_value_file(RUNS_DIR / "B1_reliability_p000_block64g16_e50" / "eval_thr050" / "eval_results.txt"),
        "b2_eval": read_key_value_file(RUNS_DIR / "B2_reliability_p015_block64g16_e50" / "eval_thr050" / "eval_results.txt"),
        "b4_eval": read_key_value_file(RUNS_DIR / "B4_reliability_p020_block64g16_e50" / "eval_thr050" / "eval_results.txt"),
        "b1_missing": read_csv(RUNS_DIR / "B1_reliability_p000_block64g16_e50" / "missing_modality" / "missing_modality_results.csv"),
        "b2_missing": read_csv(RUNS_DIR / "B2_reliability_p015_block64g16_e50" / "missing_modality" / "missing_modality_results.csv"),
        "b4_missing": read_csv(RUNS_DIR / "B4_reliability_p020_block64g16_e50" / "missing_modality" / "missing_modality_results.csv"),
    }


def collect_phase4b():
    return {
        "smoke_test": str(RUNS_DIR / "seed_reproducibility_smoke.md")
        if (RUNS_DIR / "seed_reproducibility_smoke.md").exists()
        else None,
        "seed_replication": read_csv(RUNS_DIR / "clean_block64g16_seed_replication.csv"),
        "seed_replication_report": str(RUNS_DIR / "clean_block64g16_seed_replication.md")
        if (RUNS_DIR / "clean_block64g16_seed_replication.md").exists()
        else None,
        "phase4b_report": str(RUNS_DIR / "phase4b_report.md") if (RUNS_DIR / "phase4b_report.md").exists() else None,
        "decision": read_last_nonempty_line(RUNS_DIR / "phase4b_report.md"),
        "r1_missing_seed0": read_csv(
            RUNS_DIR / "R1_reliability_p000_seed0_block64g16_e50" / "missing_modality" / "missing_modality_results.csv"
        ),
        "r1_missing_seed2": read_csv(
            RUNS_DIR / "R1_reliability_p000_seed2_block64g16_e50" / "missing_modality" / "missing_modality_results.csv"
        ),
        "r2_missing_seed0": read_csv(
            RUNS_DIR / "R2_reliability_p015_seed0_block64g16_e50" / "missing_modality" / "missing_modality_results.csv"
        ),
        "r2_missing_seed2": read_csv(
            RUNS_DIR / "R2_reliability_p015_seed2_block64g16_e50" / "missing_modality" / "missing_modality_results.csv"
        ),
        "r4_missing_seed0": read_csv(
            RUNS_DIR / "R4_reliability_p020_seed0_block64g16_e50" / "missing_modality" / "missing_modality_results.csv"
        ),
        "r4_missing_seed2": read_csv(
            RUNS_DIR / "R4_reliability_p020_seed2_block64g16_e50" / "missing_modality" / "missing_modality_results.csv"
        ),
    }


def collect_phase5a():
    return {
        "phase5a_report": str(RUNS_DIR / "phase5a_report.md") if (RUNS_DIR / "phase5a_report.md").exists() else None,
        "decision": read_last_nonempty_line(RUNS_DIR / "phase5a_report.md"),
        "paper_readiness": read_csv(RUNS_DIR / "paper_readiness_summary.csv"),
        "convergence": read_csv(RUNS_DIR / "clean_block64g16_convergence.csv"),
        "efficiency": read_csv(RUNS_DIR / "clean_efficiency_profile.csv"),
        "r4_reliability": read_csv(RUNS_DIR / "r4_reliability_weight_audit.csv"),
        "qualitative": read_csv(RUNS_DIR / "clean_qualitative_manifest.csv"),
        "yolo_seed0": read_csv(RUNS_DIR / "Y11n_rgb_seed0_block64g16_e50" / "eval_project" / "eval_results.csv"),
        "yolo_seed2": read_csv(RUNS_DIR / "Y11n_rgb_seed2_block64g16_e50" / "eval_project" / "eval_results.csv"),
        "yolo_protocol": str(RUNS_DIR / "yolo11n_rgb_baseline_protocol.md")
        if (RUNS_DIR / "yolo11n_rgb_baseline_protocol.md").exists()
        else None,
    }


def collect_phase6a():
    manuscript_dir = PROJECT_ROOT / "manuscript"
    report = RUNS_DIR / "phase6a_manuscript_report.md"
    references = manuscript_dir / "references" / "reference_inventory.csv"
    return {
        "manuscript_readme": str(manuscript_dir / "README.md") if (manuscript_dir / "README.md").exists() else None,
        "draft": str(manuscript_dir / "RA_RepDet_manuscript_v1.md")
        if (manuscript_dir / "RA_RepDet_manuscript_v1.md").exists()
        else None,
        "report": str(report) if report.exists() else None,
        "decision": read_last_nonempty_line(report),
        "table_csv_count": len(list((manuscript_dir / "tables").glob("*.csv"))) if (manuscript_dir / "tables").exists() else 0,
        "table_md_count": len(list((manuscript_dir / "tables").glob("*.md"))) if (manuscript_dir / "tables").exists() else 0,
        "figure_source_count": len(list((manuscript_dir / "figures").glob("fig*_source.csv")))
        if (manuscript_dir / "figures").exists()
        else 0,
        "figure_manifest": str(manuscript_dir / "figures" / "figure_manifest.md")
        if (manuscript_dir / "figures" / "figure_manifest.md").exists()
        else None,
        "reference_count": count_csv_rows(references),
        "claim_ledger": str(manuscript_dir / "submission_notes" / "claim_ledger.md")
        if (manuscript_dir / "submission_notes" / "claim_ledger.md").exists()
        else None,
        "self_audit": str(manuscript_dir / "submission_notes" / "manuscript_self_audit.md")
        if (manuscript_dir / "submission_notes" / "manuscript_self_audit.md").exists()
        else None,
    }


def collect_phase6b():
    submission_dir = PROJECT_ROOT / "submission" / "sivp"
    report = RUNS_DIR / "phase6b_sivp_preparation_report.md"
    return {
        "readme": str(submission_dir / "README.md") if (submission_dir / "README.md").exists() else None,
        "main_tex": str(submission_dir / "tex" / "main.tex") if (submission_dir / "tex" / "main.tex").exists() else None,
        "body_tex": str(submission_dir / "tex" / "ra_repdet_sivp.tex")
        if (submission_dir / "tex" / "ra_repdet_sivp.tex").exists()
        else None,
        "references_bib": str(submission_dir / "tex" / "references.bib")
        if (submission_dir / "tex" / "references.bib").exists()
        else None,
        "report": str(report) if report.exists() else None,
        "decision": read_last_nonempty_line(report),
        "metadata_count": len(list((submission_dir / "metadata").glob("*.md"))) if (submission_dir / "metadata").exists() else 0,
        "review_count": len(list((submission_dir / "review").glob("*.md"))) + len(list((submission_dir / "review").glob("*.csv")))
        if (submission_dir / "review").exists()
        else 0,
        "tex_source_count": len(
            [
                path
                for path in (submission_dir / "tex").glob("**/*")
                if path.is_file() and path.suffix.lower() in {".tex", ".cls", ".bst", ".bib", ".md"}
            ]
        )
        if (submission_dir / "tex").exists()
        else 0,
        "figure_map": str(submission_dir / "figures" / "FINAL_ASSET_INSERTION_MAP.md")
        if (submission_dir / "figures" / "FINAL_ASSET_INSERTION_MAP.md").exists()
        else None,
        "table_map": str(submission_dir / "tables" / "FINAL_TABLE_INSERTION_MAP.md")
        if (submission_dir / "tables" / "FINAL_TABLE_INSERTION_MAP.md").exists()
        else None,
    }


def collect_phase7b():
    ledger_rows = read_csv(PHASE7B_LEDGER_CSV)
    report_data = {}
    if PHASE7B_REPORT_JSON.exists():
        try:
            report_data = json.loads(PHASE7B_REPORT_JSON.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            report_data = {"json_error": "Could not parse phase7b report JSON."}
    open_counts = {}
    for row in ledger_rows:
        state = (row.get("current_state") or "").lower()
        effect = (row.get("strict_preflight_effect") or "").lower()
        is_open = not state.startswith("complete") and (
            "missing" in state or "pending" in state or "fail" in effect or "block" in effect
        )
        if is_open:
            category = row.get("category") or "uncategorized"
            open_counts[category] = open_counts.get(category, 0) + 1
    residual_blockers = report_data.get("residual_blockers", [])
    if "table_asset" not in open_counts:
        scrubbed = []
        for blocker in residual_blockers:
            blocker = blocker.replace("final publication Tables 1-7 remain pending; ", "")
            blocker = blocker.replace("final publication Tables 1-7 remain pending", "")
            blocker = blocker.replace("table placeholders remain pending; ", "")
            blocker = blocker.replace("table placeholders remain pending", "")
            blocker = blocker.strip(" ;")
            if blocker:
                scrubbed.append(blocker)
        residual_blockers = scrubbed
    return {
        "report": str(PHASE7B_REPORT_MD) if PHASE7B_REPORT_MD.exists() else None,
        "report_json": str(PHASE7B_REPORT_JSON) if PHASE7B_REPORT_JSON.exists() else None,
        "ledger_md": str(PHASE7B_LEDGER_MD) if PHASE7B_LEDGER_MD.exists() else None,
        "ledger_csv": str(PHASE7B_LEDGER_CSV) if PHASE7B_LEDGER_CSV.exists() else None,
        "ledger_rows": len(ledger_rows),
        "open_counts_by_category": open_counts,
        "open_item_count": sum(open_counts.values()),
        "command_outcomes": report_data.get("command_outcomes", []),
        "changed_files": report_data.get("changed_files", []),
        "residual_blockers": residual_blockers,
        "final_commit_sha": report_data.get("final_commit_sha", "pending until commit is created"),
    }


def collect_phase7c():
    report_data = {}
    if PHASE7C_REPORT_JSON.exists():
        try:
            report_data = json.loads(PHASE7C_REPORT_JSON.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            report_data = {"json_error": "Could not parse phase7c report JSON."}
    return {
        "report": str(PHASE7C_REPORT_MD) if PHASE7C_REPORT_MD.exists() else None,
        "report_json": str(PHASE7C_REPORT_JSON) if PHASE7C_REPORT_JSON.exists() else None,
        "render_check": str(PHASE7C_RENDER_CHECK_MD) if PHASE7C_RENDER_CHECK_MD.exists() else None,
        "traceability": str(PHASE7C_TRACEABILITY_MD) if PHASE7C_TRACEABILITY_MD.exists() else None,
        "table_mappings": report_data.get("table_mappings", []),
        "table_validation_outcome": report_data.get("table_validation_outcome", "pending"),
        "command_outcomes": report_data.get("command_outcomes", []),
        "changed_files": report_data.get("changed_files", []),
        "residual_blockers": report_data.get("residual_blockers", []),
        "final_commit_sha": report_data.get("final_commit_sha", "pending until commit is created"),
    }


def collect_phase7d():
    report_data = {}
    if PHASE7D_REPORT_JSON.exists():
        try:
            report_data = json.loads(PHASE7D_REPORT_JSON.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            report_data = {"json_error": "Could not parse phase7d report JSON."}
    return {
        "report": str(PHASE7D_REPORT_MD) if PHASE7D_REPORT_MD.exists() else None,
        "report_json": str(PHASE7D_REPORT_JSON) if PHASE7D_REPORT_JSON.exists() else None,
        "traceability": str(PHASE7D_TRACEABILITY_MD) if PHASE7D_TRACEABILITY_MD.exists() else None,
        "traceability_csv": str(PHASE7D_TRACEABILITY_CSV) if PHASE7D_TRACEABILITY_CSV.exists() else None,
        "build_spec": str(PHASE7D_BUILD_SPEC_MD) if PHASE7D_BUILD_SPEC_MD.exists() else None,
        "review_check": str(PHASE7D_REVIEW_CHECK_MD) if PHASE7D_REVIEW_CHECK_MD.exists() else None,
        "review_check_csv": str(PHASE7D_REVIEW_CHECK_CSV) if PHASE7D_REVIEW_CHECK_CSV.exists() else None,
        "traceability_rows": count_csv_rows(PHASE7D_TRACEABILITY_CSV),
        "review_check_rows": count_csv_rows(PHASE7D_REVIEW_CHECK_CSV),
        "figure_readiness": report_data.get("figure_readiness", []),
        "dry_run_result": report_data.get("dry_run_result", {}),
        "command_outcomes": report_data.get("command_outcomes", []),
        "changed_files": report_data.get("changed_files", []),
        "residual_blockers": report_data.get("residual_blockers", []),
        "final_commit_sha": report_data.get("final_commit_sha", "pending until commit is created"),
    }


def collect_phase7e():
    report_data = {}
    if PHASE7E_REPORT_JSON.exists():
        try:
            report_data = json.loads(PHASE7E_REPORT_JSON.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            report_data = {"json_error": "Could not parse phase7e report JSON."}
    return {
        "report": str(PHASE7E_REPORT_MD) if PHASE7E_REPORT_MD.exists() else None,
        "report_json": str(PHASE7E_REPORT_JSON) if PHASE7E_REPORT_JSON.exists() else None,
        "manifest": str(PHASE7E_MANIFEST_MD) if PHASE7E_MANIFEST_MD.exists() else None,
        "manifest_csv": str(PHASE7E_MANIFEST_CSV) if PHASE7E_MANIFEST_CSV.exists() else None,
        "render_check": str(PHASE7E_RENDER_CHECK_MD) if PHASE7E_RENDER_CHECK_MD.exists() else None,
        "render_check_csv": str(PHASE7E_RENDER_CHECK_CSV) if PHASE7E_RENDER_CHECK_CSV.exists() else None,
        "manifest_rows": count_csv_rows(PHASE7E_MANIFEST_CSV),
        "render_check_rows": count_csv_rows(PHASE7E_RENDER_CHECK_CSV),
        "local_candidates": report_data.get("local_candidates", []),
        "local_uncommitted_outputs": report_data.get("local_uncommitted_outputs", []),
        "command_outcomes": report_data.get("command_outcomes", []),
        "changed_files": report_data.get("changed_files", []),
        "residual_blockers": report_data.get("residual_blockers", []),
        "final_commit_sha": report_data.get("final_commit_sha", "pending until commit is created"),
    }


def collect_phase7f():
    report_data = {}
    if PHASE7F_REPORT_JSON.exists():
        try:
            report_data = json.loads(PHASE7F_REPORT_JSON.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            report_data = {"json_error": "Could not parse phase7f report JSON."}
    return {
        "report": str(PHASE7F_REPORT_MD) if PHASE7F_REPORT_MD.exists() else None,
        "report_json": str(PHASE7F_REPORT_JSON) if PHASE7F_REPORT_JSON.exists() else None,
        "packet": str(PHASE7F_PACKET_MD) if PHASE7F_PACKET_MD.exists() else None,
        "decisions_csv": str(PHASE7F_DECISIONS_CSV) if PHASE7F_DECISIONS_CSV.exists() else None,
        "panel_template": str(PHASE7F_PANEL_TEMPLATE_MD) if PHASE7F_PANEL_TEMPLATE_MD.exists() else None,
        "panel_template_csv": str(PHASE7F_PANEL_TEMPLATE_CSV) if PHASE7F_PANEL_TEMPLATE_CSV.exists() else None,
        "panel_check": str(PHASE7F_PANEL_CHECK_MD) if PHASE7F_PANEL_CHECK_MD.exists() else None,
        "panel_check_csv": str(PHASE7F_PANEL_CHECK_CSV) if PHASE7F_PANEL_CHECK_CSV.exists() else None,
        "decision_rows": count_csv_rows(PHASE7F_DECISIONS_CSV),
        "panel_template_rows": count_csv_rows(PHASE7F_PANEL_TEMPLATE_CSV),
        "panel_check_rows": count_csv_rows(PHASE7F_PANEL_CHECK_CSV),
        "fig3_5_review_readiness": report_data.get("fig3_5_review_readiness", []),
        "fig6_inventory": report_data.get("fig6_inventory", {}),
        "author_decisions_required": report_data.get("author_decisions_required", []),
        "remaining_ledger_categories_outside_figures": report_data.get("remaining_ledger_categories_outside_figures", {}),
        "local_uncommitted_outputs": report_data.get("local_uncommitted_outputs", []),
        "command_outcomes": report_data.get("command_outcomes", []),
        "changed_files": report_data.get("changed_files", []),
        "residual_blockers": report_data.get("residual_blockers", []),
        "final_commit_sha": report_data.get("final_commit_sha", "pending until commit is created"),
    }


def collect_phase7g():
    report_data = {}
    if PHASE7G_REPORT_JSON.exists():
        try:
            report_data = json.loads(PHASE7G_REPORT_JSON.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            report_data = {"json_error": "Could not parse phase7g report JSON."}
    after_counts = report_data.get("after_reconciliation", {})
    remaining = report_data.get("remaining_strict_preflight_blockers", [])
    return {
        "report": str(PHASE7G_REPORT_MD) if PHASE7G_REPORT_MD.exists() else None,
        "report_json": str(PHASE7G_REPORT_JSON) if PHASE7G_REPORT_JSON.exists() else None,
        "author_packet": str(PHASE7G_AUTHOR_PACKET_MD) if PHASE7G_AUTHOR_PACKET_MD.exists() else None,
        "author_responses_csv": str(PHASE7G_AUTHOR_RESPONSES_CSV) if PHASE7G_AUTHOR_RESPONSES_CSV.exists() else None,
        "environment_template": str(PHASE7G_ENV_TEMPLATE_MD) if PHASE7G_ENV_TEMPLATE_MD.exists() else None,
        "roadmap": str(PHASE7G_ROADMAP_MD) if PHASE7G_ROADMAP_MD.exists() else None,
        "completeness": str(PHASE7G_COMPLETENESS_MD) if PHASE7G_COMPLETENESS_MD.exists() else None,
        "completeness_csv": str(PHASE7G_COMPLETENESS_CSV) if PHASE7G_COMPLETENESS_CSV.exists() else None,
        "static_audit": str(PHASE7G_STATIC_AUDIT_MD) if PHASE7G_STATIC_AUDIT_MD.exists() else None,
        "static_audit_csv": str(PHASE7G_STATIC_AUDIT_CSV) if PHASE7G_STATIC_AUDIT_CSV.exists() else None,
        "crosswalk": str(PHASE7G_CROSSWALK_MD) if PHASE7G_CROSSWALK_MD.exists() else None,
        "crosswalk_csv": str(PHASE7G_CROSSWALK_CSV) if PHASE7G_CROSSWALK_CSV.exists() else None,
        "repro_audit": str(PHASE7G_REPRO_AUDIT_MD) if PHASE7G_REPRO_AUDIT_MD.exists() else None,
        "repro_audit_csv": str(PHASE7G_REPRO_AUDIT_CSV) if PHASE7G_REPRO_AUDIT_CSV.exists() else None,
        "ledger_total": after_counts.get("ledger_total", count_csv_rows(PHASE7B_LEDGER_CSV)),
        "resolved_count": after_counts.get("resolved_count", 0),
        "unresolved_count": after_counts.get("unresolved_count", 0),
        "response_rows": count_csv_rows(PHASE7G_AUTHOR_RESPONSES_CSV),
        "crosswalk_rows": count_csv_rows(PHASE7G_CROSSWALK_CSV),
        "static_audit_result": report_data.get("static_audit_result", "pending"),
        "placeholder_preflight_result": report_data.get("placeholder_preflight_result", "pending"),
        "strict_preflight_result": report_data.get("strict_preflight_result", "pending"),
        "remaining_blockers": remaining,
        "command_outcomes": report_data.get("command_outcomes", []),
        "changed_files": report_data.get("changed_files", []),
        "final_commit_sha": report_data.get("final_commit_sha", "pending until commit is created"),
    }


def collect_phase7h():
    report_data = {}
    if PHASE7H_REPORT_JSON.exists():
        try:
            report_data = json.loads(PHASE7H_REPORT_JSON.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            report_data = {"json_error": "Could not parse phase7h report JSON."}
    counts = report_data.get("counts", {})
    readiness_counts = counts.get("readiness_counts", {})
    return {
        "report": str(PHASE7H_REPORT_MD) if PHASE7H_REPORT_MD.exists() else None,
        "report_json": str(PHASE7H_REPORT_JSON) if PHASE7H_REPORT_JSON.exists() else None,
        "validator": str(PHASE7H_VALIDATOR) if PHASE7H_VALIDATOR.exists() else None,
        "validation": str(PHASE7H_VALIDATION_MD) if PHASE7H_VALIDATION_MD.exists() else None,
        "validation_csv": str(PHASE7H_VALIDATION_CSV) if PHASE7H_VALIDATION_CSV.exists() else None,
        "readiness_map": str(PHASE7H_READINESS_MD) if PHASE7H_READINESS_MD.exists() else None,
        "readiness_map_csv": str(PHASE7H_READINESS_CSV) if PHASE7H_READINESS_CSV.exists() else None,
        "gate_check": str(PHASE7H_GATE_CHECK_MD) if PHASE7H_GATE_CHECK_MD.exists() else None,
        "gate_check_csv": str(PHASE7H_GATE_CHECK_CSV) if PHASE7H_GATE_CHECK_CSV.exists() else None,
        "ledger_total": counts.get("ledger_total", count_csv_rows(PHASE7B_LEDGER_CSV)),
        "resolved_count": counts.get("resolved_count", 0),
        "unresolved_count": counts.get("unresolved_count", 0),
        "response_rows": counts.get("response_template_rows", count_csv_rows(PHASE7G_AUTHOR_RESPONSES_CSV)),
        "structural_integrity_errors": counts.get("structural_integrity_errors", 0),
        "readiness_counts": readiness_counts,
        "validator_outcome": report_data.get("validator", {}).get("outcome", "pending"),
        "placeholder_preflight_result": report_data.get("placeholder_preflight_result", "pending"),
        "strict_preflight_result": report_data.get("strict_preflight_result", "pending"),
        "remaining_blockers": report_data.get("remaining_strict_preflight_blockers", []),
        "command_outcomes": report_data.get("command_outcomes", []),
        "changed_files": report_data.get("changed_files", []),
        "final_commit_sha": report_data.get("final_commit_sha", "pending until commit is created"),
    }


def collect_phase7i():
    report_data = {}
    plan_data = {}
    if PHASE7I_REPORT_JSON.exists():
        try:
            report_data = json.loads(PHASE7I_REPORT_JSON.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            report_data = {"json_error": "Could not parse phase7i report JSON."}
    if PHASE7I_PLAN_JSON.exists():
        try:
            plan_data = json.loads(PHASE7I_PLAN_JSON.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            plan_data = {"json_error": "Could not parse confirmed update plan JSON."}
    counts = report_data.get("counts", plan_data.get("counts", {}))
    return {
        "report": str(PHASE7I_REPORT_MD) if PHASE7I_REPORT_MD.exists() else None,
        "report_json": str(PHASE7I_REPORT_JSON) if PHASE7I_REPORT_JSON.exists() else None,
        "planner": str(PHASE7I_PLANNER) if PHASE7I_PLANNER.exists() else None,
        "plan": str(PHASE7I_PLAN_MD) if PHASE7I_PLAN_MD.exists() else None,
        "plan_csv": str(PHASE7I_PLAN_CSV) if PHASE7I_PLAN_CSV.exists() else None,
        "plan_json": str(PHASE7I_PLAN_JSON) if PHASE7I_PLAN_JSON.exists() else None,
        "check": str(PHASE7I_CHECK_MD) if PHASE7I_CHECK_MD.exists() else None,
        "check_csv": str(PHASE7I_CHECK_CSV) if PHASE7I_CHECK_CSV.exists() else None,
        "ledger_total": counts.get("ledger_total", count_csv_rows(PHASE7B_LEDGER_CSV)),
        "resolved_count": counts.get("resolved_count", 0),
        "unresolved_count": counts.get("unresolved_count", 0),
        "plan_rows": counts.get("plan_rows", count_csv_rows(PHASE7I_PLAN_CSV)),
        "eligible_rows": counts.get("eligible_rows", 0),
        "plan_state_counts": counts.get("plan_state_counts", {}),
        "plan_state_counts_by_category": counts.get("plan_state_counts_by_category", {}),
        "planner_outcome": report_data.get("planner", plan_data.get("planner", {})).get("outcome", "pending"),
        "placeholder_preflight_result": report_data.get("placeholder_preflight_result", "pending"),
        "strict_preflight_result": report_data.get("strict_preflight_result", "pending"),
        "remaining_blockers": report_data.get("remaining_strict_preflight_blockers", []),
        "command_outcomes": report_data.get("command_outcomes", []),
        "changed_files": report_data.get("changed_files", []),
        "final_commit_sha": report_data.get("final_commit_sha", "pending until commit is created"),
    }


def collect_v40_component_disjoint():
    build_rows = read_csv(V40_SPLIT_BUILD_SUMMARY)
    audit_rows = read_csv(V40_AUDIT_CSV)
    build = {row.get("metric"): row.get("value") for row in build_rows}
    audit = {row.get("metric"): row.get("value") for row in audit_rows}
    return {
        "report": V40_REPORT_MD.exists(),
        "report_json": V40_REPORT_JSON.exists(),
        "build_summary": V40_SPLIT_BUILD_SUMMARY.exists(),
        "audit": V40_AUDIT_CSV.exists(),
        "status": read_json(V40_REPORT_JSON).get("status", "NA") if V40_REPORT_JSON.exists() else "NA",
        "component_gate": audit.get("final_component_disjoint_gate", "NA"),
        "inventory_count": build.get("inventory_count", audit.get("complete_inventory_count", "NA")),
        "component_count": build.get("component_count", audit.get("component_count", "NA")),
        "largest_component_size": build.get("largest_component_size", audit.get("largest_component_size", "NA")),
        "achieved_train": build.get("achieved_train", audit.get("train_rows", "NA")),
        "achieved_val": build.get("achieved_val", audit.get("val_rows", "NA")),
        "achieved_guard": build.get("achieved_guard", audit.get("guard_rows", "NA")),
        "train_sha256": build.get("train_sha256", audit.get("train_sha256", "NA")),
        "val_sha256": build.get("val_sha256", audit.get("val_sha256", "NA")),
        "guard_sha256": build.get("guard_sha256", audit.get("guard_sha256", "NA")),
    }


def read_last_nonempty_line(path):
    if not path.exists():
        return None
    for line in reversed(path.read_text(encoding="utf-8").splitlines()):
        stripped = line.strip()
        if stripped:
            return stripped
    return None


def best_by(results, metric):
    numeric = []
    for row in results:
        try:
            numeric.append((float(row.get(metric) or "nan"), row))
        except ValueError:
            continue
    if not numeric:
        return None
    return max(numeric, key=lambda item: item[0])[1]


def build_handoff():
    eval_results = collect_eval_results()
    best_ap50 = best_by(eval_results, "ap50")
    best_ap75 = best_by(eval_results, "ap75")
    phase6a = collect_phase6a()
    phase6b = collect_phase6b()
    phase7b = collect_phase7b()
    phase7c = collect_phase7c()
    phase7d = collect_phase7d()
    phase7e = collect_phase7e()
    phase7f = collect_phase7f()
    phase7g = collect_phase7g()
    phase7h = collect_phase7h()
    phase7i = collect_phase7i()
    v40_component_disjoint = collect_v40_component_disjoint()
    pending = [
        "Use runs/phase5a_report.md as the paper-readiness decision gate once Phase 5A completes.",
        "Former random-split results are historical diagnostics only and must not be paper headline results.",
        "Do not start 100-epoch training or manuscript drafting until the Phase 5A decision gate is reviewed.",
    ]
    next_tasks = [
        "Use E2 as the main robustness model unless the paper specifically needs the alpha-correctness ACRF ablation.",
        "Use E5 as an ablation showing exact zero absent-modality alpha with a small parameter increase.",
        "Use E6 as a training-strategy ablation because Phase 2C did not satisfy the E2 replacement rule.",
        "Use E2 for accuracy-first reporting and E4 as a robustness-first variant unless later split/seed audits change the decision.",
        "Use the Phase 4B R-run table for clean-split headline model selection.",
        "Use Phase 5A to separate RGB-only external-baseline evidence from tri-modal fusion ablation evidence.",
    ]
    if phase6a["decision"] == "MANUSCRIPT DRAFT READY FOR JOURNAL TARGETING":
        pending = [
            "Choose a target SCI/EI journal before final formatting.",
            "Finalize citation style and replace manuscript reference placeholders after journal selection.",
            "Prepare journal-specific figure dimensions from the commit-safe figure manifests and source CSV files.",
            "Keep random-split E-runs as historical diagnostics only.",
        ]
        next_tasks = [
            "Select the target journal and adapt manuscript formatting, citation style, and figure requirements.",
            "Review manuscript/RA_RepDet_manuscript_v1.md against the target journal scope and word limits.",
            "Render final Fig. 1 and Fig. 2 schematics only after target-journal figure specifications are known.",
            "Keep raw data, weights, rendered panels, and local qualitative assets out of Git.",
        ]
    if phase6b["decision"] == "READY FOR ASSISTANT FINAL FIGURES, TABLES, AND AUTHOR METADATA":
        pending = [
            "Produce and author-approve final SIVP figures before replacing placeholder boxes.",
            "Prepare final publication tables from the existing manuscript/table CSV sources.",
            "Collect author metadata, declarations, funding, acknowledgments, and AI-use wording.",
            "Complete a final LaTeX compile after the local environment has required Springer dependencies.",
        ]
        next_tasks = [
            "Create final SIVP figure artwork according to submission/sivp/figures/FINAL_ASSET_INSERTION_MAP.md.",
            "Create final SIVP tables according to submission/sivp/tables/FINAL_TABLE_INSERTION_MAP.md.",
            "Ask authors to complete submission/sivp/metadata placeholders.",
            "Install or enable the missing local LaTeX dependencies before final PDF compilation.",
        ]
    if phase7b["report"] or "Phase 7B" in read_text(NEXT_TASK_PATH):
        pending = [
            "Strict V18 preflight remains blocked until author-confirmed metadata, release metadata, TriAir licence/citation/access details, and final approved figure/table assets are supplied.",
            "Use submission/sivp/metadata/FINAL_SUBMISSION_INPUT_LEDGER.md and submission/sivp/review/FINAL_SUBMISSION_INPUT_LEDGER.csv as the closure checklist.",
            "Do not claim formal SIVP submission readiness or compile a final PDF until strict preflight passes without placeholders.",
        ]
        next_tasks = [
            "Collect every missing item in the Phase 7B final-submission input ledger from the authors or approved asset sources.",
            "Replace placeholders only after the corresponding ledger row has verified source evidence.",
            "Rerun strict preflight and final Springer sn-jnl compilation after all ledger blockers are closed.",
        ]
    if phase7c["report"] or "Phase 7C" in read_text(NEXT_TASK_PATH):
        pending = [
            "Strict V18 preflight remains blocked until author-confirmed metadata, TriAir governance facts, release metadata, final approved figures, final environment record, and final compile readiness are supplied.",
            "Final table placeholders have been removed and replaced with evidence-locked table fragments from unchanged manuscript/table CSV sources.",
            "Do not claim formal SIVP submission readiness or compile a final PDF until strict preflight passes without placeholders and final figures are approved.",
        ]
        next_tasks = [
            "Collect author-confirmed metadata, TriAir governance facts, release/archive metadata, final environment details, and approved final Fig. 1-6 assets.",
            "Rerun strict V18 preflight after the remaining ledger blockers are closed.",
            "Compile the final Springer sn-jnl PDF only after strict preflight passes.",
        ]
    if phase7d["report"] or "Phase 7D" in read_text(NEXT_TASK_PATH):
        pending = [
            "Strict V18 preflight remains blocked until author-confirmed metadata, TriAir governance facts, release metadata, final approved Fig. 1-6 assets, final environment record, and final compile readiness are supplied.",
            "Fig. 3-5 now have evidence-locked candidate build specifications from frozen CSV sources, but no final artwork or candidate artwork has been generated.",
            "Fig. 1-2 still require author-approved schematic design sources, and Fig. 6 still requires verified local real validation panels.",
            "Do not claim formal SIVP submission readiness or compile a final PDF until strict preflight passes without placeholders and final figures are approved.",
        ]
        next_tasks = [
            "Collect author-approved Fig. 1-2 schematic designs and verify Fig. 6 local qualitative panel selections.",
            "If separately approved, render only local untracked *_candidate.* Fig. 3-5 candidates outside the final asset path for author review.",
            "Collect author-confirmed metadata, TriAir governance facts, release/archive metadata, final environment details, and final approved Fig. 1-6 assets.",
            "Rerun strict V18 preflight and compile the final Springer sn-jnl PDF only after every remaining blocker is closed.",
        ]
    if phase7e["report"] or "Phase 7E" in read_text(NEXT_TASK_PATH):
        pending = [
            "Strict V18 preflight remains blocked until author-confirmed metadata, TriAir governance facts, release metadata, final approved Fig. 1-6 assets, final environment record, and final compile readiness are supplied.",
            "Local non-final Fig. 3-5 candidate PDFs exist under runs/local_candidate_figures/phase7e/ for author review only and remain ignored/untracked.",
            "Fig. 1-2 still require author-approved schematic design sources, and Fig. 6 still requires verified local real validation panels.",
            "Do not claim formal SIVP submission readiness or compile a final PDF until strict preflight passes without placeholders and final figures are approved.",
        ]
        next_tasks = [
            "Review the local Fig. 3-5 candidate PDFs with the authors and collect approval or requested edits.",
            "Collect author-approved Fig. 1-2 schematic designs and verify Fig. 6 local qualitative panel selections.",
            "Collect author-confirmed metadata, TriAir governance facts, release/archive metadata, final environment details, and final approved Fig. 1-6 assets.",
            "Rerun strict V18 preflight and compile the final Springer sn-jnl PDF only after every remaining blocker is closed.",
        ]
    if phase7f["report"] or "Phase 7F" in read_text(NEXT_TASK_PATH):
        pending = [
            "Strict V18 preflight remains blocked until author-confirmed metadata, TriAir governance facts, release metadata, final approved Fig. 1-6 assets, final environment record, and final compile readiness are supplied.",
            "Author review packet and decision templates now exist, but every Fig. 1-6 author decision remains pending.",
            "Fig. 6 local panel inventory found 20 locally existing manifest panels, but no panel selection, crop/redaction, or final composition is approved.",
            "Local Fig. 3-5 candidate PDFs and the Fig. 6 path-level inventory JSON remain ignored/untracked review inputs, not publication assets.",
        ]
        next_tasks = [
            "Collect written author decisions in submission/sivp/review/AUTHOR_FIGURE_REVIEW_DECISIONS.csv.",
            "Collect Fig. 6 panel selections and crop/redaction decisions in submission/sivp/review/FIGURE6_PANEL_REVIEW_TEMPLATE.csv.",
            "Collect author-confirmed metadata, TriAir governance facts, release/archive metadata, final environment details, and approved final Fig. 1-6 assets.",
            "Rerun strict V18 preflight and compile the final Springer sn-jnl PDF only after every remaining blocker is closed.",
        ]
    if phase7g["report"] or "Phase 7G" in read_text(NEXT_TASK_PATH):
        pending = [
            "Strict V18 preflight remains blocked by author-confirmed metadata, declarations, TriAir governance facts, release/archive metadata, final approved Fig. 1-6 assets, claim-scope approval, final environment record, and final compile readiness.",
            "TAB_001 is reconciled as complete after Phase 7C; no open table_asset blocker remains.",
            "Author submission intake now covers 29 unresolved ledger items with blank response fields, and static source audit passes structural checks only.",
            "Do not treat placeholder-mode preflight PASS or static-audit PASS as formal submission readiness.",
        ]
        next_tasks = [
            "Collect completed author responses in submission/sivp/metadata/AUTHOR_SUBMISSION_INPUT_RESPONSES.csv.",
            "Collect author-approved final Fig. 1-6 assets and Fig. 6 panel-selection/composition decisions before replacing figure placeholders.",
            "Collect TriAir governance, release/archive, claim-scope, and environment confirmations.",
            "Rerun strict V18 preflight and compile the final Springer sn-jnl PDF only after every remaining blocker is closed.",
        ]
    if phase7h["report"] or "Phase 7H" in read_text(NEXT_TASK_PATH):
        pending = [
            "Author-response validation gate exists and currently reports 29 pending_author_response rows with zero structurally ready rows.",
            "TAB_001 remains resolved and absent from response requirements; no open table_asset blocker remains.",
            "Strict V18 preflight remains blocked by unresolved author metadata, declarations, data governance, release/archive facts, final Fig. 1-6 assets, claim-scope approval, environment record, and compile readiness.",
            "Do not apply any response or claim formal submission readiness until rows are author-confirmed and externally verified where required.",
        ]
        next_tasks = [
            "Collect completed author responses with confirmer, confirmation date, and source-of-confirmation fields.",
            "Rerun the Phase 7H validator after responses are supplied.",
            "Promote Phase 7I only for structurally ready author metadata/declaration rows.",
            "Keep data governance, release/archive, figures, environment, strict preflight, compile, and bundle assembly gated by their queued conditional phases.",
        ]
    if phase7i["report"] or "Phase 7I" in read_text(NEXT_TASK_PATH):
        pending = [
            "Phase 7I dry-run update plan exists and currently reports 29 plan rows with zero eligible_for_future_guarded_application rows.",
            "Figure rows remain awaiting_figure_decision; all non-figure rows remain pending_author_response under the current blank response template.",
            "TAB_001 remains resolved and absent from unresolved planning work; no open table_asset blocker remains.",
            "Strict V18 preflight remains blocked by unresolved author metadata, declarations, data governance, release/archive facts, final Fig. 1-6 assets, claim-scope approval, environment record, and compile readiness.",
            "Do not apply any planned row until a future promoted phase confirms eligibility and required external evidence.",
        ]
        next_tasks = [
            "Authors must complete the response template plus figure decision files with confirmation metadata and external evidence where required.",
            "Rerun the Phase 7H validator and Phase 7I planner after responses or figure decisions are supplied.",
            "Promote Phase 7J only for eligible author_metadata/declaration rows.",
            "Keep data governance, release/archive, final figures, environment, strict preflight, compile, and final bundle assembly gated by Phases 7K-7P.",
        ]
    if v40_component_disjoint["report"] or "V40" in read_text(NEXT_TASK_PATH):
        pending = [
            "V40 component-disjoint split build and strict CPU audit passed.",
            "R4 reliability p=0.20 seed 0/2 training and standardized CUDA evaluation are deferred because the GPU was already busy for this task.",
            "Do not run synthetic missingness, aggregate, or efficiency packaging until both deferred R4 V40 runs and standardized evaluations complete.",
            "Keep V40 validation evidence separate from the official manuscript headline until a later explicit evidence-review decision.",
        ]
        next_tasks = [
            "When GPU is available, run exactly one V40 R4 p=0.20 training/evaluation job at a time for seeds 0 and 2.",
            "After both V40 R4 standardized evaluations complete, create the two-seed aggregate, synthetic missingness, and efficiency package.",
            "Do not modify manuscript/submission files or commit raw data, checkpoints, weights, prediction dumps, or visual artifacts.",
        ]
    status_short = git_lines(["status", "--short"])
    branch = git_lines(["branch", "--show-current"])
    remotes = git_lines(["remote", "-v"])

    return {
        "project_name": "RA-RepDet-TriAir",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(PROJECT_ROOT),
        "git": {
            "branch": branch[0] if branch else None,
            "remotes": remotes,
            "status_short": status_short,
        },
        "current_task": collect_current_task(),
        "dataset": {
            "root": r"D:\download\triair",
            "samples": 10489,
            "images_with_label_txt": 9751,
            "images_without_label_txt": 738,
            "empty_label_txt_files": 1,
            "classes": 1,
            "total_valid_boxes": 30634,
            "val_images": 2098,
            "val_boxes": 6074,
            "note": "Missing txt files are treated as empty-target images.",
        },
        "publication_headline": PUBLICATION_HEADLINE,
        "models": {
            "E0": "5-channel early fusion -> 1x1 Conv(5,3) -> RepViT-M0.9 -> FPN -> FCOS.",
            "E1": "RGB/Thermal/Event reliability stems -> alpha fusion -> Conv(16,3) -> RepViT-M0.9 -> FPN -> FCOS.",
            "E2": "E1 plus modality dropout 0.15 during training.",
            "E3": "E1 plus modality dropout 0.10 during training.",
            "E4": "E1 plus modality dropout 0.20 during training.",
            "E5": "Availability-conditioned reliability fusion with post-stem masking, masked softmax, and modality dropout 0.15.",
            "E6": "E2 inference architecture trained with modality-subset consistency distillation from frozen E2 full-input teacher.",
            "labels": "TriAir class 0 is shifted to torchvision detection label 1; background remains 0.",
        },
        "core_results": eval_results,
        "best_model": {
            "scope": "legacy_random_split_historical",
            "by_ap50": best_ap50,
            "by_ap75": best_ap75,
        },
        "missing_modality": collect_missing_modality(),
        "profile": collect_profile(),
        "phase2a": collect_phase2a(),
        "phase2b": collect_phase2b(),
        "phase2c": collect_phase2c(),
        "phase3a": collect_phase3a(),
        "phase3b": collect_phase3b(),
        "phase3c": collect_phase3c(),
        "phase4a": collect_phase4a(),
        "phase4b": collect_phase4b(),
        "phase5a": collect_phase5a(),
        "phase6a": phase6a,
        "phase6b": phase6b,
        "phase7b": phase7b,
        "phase7c": phase7c,
        "phase7d": phase7d,
        "phase7e": phase7e,
        "phase7f": phase7f,
        "phase7g": phase7g,
        "phase7h": phase7h,
        "phase7i": phase7i,
        "v40_component_disjoint": v40_component_disjoint,
        "current_pending_experiments": pending,
        "code_structure": {
            "dataset": "datasets/triair_dataset.py",
            "split_tool": "tools/create_triair_split.py",
            "training": "rarepdet/train_early_fusion.py",
            "evaluation": "rarepdet/eval_map.py",
            "visualization": "rarepdet/val_early_fusion.py",
            "backbones": "rarepdet/models/repvit_fpn_backbone.py",
            "detector_builder": "rarepdet/models/early_fusion_fcos.py",
            "postprocessing_tools": "rarepdet/tools/",
        },
        "recent_modified_files": status_short,
        "next_recommended_tasks": next_tasks,
    }


def write_markdown(data, path):
    headline = data["publication_headline"]
    metrics = headline["means"]
    lines = [
        "# RA-RepDet-TriAir Handoff",
        "",
        f"Generated: {data['generated_at']}",
        f"Workspace: `{data['workspace']}`",
        "",
        "## Publication Headline",
        "",
        f"- Official clean blocked-split manuscript headline: {headline['model']} on `{headline['protocol']}`, seeds {', '.join(headline['seeds'])}.",
        f"- Controlled-seed means: F1@0.50 {metrics['F1@0.50']}, AP50 {metrics['AP50']}, AP75 {metrics['AP75']}, w/o RGB AP50 {metrics['w/o RGB AP50']}, w/o Thermal AP50 {metrics['w/o Thermal AP50']}, w/o Event AP50 {metrics['w/o Event AP50']}.",
        f"- Phase 4B decision: {headline['decision']}.",
        f"- Scope note: {headline['legacy_note']}",
        "",
        "## Current Active Task",
        "",
        f"- Task file: `{data['current_task']['task_file']}`",
        f"- Current Task: {data['current_task']['current_task']}",
        f"- Goal: {data['current_task']['goal']}",
        f"- Commit Message: {data['current_task']['commit_message']}",
        "",
        "## Dataset",
        "",
        f"- Root: `{data['dataset']['root']}`",
        f"- Samples: {data['dataset']['samples']}",
        f"- Images with label txt: {data['dataset']['images_with_label_txt']}",
        f"- Images without label txt: {data['dataset']['images_without_label_txt']}",
        f"- Empty label txt files: {data['dataset']['empty_label_txt_files']}",
        f"- Total valid boxes: {data['dataset']['total_valid_boxes']}",
        f"- Val images / boxes: {data['dataset']['val_images']} / {data['dataset']['val_boxes']}",
        f"- Note: {data['dataset']['note']}",
        "",
        "## Historical/Exploratory Random-Split Results",
        "",
        "- Legacy E0-E6 rows below are retained for provenance only and are not the current manuscript headline.",
        "",
        "| Method | Precision | Recall | AP50 | AP75 | GT boxes | Predictions | Mean Confidence |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in data["core_results"]:
        lines.append(
            "| {id} {method} | {precision} | {recall} | {ap50} | {ap75} | {gt_boxes} | {predictions} | {mean_confidence} |".format(
                **{key: row.get(key) or "" for key in row}
            )
        )

    best_ap50 = data["best_model"]["by_ap50"] or {}
    best_ap75 = data["best_model"]["by_ap75"] or {}
    lines += [
        "",
        "## Legacy Random-Split Historical Ranking",
        "",
        f"- Legacy random-split AP50 leader: {best_ap50.get('id', 'NA')} {best_ap50.get('method', '')} ({best_ap50.get('ap50', 'NA')})",
        f"- Legacy random-split AP75 leader: {best_ap75.get('id', 'NA')} {best_ap75.get('method', '')} ({best_ap75.get('ap75', 'NA')})",
        "- These rankings must not be described as the current best or manuscript-selected model.",
        "",
        "## Phase 2A Outputs",
        "",
        "- Report: `runs/phase2a_report.md`" if data["phase2a"]["report"] else "- Report: NA",
        f"- Main table rows: {len(data['phase2a']['main_results'])}",
        f"- E0 profile rows: {len(data['phase2a']['profile_e0'])}",
        f"- E2 profile rows: {len(data['phase2a']['profile_e2'])}",
        f"- Brightness-proxy rows: {len(data['phase2a']['brightness_proxy'])}",
        f"- Alpha mode rows: {len(data['phase2a']['alpha_modes'])}",
        "",
        "## Phase 2B ACRF Outputs",
        "",
        "- Report: `runs/acrf_evidence_report.md`" if data["phase2b"]["evidence_report"] else "- Report: NA",
        "- Smoke test: `runs/acrf_smoke_test.md`" if data["phase2b"]["smoke_test"] else "- Smoke test: NA",
        f"- Evidence rows: {len(data['phase2b']['evidence_summary'])}",
        f"- E5 missing-modality rows: {len(data['phase2b']['e5_missing_modality'])}",
        f"- E5 alpha-mode rows: {len(data['phase2b']['e5_alpha_modes'])}",
        "",
        "## Phase 2C MSCD Outputs",
        "",
        "- Report: `runs/mscd_evidence_report.md`" if data["phase2c"]["evidence_report"] else "- Report: NA",
        "- Phase 2C report: `runs/phase2c_report.md`" if data["phase2c"]["phase2c_report"] else "- Phase 2C report: NA",
        "- Smoke test: `runs/mscd_smoke_test.md`" if data["phase2c"]["smoke_test"] else "- Smoke test: NA",
        f"- Evidence rows: {len(data['phase2c']['evidence_summary'])}",
        f"- E6 missing-modality rows: {len(data['phase2c']['e6_missing_modality'])}",
        "",
        "## Phase 3A Outputs",
        "",
        "- Dropout report: `runs/dropout_ablation_summary.md`" if data["phase3a"]["dropout_report"] else "- Dropout report: NA",
        "- Qualitative report: `runs/qualitative_cases_summary.md`" if data["phase3a"]["qualitative_report"] else "- Qualitative report: NA",
        "- Phase 3A report: `runs/phase3a_report.md`" if data["phase3a"]["phase3a_report"] else "- Phase 3A report: NA",
        f"- Dropout ablation rows: {len(data['phase3a']['dropout_ablation'])}",
        f"- Qualitative manifest rows: {len(data['phase3a']['qualitative_manifest'])}",
        "",
        "## Phase 3B Outputs",
        "",
        "- Split-integrity report: `runs/split_integrity_summary.md`" if data["phase3b"]["split_report"] else "- Split-integrity report: NA",
        "- Dropout selection note: `runs/dropout_ratio_selection_note.md`" if data["phase3b"]["selection_note"] else "- Dropout selection note: NA",
        "- Phase 3B report: `runs/phase3b_report.md`" if data["phase3b"]["phase3b_report"] else "- Phase 3B report: NA",
        f"- Split summary rows: {len(data['phase3b']['split_summary'])}",
        f"- Nearest-pair rows: {data['phase3b']['nearest_pair_count']}",
        f"- Manual-review rows: {data['phase3b']['manual_review_count']}",
        f"- Exact duplicate rows: {data['phase3b']['exact_duplicate_count']}",
        "",
        "## Phase 3C Outputs",
        "",
        "- RGB duplicate report: `runs/rgb_cross_split_duplicate_summary.md`" if data["phase3c"]["rgb_duplicate_report"] else "- RGB duplicate report: NA",
        "- Blocked split report: `runs/blocked_split_proposal_summary.md`" if data["phase3c"]["blocked_split_report"] else "- Blocked split report: NA",
        "- RGB strata report: `runs/rgb_separation_strata_summary.md`" if data["phase3c"]["strata_report"] else "- RGB strata report: NA",
        "- Phase 3C report: `runs/phase3c_report.md`" if data["phase3c"]["phase3c_report"] else "- Phase 3C report: NA",
        f"- RGB duplicate summary rows: {len(data['phase3c']['rgb_duplicate_summary'])}",
        f"- RGB exact pair rows: {data['phase3c']['rgb_exact_pair_count']}",
        f"- RGB group rows: {data['phase3c']['rgb_group_count']}",
        f"- Blocked split candidate rows: {len(data['phase3c']['blocked_split_summary'])}",
        f"- RGB strata rows: {len(data['phase3c']['strata_summary'])}",
        "",
        "## Phase 4A Outputs",
        "",
        "- Clean split protocol: `runs/clean_block64g16_protocol.md`" if data["phase4a"]["clean_protocol"] else "- Clean split protocol: NA",
        "- Clean summary: `runs/clean_block64g16_summary.md`" if data["phase4a"]["clean_summary_report"] else "- Clean summary: NA",
        "- Phase 4A report: `runs/phase4a_report.md`" if data["phase4a"]["phase4a_report"] else "- Phase 4A report: NA",
        f"- Clean summary rows: {len(data['phase4a']['clean_summary'])}",
        f"- B1 missing-modality rows: {len(data['phase4a']['b1_missing'])}",
        f"- B2 missing-modality rows: {len(data['phase4a']['b2_missing'])}",
        f"- B4 missing-modality rows: {len(data['phase4a']['b4_missing'])}",
        "",
        "## Phase 4B Controlled-Seed Outputs",
        "",
        "- Smoke test: `runs/seed_reproducibility_smoke.md`" if data["phase4b"]["smoke_test"] else "- Smoke test: NA",
        "- Seed replication report: `runs/clean_block64g16_seed_replication.md`"
        if data["phase4b"]["seed_replication_report"]
        else "- Seed replication report: NA",
        "- Phase 4B report: `runs/phase4b_report.md`" if data["phase4b"]["phase4b_report"] else "- Phase 4B report: NA",
        f"- Seed replication rows: {len(data['phase4b']['seed_replication'])}",
        f"- R1 missing-modality rows: {len(data['phase4b']['r1_missing_seed0']) + len(data['phase4b']['r1_missing_seed2'])}",
        f"- R2 missing-modality rows: {len(data['phase4b']['r2_missing_seed0']) + len(data['phase4b']['r2_missing_seed2'])}",
        f"- R4 missing-modality rows: {len(data['phase4b']['r4_missing_seed0']) + len(data['phase4b']['r4_missing_seed2'])}",
        f"- Decision: {data['phase4b']['decision'] or 'NA'}",
        "",
        "## Phase 5A Paper-Readiness Outputs",
        "",
        "- Phase 5A report: `runs/phase5a_report.md`" if data["phase5a"]["phase5a_report"] else "- Phase 5A report: NA",
        "- YOLO11n protocol: `runs/yolo11n_rgb_baseline_protocol.md`" if data["phase5a"]["yolo_protocol"] else "- YOLO11n protocol: NA",
        f"- Paper-readiness summary rows: {len(data['phase5a']['paper_readiness'])}",
        f"- Convergence rows: {len(data['phase5a']['convergence'])}",
        f"- Efficiency rows: {len(data['phase5a']['efficiency'])}",
        f"- R4 reliability-weight rows: {len(data['phase5a']['r4_reliability'])}",
        f"- Qualitative manifest rows: {len(data['phase5a']['qualitative'])}",
        f"- YOLO11n eval rows: {len(data['phase5a']['yolo_seed0']) + len(data['phase5a']['yolo_seed2'])}",
        f"- Decision: {data['phase5a']['decision'] or 'NA'}",
        "",
        "## Phase 6A Manuscript Outputs",
        "",
        "- Manuscript README: `manuscript/README.md`" if data["phase6a"]["manuscript_readme"] else "- Manuscript README: NA",
        "- Draft manuscript: `manuscript/RA_RepDet_manuscript_v1.md`" if data["phase6a"]["draft"] else "- Draft manuscript: NA",
        "- Phase 6A report: `runs/phase6a_manuscript_report.md`" if data["phase6a"]["report"] else "- Phase 6A report: NA",
        f"- Table CSV files: {data['phase6a']['table_csv_count']}",
        f"- Table Markdown files: {data['phase6a']['table_md_count']}",
        f"- Figure source CSV files: {data['phase6a']['figure_source_count']}",
        "- Figure manifest: `manuscript/figures/figure_manifest.md`" if data["phase6a"]["figure_manifest"] else "- Figure manifest: NA",
        f"- Verified reference inventory rows: {data['phase6a']['reference_count']}",
        "- Claim ledger: `manuscript/submission_notes/claim_ledger.md`" if data["phase6a"]["claim_ledger"] else "- Claim ledger: NA",
        "- Self-audit: `manuscript/submission_notes/manuscript_self_audit.md`" if data["phase6a"]["self_audit"] else "- Self-audit: NA",
        f"- Decision: {data['phase6a']['decision'] or 'NA'}",
        "",
        "## Phase 6B SIVP Submission-Source Outputs",
        "",
        "- SIVP README: `submission/sivp/README.md`" if data["phase6b"]["readme"] else "- SIVP README: NA",
        "- Main LaTeX source: `submission/sivp/tex/main.tex`" if data["phase6b"]["main_tex"] else "- Main LaTeX source: NA",
        "- Body LaTeX source: `submission/sivp/tex/ra_repdet_sivp.tex`" if data["phase6b"]["body_tex"] else "- Body LaTeX source: NA",
        "- BibTeX references: `submission/sivp/tex/references.bib`" if data["phase6b"]["references_bib"] else "- BibTeX references: NA",
        "- Phase 6B report: `runs/phase6b_sivp_preparation_report.md`" if data["phase6b"]["report"] else "- Phase 6B report: NA",
        f"- Template/LaTeX source files: {data['phase6b']['tex_source_count']}",
        f"- Metadata template files: {data['phase6b']['metadata_count']}",
        f"- Review/audit files: {data['phase6b']['review_count']}",
        "- Figure insertion map: `submission/sivp/figures/FINAL_ASSET_INSERTION_MAP.md`" if data["phase6b"]["figure_map"] else "- Figure insertion map: NA",
        "- Table insertion map: `submission/sivp/tables/FINAL_TABLE_INSERTION_MAP.md`" if data["phase6b"]["table_map"] else "- Table insertion map: NA",
        f"- Decision: {data['phase6b']['decision'] or 'NA'}",
        "",
        "## Phase 7B Publication-State Reconciliation",
        "",
        "- Reconciliation report: `runs/phase7b_publication_state_reconciliation.md`" if data["phase7b"]["report"] else "- Reconciliation report: NA",
        "- Reconciliation JSON: `runs/phase7b_publication_state_reconciliation.json`" if data["phase7b"]["report_json"] else "- Reconciliation JSON: NA",
        "- Input ledger: `submission/sivp/metadata/FINAL_SUBMISSION_INPUT_LEDGER.md`" if data["phase7b"]["ledger_md"] else "- Input ledger: NA",
        "- Input ledger CSV: `submission/sivp/review/FINAL_SUBMISSION_INPUT_LEDGER.csv`" if data["phase7b"]["ledger_csv"] else "- Input ledger CSV: NA",
        f"- Ledger rows: {data['phase7b']['ledger_rows']}",
        f"- Open ledger items: {data['phase7b']['open_item_count']}",
        "- Open categories: "
        + (
            ", ".join(f"{key}={value}" for key, value in sorted(data["phase7b"]["open_counts_by_category"].items()))
            if data["phase7b"]["open_counts_by_category"]
            else "none"
        ),
        "- Command outcomes: "
        + (
            "; ".join(data["phase7b"]["command_outcomes"])
            if data["phase7b"]["command_outcomes"]
            else "see report after Phase 7B commands are run"
        ),
        "- Phase 7B changed files: "
        + (
            ", ".join(f"`{item}`" for item in data["phase7b"]["changed_files"])
            if data["phase7b"]["changed_files"]
            else "see git diff for current task files"
        ),
        "- Residual blockers: "
        + (
            "; ".join(data["phase7b"]["residual_blockers"])
            if data["phase7b"]["residual_blockers"]
            else "none recorded"
        ),
        f"- Final commit SHA: {data['phase7b']['final_commit_sha']}",
        "- Phase 7B status: publication-state mismatch resolved; strict preflight remains blocked by author/asset inputs.",
        "",
        "## Phase 7C Evidence-Locked Table Insertion",
        "",
        "- Table insertion report: `runs/phase7c_table_insertion_report.md`" if data["phase7c"]["report"] else "- Table insertion report: NA",
        "- Table insertion JSON: `runs/phase7c_table_insertion_report.json`" if data["phase7c"]["report_json"] else "- Table insertion JSON: NA",
        "- Source traceability: `submission/sivp/tables/TABLE_SOURCE_TRACEABILITY.md`" if data["phase7c"]["traceability"] else "- Source traceability: NA",
        "- Rendering check: `submission/sivp/review/TABLE_RENDERING_CHECK.md`" if data["phase7c"]["render_check"] else "- Rendering check: NA",
        f"- Table fragments inserted: {len(data['phase7c']['table_mappings'])}",
        f"- Table validation outcome: {data['phase7c']['table_validation_outcome']}",
        "- Command outcomes: "
        + (
            "; ".join(data["phase7c"]["command_outcomes"])
            if data["phase7c"]["command_outcomes"]
            else "see report after Phase 7C commands are run"
        ),
        "- Phase 7C changed files: "
        + (
            ", ".join(f"`{item}`" for item in data["phase7c"]["changed_files"])
            if data["phase7c"]["changed_files"]
            else "see git diff for current task files"
        ),
        "- Residual blockers: "
        + (
            "; ".join(data["phase7c"]["residual_blockers"])
            if data["phase7c"]["residual_blockers"]
            else "none recorded"
        ),
        f"- Final commit SHA: {data['phase7c']['final_commit_sha']}",
        "- Phase 7C status: table placeholders removed; strict preflight remains blocked by non-table external inputs.",
        "",
        "## Phase 7D Figure Source Lock",
        "",
        "- Figure source-lock report: `runs/phase7d_figure_source_lock_report.md`" if data["phase7d"]["report"] else "- Figure source-lock report: NA",
        "- Figure source-lock JSON: `runs/phase7d_figure_source_lock_report.json`" if data["phase7d"]["report_json"] else "- Figure source-lock JSON: NA",
        "- Figure traceability: `submission/sivp/figures/FIGURE_SOURCE_TRACEABILITY.md` and `.csv`"
        if data["phase7d"]["traceability"] and data["phase7d"]["traceability_csv"]
        else "- Figure traceability: NA",
        "- Figure build spec: `submission/sivp/figures/FIGURE_BUILD_SPEC.md`" if data["phase7d"]["build_spec"] else "- Figure build spec: NA",
        "- Figure candidate check: `submission/sivp/review/FIGURE_CANDIDATE_CHECK.md` and `.csv`"
        if data["phase7d"]["review_check"] and data["phase7d"]["review_check_csv"]
        else "- Figure candidate check: NA",
        f"- Traceability rows: {data['phase7d']['traceability_rows']}",
        f"- Review-check rows: {data['phase7d']['review_check_rows']}",
        f"- Dry-run result: {data['phase7d']['dry_run_result'].get('status', 'pending')}",
        "- Figure readiness states: "
        + (
            "; ".join(
                f"{row.get('figure_id', 'NA')}={row.get('current_state', 'NA')}"
                for row in data["phase7d"]["figure_readiness"]
            )
            if data["phase7d"]["figure_readiness"]
            else "none recorded"
        ),
        "- Command outcomes: "
        + (
            "; ".join(data["phase7d"]["command_outcomes"])
            if data["phase7d"]["command_outcomes"]
            else "see report after Phase 7D commands are run"
        ),
        "- Phase 7D changed files: "
        + (
            ", ".join(f"`{item}`" for item in data["phase7d"]["changed_files"])
            if data["phase7d"]["changed_files"]
            else "see git diff for current task files"
        ),
        "- Residual blockers: "
        + (
            "; ".join(data["phase7d"]["residual_blockers"])
            if data["phase7d"]["residual_blockers"]
            else "none recorded"
        ),
        f"- Final commit SHA: {data['phase7d']['final_commit_sha']}",
        "- Phase 7D status: figure sources locked; candidate build spec ready for Fig. 3-5; strict preflight remains blocked by final figure and external author/metadata inputs.",
        "",
        "## Phase 7E Local Candidate Renders",
        "",
        "- Candidate render report: `runs/phase7e_candidate_render_report.md`" if data["phase7e"]["report"] else "- Candidate render report: NA",
        "- Candidate render JSON: `runs/phase7e_candidate_render_report.json`" if data["phase7e"]["report_json"] else "- Candidate render JSON: NA",
        "- Candidate render manifest: `submission/sivp/figures/FIGURE_CANDIDATE_RENDER_MANIFEST.md` and `.csv`"
        if data["phase7e"]["manifest"] and data["phase7e"]["manifest_csv"]
        else "- Candidate render manifest: NA",
        "- Candidate render check: `submission/sivp/review/FIGURE_CANDIDATE_RENDER_CHECK.md` and `.csv`"
        if data["phase7e"]["render_check"] and data["phase7e"]["render_check_csv"]
        else "- Candidate render check: NA",
        f"- Manifest rows: {data['phase7e']['manifest_rows']}",
        f"- Render-check rows: {data['phase7e']['render_check_rows']}",
        "- Local candidates: "
        + (
            "; ".join(
                f"{row.get('figure_id', 'NA')}={row.get('path', 'NA')} ({row.get('bytes', 'NA')} bytes, {row.get('final_asset_status', 'NA')})"
                for row in data["phase7e"]["local_candidates"]
            )
            if data["phase7e"]["local_candidates"]
            else "none recorded"
        ),
        "- Local uncommitted outputs: "
        + (
            ", ".join(f"`{item}`" for item in data["phase7e"]["local_uncommitted_outputs"])
            if data["phase7e"]["local_uncommitted_outputs"]
            else "none recorded"
        ),
        "- Command outcomes: "
        + (
            "; ".join(data["phase7e"]["command_outcomes"])
            if data["phase7e"]["command_outcomes"]
            else "see report after Phase 7E commands are run"
        ),
        "- Phase 7E changed files: "
        + (
            ", ".join(f"`{item}`" for item in data["phase7e"]["changed_files"])
            if data["phase7e"]["changed_files"]
            else "see git diff for current task files"
        ),
        "- Residual blockers: "
        + (
            "; ".join(data["phase7e"]["residual_blockers"])
            if data["phase7e"]["residual_blockers"]
            else "none recorded"
        ),
        f"- Final commit SHA: {data['phase7e']['final_commit_sha']}",
        "- Phase 7E status: local non-final Fig. 3-5 candidates generated for author review; strict preflight remains blocked by final figure and external author/metadata inputs.",
        "",
        "## Phase 7F Author Figure Review Intake",
        "",
        "- Author review report: `runs/phase7f_author_review_intake_report.md`" if data["phase7f"]["report"] else "- Author review report: NA",
        "- Author review JSON: `runs/phase7f_author_review_intake_report.json`" if data["phase7f"]["report_json"] else "- Author review JSON: NA",
        "- Author review packet: `submission/sivp/review/AUTHOR_FIGURE_REVIEW_PACKET.md`" if data["phase7f"]["packet"] else "- Author review packet: NA",
        "- Author decision CSV: `submission/sivp/review/AUTHOR_FIGURE_REVIEW_DECISIONS.csv`" if data["phase7f"]["decisions_csv"] else "- Author decision CSV: NA",
        "- Fig. 6 panel review template: `submission/sivp/review/FIGURE6_PANEL_REVIEW_TEMPLATE.md` and `.csv`"
        if data["phase7f"]["panel_template"] and data["phase7f"]["panel_template_csv"]
        else "- Fig. 6 panel review template: NA",
        "- Fig. 6 inventory check: `submission/sivp/review/FIGURE6_PANEL_INVENTORY_CHECK.md` and `.csv`"
        if data["phase7f"]["panel_check"] and data["phase7f"]["panel_check_csv"]
        else "- Fig. 6 inventory check: NA",
        f"- Author decision rows: {data['phase7f']['decision_rows']}",
        f"- Fig. 6 review-template rows: {data['phase7f']['panel_template_rows']}",
        "- Fig. 6 local inventory: "
        + (
            "manifest rows={manifest_row_count}; rows with path metadata={rows_with_path_metadata}; "
            "existing local panels={locally_existing_panels}; missing/unverifiable={missing_or_unverifiable}; status={status}"
        ).format(**data["phase7f"]["fig6_inventory"])
        if data["phase7f"]["fig6_inventory"]
        else "- Fig. 6 local inventory: none recorded",
        "- Local uncommitted outputs: "
        + (
            ", ".join(f"`{item}`" for item in data["phase7f"]["local_uncommitted_outputs"])
            if data["phase7f"]["local_uncommitted_outputs"]
            else "none recorded"
        ),
        "- Command outcomes: "
        + (
            "; ".join(data["phase7f"]["command_outcomes"])
            if data["phase7f"]["command_outcomes"]
            else "see report after Phase 7F commands are run"
        ),
        "- Phase 7F changed files: "
        + (
            ", ".join(f"`{item}`" for item in data["phase7f"]["changed_files"])
            if data["phase7f"]["changed_files"]
            else "see git diff for current task files"
        ),
        "- Residual blockers: "
        + (
            "; ".join(data["phase7f"]["residual_blockers"])
            if data["phase7f"]["residual_blockers"]
            else "none recorded"
        ),
        f"- Final commit SHA: {data['phase7f']['final_commit_sha']}",
        "- Phase 7F status: author review intake and Fig. 6 local panel inventory completed; strict preflight remains blocked by author decisions, final figure assets, and external metadata inputs.",
        "",
        "## Phase 7G Expanded Submission Intake And Static Audit",
        "",
        "- Submission intake report: `runs/phase7g_submission_intake_report.md`" if data["phase7g"]["report"] else "- Submission intake report: NA",
        "- Submission intake JSON: `runs/phase7g_submission_intake_report.json`" if data["phase7g"]["report_json"] else "- Submission intake JSON: NA",
        "- Author intake packet: `submission/sivp/metadata/AUTHOR_SUBMISSION_INPUT_PACKET.md`" if data["phase7g"]["author_packet"] else "- Author intake packet: NA",
        "- Author response CSV: `submission/sivp/metadata/AUTHOR_SUBMISSION_INPUT_RESPONSES.csv`" if data["phase7g"]["author_responses_csv"] else "- Author response CSV: NA",
        "- Environment template: `submission/sivp/metadata/ENVIRONMENT_RECORD_TEMPLATE.md`" if data["phase7g"]["environment_template"] else "- Environment template: NA",
        "- Closure roadmap: `submission/sivp/metadata/SUBMISSION_CLOSURE_ROADMAP.md`" if data["phase7g"]["roadmap"] else "- Closure roadmap: NA",
        "- Static audit: `submission/sivp/review/STATIC_SUBMISSION_SOURCE_AUDIT.md` and `.csv`"
        if data["phase7g"]["static_audit"] and data["phase7g"]["static_audit_csv"]
        else "- Static audit: NA",
        "- Figure/table crosswalk: `submission/sivp/review/FIGURE_TABLE_CROSSWALK.md` and `.csv`"
        if data["phase7g"]["crosswalk"] and data["phase7g"]["crosswalk_csv"]
        else "- Figure/table crosswalk: NA",
        "- Reproducibility closure audit: `submission/sivp/review/REPRODUCIBILITY_CLOSURE_AUDIT.md` and `.csv`"
        if data["phase7g"]["repro_audit"] and data["phase7g"]["repro_audit_csv"]
        else "- Reproducibility closure audit: NA",
        "- Completeness check: `submission/sivp/review/SUBMISSION_INPUT_COMPLETENESS_CHECK.md` and `.csv`"
        if data["phase7g"]["completeness"] and data["phase7g"]["completeness_csv"]
        else "- Completeness check: NA",
        f"- Ledger counts after reconciliation: total={data['phase7g']['ledger_total']}; resolved={data['phase7g']['resolved_count']}; unresolved={data['phase7g']['unresolved_count']}",
        f"- Author-response rows: {data['phase7g']['response_rows']}",
        f"- Figure/table crosswalk rows: {data['phase7g']['crosswalk_rows']}",
        f"- Static audit result: {data['phase7g']['static_audit_result']}",
        f"- Placeholder-mode preflight result: {data['phase7g']['placeholder_preflight_result']}",
        f"- Strict preflight result: {data['phase7g']['strict_preflight_result']}",
        "- Command outcomes: "
        + (
            "; ".join(data["phase7g"]["command_outcomes"])
            if data["phase7g"]["command_outcomes"]
            else "see report after Phase 7G commands are run"
        ),
        "- Phase 7G changed files: "
        + (
            ", ".join(f"`{item}`" for item in data["phase7g"]["changed_files"])
            if data["phase7g"]["changed_files"]
            else "see git diff for current task files"
        ),
        "- Residual blockers: "
        + (
            "; ".join(data["phase7g"]["remaining_blockers"])
            if data["phase7g"]["remaining_blockers"]
            else "none recorded"
        ),
        f"- Final commit SHA: {data['phase7g']['final_commit_sha']}",
        "- Phase 7G status: table ledger reconciled and author intake/static audit package completed; strict preflight remains blocked by non-table external inputs and final figure assets.",
        "",
        "## Phase 7H Author Response Validation Gate",
        "",
        "- Author-response validation report: `runs/phase7h_author_response_validation_report.md`" if data["phase7h"]["report"] else "- Author-response validation report: NA",
        "- Author-response validation JSON: `runs/phase7h_author_response_validation_report.json`" if data["phase7h"]["report_json"] else "- Author-response validation JSON: NA",
        "- Validator script: `submission/sivp/metadata/validate_author_submission_inputs.py`" if data["phase7h"]["validator"] else "- Validator script: NA",
        "- Validation report: `submission/sivp/metadata/AUTHOR_RESPONSE_VALIDATION.md` and `.csv`"
        if data["phase7h"]["validation"] and data["phase7h"]["validation_csv"]
        else "- Validation report: NA",
        "- Application readiness map: `submission/sivp/metadata/METADATA_APPLICATION_READINESS_MAP.md` and `.csv`"
        if data["phase7h"]["readiness_map"] and data["phase7h"]["readiness_map_csv"]
        else "- Application readiness map: NA",
        "- Gate check: `submission/sivp/review/AUTHOR_RESPONSE_GATE_CHECK.md` and `.csv`"
        if data["phase7h"]["gate_check"] and data["phase7h"]["gate_check_csv"]
        else "- Gate check: NA",
        f"- Ledger/template counts: total={data['phase7h']['ledger_total']}; resolved={data['phase7h']['resolved_count']}; unresolved={data['phase7h']['unresolved_count']}; response_rows={data['phase7h']['response_rows']}",
        f"- Structural integrity errors: {data['phase7h']['structural_integrity_errors']}",
        "- Readiness counts: "
        + (
            ", ".join(f"{key}={value}" for key, value in sorted(data["phase7h"]["readiness_counts"].items()))
            if data["phase7h"]["readiness_counts"]
            else "none recorded"
        ),
        f"- Validator outcome: {data['phase7h']['validator_outcome']}",
        f"- Placeholder-mode preflight result: {data['phase7h']['placeholder_preflight_result']}",
        f"- Strict preflight result: {data['phase7h']['strict_preflight_result']}",
        "- Command outcomes: "
        + (
            "; ".join(data["phase7h"]["command_outcomes"])
            if data["phase7h"]["command_outcomes"]
            else "see report after Phase 7H commands are run"
        ),
        "- Phase 7H changed files: "
        + (
            ", ".join(f"`{item}`" for item in data["phase7h"]["changed_files"])
            if data["phase7h"]["changed_files"]
            else "see git diff for current task files"
        ),
        "- Residual blockers: "
        + (
            "; ".join(data["phase7h"]["remaining_blockers"])
            if data["phase7h"]["remaining_blockers"]
            else "none recorded"
        ),
        f"- Final commit SHA: {data['phase7h']['final_commit_sha']}",
        "- Phase 7H status: report-only validation gate completed; current blank template remains pending and no author facts are applied.",
        "",
        "## Phase 7I Confirmation-Gated Update Planning",
        "",
        "- Update planning report: `runs/phase7i_update_planning_report.md`" if data["phase7i"]["report"] else "- Update planning report: NA",
        "- Update planning JSON: `runs/phase7i_update_planning_report.json`" if data["phase7i"]["report_json"] else "- Update planning JSON: NA",
        "- Planner script: `submission/sivp/metadata/plan_confirmed_submission_updates.py`" if data["phase7i"]["planner"] else "- Planner script: NA",
        "- Confirmed update plan: `submission/sivp/metadata/CONFIRMED_UPDATE_PLAN.md`, `.csv`, and `.json`"
        if data["phase7i"]["plan"] and data["phase7i"]["plan_csv"] and data["phase7i"]["plan_json"]
        else "- Confirmed update plan: NA",
        "- Plan gate check: `submission/sivp/review/CONFIRMED_UPDATE_PLAN_CHECK.md` and `.csv`"
        if data["phase7i"]["check"] and data["phase7i"]["check_csv"]
        else "- Plan gate check: NA",
        f"- Ledger/plan counts: total={data['phase7i']['ledger_total']}; resolved={data['phase7i']['resolved_count']}; unresolved={data['phase7i']['unresolved_count']}; plan_rows={data['phase7i']['plan_rows']}; eligible_rows={data['phase7i']['eligible_rows']}",
        "- Plan-state counts: "
        + (
            ", ".join(f"{key}={value}" for key, value in sorted(data["phase7i"]["plan_state_counts"].items()))
            if data["phase7i"]["plan_state_counts"]
            else "none recorded"
        ),
        "- Plan-state counts by category: "
        + (
            ", ".join(f"{key}={value}" for key, value in sorted(data["phase7i"]["plan_state_counts_by_category"].items()))
            if data["phase7i"]["plan_state_counts_by_category"]
            else "none recorded"
        ),
        f"- Planner outcome: {data['phase7i']['planner_outcome']}",
        f"- Placeholder-mode preflight result: {data['phase7i']['placeholder_preflight_result']}",
        f"- Strict preflight result: {data['phase7i']['strict_preflight_result']}",
        "- Command outcomes: "
        + (
            "; ".join(data["phase7i"]["command_outcomes"])
            if data["phase7i"]["command_outcomes"]
            else "see report after Phase 7I commands are run"
        ),
        "- Phase 7I changed files: "
        + (
            ", ".join(f"`{item}`" for item in data["phase7i"]["changed_files"])
            if data["phase7i"]["changed_files"]
            else "see git diff for current task files"
        ),
        "- Residual blockers: "
        + (
            "; ".join(data["phase7i"]["remaining_blockers"])
            if data["phase7i"]["remaining_blockers"]
            else "none recorded"
        ),
        f"- Final commit SHA: {data['phase7i']['final_commit_sha']}",
        "- Phase 7I status: report-only dry-run plan completed; no author facts, destination metadata, TeX, figures, release manifests, or final assets are applied.",
        "",
        "## V40 Component-Disjoint Split Audit",
        "",
        "- Report: `runs/phase_v40_component_disjoint_report.md`" if data["v40_component_disjoint"]["report"] else "- Report: NA",
        "- Report JSON: `runs/phase_v40_component_disjoint_report.json`" if data["v40_component_disjoint"]["report_json"] else "- Report JSON: NA",
        f"- Status: {data['v40_component_disjoint']['status']}",
        f"- Final component-disjoint gate: {data['v40_component_disjoint']['component_gate']}",
        f"- Inventory/components/largest component: {data['v40_component_disjoint']['inventory_count']} / {data['v40_component_disjoint']['component_count']} / {data['v40_component_disjoint']['largest_component_size']}",
        f"- Achieved train/val/guard rows: {data['v40_component_disjoint']['achieved_train']} / {data['v40_component_disjoint']['achieved_val']} / {data['v40_component_disjoint']['achieved_guard']}",
        f"- Split SHA256 train/val/guard: {data['v40_component_disjoint']['train_sha256']} / {data['v40_component_disjoint']['val_sha256']} / {data['v40_component_disjoint']['guard_sha256']}",
        "- GPU work: skipped/deferred by user constraint; no V40 R4 p=0.20 training or CUDA evaluation was started in this task.",
        "",
        "## Model And Code Structure",
        "",
    ]
    for key, value in data["models"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    for key, value in data["code_structure"].items():
        lines.append(f"- {key}: `{value}`")

    lines += [
        "",
        "## Current Pending Experiments",
        "",
    ]
    lines += [f"- {item}" for item in data["current_pending_experiments"]]

    lines += [
        "",
        "## Recently Modified Files",
        "",
    ]
    if data["recent_modified_files"]:
        lines += [f"- `{item}`" for item in data["recent_modified_files"]]
    else:
        lines.append("- Working tree was clean when this report was generated.")

    lines += [
        "",
        "## Next Recommended Tasks",
        "",
    ]
    lines += [f"- {item}" for item in data["next_recommended_tasks"]]
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    data = build_handoff()
    json_path = RUNS_DIR / "handoff_latest.json"
    md_path = RUNS_DIR / "handoff_latest.md"
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=True), encoding="utf-8")
    write_markdown(data, md_path)
    print(f"Saved: {md_path}")
    print(f"Saved: {json_path}")


if __name__ == "__main__":
    main()
