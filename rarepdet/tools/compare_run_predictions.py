#!/usr/bin/env python
"""Compare E0/E1/E2 predictions side-by-side on the same validation images.

This is a post-processing/qualitative-analysis tool. It does not modify
training code, checkpoints, datasets, or running experiments.
"""

import argparse
from pathlib import Path
import random
import sys

import torch
from PIL import Image, ImageDraw, ImageFont


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rarepdet.data import DetectionTriAirDataset, get_sample_info
from rarepdet.models.early_fusion_fcos import build_detector


RUN_SPECS = [
    ("E0 Early Fusion", "early", "weights_e0"),
    ("E1 Reliability", "reliability", "weights_e1"),
    ("E2 Reliability + Dropout", "reliability", "weights_e2"),
]


def resolve_path(path):
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def load_font():
    try:
        return ImageFont.load_default()
    except Exception:
        return None


def image_to_pil_rgb(image):
    rgb = (image[:3] * 255.0).permute(1, 2, 0).clamp(0, 255).byte().cpu().numpy()
    return Image.fromarray(rgb)


def draw_title(draw, title, width, font):
    draw.rectangle((0, 0, width, 20), fill=(255, 255, 255))
    draw.text((4, 4), title[:95], fill=(0, 0, 0), font=font)


def draw_gt_panel(image, target, title):
    panel = image.copy()
    draw = ImageDraw.Draw(panel)
    font = load_font()
    draw_title(draw, title, panel.width, font)
    boxes = target["boxes"].detach().cpu()
    labels = target["labels"].detach().cpu()
    for box, label in zip(boxes, labels):
        x1, y1, x2, y2 = [float(value) for value in box.tolist()]
        draw.rectangle((x1, y1, x2, y2), outline=(0, 220, 0), width=2)
        # labels are already shifted for torchvision, so class 1 is vehicle.
        draw.text((x1, max(21, y1 - 12)), f"GT {int(label)}", fill=(0, 180, 0), font=font)
    return panel


def draw_prediction_panel(image, prediction, title, score_thr, alpha=None):
    panel = image.copy()
    draw = ImageDraw.Draw(panel)
    font = load_font()
    if alpha is not None:
        title = f"{title}  a=({alpha[0]:.2f},{alpha[1]:.2f},{alpha[2]:.2f})"
    draw_title(draw, title, panel.width, font)

    boxes = prediction["boxes"].detach().cpu()
    scores = prediction["scores"].detach().cpu()
    labels = prediction["labels"].detach().cpu()
    for box, score, label in zip(boxes, scores, labels):
        if float(score) < score_thr:
            continue
        x1, y1, x2, y2 = [float(value) for value in box.tolist()]
        draw.rectangle((x1, y1, x2, y2), outline=(255, 40, 40), width=2)
        draw.text((x1, max(21, y1 - 12)), f"{int(label)} {float(score):.2f}", fill=(255, 40, 40), font=font)
    return panel


def draw_missing_panel(size, title, warning):
    panel = Image.new("RGB", size, (245, 245, 245))
    draw = ImageDraw.Draw(panel)
    font = load_font()
    draw_title(draw, title, size[0], font)
    draw.text((10, 45), "SKIPPED", fill=(170, 0, 0), font=font)
    draw.text((10, 65), warning[:70], fill=(170, 0, 0), font=font)
    return panel


def get_alpha(model):
    alpha = getattr(model.backbone, "last_alpha", None)
    if alpha is None:
        return None
    return alpha.detach().float().mean(dim=0).cpu().tolist()


def load_one_model(label, model_type, weights_path, img_size, score_thr, device):
    weights_path = resolve_path(weights_path)
    if not weights_path.is_file():
        return {
            "label": label,
            "model_type": model_type,
            "model": None,
            "warning": f"missing weights: {weights_path}",
        }

    checkpoint = torch.load(weights_path, map_location=device)
    model_cfg = checkpoint.get("model_cfg", {})
    model = build_detector(
        model_type=model_type,
        model_name=model_cfg.get("model_name", "repvit_m0_9.dist_300e_in1k"),
        img_size=model_cfg.get("img_size", img_size),
        num_classes=model_cfg.get("num_classes", 2),
        fpn_out_channels=model_cfg.get("fpn_out_channels", 128),
        score_thresh=min(score_thr, 0.2),
    )
    model.load_state_dict(checkpoint["model_state"], strict=True)
    model.to(device).eval()
    return {
        "label": label,
        "model_type": model_type,
        "model": model,
        "warning": "",
        "weights": str(weights_path),
    }


def make_grid(panels):
    width = max(panel.width for panel in panels)
    height = max(panel.height for panel in panels)
    canvas = Image.new("RGB", (width * len(panels), height), (255, 255, 255))
    for idx, panel in enumerate(panels):
        canvas.paste(panel, (idx * width, 0))
    return canvas


def main():
    parser = argparse.ArgumentParser(description="Compare E0/E1/E2 predictions on val images.")
    parser.add_argument("--data", default=r"D:\download\triair")
    parser.add_argument("--split-file", default=r"D:\download\triair\splits\val.txt")
    parser.add_argument("--weights-e0", default="runs/E0_early_repvit_fcos_e50/weights/best.pt")
    parser.add_argument("--weights-e1", default="runs/E1_reliability_repvit_fcos_e50/weights/best.pt")
    parser.add_argument("--weights-e2", default="runs/E2_reliability_dropout015_repvit_fcos_e50/weights/best.pt")
    parser.add_argument("--img-size", default=640, type=int)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--num", default=50, type=int)
    parser.add_argument("--score-thr", "--score-thresh", dest="score_thr", default=0.2, type=float)
    parser.add_argument("--out", default="runs/compare_E0_E1_E2")
    parser.add_argument("--seed", default=20260617, type=int)
    args = parser.parse_args()

    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        print("WARNING: CUDA requested but unavailable; using CPU.")
        device = torch.device("cpu")

    loaded = []
    for label, model_type, arg_name in RUN_SPECS:
        loaded.append(load_one_model(label, model_type, getattr(args, arg_name), args.img_size, args.score_thr, device))

    dataset = DetectionTriAirDataset(args.data, split_file=args.split_file, mode="rgbte", train=False)
    indices = list(range(len(dataset)))
    random.Random(args.seed).shuffle(indices)
    indices = indices[: min(args.num, len(indices))]

    out_dir = resolve_path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    summary_path = out_dir / "compare_summary.txt"

    rows = []
    with torch.no_grad():
        for rank, index in enumerate(indices, 1):
            image, target = dataset[index]
            base = image_to_pil_rgb(image)
            info = get_sample_info(dataset, index)
            panels = [draw_gt_panel(base, target, f"GT | {info['image_path'].name}")]

            row = {
                "rank": rank,
                "index": index,
                "file": info["image_path"].name,
                "gt_boxes": int(target["boxes"].shape[0]),
            }

            for item in loaded:
                if item["model"] is None:
                    panels.append(draw_missing_panel(base.size, item["label"], item["warning"]))
                    row[item["label"]] = "SKIPPED"
                    continue

                prediction = item["model"]([image.to(device)])[0]
                prediction = {key: value.detach().cpu() for key, value in prediction.items()}
                alpha = get_alpha(item["model"]) if item["model_type"] == "reliability" else None
                panels.append(draw_prediction_panel(base, prediction, item["label"], args.score_thr, alpha=alpha))
                kept = int((prediction["scores"] >= args.score_thr).sum().item())
                row[item["label"]] = f"predictions={kept}"
                if alpha is not None:
                    row[item["label"] + " alpha"] = f"{alpha[0]:.6f},{alpha[1]:.6f},{alpha[2]:.6f}"

            grid = make_grid(panels)
            out_path = out_dir / f"compare_{rank:03d}_{info['image_path'].stem}.png"
            grid.save(out_path)
            row["output"] = out_path.name
            rows.append(row)
            print(f"[{rank:03d}/{len(indices)}] {info['image_path'].name} -> {out_path.name}")

    with summary_path.open("w", encoding="utf-8") as f:
        f.write("E0/E1/E2 prediction comparison summary\n")
        f.write("======================================\n")
        f.write(f"data: {args.data}\n")
        f.write(f"split_file: {args.split_file}\n")
        f.write(f"score_thr: {args.score_thr}\n")
        f.write(f"num_images: {len(rows)}\n\n")
        for item in loaded:
            if item["warning"]:
                f.write(f"WARNING {item['label']}: {item['warning']}\n")
            else:
                f.write(f"{item['label']} weights: {item['weights']}\n")
        f.write("\n")
        for row in rows:
            parts = [f"{key}={value}" for key, value in row.items()]
            f.write("\t".join(parts) + "\n")

    print(f"Saved comparison images to: {out_dir}")
    print(f"Saved summary to: {summary_path}")


if __name__ == "__main__":
    main()
