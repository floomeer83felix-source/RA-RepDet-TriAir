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
    ("E0", "Early Fusion", RUNS_DIR / "E0_early_repvit_fcos_e50"),
    ("E1", "Reliability Fusion", RUNS_DIR / "E1_reliability_repvit_fcos_e50"),
    ("E2", "Reliability + Dropout 0.15", RUNS_DIR / "E2_reliability_dropout015_repvit_fcos_e50"),
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
    for exp_id, method, exp_dir in EXPERIMENTS:
        values = read_key_values(exp_dir / "eval" / "eval_results.txt")
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

    current_task = first_paragraph(next_sections.get("Current Task", "NA"))
    current_goal = first_paragraph(next_sections.get("Goal", "NA"))

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
        "## Current active task",
        "",
        f"- Task file: `docs/NEXT_TASK.md`",
        f"- Current Task: {current_task}",
        f"- Goal: {current_goal}",
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
