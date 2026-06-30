#!/usr/bin/env python
"""Select lightweight qualitative case manifests for E0/E1/E2."""

import argparse
import csv
from pathlib import Path
import sys

import torch
from torch.utils.data import DataLoader


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from datasets.triair_dataset import collate_fn
from rarepdet.data import DetectionTriAirDataset, get_sample_info
from rarepdet.metrics import box_iou
from rarepdet.models.early_fusion_fcos import build_detector


MODEL_SPECS = [
    ("E0", "Early Fusion", "early", "weights_e0"),
    ("E1", "Reliability Fusion", "reliability", "weights_e1"),
    ("E2", "Reliability + Dropout 0.15", "reliability", "weights_e2"),
]


MANIFEST_HEADERS = [
    "Category",
    "Rank",
    "Image ID",
    "Image Path",
    "Brightness Proxy",
    "Brightness Group",
    "GT Count",
    "E0 TP",
    "E0 FP",
    "E0 FN",
    "E1 TP",
    "E1 FP",
    "E1 FN",
    "E2 TP",
    "E2 FP",
    "E2 FN",
    "Notes",
]


def resolve_path(path):
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def load_model(model_type, weights_path, img_size, score_thr, device):
    weights_path = resolve_path(weights_path)
    if not weights_path.is_file():
        raise FileNotFoundError(f"Weights not found: {weights_path}")
    checkpoint = torch.load(weights_path, map_location=device)
    model_cfg = checkpoint.get("model_cfg", {})
    model = build_detector(
        model_type=model_type,
        model_name=model_cfg.get("model_name", "repvit_m0_9.dist_300e_in1k"),
        img_size=model_cfg.get("img_size", img_size),
        num_classes=model_cfg.get("num_classes", 2),
        fpn_out_channels=model_cfg.get("fpn_out_channels", 128),
        score_thresh=score_thr,
    )
    model.load_state_dict(checkpoint["model_state"], strict=True)
    model.to(device)
    model.eval()
    return model


def match_counts(prediction, target, score_thr=0.5, iou_thr=0.5):
    gt_boxes = target["boxes"].detach().cpu()
    gt_labels = target["labels"].detach().cpu()
    gt_boxes = gt_boxes[gt_labels == 1]

    pred_boxes = prediction["boxes"].detach().cpu()
    pred_scores = prediction["scores"].detach().cpu()
    pred_labels = prediction["labels"].detach().cpu()
    keep = (pred_labels == 1) & (pred_scores >= score_thr)
    pred_boxes = pred_boxes[keep]
    pred_scores = pred_scores[keep]
    order = torch.argsort(pred_scores, descending=True)
    pred_boxes = pred_boxes[order]

    matched = torch.zeros((gt_boxes.shape[0],), dtype=torch.bool)
    tp = 0
    fp = 0
    for box in pred_boxes:
        if gt_boxes.numel() == 0:
            fp += 1
            continue
        ious = box_iou(box.view(1, 4), gt_boxes).view(-1)
        best_iou, best_index = torch.max(ious, dim=0)
        best_index = int(best_index)
        if float(best_iou) >= iou_thr and not bool(matched[best_index]):
            matched[best_index] = True
            tp += 1
        else:
            fp += 1
    fn = int(gt_boxes.shape[0]) - tp
    return {"tp": tp, "fp": fp, "fn": fn}


def base_records(dataset):
    rows = []
    for index in range(len(dataset)):
        image, target = dataset[index]
        info = get_sample_info(dataset, index)
        rows.append(
            {
                "index": index,
                "image_path": str(info["image_path"]),
                "brightness": float(image[:3].mean().item()),
                "gt_count": int(target["boxes"].shape[0]),
            }
        )
    return rows


def assign_brightness_groups(rows):
    values = sorted(row["brightness"] for row in rows)
    if not values:
        return
    low_cut = values[len(values) // 3]
    high_cut = values[(2 * len(values)) // 3]
    for row in rows:
        if row["brightness"] <= low_cut:
            row["brightness_group"] = "low"
        elif row["brightness"] <= high_cut:
            row["brightness_group"] = "mid"
        else:
            row["brightness_group"] = "high"


def evaluate_model(rows, dataset, model, device, score_thr, batch_size, num_workers):
    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        collate_fn=collate_fn,
        pin_memory=(device.type == "cuda"),
    )
    by_index = {row["index"]: row for row in rows}
    with torch.no_grad():
        for images, targets in loader:
            device_images = [image.to(device, non_blocking=True) for image in images]
            outputs = model(device_images)
            for output, target in zip(outputs, targets):
                index = int(target["image_id"].item())
                yield index, match_counts(
                    {key: value.detach().cpu() for key, value in output.items()},
                    {key: value.detach().cpu() for key, value in target.items()},
                    score_thr=score_thr,
                )


def attach_model_counts(rows, args, device):
    dataset = DetectionTriAirDataset(args.data, split_file=args.split_file, mode="rgbte", train=False)
    by_index = {row["index"]: row for row in rows}
    for prefix, label, model_type, weight_arg in MODEL_SPECS:
        model = load_model(model_type, getattr(args, weight_arg), args.img_size, args.score_thr, device)
        for index, counts in evaluate_model(rows, dataset, model, device, args.score_thr, args.batch_size, args.num_workers):
            row = by_index[index]
            row[f"{prefix}_tp"] = counts["tp"]
            row[f"{prefix}_fp"] = counts["fp"]
            row[f"{prefix}_fn"] = counts["fn"]
        del model
        if device.type == "cuda":
            torch.cuda.empty_cache()
        print(f"Evaluated {label}")


def row_with_note(row, category, rank, note):
    return {
        "Category": category,
        "Rank": rank,
        "Image ID": row["index"],
        "Image Path": row["image_path"],
        "Brightness Proxy": f"{row['brightness']:.6f}",
        "Brightness Group": row["brightness_group"],
        "GT Count": row["gt_count"],
        "E0 TP": row.get("E0_tp", 0),
        "E0 FP": row.get("E0_fp", 0),
        "E0 FN": row.get("E0_fn", 0),
        "E1 TP": row.get("E1_tp", 0),
        "E1 FP": row.get("E1_fp", 0),
        "E1 FN": row.get("E1_fn", 0),
        "E2 TP": row.get("E2_tp", 0),
        "E2 FP": row.get("E2_fp", 0),
        "E2 FN": row.get("E2_fn", 0),
        "Notes": note,
    }


def take_ranked(rows, predicate, sort_key, limit):
    selected = [row for row in rows if predicate(row)]
    selected.sort(key=sort_key)
    return selected[:limit]


def select_cases(rows, limit):
    categories = [
        (
            "E0 miss, E2 hit",
            lambda row: row["gt_count"] > 0 and row.get("E0_fn", 0) > 0 and row.get("E2_fn", 0) == 0,
            lambda row: (-row.get("E0_fn", 0), row.get("E2_fp", 0), row["brightness"], row["index"]),
            "E2 covers all GT while E0 leaves at least one GT unmatched.",
        ),
        (
            "E1 miss, E2 hit",
            lambda row: row["gt_count"] > 0 and row.get("E1_fn", 0) > 0 and row.get("E2_fn", 0) == 0,
            lambda row: (-row.get("E1_fn", 0), row.get("E2_fp", 0), row["brightness"], row["index"]),
            "E2 covers all GT while E1 leaves at least one GT unmatched.",
        ),
        (
            "low-brightness E2-success case",
            lambda row: row["gt_count"] > 0 and row["brightness_group"] == "low" and row.get("E2_fn", 0) == 0,
            lambda row: (row["brightness"], row.get("E2_fp", 0), -row["gt_count"], row["index"]),
            "Low-brightness proxy sample where E2 covers all GT.",
        ),
        (
            "representative shared success case",
            lambda row: row["gt_count"] > 0
            and row.get("E0_fn", 0) == 0
            and row.get("E1_fn", 0) == 0
            and row.get("E2_fn", 0) == 0,
            lambda row: (
                row.get("E0_fp", 0) + row.get("E1_fp", 0) + row.get("E2_fp", 0),
                -row["gt_count"],
                abs(row["brightness"] - 0.5),
                row["index"],
            ),
            "All three models cover all GT; lower total FP ranked first.",
        ),
        (
            "representative E2 failure case",
            lambda row: row["gt_count"] > 0 and (row.get("E2_fn", 0) > 0 or row.get("E2_fp", 0) > 0),
            lambda row: (-row.get("E2_fn", 0), -row.get("E2_fp", 0), -row["gt_count"], row["index"]),
            "E2 has at least one unmatched GT or false positive.",
        ),
    ]

    manifest = []
    for category, predicate, sort_key, note in categories:
        for rank, row in enumerate(take_ranked(rows, predicate, sort_key, limit), 1):
            manifest.append(row_with_note(row, category, rank, note))
    return manifest


def write_manifest(rows, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=MANIFEST_HEADERS)
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(rows):
    headers = ["Category", "Rank", "Image ID", "Brightness Group", "GT Count", "E0 TP/FP/FN", "E1 TP/FP/FN", "E2 TP/FP/FN"]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append(
            "| {Category} | {Rank} | {Image ID} | {Brightness Group} | {GT Count} | {e0} | {e1} | {e2} |".format(
                **row,
                e0=f"{row['E0 TP']}/{row['E0 FP']}/{row['E0 FN']}",
                e1=f"{row['E1 TP']}/{row['E1 FP']}/{row['E1 FN']}",
                e2=f"{row['E2 TP']}/{row['E2 FP']}/{row['E2 FN']}",
            )
        )
    return lines


def write_report(manifest, path, score_thr):
    counts = {}
    for row in manifest:
        counts[row["Category"]] = counts.get(row["Category"], 0) + 1
    lines = [
        "# Qualitative Cases Summary",
        "",
        f"Score threshold: {score_thr:.2f}",
        "",
        "This report lists candidate validation images for paper qualitative panels. It records model-level TP/FP/FN summaries only; no images are committed.",
        "",
        "## Selected Counts",
        "",
    ]
    for category in sorted(counts):
        lines.append(f"- {category}: {counts[category]}")
    if not counts:
        lines.append("- No cases selected.")
    lines.extend(
        [
            "",
            "## Manifest Preview",
            "",
            *markdown_table(manifest),
            "",
            "## Proposed Figure Caption",
            "",
            "Qualitative comparison of RepViT-FCOS variants on selected TriAir validation cases. Green boxes denote ground truth and red boxes denote predictions at score threshold 0.50; examples include missed detections recovered by the dropout-trained reliability model, low-brightness proxy successes, shared successes, and representative remaining failures.",
            "",
            "Note: These examples are selected for qualitative illustration and should not be used as causal evidence for any single modality or scene factor.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Select E0/E1/E2 qualitative cases without writing images.")
    parser.add_argument("--data", default=r"D:\download\triair")
    parser.add_argument("--split-file", default=r"D:\download\triair\splits\val.txt")
    parser.add_argument("--weights-e0", default="runs/E0_early_repvit_fcos_e50/weights/best.pt")
    parser.add_argument("--weights-e1", default="runs/E1_reliability_repvit_fcos_e50/weights/best.pt")
    parser.add_argument("--weights-e2", default="runs/E2_reliability_dropout015_repvit_fcos_e50/weights/best.pt")
    parser.add_argument("--img-size", default=640, type=int)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--batch-size", default=4, type=int)
    parser.add_argument("--num-workers", default=0, type=int)
    parser.add_argument("--score-thr", default=0.50, type=float)
    parser.add_argument("--max-per-category", default=5, type=int)
    parser.add_argument("--manifest", default="runs/qualitative_cases_manifest.csv")
    parser.add_argument("--report", default="runs/qualitative_cases_summary.md")
    args = parser.parse_args()

    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        print("WARNING: CUDA requested but unavailable; using CPU.")
        device = torch.device("cpu")

    dataset = DetectionTriAirDataset(args.data, split_file=args.split_file, mode="rgbte", train=False)
    rows = base_records(dataset)
    assign_brightness_groups(rows)
    attach_model_counts(rows, args, device)
    manifest = select_cases(rows, args.max_per_category)

    manifest_path = resolve_path(args.manifest)
    report_path = resolve_path(args.report)
    write_manifest(manifest, manifest_path)
    write_report(manifest, report_path, args.score_thr)
    print(f"Saved: {manifest_path}")
    print(f"Saved: {report_path}")


if __name__ == "__main__":
    main()
