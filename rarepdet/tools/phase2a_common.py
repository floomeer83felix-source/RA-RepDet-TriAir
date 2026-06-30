"""Shared helpers for Phase 2A post-processing scripts."""

import csv
from pathlib import Path
import sys

import torch


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


RUNS = (
    {
        "experiment": "E0",
        "method": "E0 Early Fusion",
        "model": "early",
        "weights": "runs/E0_early_repvit_fcos_e50/weights/best.pt",
    },
    {
        "experiment": "E1",
        "method": "E1 Reliability Fusion",
        "model": "reliability",
        "weights": "runs/E1_reliability_repvit_fcos_e50/weights/best.pt",
    },
    {
        "experiment": "E2",
        "method": "E2 Reliability + Dropout 0.15",
        "model": "reliability",
        "weights": "runs/E2_reliability_dropout015_repvit_fcos_e50/weights/best.pt",
    },
)


def resolve_path(path):
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def read_csv(path):
    path = resolve_path(path)
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fieldnames=None):
    path = resolve_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path


def format_float(value, digits=6):
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return "NA"


def markdown_table(headers, rows):
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(header, "NA")) for header in headers) + " |")
    return lines


def pick_device(device_name):
    device = torch.device(device_name)
    if device.type == "cuda" and not torch.cuda.is_available():
        print("WARNING: CUDA requested but unavailable; using CPU.")
        device = torch.device("cpu")
    return device


def f1_score(precision, recall):
    precision = float(precision)
    recall = float(recall)
    denom = precision + recall
    return 0.0 if denom <= 0 else 2.0 * precision * recall / denom

