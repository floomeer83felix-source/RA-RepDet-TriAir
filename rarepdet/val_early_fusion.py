#!/usr/bin/env python
"""Visualize validation predictions for Early/Reliability RarePDet."""

import argparse
from pathlib import Path
import random
import sys

import torch
from PIL import Image, ImageDraw, ImageFont


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rarepdet.data import DetectionTriAirDataset, get_sample_info
from rarepdet.models.early_fusion_fcos import build_detector


def resolve_path(path):
    path = Path(path)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def resolve_weights(path):
    path = resolve_path(path)
    if path.is_file():
        return path
    if path.name == "best.pt":
        fallback = path.with_name("last.pt")
        if fallback.is_file():
            print(f"WARNING: best.pt not found, using last.pt: {fallback}")
            return fallback
    raise FileNotFoundError(f"Weights not found: {path}")


def image_to_pil_rgb(image):
    rgb = (image[:3] * 255.0).permute(1, 2, 0).clamp(0, 255).byte().cpu().numpy()
    return Image.fromarray(rgb)


def draw_boxes(draw, boxes, color, labels=None, scores=None, font=None, max_dets=None, score_thresh=0.0):
    drawn = 0
    for index, box in enumerate(boxes):
        if scores is not None and float(scores[index]) < score_thresh:
            continue
        if max_dets is not None and drawn >= max_dets:
            break

        x1, y1, x2, y2 = [float(value) for value in box.tolist()]
        draw.rectangle((x1, y1, x2, y2), outline=color, width=2)
        text_parts = []
        if labels is not None:
            text_parts.append(str(int(labels[index])))
        if scores is not None:
            text_parts.append(f"{float(scores[index]):.2f}")
        if text_parts:
            draw.text((x1, max(0, y1 - 12)), " ".join(text_parts), fill=color, font=font)
        drawn += 1
    return drawn


def get_alpha(model):
    alpha = getattr(model.backbone, "last_alpha", None)
    if alpha is None:
        return None
    return alpha.detach().float().mean(dim=0).cpu().tolist()


def main():
    parser = argparse.ArgumentParser(description="Visualize RarePDet validation predictions.")
    parser.add_argument("--model", default=None, choices=("early", "reliability"), help="Override checkpoint model type")
    parser.add_argument("--data", default=r"D:\download\triair")
    parser.add_argument("--split-file", default=r"D:\download\triair\splits\val.txt")
    parser.add_argument("--weights", default="runs/rarepdet_early/best.pt", help="best.pt or last.pt")
    parser.add_argument("--out", default="runs/rarepdet_early/vis_pred")
    parser.add_argument("--img-size", default=640, type=int)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--samples", "--num", dest="samples", default=100, type=int)
    parser.add_argument("--seed", default=20260617, type=int)
    parser.add_argument("--score-thresh", "--score-thr", dest="score_thresh", default=0.3, type=float)
    parser.add_argument("--max-dets", default=50, type=int)
    args = parser.parse_args()

    requested_device = torch.device(args.device)
    if requested_device.type == "cuda" and not torch.cuda.is_available():
        print("WARNING: CUDA requested but not available. Falling back to CPU.")
        requested_device = torch.device("cpu")
    device = requested_device
    print(f"Using device: {device}")

    weights = resolve_weights(args.weights)
    checkpoint = torch.load(weights, map_location=device)
    model_cfg = checkpoint.get("model_cfg", {})
    model_type = args.model or model_cfg.get("model_type", "early")
    model = build_detector(
        model_type=model_type,
        model_name=model_cfg.get("model_name", "repvit_m0_9.dist_300e_in1k"),
        img_size=model_cfg.get("img_size", args.img_size),
        num_classes=model_cfg.get("num_classes", 2),
        fpn_out_channels=model_cfg.get("fpn_out_channels", 128),
        score_thresh=min(args.score_thresh, 0.2),
    )
    model.load_state_dict(checkpoint["model_state"], strict=True)
    model.to(device)
    model.eval()

    dataset = DetectionTriAirDataset(args.data, split_file=args.split_file, mode="rgbte", train=False)
    rng = random.Random(args.seed)
    indices = list(range(len(dataset)))
    rng.shuffle(indices)
    indices = indices[: min(args.samples, len(indices))]

    out_dir = resolve_path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    summary_path = out_dir / "pred_summary.txt"

    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    rows = []
    with torch.no_grad():
        for rank, index in enumerate(indices, 1):
            image, target = dataset[index]
            prediction = model([image.to(device)])[0]
            prediction = {key: value.detach().cpu() for key, value in prediction.items()}

            canvas = image_to_pil_rgb(image)
            draw = ImageDraw.Draw(canvas)
            gt_count = draw_boxes(draw, target["boxes"], (0, 220, 0), labels=target["labels"], font=font)
            pred_count = draw_boxes(
                draw,
                prediction["boxes"],
                (255, 40, 40),
                labels=prediction["labels"],
                scores=prediction["scores"],
                font=font,
                max_dets=args.max_dets,
                score_thresh=args.score_thresh,
            )

            alpha = get_alpha(model)
            image_stem = get_sample_info(dataset, index)["image_path"].stem
            out_path = out_dir / f"{rank:03d}_{image_stem}_gt_pred.png"
            canvas.save(out_path)
            rows.append((index, image_stem, gt_count, pred_count, tuple(image.shape), out_path.name, alpha))
            print(f"[{rank:03d}/{len(indices)}] {image_stem} gt={gt_count} pred={pred_count}")

    with summary_path.open("w", encoding="utf-8") as f:
        f.write("RarePDet prediction visualization\n")
        f.write("================================\n")
        f.write(f"model: {model_type}\n")
        f.write(f"weights: {weights}\n")
        f.write(f"split_file: {args.split_file}\n")
        f.write(f"samples: {len(rows)}\n")
        f.write("colors: GT=green, Prediction=red\n\n")
        for index, image_stem, gt_count, pred_count, shape, output_name, alpha in rows:
            line = (
                f"idx={index}\tfile={image_stem}\tgt={gt_count}\tpred={pred_count}\t"
                f"shape={shape}\toutput={output_name}"
            )
            if model_type == "reliability" and alpha is not None:
                line += f"\talpha_rgb={alpha[0]:.6f}\talpha_thermal={alpha[1]:.6f}\talpha_event={alpha[2]:.6f}"
            f.write(line + "\n")

    print(f"Prediction visualizations saved to: {out_dir}")
    print(f"Summary saved to: {summary_path}")


if __name__ == "__main__":
    main()
