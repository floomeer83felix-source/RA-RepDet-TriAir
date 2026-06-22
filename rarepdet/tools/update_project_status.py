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

    active_status = "completed" if phase3b_report_exists and split_integrity else "pending"
    current_task = first_paragraph(next_sections.get("Current Task", "NA"))
    current_goal = first_paragraph(next_sections.get("Goal", "NA"))
    if current_task == "NA" and "Phase 2B" in read_text(NEXT_TASK_PATH):
        current_task = "Phase 2B - Availability-Conditioned Reliability Fusion (ACRF)"
    if current_task == "NA" and "Phase 2C" in read_text(NEXT_TASK_PATH):
        current_task = "Phase 2C - Modality-Subset Consistency Distillation (MSCD)"
    if current_task == "NA" and "Phase 3B" in read_text(NEXT_TASK_PATH):
        current_task = "Phase 3B - Split Integrity and Model-Selection Audit"
    if current_task == "NA" and "Phase 3A" in read_text(NEXT_TASK_PATH):
        current_task = "Phase 3A - Dropout-Ratio Ablation and Paper Evidence Package"
    if current_goal == "NA" and acrf_evidence:
        current_goal = "Implement, train, evaluate, and summarize the E5 ACRF ablation."
    if mscd_evidence:
        current_goal = "Implement, train, evaluate, and summarize the E6 MSCD training-strategy ablation."
    if "Phase 3A" in read_text(NEXT_TASK_PATH):
        current_goal = "Train E3/E4 dropout-ratio ablations and build qualitative evidence package."
    if "Phase 3B" in read_text(NEXT_TASK_PATH):
        current_goal = "Audit split integrity and correct E2/E4 model-selection positioning."

    lines = [
        "# Experiment Status",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"Handoff source: `{HANDOFF_PATH}`" if HANDOFF_PATH.exists() else "Handoff source: `NA`",
        "",
        "## Current best model",
        "",
        f"- Best AP50: {na(best_ap50.get('Experiment') if best_ap50 else None)} {na(best_ap50.get('Method') if best_ap50 else None)} ({na(best_ap50.get('AP50') if best_ap50 else None)})",
        f"- Best AP75: {na(best_ap75.get('Experiment') if best_ap75 else None)} {na(best_ap75.get('Method') if best_ap75 else None)} ({na(best_ap75.get('AP75') if best_ap75 else None)})",
        "",
        "## Latest completed experiments",
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
        "",
        "## Important research decisions",
        "",
        "- Missing txt labels are treated as empty-target images.",
        "- TriAir class 0 is shifted to torchvision label 1; background remains label 0.",
        "- E0/E1/E2 completed 50-epoch first-batch experiments and should not be retrained without explicit instruction.",
        "- E2 is the strongest robustness-oriented model by missing-modality AP50/AP75.",
        "- E1 has the highest F1 in the threshold sweep at threshold 0.50.",
        "- E5 ACRF enforces exact zero alpha for synthetic absent modalities, but should remain an ablation unless the paper prioritizes alpha correctness over E2 full-modality AP.",
        "- E6 MSCD keeps E2 inference architecture unchanged; use it as the main model only if the Phase 2C decision rule accepts it.",
        "- Phase 3A should be used to justify the selected modality-dropout ratio without adding a new model family.",
        "- Phase 3B corrects the ratio interpretation: E2 is accuracy-first, E4 is robustness-first; no ratio is universally dominant in the current single-seed ablation.",
        "",
        "## Files or scripts currently under review",
        "",
        "- `AGENTS.md`",
        "- `docs/NEXT_TASK.md`",
        "- `docs/EXPERIMENT_STATUS.md`",
        "- `docs/PROJECT_CONTEXT.md`",
        "- `rarepdet/tools/update_project_status.py`",
        "- `rarepdet/tools/finish_task.ps1`",
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
