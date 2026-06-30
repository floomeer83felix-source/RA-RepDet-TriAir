#!/usr/bin/env python
"""Run and package the V23 standardized-threshold reevaluation.

This script does not train models. It verifies the frozen clean split and the
existing R0/R1/R2/R4 checkpoints, runs the project evaluation scripts with a
detector-output threshold of 0.001 and a metric operating threshold of 0.50,
then writes CSV/MD/TXT audit files for manuscript reconciliation.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
import zipfile


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results_v23"
RAW = RESULTS / "raw_eval_outputs"
HANDOFF = ROOT / "RA_RepDet_V23_StandardizedReevaluation_Handoff"
DATA_ROOT = Path(r"D:\download\triair")
SPLIT_TRAIN = ROOT / "runs" / "blocked_split_candidates" / "block64_guard16_seed0_train.txt"
SPLIT_VAL = ROOT / "runs" / "blocked_split_candidates" / "block64_guard16_seed0_val.txt"
SPLIT_GUARD = ROOT / "runs" / "blocked_split_candidates" / "block64_guard16_seed0_guard.txt"
DETECTOR_SCORE_THR = 0.001
METRIC_SCORE_THR = 0.50
IMG_SIZE = 640
BATCH_SIZE = 4
NUM_WORKERS = 0
DEVICE = "cuda"
NMS_THRESH = 0.6
DETECTIONS_PER_IMG = 100


RUNS = [
    {
        "variant": "R0 Early Fusion",
        "run_id": "R0_seed0",
        "seed": 0,
        "model_type": "early",
        "modality_dropout": "NA",
        "run_dir": ROOT / "runs" / "R0_early_seed0_block64g16_e50",
    },
    {
        "variant": "R0 Early Fusion",
        "run_id": "R0_seed2",
        "seed": 2,
        "model_type": "early",
        "modality_dropout": "NA",
        "run_dir": ROOT / "runs" / "R0_early_seed2_block64g16_e50",
    },
    {
        "variant": "R1 Reliability p=0.00",
        "run_id": "R1_seed0",
        "seed": 0,
        "model_type": "reliability",
        "modality_dropout": "0.00",
        "run_dir": ROOT / "runs" / "R1_reliability_p000_seed0_block64g16_e50",
    },
    {
        "variant": "R1 Reliability p=0.00",
        "run_id": "R1_seed2",
        "seed": 2,
        "model_type": "reliability",
        "modality_dropout": "0.00",
        "run_dir": ROOT / "runs" / "R1_reliability_p000_seed2_block64g16_e50",
    },
    {
        "variant": "R2 Reliability p=0.15",
        "run_id": "R2_seed0",
        "seed": 0,
        "model_type": "reliability",
        "modality_dropout": "0.15",
        "run_dir": ROOT / "runs" / "R2_reliability_p015_seed0_block64g16_e50",
    },
    {
        "variant": "R2 Reliability p=0.15",
        "run_id": "R2_seed2",
        "seed": 2,
        "model_type": "reliability",
        "modality_dropout": "0.15",
        "run_dir": ROOT / "runs" / "R2_reliability_p015_seed2_block64g16_e50",
    },
    {
        "variant": "R4 Reliability p=0.20",
        "run_id": "R4_seed0",
        "seed": 0,
        "model_type": "reliability",
        "modality_dropout": "0.20",
        "run_dir": ROOT / "runs" / "R4_reliability_p020_seed0_block64g16_e50",
    },
    {
        "variant": "R4 Reliability p=0.20",
        "run_id": "R4_seed2",
        "seed": 2,
        "model_type": "reliability",
        "modality_dropout": "0.20",
        "run_dir": ROOT / "runs" / "R4_reliability_p020_seed2_block64g16_e50",
    },
]

MISSING_RUNS = [run for run in RUNS if run["model_type"] == "reliability"]
MANUSCRIPT_MISSING_MODES = {"full", "no_rgb", "no_thermal", "no_event"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return str(path)


def git_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True, stderr=subprocess.STDOUT).strip()
    except Exception as exc:
        return f"NA ({exc})"


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{key: row.get(key, "NA") for key in fieldnames} for row in rows])


def read_csv(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def safe_float(value) -> float | None:
    if value in (None, "", "NA"):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def aggregate(rows: list[dict], group_fields: list[str], metric_fields: list[str]) -> list[dict]:
    grouped: dict[tuple, list[dict]] = {}
    for row in rows:
        key = tuple(row[field] for field in group_fields)
        grouped.setdefault(key, []).append(row)

    out = []
    for key, items in sorted(grouped.items()):
        for metric in metric_fields:
            seed_values = {}
            values = []
            for item in items:
                value = safe_float(item.get(metric))
                if value is None:
                    continue
                seed = str(item.get("seed", item.get("Seed", "NA")))
                seed_values[seed] = value
                values.append(value)
            if not values:
                continue
            row = {field: key[index] for index, field in enumerate(group_fields)}
            row.update(
                {
                    "metric": metric,
                    "mean": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "range": max(values) - min(values),
                    "seed0": seed_values.get("0", "NA"),
                    "seed2": seed_values.get("2", "NA"),
                    "detector_score_thr": DETECTOR_SCORE_THR,
                    "metric_score_thr": METRIC_SCORE_THR,
                }
            )
            out.append(row)
    return out


def run_command(command: list[str], stdout_path: Path, stderr_path: Path) -> int:
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    start = time.time()
    with stdout_path.open("w", encoding="utf-8") as out, stderr_path.open("w", encoding="utf-8") as err:
        out.write("$ " + " ".join(command) + "\n\n")
        out.flush()
        code = subprocess.call(command, cwd=ROOT, stdout=out, stderr=err)
        out.write(f"\nreturncode: {code}\nruntime_seconds: {time.time() - start:.3f}\n")
    return code


def detect_v22_sources() -> list[Path]:
    candidates = []
    for base in [ROOT, Path(r"D:\download"), Path.home() / "Downloads", Path.home() / "Desktop"]:
        if not base.exists():
            continue
        try:
            candidates.extend(base.rglob("RA_RepDet_SIVP_v22_MethodsMetricsPolish_Source*"))
        except OSError:
            pass
    return sorted(candidates)


def precheck(blockers: list[str]) -> list[dict]:
    manifest_rows = []
    v22_sources = detect_v22_sources()
    if not v22_sources:
        blockers.append("Missing exact v22 manuscript source package: RA_RepDet_SIVP_v22_MethodsMetricsPolish_Source*")
    if not DATA_ROOT.exists():
        blockers.append(f"Missing TriAir data root: {DATA_ROOT}")

    for split in [SPLIT_TRAIN, SPLIT_VAL, SPLIT_GUARD]:
        if not split.is_file():
            blockers.append(f"Missing split manifest: {split}")

    git_commit = git_output(["rev-parse", "HEAD"])
    for run in RUNS:
        checkpoint = run["run_dir"] / "weights" / "best.pt"
        status = "ready"
        if not checkpoint.is_file():
            blockers.append(f"Missing checkpoint for {run['run_id']}: {checkpoint}")
            status = "missing_checkpoint"
        if not SPLIT_VAL.is_file():
            status = "missing_split"
        row = {
            "variant": run["variant"],
            "seed": run["seed"],
            "model_type": run["model_type"],
            "modality_dropout": run["modality_dropout"],
            "checkpoint_path": str(checkpoint),
            "checkpoint_sha256": sha256(checkpoint) if checkpoint.is_file() else "NA",
            "split_path": str(SPLIT_VAL),
            "split_sha256": sha256(SPLIT_VAL) if SPLIT_VAL.is_file() else "NA",
            "image_size": IMG_SIZE,
            "batch_size": BATCH_SIZE,
            "device": DEVICE,
            "git_commit": git_commit,
            "status": status,
        }
        manifest_rows.append(row)
    return manifest_rows


def write_manifest_yaml(rows: list[dict], path: Path) -> None:
    lines = [
        "protocol: block64_guard16_seed0",
        f"detector_score_thr: {DETECTOR_SCORE_THR}",
        f"metric_score_thr: {METRIC_SCORE_THR}",
        f"nms_thresh: {NMS_THRESH}",
        f"detections_per_img: {DETECTIONS_PER_IMG}",
        f"data_root: {DATA_ROOT}",
        "runs:",
    ]
    for row in rows:
        lines.append("  -")
        for key, value in row.items():
            text = str(value).replace("\\", "/")
            lines.append(f"    {key}: {json.dumps(text, ensure_ascii=False)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def environment_text() -> str:
    lines = [
        f"timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"cwd: {ROOT}",
        f"git_commit: {git_output(['rev-parse', 'HEAD'])}",
        f"git_log_1: {git_output(['log', '-1', '--oneline'])}",
        f"git_status_short:\n{git_output(['status', '--short'])}",
        f"python: {platform.python_version()}",
        f"os: {platform.platform()}",
    ]
    try:
        import torch
        import torchvision
        import timm
        import numpy

        lines.extend(
            [
                f"torch: {torch.__version__}",
                f"torchvision: {torchvision.__version__}",
                f"timm: {getattr(timm, '__version__', 'NA')}",
                f"numpy: {numpy.__version__}",
                f"torch_cuda: {torch.version.cuda}",
                f"cuda_available: {torch.cuda.is_available()}",
                f"gpu: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NA'}",
            ]
        )
    except Exception as exc:
        lines.append(f"python_env_error: {exc}")
    try:
        smi = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"],
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()
        lines.append(f"nvidia_smi: {smi}")
    except Exception as exc:
        lines.append(f"nvidia_smi_error: {exc}")
    return "\n".join(lines) + "\n"


def build_full_command(run: dict, out_txt: Path) -> list[str]:
    return [
        sys.executable,
        "rarepdet/eval_map.py",
        "--model",
        run["model_type"],
        "--data",
        str(DATA_ROOT),
        "--split-file",
        str(SPLIT_VAL),
        "--weights",
        str(run["run_dir"] / "weights" / "best.pt"),
        "--img-size",
        str(IMG_SIZE),
        "--device",
        DEVICE,
        "--batch-size",
        str(BATCH_SIZE),
        "--num-workers",
        str(NUM_WORKERS),
        "--detector-score-thr",
        str(DETECTOR_SCORE_THR),
        "--metric-score-thr",
        str(METRIC_SCORE_THR),
        "--out",
        str(out_txt),
    ]


def build_missing_command(run: dict, out_dir: Path) -> list[str]:
    return [
        sys.executable,
        "rarepdet/tools/eval_missing_modality.py",
        "--model",
        run["model_type"],
        "--data",
        str(DATA_ROOT),
        "--split-file",
        str(SPLIT_VAL),
        "--weights",
        str(run["run_dir"] / "weights" / "best.pt"),
        "--img-size",
        str(IMG_SIZE),
        "--device",
        DEVICE,
        "--batch-size",
        str(BATCH_SIZE),
        "--num-workers",
        str(NUM_WORKERS),
        "--detector-score-thr",
        str(DETECTOR_SCORE_THR),
        "--metric-score-thr",
        str(METRIC_SCORE_THR),
        "--out",
        str(out_dir),
    ]


def run_evaluations(blockers: list[str]) -> tuple[list[dict], list[dict], list[str]]:
    commands = []
    full_rows = []
    missing_rows = []

    for run in RUNS:
        out_txt = RAW / "full_input" / run["run_id"] / "eval_results.txt"
        command = build_full_command(run, out_txt)
        commands.append(" ".join(command))
        code = run_command(command, out_txt.with_suffix(".stdout.log"), out_txt.with_suffix(".stderr.log"))
        if code != 0:
            blockers.append(f"Full-input eval failed for {run['run_id']} with return code {code}")
            continue
        csv_path = out_txt.with_suffix(".csv")
        rows = read_csv(csv_path)
        if not rows:
            blockers.append(f"Full-input eval CSV missing or empty for {run['run_id']}: {csv_path}")
            continue
        row = rows[0]
        row.update({"variant": run["variant"], "run_id": run["run_id"], "seed": str(run["seed"])})
        full_rows.append(row)

    for run in MISSING_RUNS:
        out_dir = RAW / "missing_modality" / run["run_id"]
        command = build_missing_command(run, out_dir)
        commands.append(" ".join(command))
        code = run_command(command, out_dir / "missing_modality_stdout.log", out_dir / "missing_modality_stderr.log")
        if code != 0:
            blockers.append(f"Missing-modality eval failed for {run['run_id']} with return code {code}")
            continue
        rows = read_csv(out_dir / "missing_modality_results.csv")
        if not rows:
            blockers.append(f"Missing-modality CSV missing or empty for {run['run_id']}")
            continue
        for row in rows:
            mode = row["Mode"]
            row.update(
                {
                    "variant": run["variant"],
                    "run_id": run["run_id"],
                    "seed": str(run["seed"]),
                    "condition": mode,
                    "manuscript_condition": str(mode in MANUSCRIPT_MISSING_MODES).lower(),
                }
            )
            missing_rows.append(row)

    return full_rows, missing_rows, commands


def normalize_full_rows(rows: list[dict]) -> list[dict]:
    out = []
    for row in rows:
        out.append(
            {
                "variant": row["variant"],
                "run_id": row["run_id"],
                "seed": row["seed"],
                "model_type": row["model"],
                "precision": row["precision"],
                "recall": row["recall"],
                "f1": row["f1"],
                "ap50": row["ap50"],
                "ap75": row["ap75"],
                "gt_boxes": row["gt_boxes"],
                "predictions": row["predictions"],
                "mean_confidence": row["mean_confidence"],
                "detector_score_thr": row["detector_score_thr"],
                "metric_score_thr": row["metric_score_thr"],
                "nms_thresh": row["nms_thresh"],
                "detections_per_img": row["detections_per_img"],
                "checkpoint_path": row["weights"],
                "checkpoint_sha256": row["checkpoint_sha256"],
                "split_path": row["split_file"],
                "split_sha256": row["split_sha256"],
                "runtime_seconds": row["runtime_seconds"],
                "fps": row["fps"],
                "gpu": row["env_gpu"],
                "cuda": row["env_torch_cuda"],
                "pytorch": row["env_pytorch"],
                "git_commit": row["git_commit"],
            }
        )
    return out


def normalize_missing_rows(rows: list[dict]) -> list[dict]:
    out = []
    for row in rows:
        out.append(
            {
                "variant": row["variant"],
                "run_id": row["run_id"],
                "seed": row["seed"],
                "condition": row["condition"],
                "manuscript_condition": row["manuscript_condition"],
                "precision": row["Precision"],
                "recall": row["Recall"],
                "f1": row["F1"],
                "ap50": row["AP50"],
                "ap75": row["AP75"],
                "gt_boxes": row["GT boxes"],
                "predictions": row["Predictions"],
                "mean_confidence": row["Mean Confidence"],
                "detector_score_thr": row["Detector Score Thr"],
                "metric_score_thr": row["Metric Score Thr"],
                "nms_thresh": row["NMS Thr"],
                "detections_per_img": row["Detections Per Img"],
                "checkpoint_path": row["Weights"],
                "checkpoint_sha256": row["Checkpoint SHA256"],
                "split_path": row["Split File"],
                "split_sha256": row["Split SHA256"],
                "runtime_seconds": row["Runtime Seconds"],
                "fps": row["FPS"],
                "gpu": row["GPU"],
                "cuda": row["Torch CUDA"],
                "pytorch": row["PyTorch"],
                "git_commit": row["Git Commit"],
            }
        )
    return out


def old_full_rows() -> dict[tuple[str, str, str], float]:
    old = {}
    path = ROOT / "runs" / "clean_block64g16_seed_replication.csv"
    for row in read_csv(path):
        variant = row.get("Variant")
        seed = row.get("Seed")
        if not variant or seed not in {"0", "2"}:
            continue
        mapping = {
            "precision": "P@0.50",
            "recall": "R@0.50",
            "f1": "F1@0.50",
            "ap50": "AP50",
            "ap75": "AP75",
        }
        for metric, col in mapping.items():
            value = safe_float(row.get(col))
            if value is not None:
                old[(variant, seed, metric)] = value
    return old


def old_missing_rows() -> dict[tuple[str, str, str, str], float]:
    old = {}
    path = ROOT / "manuscript" / "tables" / "Table_4_missing_modality_robustness.csv"
    for row in read_csv(path):
        if row.get("Row Type") != "per-seed":
            continue
        value = safe_float(row.get("AP50"))
        if value is not None:
            old[(row["Variant"], row["Seed"], row["Condition"], "ap50")] = value
    return old


def write_diff(full_rows: list[dict], missing_rows: list[dict]) -> list[dict]:
    diff_rows = []
    old_full = old_full_rows()
    for row in full_rows:
        for metric in ["precision", "recall", "f1", "ap50", "ap75"]:
            old_value = old_full.get((row["variant"], row["seed"], metric))
            new_value = safe_float(row.get(metric))
            if old_value is None or new_value is None:
                continue
            diff_rows.append(
                {
                    "table_or_figure": "Table 3 / Fig. 3",
                    "variant": row["variant"],
                    "seed": row["seed"],
                    "condition": "full",
                    "metric": metric,
                    "v22_value": old_value,
                    "v23_value": new_value,
                    "absolute_difference": abs(new_value - old_value),
                    "reason_for_change": "detector-output threshold standardized to 0.001; operating threshold kept at 0.50",
                }
            )

    old_missing = old_missing_rows()
    for row in missing_rows:
        if row["condition"] not in {"no_rgb", "no_thermal", "no_event"}:
            continue
        old_value = old_missing.get((row["variant"], row["seed"], mode_label(row["condition"]), "ap50"))
        new_value = safe_float(row.get("ap50"))
        if old_value is None or new_value is None:
            continue
        diff_rows.append(
            {
                "table_or_figure": "Table 4 / Fig. 4",
                "variant": row["variant"],
                "seed": row["seed"],
                "condition": mode_label(row["condition"]),
                "metric": "ap50",
                "v22_value": old_value,
                "v23_value": new_value,
                "absolute_difference": abs(new_value - old_value),
                "reason_for_change": "missing-modality AP recomputed from detector-output threshold 0.001 candidates",
            }
        )
    fieldnames = [
        "table_or_figure",
        "variant",
        "seed",
        "condition",
        "metric",
        "v22_value",
        "v23_value",
        "absolute_difference",
        "reason_for_change",
    ]
    write_csv(RESULTS / "result_diff_v22_to_v23.csv", diff_rows, fieldnames)
    return diff_rows


def mode_label(mode: str) -> str:
    return {
        "full": "full",
        "no_rgb": "w/o RGB",
        "no_thermal": "w/o Thermal",
        "no_event": "w/o Event",
        "rgb_only": "RGB only",
        "thermal_only": "Thermal only",
        "event_only": "Event only",
    }.get(mode, mode)


def write_reconciliation(full_rows: list[dict], full_agg: list[dict], missing_rows: list[dict], blockers: list[str]) -> None:
    r4_old = {
        "ap50": 0.962495,
        "ap75": 0.891266,
        "f1": 0.920861,
    }
    r4_new = {
        row["metric"]: row["mean"]
        for row in full_agg
        if row["variant"] == "R4 Reliability p=0.20" and row["metric"] in r4_old
    }
    lines = [
        "# V23 Result Reconciliation",
        "",
        "All detector outputs were generated with a detector-output score threshold of 0.001. AP50 and AP75 were computed from this common candidate set. Precision, recall, and F1 were computed at an operating threshold of 0.50.",
        "",
        "AP50/AP75 are project-local single-class metrics and are not COCO AP50:95.",
        "",
        "## R4 Main Result",
        "",
        "| Metric | V22 | V23 |",
        "| --- | --- | --- |",
    ]
    for metric in ["ap50", "ap75", "f1"]:
        lines.append(f"| {metric.upper()} | {r4_old.get(metric, 'NA')} | {r4_new.get(metric, 'NA')} |")
    lines.extend(
        [
            "",
            "## Completeness",
            "",
            f"- Full-input runs completed: {len(full_rows)} / 8",
            f"- Missing-modality rows completed: {len(missing_rows)} / 42 total rows (including supplementary single-modality rows)",
            f"- Manuscript missing-modality cells completed: {sum(1 for row in missing_rows if row['condition'] in MANUSCRIPT_MISSING_MODES)} / 24",
            "",
            "## Blockers",
            "",
        ]
    )
    if blockers:
        lines.extend(f"- {item}" for item in blockers)
    else:
        lines.append("- None")
    (RESULTS / "result_reconciliation_v23.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_blockers(blockers: list[str]) -> None:
    text = "# RERUN_BLOCKERS\n\n"
    if blockers:
        text += "\n".join(f"- {item}" for item in blockers) + "\n"
    else:
        text += "- None\n"
    (RESULTS / "RERUN_BLOCKERS.md").write_text(text, encoding="utf-8")


def run_preflight(blockers: list[str]) -> str:
    script = ROOT / "scripts" / "preflight_submission.py"
    out = RESULTS / "PREFLIGHT_V23.txt"
    if not script.is_file():
        msg = f"Missing preflight script: {script}"
        blockers.append(msg)
        out.write_text(msg + "\n", encoding="utf-8")
        return "BLOCKED"
    code = run_command([sys.executable, str(script), "--root", str(ROOT)], out, RESULTS / "PREFLIGHT_V23.stderr.log")
    if code != 0:
        blockers.append(f"preflight_submission.py failed with return code {code}")
        return "FAIL"
    text = out.read_text(encoding="utf-8", errors="replace")
    return "PASS" if "PASS" in text else "UNKNOWN"


def try_compile_pdf(blockers: list[str]) -> tuple[str, str]:
    tex = ROOT / "main_sivp_snjnl.tex"
    if not tex.is_file():
        blockers.append(f"Missing SIVP main TeX source: {tex}")
        return "NA", "NA"
    compile_log = RESULTS / "compile.log"
    latexmk_log = RESULTS / "latexmk.log"
    latexmk = shutil.which("latexmk")
    if latexmk:
        code = run_command([latexmk, "-pdf", "-interaction=nonstopmode", str(tex)], latexmk_log, RESULTS / "latexmk.stderr.log")
        compile_log.write_text(latexmk_log.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
    else:
        pdflatex = shutil.which("pdflatex")
        if not pdflatex:
            blockers.append("No latexmk or pdflatex executable found for PDF compilation")
            compile_log.write_text("No latexmk or pdflatex executable found.\n", encoding="utf-8")
            latexmk_log.write_text("No latexmk executable found.\n", encoding="utf-8")
            return "NA", "NA"
        code = run_command([pdflatex, "-interaction=nonstopmode", str(tex)], compile_log, RESULTS / "pdflatex.stderr.log")
        latexmk_log.write_text("latexmk unavailable; pdflatex attempted.\n", encoding="utf-8")
    pdf = tex.with_suffix(".pdf")
    if code != 0 or not pdf.is_file():
        blockers.append(f"LaTeX compilation failed or PDF not produced for {tex}")
        return "NA", "NA"
    target = RESULTS / "final_submission_candidate.pdf"
    shutil.copy2(pdf, target)
    page_count = "NA"
    try:
        import pypdf

        page_count = str(len(pypdf.PdfReader(str(target)).pages))
    except Exception:
        try:
            import PyPDF2

            page_count = str(len(PyPDF2.PdfReader(str(target)).pages))
        except Exception:
            page_count = "unknown"
    return str(target), page_count


def write_audit_files(status: str, blockers: list[str], full_count: int, missing_count: int, preflight: str, page_count: str) -> None:
    lines = [
        status,
        "",
        f"detector_score_thr: {DETECTOR_SCORE_THR}",
        f"metric_score_thr: {METRIC_SCORE_THR}",
        f"full_input_runs_completed: {full_count} / 8",
        f"missing_modality_rows_completed: {missing_count} / 42",
        f"strict_preflight_result: {preflight}",
        f"pdf_page_count: {page_count}",
        "",
        "blockers:",
    ]
    lines.extend(f"- {item}" for item in blockers) if blockers else lines.append("- None")
    (RESULTS / "RERUN_STATUS_V23.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (RESULTS / "MANUSCRIPT_CONSISTENCY_AUDIT_V23.md").write_text(
        "# Manuscript Consistency Audit V23\n\n"
        "BLOCKED: exact v22 source package must be present before manuscript text, tables, figures, and PDF can be certified.\n"
        if blockers
        else "# Manuscript Consistency Audit V23\n\nNo blockers recorded by the orchestration script.\n",
        encoding="utf-8",
    )
    (RESULTS / "FIGURE_TABLE_AUDIT_V23.md").write_text(
        "# Figure/Table Audit V23\n\n"
        "Generated v23 CSV outputs are available under `results_v23/`. Figure/table source replacement is blocked unless the exact v22 manuscript source package is available.\n",
        encoding="utf-8",
    )


def package_handoff(status: str, final_pdf: str) -> Path:
    if HANDOFF.exists():
        shutil.rmtree(HANDOFF)
    (HANDOFF / "manuscript" / "figures").mkdir(parents=True)
    (HANDOFF / "manuscript" / "tables").mkdir(parents=True)
    (HANDOFF / "results_v23").mkdir(parents=True)
    (HANDOFF / "code_changes").mkdir(parents=True)
    (HANDOFF / "audit").mkdir(parents=True)

    for src in [ROOT / "main.tex", ROOT / "main_sivp_snjnl.tex", ROOT / "references.bib"]:
        if src.is_file():
            shutil.copy2(src, HANDOFF / "manuscript" / src.name)
    if final_pdf != "NA" and Path(final_pdf).is_file():
        shutil.copy2(final_pdf, HANDOFF / "manuscript" / "final_submission_candidate.pdf")
    for src in [RESULTS / "compile.log", RESULTS / "latexmk.log"]:
        if src.is_file():
            shutil.copy2(src, HANDOFF / "manuscript" / src.name)
    for src_dir, dst_dir in [
        (ROOT / "manuscript" / "figures", HANDOFF / "manuscript" / "figures"),
        (ROOT / "manuscript" / "tables", HANDOFF / "manuscript" / "tables"),
    ]:
        if src_dir.is_dir():
            for src in src_dir.iterdir():
                if src.is_file() and src.suffix.lower() in {".csv", ".md", ".tex"}:
                    shutil.copy2(src, dst_dir / src.name)

    manifest_lines = []
    for src in (HANDOFF / "manuscript").rglob("*"):
        if src.is_file():
            manifest_lines.append(f"{sha256(src)}  {rel(src)}")
    (HANDOFF / "manuscript" / "source_manifest_sha256.txt").write_text(
        "\n".join(sorted(manifest_lines)) + "\n",
        encoding="utf-8",
    )

    for src in RESULTS.iterdir():
        if src.name in {"raw_eval_outputs"}:
            continue
        if src.is_file() and src.suffix.lower() in {".csv", ".txt", ".md", ".yaml", ".log"}:
            shutil.copy2(src, HANDOFF / "results_v23" / src.name)
    if RAW.is_dir():
        shutil.copytree(RAW, HANDOFF / "results_v23" / "raw_eval_outputs")

    for src in [ROOT / "rarepdet" / "eval_map.py", ROOT / "rarepdet" / "tools" / "eval_missing_modality.py"]:
        shutil.copy2(src, HANDOFF / "code_changes" / src.name)
    diff = subprocess.check_output(
        ["git", "diff", "--", "rarepdet/eval_map.py", "rarepdet/tools/eval_missing_modality.py"],
        cwd=ROOT,
        text=True,
        stderr=subprocess.STDOUT,
    )
    (HANDOFF / "code_changes" / "code_diff_v22_to_v23.patch").write_text(diff, encoding="utf-8")
    (HANDOFF / "code_changes" / "CODE_CHANGE_EXPLANATION.md").write_text(
        "# Code Change Explanation\n\n"
        "- Added explicit `--detector-score-thr` and `--metric-score-thr` arguments.\n"
        "- Removed implicit detector threshold clamping from V23 evaluation paths.\n"
        "- Kept NMS threshold, detections_per_img, model structure, checkpoint, split, and AP implementation unchanged.\n",
        encoding="utf-8",
    )

    audit_map = {
        "RERUN_STATUS_V23.md": "RERUN_STATUS_V23.md",
        "RERUN_BLOCKERS.md": "RERUN_BLOCKERS.md",
        "PREFLIGHT_V23.txt": "PREFLIGHT_V23.txt",
        "MANUSCRIPT_CONSISTENCY_AUDIT_V23.md": "MANUSCRIPT_CONSISTENCY_AUDIT_V23.md",
        "FIGURE_TABLE_AUDIT_V23.md": "FIGURE_TABLE_AUDIT_V23.md",
    }
    for src_name, dst_name in audit_map.items():
        src = RESULTS / src_name
        if src.is_file():
            shutil.copy2(src, HANDOFF / "audit" / dst_name)
    (HANDOFF / "audit" / "FINAL_COMMAND_OUTPUT.txt").write_text(
        f"status: {status}\n"
        f"detector_score_thr: {DETECTOR_SCORE_THR}\n"
        f"metric_score_thr: {METRIC_SCORE_THR}\n"
        f"git_commit: {git_output(['rev-parse', 'HEAD'])}\n",
        encoding="utf-8",
    )
    (HANDOFF / "README_V23_HANDOFF.md").write_text(
        "# RA-RepDet V23 Standardized Reevaluation Handoff\n\n"
        f"- Status: {status}\n"
        f"- Detector-output threshold: {DETECTOR_SCORE_THR}\n"
        f"- Metric operating threshold: {METRIC_SCORE_THR}\n"
        "- This package contains real generated evaluation outputs and audit files. If status is BLOCKED, see `audit/RERUN_BLOCKERS.md`.\n",
        encoding="utf-8",
    )

    zip_path = ROOT / "RA_RepDet_V23_StandardizedReevaluation_Handoff.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for src in HANDOFF.rglob("*"):
            if src.is_file():
                zf.write(src, src.relative_to(HANDOFF.parent))
    return zip_path


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    blockers: list[str] = []
    manifest_rows = precheck(blockers)
    write_manifest_yaml(manifest_rows, RESULTS / "evaluation_manifest_v23.yaml")
    write_csv(
        RESULTS / "checkpoint_manifest_v23.csv",
        manifest_rows,
        [
            "variant",
            "seed",
            "model_type",
            "modality_dropout",
            "checkpoint_path",
            "checkpoint_sha256",
            "split_path",
            "split_sha256",
            "image_size",
            "batch_size",
            "device",
            "git_commit",
            "status",
        ],
    )
    (RESULTS / "evaluation_environment_v23.txt").write_text(environment_text(), encoding="utf-8")

    ready_to_eval = not any("Missing checkpoint" in item or "Missing split" in item or "Missing TriAir" in item for item in blockers)
    commands: list[str] = []
    full_rows_raw: list[dict] = []
    missing_rows_raw: list[dict] = []
    if ready_to_eval:
        full_rows_raw, missing_rows_raw, commands = run_evaluations(blockers)
    else:
        blockers.append("Evaluation skipped because required checkpoint, split, or data input is missing.")

    (RESULTS / "evaluation_commands_v23.txt").write_text("\n\n".join(commands) + "\n", encoding="utf-8")

    full_rows = normalize_full_rows(full_rows_raw)
    missing_rows = normalize_missing_rows(missing_rows_raw)
    write_csv(
        RESULTS / "full_input_per_run.csv",
        full_rows,
        [
            "variant",
            "run_id",
            "seed",
            "model_type",
            "precision",
            "recall",
            "f1",
            "ap50",
            "ap75",
            "gt_boxes",
            "predictions",
            "mean_confidence",
            "detector_score_thr",
            "metric_score_thr",
            "nms_thresh",
            "detections_per_img",
            "checkpoint_path",
            "checkpoint_sha256",
            "split_path",
            "split_sha256",
            "runtime_seconds",
            "fps",
            "gpu",
            "cuda",
            "pytorch",
            "git_commit",
        ],
    )
    write_csv(
        RESULTS / "missing_modality_per_run.csv",
        missing_rows,
        [
            "variant",
            "run_id",
            "seed",
            "condition",
            "manuscript_condition",
            "precision",
            "recall",
            "f1",
            "ap50",
            "ap75",
            "gt_boxes",
            "predictions",
            "mean_confidence",
            "detector_score_thr",
            "metric_score_thr",
            "nms_thresh",
            "detections_per_img",
            "checkpoint_path",
            "checkpoint_sha256",
            "split_path",
            "split_sha256",
            "runtime_seconds",
            "fps",
            "gpu",
            "cuda",
            "pytorch",
            "git_commit",
        ],
    )

    full_agg = aggregate(full_rows, ["variant"], ["precision", "recall", "f1", "ap50", "ap75"])
    missing_agg = aggregate(missing_rows, ["variant", "condition"], ["precision", "recall", "f1", "ap50", "ap75"])
    write_csv(
        RESULTS / "full_input_aggregate.csv",
        full_agg,
        ["variant", "metric", "mean", "min", "max", "range", "seed0", "seed2", "detector_score_thr", "metric_score_thr"],
    )
    write_csv(
        RESULTS / "missing_modality_aggregate.csv",
        missing_agg,
        [
            "variant",
            "condition",
            "metric",
            "mean",
            "min",
            "max",
            "range",
            "seed0",
            "seed2",
            "detector_score_thr",
            "metric_score_thr",
        ],
    )
    write_diff(full_rows, missing_rows)
    write_reconciliation(full_rows, full_agg, missing_rows, blockers)

    preflight = run_preflight(blockers)
    final_pdf, page_count = try_compile_pdf(blockers)
    required_missing = sum(1 for row in missing_rows if row["condition"] in MANUSCRIPT_MISSING_MODES)
    if len(full_rows) == 8 and required_missing == 24 and not blockers and preflight == "PASS" and final_pdf != "NA":
        status = "RERUN COMPLETE"
    else:
        status = "BLOCKED"
    write_blockers(blockers)
    write_audit_files(status, blockers, len(full_rows), len(missing_rows), preflight, page_count)
    zip_path = package_handoff(status, final_pdf)

    summary = {
        "status": status,
        "git_commit": git_output(["rev-parse", "HEAD"]),
        "detector_score_thr": DETECTOR_SCORE_THR,
        "metric_score_thr": METRIC_SCORE_THR,
        "full_input_completed": len(full_rows),
        "missing_modality_rows_completed": len(missing_rows),
        "manuscript_missing_cells_completed": required_missing,
        "preflight": preflight,
        "pdf": final_pdf,
        "page_count": page_count,
        "zip": str(zip_path),
        "blockers": blockers,
    }
    (RESULTS / "run_v23_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
