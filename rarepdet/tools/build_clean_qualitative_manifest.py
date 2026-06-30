#!/usr/bin/env python
"""Build illustrative clean-split qualitative manifest and local panels."""

import argparse
import csv
from datetime import datetime
from pathlib import Path
import sys

import torch
from PIL import Image, ImageDraw
from torch.utils.data import DataLoader


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from datasets.triair_dataset import collate_fn
from rarepdet.data import DetectionTriAirDataset, get_sample_info
from rarepdet.metrics import box_iou
from rarepdet.models.early_fusion_fcos import build_detector
from rarepdet.tools.eval_missing_modality import apply_missing_mode


HEADERS = [
    "Category",
    "Rank",
    "Image Index",
    "Image Path",
    "GT Count",
    "Panel Path",
    "Prediction Summary",
    "Rationale",
]


def resolve_path(path):
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def pick_device(requested):
    device = torch.device(requested)
    if device.type == "cuda" and not torch.cuda.is_available():
        print("WARNING: CUDA requested but unavailable; using CPU.")
        return torch.device("cpu")
    return device


def load_model(model_type, weights, img_size, score_thr, device):
    checkpoint = torch.load(resolve_path(weights), map_location=device)
    cfg = checkpoint.get("model_cfg", {})
    model = build_detector(
        model_type=model_type,
        model_name=cfg.get("model_name", "repvit_m0_9.dist_300e_in1k"),
        img_size=cfg.get("img_size", img_size),
        num_classes=cfg.get("num_classes", 2),
        fpn_out_channels=cfg.get("fpn_out_channels", 128),
        score_thresh=score_thr,
    )
    model.load_state_dict(checkpoint["model_state"], strict=True)
    model.to(device).eval()
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
    pred_scores = pred_scores[order]

    matched = torch.zeros((gt_boxes.shape[0],), dtype=torch.bool)
    tp = 0
    fp = 0
    best_scores = []
    for box, score in zip(pred_boxes, pred_scores):
        if gt_boxes.numel() == 0:
            fp += 1
            continue
        ious = box_iou(box.view(1, 4), gt_boxes).view(-1)
        best_iou, best_index = torch.max(ious, dim=0)
        best_index = int(best_index)
        if float(best_iou) >= iou_thr and not bool(matched[best_index]):
            matched[best_index] = True
            tp += 1
            best_scores.append(float(score))
        else:
            fp += 1
    fn = int(gt_boxes.shape[0]) - tp
    return {"tp": tp, "fp": fp, "fn": fn, "pred": int(pred_boxes.shape[0]), "scores": best_scores}


def evaluate_model(dataset, model, device, mode, score_thr, batch_size, num_workers):
    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        collate_fn=collate_fn,
        pin_memory=(device.type == "cuda"),
    )
    metrics = {}
    predictions = {}
    with torch.no_grad():
        for images, targets in loader:
            device_images = [apply_missing_mode(image, mode).to(device, non_blocking=True) for image in images]
            outputs = model(device_images)
            for output, target in zip(outputs, targets):
                index = int(target["image_id"].item())
                cpu_output = {key: value.detach().cpu() for key, value in output.items()}
                cpu_target = {key: value.detach().cpu() for key, value in target.items()}
                predictions[index] = cpu_output
                metrics[index] = match_counts(cpu_output, cpu_target, score_thr=score_thr)
    return metrics, predictions


def image_to_pil(image_tensor):
    rgb = image_tensor[:3].detach().cpu().clamp(0, 1)
    rgb = (rgb.permute(1, 2, 0).numpy() * 255.0).round().astype("uint8")
    return Image.fromarray(rgb, mode="RGB")


def prediction_boxes(prediction, score_thr):
    boxes = prediction["boxes"].detach().cpu()
    scores = prediction["scores"].detach().cpu()
    labels = prediction["labels"].detach().cpu()
    keep = (labels == 1) & (scores >= score_thr)
    order = torch.argsort(scores[keep], descending=True)
    return boxes[keep][order], scores[keep][order]


def draw_panel(base, target, prediction, title, score_thr):
    panel = base.copy()
    draw = ImageDraw.Draw(panel)
    for box in target["boxes"].detach().cpu():
        x1, y1, x2, y2 = [float(v) for v in box.tolist()]
        draw.rectangle((x1, y1, x2, y2), outline=(0, 220, 0), width=3)
    boxes, scores = prediction_boxes(prediction, score_thr)
    for box, score in zip(boxes, scores):
        x1, y1, x2, y2 = [float(v) for v in box.tolist()]
        draw.rectangle((x1, y1, x2, y2), outline=(230, 0, 0), width=3)
        draw.text((x1 + 2, max(0, y1 - 14)), f"{float(score):.2f}", fill=(230, 0, 0))
    title_h = 24
    canvas = Image.new("RGB", (panel.width, panel.height + title_h), (255, 255, 255))
    title_draw = ImageDraw.Draw(canvas)
    title_draw.text((6, 5), title, fill=(0, 0, 0))
    canvas.paste(panel, (0, title_h))
    return canvas


def save_case_panel(dataset, index, panels, predictions, out_dir, filename, score_thr):
    image, target = dataset[index]
    base = image_to_pil(image)
    rendered = [draw_panel(base, target, predictions[key][index], title, score_thr) for key, title in panels]
    width = sum(panel.width for panel in rendered)
    height = max(panel.height for panel in rendered)
    canvas = Image.new("RGB", (width, height), (255, 255, 255))
    x = 0
    for panel in rendered:
        canvas.paste(panel, (x, 0))
        x += panel.width
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / filename
    canvas.save(path)
    return path


def summary(item, prefix):
    return f"{prefix}: TP={item['tp']} FP={item['fp']} FN={item['fn']} Pred={item['pred']}"


def select_unique(candidates, used, count):
    selected = []
    for index in candidates:
        if index in used:
            continue
        selected.append(index)
        used.add(index)
        if len(selected) >= count:
            break
    return selected


def build_manifest(dataset, metric_sets, predictions, panel_dir, score_thr):
    used = set()
    rows = []

    def gt_count(index):
        return int(metric_sets["r4_full"][index]["tp"] + metric_sets["r4_full"][index]["fn"])

    corrected = sorted(
        [
            idx
            for idx in range(len(dataset))
            if gt_count(idx) > 0 and metric_sets["r0_full"][idx]["fn"] > metric_sets["r4_full"][idx]["fn"]
        ],
        key=lambda idx: (-metric_sets["r0_full"][idx]["fn"], metric_sets["r4_full"][idx]["fp"], idx),
    )
    shared = sorted(
        [
            idx
            for idx in range(len(dataset))
            if gt_count(idx) > 0 and metric_sets["r0_full"][idx]["fn"] == 0 and metric_sets["r4_full"][idx]["fn"] == 0
        ],
        key=lambda idx: (metric_sets["r0_full"][idx]["fp"] + metric_sets["r4_full"][idx]["fp"], -gt_count(idx), idx),
    )
    failures = sorted(
        [
            idx
            for idx in range(len(dataset))
            if gt_count(idx) > 0 and (metric_sets["r4_full"][idx]["fn"] > 0 or metric_sets["r4_full"][idx]["fp"] > 0)
        ],
        key=lambda idx: (-metric_sets["r4_full"][idx]["fn"], -metric_sets["r4_full"][idx]["fp"], -gt_count(idx), idx),
    )

    categories = [
        ("R4 corrects R0 miss/localization failure", select_unique(corrected, used, 5), ("r0_full", "r4_full")),
        ("Shared successful detection", select_unique(shared, used, 5), ("r0_full", "r4_full")),
        ("R4 failure/hard case", select_unique(failures, used, 5), ("r0_full", "r4_full")),
    ]

    missing_candidates = []
    mode_quota = [("r4_no_rgb", 2), ("r4_no_thermal", 2), ("r4_no_event", 1)]
    for mode_key, quota in mode_quota:
        candidates = sorted(
            [
                idx
                for idx in range(len(dataset))
                if gt_count(idx) > 0
                and (
                    metric_sets[mode_key][idx]["fn"] > metric_sets["r4_full"][idx]["fn"]
                    or metric_sets[mode_key][idx]["fp"] > metric_sets["r4_full"][idx]["fp"]
                )
            ],
            key=lambda idx: (
                -(metric_sets[mode_key][idx]["fn"] - metric_sets["r4_full"][idx]["fn"]),
                -(metric_sets[mode_key][idx]["fp"] - metric_sets["r4_full"][idx]["fp"]),
                idx,
            ),
        )
        missing_candidates.extend((mode_key, idx) for idx in select_unique(candidates, used, quota))
    categories.append(("R4 missing-modality illustrative case", missing_candidates, ("r4_full", "mode_specific")))

    for category, items, panel_keys in categories:
        for rank, item in enumerate(items, 1):
            if isinstance(item, tuple):
                mode_key, index = item
                keys = ("r4_full", mode_key)
                title_map = {"r4_full": "R4 full", mode_key: mode_key.replace("r4_", "R4 ")}
                rationale = f"Illustrates R4 behavior under synthetic {mode_key.replace('r4_', '').replace('_', ' ')} input removal."
            else:
                index = item
                keys = panel_keys
                title_map = {"r0_full": "R0 full", "r4_full": "R4 full"}
                if category.startswith("R4 corrects"):
                    rationale = "R4 has fewer unmatched GT boxes than R0 at score threshold 0.50."
                elif category.startswith("Shared"):
                    rationale = "Both R0 and R4 cover all GT boxes; this is a shared success example."
                else:
                    rationale = "R4 retains at least one false positive or unmatched GT box; this is an illustrative hard case."
            info = get_sample_info(dataset, index)
            panel_specs = [(key, title_map[key]) for key in keys]
            panel_path = save_case_panel(
                dataset,
                index,
                panel_specs,
                predictions,
                panel_dir,
                f"clean_case_{len(rows)+1:02d}_{Path(info['image_path']).stem}.png",
                score_thr,
            )
            pred_summary = "; ".join(summary(metric_sets[key][index], key) for key in keys)
            rows.append(
                {
                    "Category": category,
                    "Rank": rank,
                    "Image Index": index,
                    "Image Path": str(info["image_path"]),
                    "GT Count": gt_count(index),
                    "Panel Path": str(panel_path),
                    "Prediction Summary": pred_summary,
                    "Rationale": rationale,
                }
            )
    return rows[:20]


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(rows)


def write_md(path, rows):
    counts = {}
    for row in rows:
        counts[row["Category"]] = counts.get(row["Category"], 0) + 1
    lines = [
        "# Clean Qualitative Summary",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "These cases are illustrative only and are not cherry-picked to claim universal superiority.",
        "",
        "Local panels are written under `runs/local_clean_qualitative_panels/` and are not committed.",
        "",
        "## Counts",
        "",
    ]
    for category in sorted(counts):
        lines.append(f"- {category}: {counts[category]}")
    lines.extend(["", "## Manifest", ""])
    lines.extend(
        [
            "| Category | Rank | Image Index | GT Count | Prediction Summary | Rationale |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        lines.append(
            f"| {row['Category']} | {row['Rank']} | {row['Image Index']} | {row['GT Count']} | "
            f"{row['Prediction Summary']} | {row['Rationale']} |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Build clean qualitative manifest.")
    parser.add_argument("--data", default=r"D:\download\triair")
    parser.add_argument("--split-file", default=r"runs\blocked_split_candidates\block64_guard16_seed0_val.txt")
    parser.add_argument("--weights-r0", default=r"runs\R0_early_seed0_block64g16_e50\weights\best.pt")
    parser.add_argument("--weights-r4", default=r"runs\R4_reliability_p020_seed0_block64g16_e50\weights\best.pt")
    parser.add_argument("--img-size", default=640, type=int)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--batch-size", default=4, type=int)
    parser.add_argument("--num-workers", default=0, type=int)
    parser.add_argument("--score-thr", default=0.50, type=float)
    parser.add_argument("--panel-dir", default=r"runs\local_clean_qualitative_panels")
    parser.add_argument("--manifest", default=r"runs\clean_qualitative_manifest.csv")
    parser.add_argument("--summary", default=r"runs\clean_qualitative_summary.md")
    args = parser.parse_args()

    device = pick_device(args.device)
    dataset = DetectionTriAirDataset(args.data, split_file=resolve_path(args.split_file), mode="rgbte", train=False)

    r0 = load_model("early", args.weights_r0, args.img_size, args.score_thr, device)
    r4 = load_model("reliability", args.weights_r4, args.img_size, args.score_thr, device)
    metric_sets = {}
    predictions = {}
    for key, model, mode in (
        ("r0_full", r0, "full"),
        ("r4_full", r4, "full"),
        ("r4_no_rgb", r4, "no_rgb"),
        ("r4_no_thermal", r4, "no_thermal"),
        ("r4_no_event", r4, "no_event"),
    ):
        print(f"Evaluating {key}")
        metrics, preds = evaluate_model(dataset, model, device, mode, args.score_thr, args.batch_size, args.num_workers)
        metric_sets[key] = metrics
        predictions[key] = preds
    del r0, r4
    if device.type == "cuda":
        torch.cuda.empty_cache()

    rows = build_manifest(dataset, metric_sets, predictions, resolve_path(args.panel_dir), args.score_thr)
    if len(rows) != 20:
        raise RuntimeError(f"Expected 20 qualitative rows, got {len(rows)}")
    write_csv(resolve_path(args.manifest), rows)
    write_md(resolve_path(args.summary), rows)
    print(f"Saved: {resolve_path(args.manifest)}")
    print(f"Saved: {resolve_path(args.summary)}")
    print(f"Panels: {resolve_path(args.panel_dir)}")


if __name__ == "__main__":
    main()
