#!/usr/bin/env python3
"""Verify six M3OT best checkpoints and produce matched metrics and figures."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import statistics
import sys

from PIL import Image, ImageDraw, ImageFont
import torch
from torch.utils.data import DataLoader

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from datasets.m3ot_dataset import M3OTExternalDataset
from datasets.triair_dataset import collate_fn
from rarepdet.coco_metrics import coco_detection_metrics
from rarepdet.train_early_fusion import configure_reproducibility
from tools.m3ot_matching import match_prediction
from tools.train_m3ot_supervised import assert_audit, make_model, sha256


MODELS = ("early", "reliability_rgbt")
METRICS = ("AP", "AP50", "AP75", "AR100", "P", "R")


def write_csv(path: Path, rows: list[dict], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def verify_run(root: Path, model_type: str, seed: int, manifest_hash: str) -> tuple[Path, dict]:
    run = root / "training" / f"{model_type}_seed{seed}"
    config = json.loads((run / "config.json").read_text(encoding="utf-8"))
    status = json.loads((run / "status.json").read_text(encoding="utf-8"))
    history = [json.loads(line) for line in (run / "history.jsonl").read_text(encoding="utf-8").splitlines()]
    if (status["status"], status["completed_epochs"], len(history)) != ("COMPLETE", 50, 50):
        raise RuntimeError(f"Run is not complete: {run}")
    if (config["model"], config["seed"], config["val_manifest_sha256"]) != (
            model_type, seed, manifest_hash):
        raise RuntimeError(f"Run identity mismatch: {run}")
    best = max(history, key=lambda row: row["val_AP50"])
    path = run / "weights" / "best.pt"
    if status["best_epoch"] != best["epoch"] or status["best_checkpoint_sha256"] != sha256(path):
        raise RuntimeError(f"Best-checkpoint selection/hash mismatch: {run}")
    checkpoint = torch.load(path, map_location="cpu", weights_only=False)
    if checkpoint["epoch"] != best["epoch"]:
        raise RuntimeError(f"Best-checkpoint epoch mismatch: {path}")
    return path, {"config": config, "status": status, "checkpoint": checkpoint}


def evaluate_run(model: torch.nn.Module, dataset: M3OTExternalDataset,
                 device: torch.device) -> tuple[dict, dict, list[dict]]:
    loader = DataLoader(dataset, batch_size=4, shuffle=False, num_workers=2,
                        collate_fn=collate_fn, pin_memory=True)
    predictions, targets = [], []
    model.eval()
    with torch.inference_mode():
        for batch_number, (images, batch_targets) in enumerate(loader, 1):
            outputs = model([image.to(device, non_blocking=True) for image in images])
            predictions.extend({key: output[key].detach().cpu() for key in ("boxes", "scores", "labels")}
                               for output in outputs)
            targets.extend(batch_targets)
            if batch_number % 100 == 0:
                print(f"  evaluated {len(predictions)}/{len(dataset)} frames", flush=True)
    coco = coco_detection_metrics(predictions, targets, score_thresh=0.0,
                                  max_detections=100)
    counts = {"TP": 0, "FP": 0, "FN": 0}
    for prediction, target in zip(predictions, targets):
        matched = match_prediction(prediction, target, score_thr=0.25, iou_thr=0.50)
        for key in counts:
            counts[key] += matched[key.lower()]
    counts["P"] = counts["TP"] / (counts["TP"] + counts["FP"]) if counts["TP"] + counts["FP"] else 0.0
    counts["R"] = counts["TP"] / (counts["TP"] + counts["FN"]) if counts["TP"] + counts["FN"] else 0.0
    return coco, counts, predictions


def font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def draw_boxes(image: Image.Image, boxes: list, color: tuple[int, int, int]) -> Image.Image:
    panel = image.copy()
    painter = ImageDraw.Draw(panel)
    for box in boxes:
        painter.rectangle(tuple(float(value) for value in box), outline=color, width=3)
    return panel


def render_scenes(dataset: M3OTExternalDataset, selection_path: Path,
                  predictions: dict[str, list[dict]], out: Path) -> list[dict]:
    selected = json.loads(selection_path.read_text(encoding="utf-8"))
    if (selected.get("source_split"), selected.get("prediction_independent"),
            selected.get("manifest_sha256")) != ("val", True, sha256(dataset.manifest_path)):
        raise RuntimeError("Qualitative scene selection is not frozen to audited val")
    id_to_index = {row["sample_id"]: index for index, row in enumerate(dataset.records)}
    scene_names = ("group1_typical", "group2_typical", "dense")
    if set(selected["selected"]) != set(scene_names):
        raise RuntimeError("Expected three predetermined M3OT scenes")
    header, footer = 56, 56
    canvas = Image.new("RGB", (5 * 640, 3 * (512 + header) + footer), "white")
    draw = ImageDraw.Draw(canvas)
    rows = []
    out.mkdir(parents=True, exist_ok=True)
    for row_index, name in enumerate(scene_names):
        sample_id = selected["selected"][name]["sample_id"]
        index = id_to_index[sample_id]
        rgb_array, ir_array = dataset.read_images(index)
        rgb = Image.fromarray(rgb_array, mode="RGB")
        ir = Image.fromarray(ir_array, mode="L").convert("RGB")
        gt = dataset.target(index)
        early = predictions["early"][index]
        dynamic = predictions["reliability_rgbt"][index]
        def visible_boxes(prediction: dict) -> list:
            keep = (prediction["labels"] == 1) & (prediction["scores"] >= 0.25)
            return prediction["boxes"][keep].tolist()
        early_boxes, dynamic_boxes = visible_boxes(early), visible_boxes(dynamic)
        panels = (rgb, ir, draw_boxes(rgb, gt["boxes"].tolist(), (0, 220, 75)),
                  draw_boxes(rgb, early_boxes, (20, 105, 240)),
                  draw_boxes(rgb, dynamic_boxes, (20, 105, 240)))
        labels = ("RGB", "IR", f"GT ({len(gt['boxes'])})",
                  f"Early seed 0 ({len(early_boxes)})",
                  f"Dynamic seed 0 ({len(dynamic_boxes)})")
        y = row_index * (512 + header)
        for column, (panel, label) in enumerate(zip(panels, labels)):
            x = column * 640
            draw.text((x + 12, y + 12), f"{name}  {label}", fill="black", font=font(25))
            canvas.paste(panel, (x, y + header))
        rows.append({"scene": name, "sample_id": sample_id, "gt_boxes": len(gt["boxes"]),
                     "early_display_boxes": len(early_boxes),
                     "dynamic_display_boxes": len(dynamic_boxes)})
    draw.text((12, canvas.height - footer + 10),
              "Green: official RGB GT. Blue: prediction score >= 0.25. IR is shown raw; RGB boxes are not projected to IR.",
              fill="black", font=font(24))
    canvas.save(out / "three_scene_comparison.png", dpi=(300, 300))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    audit = root / "audit"
    manifest = audit / "val_manifest.json"
    assert_audit(audit, audit / "train_manifest.json", manifest)
    selection = root / "qualitative_selection_grouped.json"
    output = root / "results"
    if output.exists():
        parser.error(f"Refusing to overwrite existing final results: {output}")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for frozen best-checkpoint evaluation")
    device = torch.device("cuda")
    manifest_hash = sha256(manifest)
    rows, seed0_predictions = [], {}
    for seed in (0, 1, 2):
        for model_type in MODELS:
            path, identity = verify_run(root, model_type, seed, manifest_hash)
            reproducibility = configure_reproducibility(seed)
            if reproducibility != identity["config"]["reproducibility"]:
                raise RuntimeError(f"Reproducibility settings differ: {model_type} seed {seed}")
            dataset = M3OTExternalDataset(manifest, model_type=model_type,
                                          expected_split="val")
            model = make_model(model_type)
            model.load_state_dict(identity["checkpoint"]["model_state"], strict=True)
            model.to(device)
            print(f"FINAL_EVAL {model_type} seed={seed} best_epoch="
                  f"{identity['checkpoint']['epoch']}", flush=True)
            coco, counts, predictions = evaluate_run(model, dataset, device)
            if coco["images"] != 1200 or coco["gt_boxes"] != 13781:
                raise RuntimeError(f"Incomplete best-checkpoint val evaluation: {model_type} seed {seed}")
            for key in ("ap50_95", "ap50", "ap75", "ar100"):
                if abs(coco[key] - identity["checkpoint"]["metrics"][key]) > 1e-6:
                    raise RuntimeError(f"Recomputed {key} differs from best epoch: {model_type} seed {seed}")
            rows.append({"model": model_type, "seed": seed,
                         "best_epoch": identity["checkpoint"]["epoch"],
                         "checkpoint_sha256": sha256(path),
                         "AP": coco["ap50_95"], "AP50": coco["ap50"],
                         "AP75": coco["ap75"], "AR100": coco["ar100"],
                         **counts})
            if seed == 0:
                seed0_predictions[model_type] = predictions
            del model
            torch.cuda.empty_cache()

    summaries = []
    for model_type in MODELS:
        selected = [row for row in rows if row["model"] == model_type]
        for key in METRICS:
            values = [row[key] for row in selected]
            summaries.append({"model": model_type, "metric": key,
                              "mean": statistics.mean(values),
                              "sample_std": statistics.stdev(values)})
    paired = []
    for seed in (0, 1, 2):
        early = next(row for row in rows if row["model"] == "early" and row["seed"] == seed)
        dynamic = next(row for row in rows if row["model"] == "reliability_rgbt" and row["seed"] == seed)
        paired.append({"seed": seed, "early_AP": early["AP"],
                       "dynamic_AP": dynamic["AP"], "dynamic_minus_early_AP": dynamic["AP"] - early["AP"]})
    deltas = [row["dynamic_minus_early_AP"] for row in paired]
    output.mkdir(parents=True)
    write_csv(output / "per_seed.csv", rows,
              ["model", "seed", "best_epoch", "checkpoint_sha256",
               "AP", "AP50", "AP75", "AR100", "TP", "FP", "FN", "P", "R"])
    write_csv(output / "summary.csv", summaries, ["model", "metric", "mean", "sample_std"])
    write_csv(output / "paired_ap_differences.csv", paired,
              ["seed", "early_AP", "dynamic_AP", "dynamic_minus_early_AP"])
    scene_rows = render_scenes(M3OTExternalDataset(manifest, model_type="early",
                                                  expected_split="val"),
                               selection, seed0_predictions, output / "figures")
    (output / "scene_provenance.json").write_text(json.dumps(scene_rows, indent=2) + "\n", encoding="utf-8")
    report = ["# M3OT supervised RGB+thermal comparison", "",
              "Protocol: official M3OT train/val, from-scratch RepViT-FPN-FCOS,",
              "matched seeds 0/1/2, 50 epochs, batch 4, 640x640, AdamW 1e-4/1e-4,",
              "no augmentation; best checkpoint by val AP50. No public test use.", "",
              "This is supervised external-dataset development, not zero-shot or a blind test.",
              "The two cameras share frame IDs but are not perfectly pixel-aligned.", "",
              "| Model | AP mean +/- sample SD | AP50 mean +/- sample SD | AP75 mean +/- sample SD | AR100 mean +/- sample SD |",
              "| --- | ---: | ---: | ---: | ---: |"]
    for model_type in MODELS:
        def cell(metric: str) -> str:
            item = next(row for row in summaries if row["model"] == model_type and row["metric"] == metric)
            return f"{item['mean']:.4f} +/- {item['sample_std']:.4f}"
        report.append(f"| {model_type} | {cell('AP')} | {cell('AP50')} | {cell('AP75')} | {cell('AR100')} |")
    report += ["", "Paired dynamic-minus-early AP by seed: " + ", ".join(f"{value:+.6f}" for value in deltas) + ".",
               f"Mean paired delta: {statistics.mean(deltas):+.6f} +/- {statistics.stdev(deltas):.6f} (sample SD).",
               "Fixed score >= 0.25, IoU >= 0.50 TP/FP/FN/P/R and all per-seed metrics are in per_seed.csv.",
               "The three figure scenes were frozen before training or prediction review.",
               "No unfavorable seed was removed, and no significance claim is made.", ""]
    (output / "experiment_report.md").write_text("\n".join(report), encoding="utf-8")
    print(f"FINAL_RESULTS_COMPLETE {output}", flush=True)


if __name__ == "__main__":
    main()
