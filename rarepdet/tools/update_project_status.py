#!/usr/bin/env python
"""Update docs/EXPERIMENT_STATUS.md from lightweight experiment summaries."""

import csv
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = PROJECT_ROOT / "runs"
DOCS_DIR = PROJECT_ROOT / "docs"
STATUS_PATH = DOCS_DIR / "EXPERIMENT_STATUS.md"
NEXT_TASK_PATH = DOCS_DIR / "NEXT_TASK.md"
HANDOFF_PATH = RUNS_DIR / "handoff_latest.md"

PUBLICATION_HEADLINE = {
    "model": "R4 Reliability p=0.20",
    "protocol": "block64_guard16_seed0",
    "seeds": "0, 2",
    "decision": "SELECT R4 AS CLEAN-SPLIT MAIN VARIANT",
    "F1@0.50": "0.920861",
    "AP50": "0.962495",
    "AP75": "0.891266",
    "w/o RGB AP50": "0.916051",
    "w/o Thermal AP50": "0.718277",
    "w/o Event AP50": "0.961577",
}

PHASE7B_REPORT = RUNS_DIR / "phase7b_publication_state_reconciliation.md"
PHASE7B_LEDGER_MD = PROJECT_ROOT / "submission" / "sivp" / "metadata" / "FINAL_SUBMISSION_INPUT_LEDGER.md"
PHASE7B_LEDGER_CSV = PROJECT_ROOT / "submission" / "sivp" / "review" / "FINAL_SUBMISSION_INPUT_LEDGER.csv"


EXPERIMENTS = [
    ("E0", "Early Fusion", RUNS_DIR / "E0_early_repvit_fcos_e50", "eval"),
    ("E1", "Reliability Fusion", RUNS_DIR / "E1_reliability_repvit_fcos_e50", "eval"),
    ("E2", "Reliability + Dropout 0.15", RUNS_DIR / "E2_reliability_dropout015_repvit_fcos_e50", "eval"),
    ("E3", "Reliability + Dropout 0.10", RUNS_DIR / "E3_reliability_dropout010_repvit_fcos_e50", "eval_thr050"),
    ("E4", "Reliability + Dropout 0.20", RUNS_DIR / "E4_reliability_dropout020_repvit_fcos_e50", "eval_thr050"),
    ("E5", "ACRF + Dropout 0.15", RUNS_DIR / "E5_acrf_dropout015_repvit_fcos_e50", "eval_thr050"),
    ("E6", "MSCD + Dropout 0.15", RUNS_DIR / "E6_mscd_dropout015_repvit_fcos_e50", "eval_thr050"),
]


def na(value=None):
    return value if value not in (None, "") else "NA"


def read_text(path):
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def read_key_values(path):
    data = {}
    if not path.exists():
        return data
    for line in read_text(path).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def read_csv(path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def count_csv_rows(path):
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        next(reader, None)
        return sum(1 for _ in reader)


def read_last_nonempty_line(path):
    if not path.exists():
        return None
    for line in reversed(read_text(path).splitlines()):
        stripped = line.strip()
        if stripped:
            return stripped
    return None


def parse_sections(path):
    sections = {}
    current = None
    for raw_line in read_text(path).splitlines():
        line = raw_line.strip()
        if line.startswith("#"):
            title = line.lstrip("#").strip()
            current = title
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


def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def collect_eval_results():
    rows = []
    for exp_id, method, exp_dir, eval_subdir in EXPERIMENTS:
        values = read_key_values(exp_dir / eval_subdir / "eval_results.txt")
        rows.append(
            {
                "Experiment": exp_id,
                "Method": method,
                "Precision": na(values.get("Precision")),
                "Recall": na(values.get("Recall")),
                "AP50": na(values.get("AP50")),
                "AP75": na(values.get("AP75")),
                "GT boxes": na(values.get("GT boxes")),
                "Predictions": na(values.get("Predictions")),
                "Mean Confidence": na(values.get("Mean Confidence")),
            }
        )
    return rows


def best_row(rows, metric):
    best = None
    for row in rows:
        value = to_float(row.get(metric))
        if value is None:
            continue
        if best is None or value > best[0]:
            best = (value, row)
    return best[1] if best else None


def collect_threshold_best():
    rows = read_csv(RUNS_DIR / "threshold_sweep" / "threshold_sweep_results.csv")
    best_by_method = {}
    for row in rows:
        method = row.get("Method", "NA")
        f1 = to_float(row.get("F1"))
        if f1 is None:
            continue
        if method not in best_by_method or f1 > best_by_method[method][0]:
            best_by_method[method] = (f1, row)
    return [item[1] for item in best_by_method.values()]


def table(headers, rows):
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    if not rows:
        lines.append("| " + " | ".join(["NA"] * len(headers)) + " |")
        return lines
    for row in rows:
        lines.append("| " + " | ".join(na(row.get(header)) for header in headers) + " |")
    return lines


def handoff_pending_tasks():
    text = read_text(HANDOFF_PATH)
    if not text:
        return ["NA"]
    capture = False
    items = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "## Current Pending Experiments":
            capture = True
            continue
        if capture and stripped.startswith("## "):
            break
        if capture and stripped.startswith("- "):
            items.append(stripped[2:])
    return items or ["NA"]


def build_status():
    next_sections = parse_sections(NEXT_TASK_PATH)
    eval_rows = collect_eval_results()
    best_ap50 = best_row(eval_rows, "AP50")
    best_ap75 = best_row(eval_rows, "AP75")
    threshold_best = collect_threshold_best()
    missing_ap50 = read_csv(RUNS_DIR / "missing_modality_summary.csv")
    missing_ap75 = read_csv(RUNS_DIR / "missing_modality_summary_ap75.csv")
    profile = read_csv(RUNS_DIR / "profile_summary.csv")
    phase2a_main = read_csv(RUNS_DIR / "phase2a_main_results.csv")
    phase2a_profile_e0 = read_csv(RUNS_DIR / "phase2a_profile_e0" / "profile_results.csv")
    phase2a_profile_e2 = read_csv(RUNS_DIR / "phase2a_profile_e2" / "profile_results.csv")
    phase2a_brightness = read_csv(RUNS_DIR / "phase2a_brightness_proxy" / "brightness_proxy_results.csv")
    phase2a_alpha = read_csv(RUNS_DIR / "phase2a_alpha" / "alpha_mode_summary.csv")
    acrf_evidence = read_csv(RUNS_DIR / "acrf_evidence_summary.csv")
    e5_missing = read_csv(RUNS_DIR / "E5_acrf_dropout015_repvit_fcos_e50" / "missing_modality" / "missing_modality_results.csv")
    e5_alpha = read_csv(RUNS_DIR / "E5_acrf_dropout015_repvit_fcos_e50" / "alpha_modes" / "alpha_mode_summary.csv")
    mscd_evidence = read_csv(RUNS_DIR / "mscd_evidence_summary.csv")
    e6_missing = read_csv(RUNS_DIR / "E6_mscd_dropout015_repvit_fcos_e50" / "missing_modality" / "missing_modality_results.csv")
    dropout_ablation = read_csv(RUNS_DIR / "dropout_ablation_summary.csv")
    qualitative_manifest = read_csv(RUNS_DIR / "qualitative_cases_manifest.csv")
    phase3a_report_exists = (RUNS_DIR / "phase3a_report.md").exists()
    split_integrity = read_csv(RUNS_DIR / "split_integrity_summary.csv")
    split_manual_review = read_csv(RUNS_DIR / "split_integrity_manual_review.csv")
    phase3b_report_exists = (RUNS_DIR / "phase3b_report.md").exists()
    rgb_duplicate_summary = read_csv(RUNS_DIR / "rgb_cross_split_duplicate_summary.csv")
    blocked_split_summary = read_csv(RUNS_DIR / "blocked_split_proposal_summary.csv")
    rgb_strata_summary = read_csv(RUNS_DIR / "rgb_separation_strata_summary.csv")
    phase3c_report_exists = (RUNS_DIR / "phase3c_report.md").exists()
    clean_block_summary = read_csv(RUNS_DIR / "clean_block64g16_summary.csv")
    phase4a_report_exists = (RUNS_DIR / "phase4a_report.md").exists()
    clean_seed_replication = read_csv(RUNS_DIR / "clean_block64g16_seed_replication.csv")
    phase4b_report_exists = (RUNS_DIR / "phase4b_report.md").exists()
    seed_smoke_exists = (RUNS_DIR / "seed_reproducibility_smoke.md").exists()
    phase4b_decision = read_last_nonempty_line(RUNS_DIR / "phase4b_report.md")
    paper_readiness = read_csv(RUNS_DIR / "paper_readiness_summary.csv")
    phase5a_report_exists = (RUNS_DIR / "phase5a_report.md").exists()
    phase5a_decision = read_last_nonempty_line(RUNS_DIR / "phase5a_report.md")
    clean_convergence = read_csv(RUNS_DIR / "clean_block64g16_convergence.csv")
    clean_efficiency = read_csv(RUNS_DIR / "clean_efficiency_profile.csv")
    r4_reliability_audit = read_csv(RUNS_DIR / "r4_reliability_weight_audit.csv")
    clean_qualitative = read_csv(RUNS_DIR / "clean_qualitative_manifest.csv")
    yolo_seed0 = read_csv(RUNS_DIR / "Y11n_rgb_seed0_block64g16_e50" / "eval_project" / "eval_results.csv")
    yolo_seed2 = read_csv(RUNS_DIR / "Y11n_rgb_seed2_block64g16_e50" / "eval_project" / "eval_results.csv")
    manuscript_dir = PROJECT_ROOT / "manuscript"
    phase6a_report_exists = (RUNS_DIR / "phase6a_manuscript_report.md").exists()
    phase6a_decision = read_last_nonempty_line(RUNS_DIR / "phase6a_manuscript_report.md")
    phase6a_table_csv_count = len(list((manuscript_dir / "tables").glob("*.csv"))) if (manuscript_dir / "tables").exists() else 0
    phase6a_table_md_count = len(list((manuscript_dir / "tables").glob("*.md"))) if (manuscript_dir / "tables").exists() else 0
    phase6a_reference_count = count_csv_rows(manuscript_dir / "references" / "reference_inventory.csv")
    phase6a_figure_source_count = len(list((manuscript_dir / "figures").glob("fig*_source.csv"))) if (manuscript_dir / "figures").exists() else 0
    submission_dir = PROJECT_ROOT / "submission" / "sivp"
    phase6b_report_exists = (RUNS_DIR / "phase6b_sivp_preparation_report.md").exists()
    phase6b_decision = read_last_nonempty_line(RUNS_DIR / "phase6b_sivp_preparation_report.md")
    phase6b_tex_source_count = (
        len(
            [
                path
                for path in (submission_dir / "tex").glob("**/*")
                if path.is_file() and path.suffix.lower() in {".tex", ".cls", ".bst", ".bib", ".md"}
            ]
        )
        if (submission_dir / "tex").exists()
        else 0
    )
    phase6b_metadata_count = len(list((submission_dir / "metadata").glob("*.md"))) if (submission_dir / "metadata").exists() else 0
    phase6b_review_count = (
        len(list((submission_dir / "review").glob("*.md"))) + len(list((submission_dir / "review").glob("*.csv")))
        if (submission_dir / "review").exists()
        else 0
    )
    phase7b_report_exists = PHASE7B_REPORT.exists()
    phase7b_ledger_md_exists = PHASE7B_LEDGER_MD.exists()
    phase7b_ledger_csv_exists = PHASE7B_LEDGER_CSV.exists()
    phase7b_ledger_rows = count_csv_rows(PHASE7B_LEDGER_CSV)

    next_text = read_text(NEXT_TASK_PATH)
    active_status = "pending"
    if "Phase 3C" in next_text:
        active_status = "completed" if phase3c_report_exists and rgb_duplicate_summary and blocked_split_summary else "pending"
    if "Phase 4A" in next_text:
        active_status = "completed" if phase4a_report_exists and clean_block_summary else "pending"
    if "Phase 4B" in next_text:
        active_status = "completed" if phase4b_report_exists and clean_seed_replication and seed_smoke_exists else "pending"
    if "Phase 5A" in next_text:
        active_status = "completed" if phase5a_report_exists and phase5a_decision == "READY FOR MANUSCRIPT DRAFTING" else "pending"
    if "Phase 6A" in next_text:
        active_status = "completed" if phase6a_report_exists and phase6a_decision == "MANUSCRIPT DRAFT READY FOR JOURNAL TARGETING" else "pending"
    if "Phase 6B" in next_text:
        active_status = (
            "completed"
            if phase6b_report_exists and phase6b_decision == "READY FOR ASSISTANT FINAL FIGURES, TABLES, AND AUTHOR METADATA"
            else "pending"
        )
    if "Phase 7A" in next_text:
        active_status = "pending"
    if "Phase 7B" in next_text:
        active_status = "completed" if phase7b_report_exists and phase7b_ledger_md_exists and phase7b_ledger_csv_exists else "pending"
    current_task = first_paragraph(next_sections.get("Current Task", "NA"))
    current_goal = first_paragraph(next_sections.get("Goal", "NA"))
    if current_task == "NA" and "Phase 2B" in next_text:
        current_task = "Phase 2B - Availability-Conditioned Reliability Fusion (ACRF)"
    if current_task == "NA" and "Phase 2C" in next_text:
        current_task = "Phase 2C - Modality-Subset Consistency Distillation (MSCD)"
    if current_task == "NA" and "Phase 3C" in next_text:
        current_task = "Phase 3C - RGB Duplicate Audit and Leakage-Aware Split Proposal"
    if current_task == "NA" and "Phase 4A" in next_text:
        current_task = "Phase 4A - Clean Blocked-Split Core Comparison"
    if "Phase 4B" in next_text:
        current_task = "Phase 4B - Controlled Seed Replication on the Clean Blocked Split"
    if "Phase 5A" in next_text:
        current_task = "Phase 5A - Paper-Readiness Supplemental Evaluation"
    if "Phase 6A" in next_text:
        current_task = "Phase 6A - Journal-Neutral English Manuscript Draft"
    if "Phase 6B" in next_text:
        current_task = "Phase 6B - SIVP Submission-Source Preparation"
    if "Phase 7A" in next_text:
        current_task = "Phase 7A - Final SIVP Asset Readiness and Author Metadata Intake"
    if "Phase 7B" in next_text:
        current_task = "Phase 7B - Publication-State Reconciliation and Submission-Input Ledger"
    if current_task == "NA" and "Phase 3B" in next_text:
        current_task = "Phase 3B - Split Integrity and Model-Selection Audit"
    if current_task == "NA" and "Phase 3A" in next_text:
        current_task = "Phase 3A - Dropout-Ratio Ablation and Paper Evidence Package"
    if current_goal == "NA" and acrf_evidence:
        current_goal = "Implement, train, evaluate, and summarize the E5 ACRF ablation."
    if mscd_evidence:
        current_goal = "Implement, train, evaluate, and summarize the E6 MSCD training-strategy ablation."
    if "Phase 3A" in next_text:
        current_goal = "Train E3/E4 dropout-ratio ablations and build qualitative evidence package."
    if "Phase 3B" in next_text:
        current_goal = "Audit split integrity and correct E2/E4 model-selection positioning."
    if "Phase 3C" in next_text:
        current_goal = "Audit exact RGB-content cross-split duplication and propose leakage-aware blocked split candidates."
    if "Phase 4A" in next_text:
        current_goal = "Train and evaluate B0/B1/B2/B4 on the validated block64/guard16 clean split."
    if "Phase 4B" in next_text:
        current_goal = "Train and evaluate R0/R1/R2/R4 at seeds 0 and 2 on the frozen clean block64/guard16 split."
    if "Phase 5A" in next_text:
        current_goal = "Complete paper-readiness evidence: YOLO11n RGB baseline, efficiency, alpha, qualitative, and convergence audits."
    if "Phase 6A" in next_text:
        current_goal = "Create a complete journal-neutral English manuscript package from frozen clean-split evidence."
    if "Phase 6B" in next_text:
        current_goal = "Prepare a pre-final SIVP LaTeX source package, metadata placeholders, and compliance audits."
    if "Phase 7A" in next_text:
        current_goal = (
            "Prepare final SIVP figure/table readiness, author metadata intake, and compile-blocker tracking "
            "without retraining models or changing experimental evidence."
        )
    if "Phase 7B" in next_text:
        current_goal = (
            "Reconcile the official clean blocked-split R4 manuscript headline with legacy random-split summaries "
            "and create the strict-preflight final-submission input ledger."
        )

    lines = [
        "# Experiment Status",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"Handoff source: `{HANDOFF_PATH}`" if HANDOFF_PATH.exists() else "Handoff source: `NA`",
        "",
        "## Publication headline model",
        "",
        f"- Official clean blocked-split manuscript headline: {PUBLICATION_HEADLINE['model']} on `{PUBLICATION_HEADLINE['protocol']}`, seeds {PUBLICATION_HEADLINE['seeds']}.",
        f"- Controlled-seed means: F1@0.50 {PUBLICATION_HEADLINE['F1@0.50']}, AP50 {PUBLICATION_HEADLINE['AP50']}, AP75 {PUBLICATION_HEADLINE['AP75']}, w/o RGB AP50 {PUBLICATION_HEADLINE['w/o RGB AP50']}, w/o Thermal AP50 {PUBLICATION_HEADLINE['w/o Thermal AP50']}, w/o Event AP50 {PUBLICATION_HEADLINE['w/o Event AP50']}.",
        f"- Phase 4B decision: {PUBLICATION_HEADLINE['decision']}.",
        "- Former E0-E6 random-split results are historical/exploratory diagnostics only and must not be described as the current best or manuscript headline.",
        "",
        "## Legacy random-split historical ranking",
        "",
        f"- Legacy random-split AP50 leader: {na(best_ap50.get('Experiment') if best_ap50 else None)} {na(best_ap50.get('Method') if best_ap50 else None)} ({na(best_ap50.get('AP50') if best_ap50 else None)})",
        f"- Legacy random-split AP75 leader: {na(best_ap75.get('Experiment') if best_ap75 else None)} {na(best_ap75.get('Method') if best_ap75 else None)} ({na(best_ap75.get('AP75') if best_ap75 else None)})",
        "",
        "## Historical/exploratory random-split experiments",
        "",
    ]

    eval_headers = ["Experiment", "Method", "Precision", "Recall", "AP50", "AP75", "GT boxes", "Predictions", "Mean Confidence"]
    lines.extend(table(eval_headers, eval_rows))

    lines += [
        "",
        "### Best threshold by F1",
        "",
    ]
    threshold_headers = ["Method", "Threshold", "Precision", "Recall", "F1", "AP50", "AP75", "Predictions"]
    lines.extend(table(threshold_headers, threshold_best))

    lines += [
        "",
        "### Missing modality AP50",
        "",
    ]
    missing_headers = ["Method", "Full", "w/o RGB", "w/o Thermal", "w/o Event", "RGB only", "Thermal only", "Event only"]
    lines.extend(table(missing_headers, missing_ap50))

    lines += [
        "",
        "### Missing modality AP75",
        "",
    ]
    lines.extend(table(missing_headers, missing_ap75))

    lines += [
        "",
        "### Model profile",
        "",
    ]
    profile_headers = ["Model", "Params", "Trainable Params", "GFLOPs", "FPS", "Latency ms/img", "CUDA Memory MB"]
    lines.extend(table(profile_headers, profile))

    lines += [
        "",
        "## Phase 2A outputs",
        "",
        "### Paper main results at score threshold 0.50",
        "",
    ]
    phase2a_main_headers = ["Method", "Threshold", "Precision", "Recall", "F1", "AP50", "AP75", "GT boxes", "Predictions", "Mean Confidence"]
    lines.extend(table(phase2a_main_headers, phase2a_main))

    lines += [
        "",
        "### Phase 2A profile summary",
        "",
    ]
    phase2a_profile_headers = [
        "Model",
        "Path",
        "Batch Size",
        "Img Size",
        "Warmup",
        "Iters",
        "Repeats",
        "Params",
        "FPS mean",
        "Latency ms/img mean",
        "CUDA Memory MB mean",
    ]
    lines.extend(table(phase2a_profile_headers, phase2a_profile_e0 + phase2a_profile_e2))

    lines += [
        "",
        "### Phase 2A brightness-proxy outputs",
        "",
        f"- Rows: {len(phase2a_brightness) if phase2a_brightness else 'NA'}",
        "- Groups: RGB mean-intensity terciles, not day/night labels.",
        "",
        "### Phase 2A alpha outputs",
        "",
        f"- Rows: {len(phase2a_alpha) if phase2a_alpha else 'NA'}",
        "- Modes: full, no_rgb, no_thermal, no_event for E1 and E2.",
        "",
        "",
        "## Current active task",
        "",
        f"- Task file: `docs/NEXT_TASK.md`",
        f"- Current Task: {current_task}",
        f"- Goal: {current_goal}",
        f"- Status: {active_status}",
        "",
        "## Phase 2B ACRF outputs",
        "",
        "- Report: `runs/acrf_evidence_report.md`" if (RUNS_DIR / "acrf_evidence_report.md").exists() else "- Report: NA",
        "- Smoke test: `runs/acrf_smoke_test.md`" if (RUNS_DIR / "acrf_smoke_test.md").exists() else "- Smoke test: NA",
        f"- Evidence rows: {len(acrf_evidence) if acrf_evidence else 'NA'}",
        f"- E5 missing-modality rows: {len(e5_missing) if e5_missing else 'NA'}",
        f"- E5 alpha-mode rows: {len(e5_alpha) if e5_alpha else 'NA'}",
        "",
        "### ACRF evidence summary",
        "",
    ]
    acrf_headers = [
        "Method",
        "Params",
        "Full AP50",
        "Full AP75",
        "P@0.50",
        "R@0.50",
        "F1@0.50",
        "w/o RGB AP50",
        "w/o Thermal AP50",
        "w/o Event AP50",
        "Mean Missing-Modality AP50",
    ]
    lines.extend(table(acrf_headers, acrf_evidence))

    lines += [
        "",
        "## Phase 2C MSCD outputs",
        "",
        "- Report: `runs/mscd_evidence_report.md`" if (RUNS_DIR / "mscd_evidence_report.md").exists() else "- Report: NA",
        "- Phase 2C report: `runs/phase2c_report.md`" if (RUNS_DIR / "phase2c_report.md").exists() else "- Phase 2C report: NA",
        "- Smoke test: `runs/mscd_smoke_test.md`" if (RUNS_DIR / "mscd_smoke_test.md").exists() else "- Smoke test: NA",
        f"- Evidence rows: {len(mscd_evidence) if mscd_evidence else 'NA'}",
        f"- E6 missing-modality rows: {len(e6_missing) if e6_missing else 'NA'}",
        "",
        "### MSCD evidence summary",
        "",
    ]
    mscd_headers = [
        "Method",
        "Extra inference params",
        "Full AP50",
        "Full AP75",
        "P@0.50",
        "R@0.50",
        "F1@0.50",
        "w/o RGB AP50",
        "w/o Thermal AP50",
        "w/o Event AP50",
        "Mean Missing-Modality AP50",
    ]
    lines.extend(table(mscd_headers, mscd_evidence))

    lines += [
        "",
        "## Phase 3A outputs",
        "",
        "- Dropout report: `runs/dropout_ablation_summary.md`" if (RUNS_DIR / "dropout_ablation_summary.md").exists() else "- Dropout report: NA",
        "- Qualitative report: `runs/qualitative_cases_summary.md`" if (RUNS_DIR / "qualitative_cases_summary.md").exists() else "- Qualitative report: NA",
        "- Phase 3A report: `runs/phase3a_report.md`" if phase3a_report_exists else "- Phase 3A report: NA",
        f"- Dropout ablation rows: {len(dropout_ablation) if dropout_ablation else 'NA'}",
        f"- Qualitative manifest rows: {len(qualitative_manifest) if qualitative_manifest else 'NA'}",
        "",
        "### Dropout-ratio ablation",
        "",
    ]
    dropout_headers = [
        "Method",
        "Dropout Ratio",
        "P@0.50",
        "R@0.50",
        "F1@0.50",
        "Full AP50",
        "Full AP75",
        "w/o RGB AP50",
        "w/o Thermal AP50",
        "w/o Event AP50",
        "Mean Missing-Modality AP50",
    ]
    lines.extend(table(dropout_headers, dropout_ablation))

    lines += [
        "",
        "## Phase 3B outputs",
        "",
        "- Split-integrity report: `runs/split_integrity_summary.md`" if (RUNS_DIR / "split_integrity_summary.md").exists() else "- Split-integrity report: NA",
        "- Dropout selection note: `runs/dropout_ratio_selection_note.md`" if (RUNS_DIR / "dropout_ratio_selection_note.md").exists() else "- Dropout selection note: NA",
        "- Phase 3B report: `runs/phase3b_report.md`" if phase3b_report_exists else "- Phase 3B report: NA",
        f"- Split summary rows: {len(split_integrity) if split_integrity else 'NA'}",
        f"- Manual-review rows: {len(split_manual_review) if split_manual_review else 'NA'}",
        "",
        "### Split-integrity summary",
        "",
    ]
    split_headers = ["Metric", "Value", "Notes"]
    lines.extend(table(split_headers, split_integrity))

    lines += [
        "",
        "## Phase 3C outputs",
        "",
        "- RGB duplicate report: `runs/rgb_cross_split_duplicate_summary.md`" if (RUNS_DIR / "rgb_cross_split_duplicate_summary.md").exists() else "- RGB duplicate report: NA",
        "- Blocked split report: `runs/blocked_split_proposal_summary.md`" if (RUNS_DIR / "blocked_split_proposal_summary.md").exists() else "- Blocked split report: NA",
        "- RGB strata report: `runs/rgb_separation_strata_summary.md`" if (RUNS_DIR / "rgb_separation_strata_summary.md").exists() else "- RGB strata report: NA",
        "- Phase 3C report: `runs/phase3c_report.md`" if phase3c_report_exists else "- Phase 3C report: NA",
        f"- RGB duplicate summary rows: {len(rgb_duplicate_summary) if rgb_duplicate_summary else 'NA'}",
        f"- Blocked split candidate rows: {len(blocked_split_summary) if blocked_split_summary else 'NA'}",
        f"- RGB separation strata rows: {len(rgb_strata_summary) if rgb_strata_summary else 'NA'}",
        "",
        "### RGB duplicate summary",
        "",
    ]
    lines.extend(table(split_headers, rgb_duplicate_summary))

    lines += [
        "",
        "### Blocked split candidates",
        "",
    ]
    blocked_headers = [
        "candidate",
        "block_size",
        "guard_band",
        "train_images",
        "val_images",
        "guard_images",
        "val_share_all_images",
        "exact_rgb_matched_val_images",
        "id_guard_violations",
        "val_gt_boxes",
        "recommended",
    ]
    lines.extend(table(blocked_headers, blocked_split_summary))

    lines += [
        "",
        "### RGB separation strata",
        "",
    ]
    strata_headers = ["subset", "model", "image_count", "gt_boxes", "precision", "recall", "f1", "ap50", "ap75", "predictions"]
    lines.extend(table(strata_headers, rgb_strata_summary))

    lines += [
        "",
        "## Phase 4A outputs",
        "",
        "- Clean split protocol: `runs/clean_block64g16_protocol.md`" if (RUNS_DIR / "clean_block64g16_protocol.md").exists() else "- Clean split protocol: NA",
        "- Clean summary: `runs/clean_block64g16_summary.md`" if (RUNS_DIR / "clean_block64g16_summary.md").exists() else "- Clean summary: NA",
        "- Phase 4A report: `runs/phase4a_report.md`" if phase4a_report_exists else "- Phase 4A report: NA",
        f"- Clean summary rows: {len(clean_block_summary) if clean_block_summary else 'NA'}",
        "",
        "### Clean block64/guard16 summary",
        "",
    ]
    clean_headers = [
        "Method",
        "Dropout Ratio",
        "Params",
        "P@0.50",
        "R@0.50",
        "F1@0.50",
        "Full AP50",
        "Full AP75",
        "w/o RGB AP50",
        "w/o Thermal AP50",
        "w/o Event AP50",
    ]
    lines.extend(table(clean_headers, clean_block_summary))

    lines += [
        "",
        "## Phase 4B outputs",
        "",
        "- Seed reproducibility smoke: `runs/seed_reproducibility_smoke.md`" if seed_smoke_exists else "- Seed reproducibility smoke: NA",
        "- Seed replication summary: `runs/clean_block64g16_seed_replication.md`"
        if (RUNS_DIR / "clean_block64g16_seed_replication.md").exists()
        else "- Seed replication summary: NA",
        "- Phase 4B report: `runs/phase4b_report.md`" if phase4b_report_exists else "- Phase 4B report: NA",
        f"- Seed replication rows: {len(clean_seed_replication) if clean_seed_replication else 'NA'}",
        f"- Decision: {phase4b_decision or 'NA'}",
        "",
        "### Controlled-seed clean block64/guard16 summary",
        "",
    ]
    seed_headers = [
        "Variant",
        "Seed",
        "Dropout Ratio",
        "P@0.50",
        "R@0.50",
        "F1@0.50",
        "AP50",
        "AP75",
        "w/o RGB AP50",
        "w/o Thermal AP50",
        "w/o Event AP50",
    ]
    lines.extend(table(seed_headers, clean_seed_replication))

    lines += [
        "",
        "## Phase 5A outputs",
        "",
        "- Phase 5A report: `runs/phase5a_report.md`" if phase5a_report_exists else "- Phase 5A report: NA",
        "- Paper-readiness summary: `runs/paper_readiness_summary.csv`" if paper_readiness else "- Paper-readiness summary: NA",
        "- YOLO11n protocol: `runs/yolo11n_rgb_baseline_protocol.md`"
        if (RUNS_DIR / "yolo11n_rgb_baseline_protocol.md").exists()
        else "- YOLO11n protocol: NA",
        f"- Convergence rows: {len(clean_convergence) if clean_convergence else 'NA'}",
        f"- Efficiency rows: {len(clean_efficiency) if clean_efficiency else 'NA'}",
        f"- R4 reliability-weight rows: {len(r4_reliability_audit) if r4_reliability_audit else 'NA'}",
        f"- Qualitative manifest rows: {len(clean_qualitative) if clean_qualitative else 'NA'}",
        f"- YOLO11n eval rows: {len(yolo_seed0) + len(yolo_seed2)}",
        f"- Decision: {phase5a_decision or 'NA'}",
        "",
        "### YOLO11n RGB-only baseline",
        "",
    ]
    yolo_headers = [
        "Method",
        "Seed",
        "Precision",
        "Recall",
        "F1",
        "AP50",
        "AP75",
        "GT boxes",
        "Predictions",
        "Mean Confidence",
    ]
    lines.extend(table(yolo_headers, yolo_seed0 + yolo_seed2))

    lines += [
        "",
        "### Clean efficiency profile",
        "",
    ]
    clean_eff_headers = [
        "Model",
        "Path",
        "Params",
        "FPS mean",
        "Latency ms/img mean",
        "CUDA Memory MB mean",
        "Note",
    ]
    lines.extend(table(clean_eff_headers, clean_efficiency))

    lines += [
        "",
        "## Phase 6A outputs",
        "",
        "- Manuscript README: `manuscript/README.md`" if (manuscript_dir / "README.md").exists() else "- Manuscript README: NA",
        "- Draft manuscript: `manuscript/RA_RepDet_manuscript_v1.md`"
        if (manuscript_dir / "RA_RepDet_manuscript_v1.md").exists()
        else "- Draft manuscript: NA",
        "- Phase 6A report: `runs/phase6a_manuscript_report.md`" if phase6a_report_exists else "- Phase 6A report: NA",
        "- Figure manifest: `manuscript/figures/figure_manifest.md`"
        if (manuscript_dir / "figures" / "figure_manifest.md").exists()
        else "- Figure manifest: NA",
        "- Claim ledger: `manuscript/submission_notes/claim_ledger.md`"
        if (manuscript_dir / "submission_notes" / "claim_ledger.md").exists()
        else "- Claim ledger: NA",
        "- Self-audit: `manuscript/submission_notes/manuscript_self_audit.md`"
        if (manuscript_dir / "submission_notes" / "manuscript_self_audit.md").exists()
        else "- Self-audit: NA",
        f"- Table CSV files: {phase6a_table_csv_count}",
        f"- Table Markdown files: {phase6a_table_md_count}",
        f"- Figure source CSV files: {phase6a_figure_source_count}",
        f"- Verified reference inventory rows: {phase6a_reference_count}",
        f"- Decision: {phase6a_decision or 'NA'}",
        "",
        "## Phase 6B outputs",
        "",
        "- SIVP README: `submission/sivp/README.md`" if (submission_dir / "README.md").exists() else "- SIVP README: NA",
        "- Main LaTeX source: `submission/sivp/tex/main.tex`"
        if (submission_dir / "tex" / "main.tex").exists()
        else "- Main LaTeX source: NA",
        "- Body LaTeX source: `submission/sivp/tex/ra_repdet_sivp.tex`"
        if (submission_dir / "tex" / "ra_repdet_sivp.tex").exists()
        else "- Body LaTeX source: NA",
        "- BibTeX references: `submission/sivp/tex/references.bib`"
        if (submission_dir / "tex" / "references.bib").exists()
        else "- BibTeX references: NA",
        "- Phase 6B report: `runs/phase6b_sivp_preparation_report.md`" if phase6b_report_exists else "- Phase 6B report: NA",
        "- Figure insertion map: `submission/sivp/figures/FINAL_ASSET_INSERTION_MAP.md`"
        if (submission_dir / "figures" / "FINAL_ASSET_INSERTION_MAP.md").exists()
        else "- Figure insertion map: NA",
        "- Table insertion map: `submission/sivp/tables/FINAL_TABLE_INSERTION_MAP.md`"
        if (submission_dir / "tables" / "FINAL_TABLE_INSERTION_MAP.md").exists()
        else "- Table insertion map: NA",
        f"- Template/LaTeX source files: {phase6b_tex_source_count}",
        f"- Metadata template files: {phase6b_metadata_count}",
        f"- Review/audit files: {phase6b_review_count}",
        f"- Decision: {phase6b_decision or 'NA'}",
        "",
        "## Phase 7B outputs",
        "",
        "- Reconciliation report: `runs/phase7b_publication_state_reconciliation.md`" if phase7b_report_exists else "- Reconciliation report: NA",
        "- Input ledger: `submission/sivp/metadata/FINAL_SUBMISSION_INPUT_LEDGER.md`" if phase7b_ledger_md_exists else "- Input ledger: NA",
        "- Input ledger CSV: `submission/sivp/review/FINAL_SUBMISSION_INPUT_LEDGER.csv`" if phase7b_ledger_csv_exists else "- Input ledger CSV: NA",
        f"- Input ledger rows: {phase7b_ledger_rows if phase7b_ledger_csv_exists else 'NA'}",
        "- Decision: PUBLICATION-STATE MISMATCH RESOLVED; STRICT PREFLIGHT REMAINS BLOCKED BY AUTHOR/ASSET INPUTS" if phase7b_report_exists else "- Decision: NA",
        "",
        "",
        "## Pending tasks",
        "",
    ]
    lines.extend(f"- {item}" for item in handoff_pending_tasks())

    lines += [
        "",
        "## Known metric caveats",
        "",
        "- Precision in the first-batch eval at score threshold 0.001 is artificially low because many low-confidence FCOS predictions are retained.",
        "- AP50/AP75 are computed by score sorting and are not directly tied to the display threshold.",
        "- Threshold sweep indicates 0.50 is the best F1 threshold for E0/E1/E2 in the current val split.",
        "- Missing-modality tables use score threshold 0.05.",
        "- Current AP implementation is project-local and does not depend on pycocotools.",
        "- Phase 3C RGB-separation strata are diagnostics only and are not a clean independent test set.",
        "- Phase 4A clean-split results use block64_guard16_seed0 only and should not be mixed with former random-split metrics.",
        "- Phase 4B controlled-seed results use the same frozen block64_guard16_seed0 split with explicit seeds 0 and 2.",
        "- Phase 4B still uses only two seeds; do not claim statistical significance.",
        "- Phase 5A YOLO11n is an RGB-only external baseline and not an architecture-only ablation.",
        "- Phase 6A manuscript is journal-neutral and citation style remains pending target journal selection.",
        "- Phase 6B source package is pre-final and uses placeholders for final figures, tables, author details, and declarations.",
        "- Phase 6B dry-run compilation was skipped if the local LaTeX environment lacks required Springer dependencies.",
        "- Phase 7A is an asset-readiness and metadata-intake phase; it must not change clean-split metrics or retrain models.",
        "- Phase 7B reconciles publication-state documentation only; it does not change metrics, checkpoints, splits, source data, or model code.",
        "",
        "## Important research decisions",
        "",
        "- Missing txt labels are treated as empty-target images.",
        "- TriAir class 0 is shifted to torchvision label 1; background remains label 0.",
        "- E0/E1/E2 completed 50-epoch first-batch experiments and should not be retrained without explicit instruction.",
        "- Legacy random-split E2 is the strongest robustness-oriented E-run by missing-modality AP50/AP75, but it is not the manuscript headline.",
        "- E1 has the highest F1 in the threshold sweep at threshold 0.50.",
        "- E5 ACRF enforces exact zero alpha for synthetic absent modalities, but should remain an ablation unless the paper prioritizes alpha correctness over E2 full-modality AP.",
        "- E6 MSCD keeps E2 inference architecture unchanged; use it as the main model only if the Phase 2C decision rule accepts it.",
        "- Phase 3A should be used to justify the selected modality-dropout ratio without adding a new model family.",
        "- Phase 3B corrects the ratio interpretation: E2 is accuracy-first, E4 is robustness-first; no ratio is universally dominant in the current single-seed ablation.",
        "- If Phase 3C confirms exact RGB-content overlap, do not use the random split as a publication-grade independent benchmark.",
        "- Phase 4A is the first clean blocked-split comparison and is single training-seed evidence only.",
        f"- Official manuscript headline: {PUBLICATION_HEADLINE['model']} on `{PUBLICATION_HEADLINE['protocol']}` with controlled seeds {PUBLICATION_HEADLINE['seeds']}.",
        f"- Phase 4B decision gate: {phase4b_decision or 'NA'}.",
        f"- Phase 5A decision gate: {phase5a_decision or 'NA'}.",
        f"- Phase 6A decision gate: {phase6a_decision or 'NA'}.",
        f"- Phase 6B decision gate: {phase6b_decision or 'NA'}.",
        "- Phase 7A starts from the completed Phase 6B SIVP source skeleton and should replace placeholders only after author approval.",
        "- Phase 7B final-submission ledger is the closure checklist for strict V18 preflight blockers.",
        "",
        "## Files or scripts currently under review",
        "",
        "- `AGENTS.md`",
        "- `docs/NEXT_TASK.md`",
        "- `docs/EXPERIMENT_STATUS.md`",
        "- `docs/PROJECT_CONTEXT.md`",
        "- `rarepdet/tools/update_project_status.py`",
        "- `rarepdet/tools/finish_task.ps1`",
        "- `rarepdet/tools/audit_rgb_cross_split_duplicates.py`",
        "- `rarepdet/tools/propose_blocked_split.py`",
        "- `rarepdet/tools/build_rgb_separation_subsets.py`",
        "- `rarepdet/tools/validate_clean_block64_protocol.py`",
        "- `rarepdet/tools/build_clean_block64_summary.py`",
        "- `runs/handoff_latest.md`",
        "- `runs/handoff_latest.json`",
        "",
    ]
    return "\n".join(lines)


def main():
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    STATUS_PATH.write_text(build_status(), encoding="utf-8")
    print(f"Saved: {STATUS_PATH}")


if __name__ == "__main__":
    main()
