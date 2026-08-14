"""Build the V85 real, checkpoint-backed TriAir qualitative figure."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFont


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rarepdet.data import DetectionTriAirDataset, get_sample_info
from rarepdet.models.early_fusion_fcos import build_detector


SPLIT = PROJECT_ROOT / "reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt"
COMPONENTS = PROJECT_ROOT / "reproducibility/v40_expanded_adjacency_component_split_v2/extended_graph/component_membership.csv"
REGISTRY = PROJECT_ROOT / "runs/v48_complete_ablation/causal_ablation_summary.json"
EXPECTED_SPLIT_SHA256 = "722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f"
DISPLAY_SCORE_THRESHOLD = 0.25
NMS_THRESHOLD = 0.60
MAX_DETECTIONS = 100
MODEL_SPECS = (
    ("matched_early_seed0", "early", "matched_early"),
    ("ra_no_moddrop_seed0", "reliability", "dynamic_gate"),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def load_component_map() -> dict[str, str]:
    with COMPONENTS.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return {row["sample_id"]: row["component_id"] for row in rows}


def load_checkpoint_specs() -> list[dict[str, object]]:
    rows = json.loads(REGISTRY.read_text(encoding="utf-8"))["per_run"]
    by_id = {row["run_id"]: row for row in rows}
    selected = []
    for run_id, model_type, display_name in MODEL_SPECS:
        row = dict(by_id[run_id])
        checkpoint = Path(row["weights"])
        if int(row["seed"]) != 0:
            raise RuntimeError(f"V85 requires seed 0: {run_id}")
        if not checkpoint.is_file():
            raise FileNotFoundError(f"Missing frozen checkpoint: {checkpoint}")
        actual = sha256(checkpoint)
        if actual != row["checkpoint_sha256"]:
            raise RuntimeError(f"Checkpoint SHA256 mismatch: {run_id}")
        row.update(model_type=model_type, display_name=display_name, checkpoint_path=str(checkpoint), actual_sha256=actual)
        selected.append(row)
    return selected


def build_candidate_table(dataset: DetectionTriAirDataset, components: dict[str, str]) -> list[dict[str, object]]:
    rows = []
    for index in range(len(dataset)):
        image, target = dataset[index]
        info = get_sample_info(dataset, index)
        sample_id = Path(info["image_path"]).stem
        luminance = 0.299 * image[0] + 0.587 * image[1] + 0.114 * image[2]
        thermal = image[3]
        event = image[4]
        rows.append({
            "sample_index": index,
            "sample_id": sample_id,
            "relative_path": Path(info["image_path"]).relative_to(dataset.dataset.data_root).as_posix(),
            "component_id": components[sample_id],
            "gt_box_count": int(target["boxes"].shape[0]),
            "rgb_mean_luminance": float(luminance.mean()),
            "rgb_std_luminance": float(luminance.std(unbiased=False)),
            "thermal_mean": float(thermal.mean()),
            "thermal_std": float(thermal.std(unbiased=False)),
            "event_mean": float(event.mean()),
            "event_std": float(event.std(unbiased=False)),
            "event_min": float(event.min()),
            "event_max": float(event.max()),
            "height": int(image.shape[1]),
            "width": int(image.shape[2]),
            "selected_scene": "",
        })
    if len(rows) != 2213:
        raise RuntimeError(f"Expected 2,213 development-validation rows, got {len(rows)}")
    return rows


def choose_ranked(candidates: list[dict[str, object]], score, used_components: set[str]) -> dict[str, object]:
    eligible = [row for row in candidates if str(row["component_id"]) not in used_components]
    if not eligible:
        raise RuntimeError("No candidate remains after distinct-component filtering")
    return min(eligible, key=lambda row: (float(score(row)), str(row["sample_id"])))


def select_samples(rows: list[dict[str, object]]) -> tuple[list[dict[str, object]], dict[str, float]]:
    rgb = np.asarray([float(row["rgb_mean_luminance"]) for row in rows])
    gt = np.asarray([int(row["gt_box_count"]) for row in rows])
    q25, q75 = (float(value) for value in np.quantile(rgb, [0.25, 0.75], method="linear"))
    gt_q90 = float(np.quantile(gt, 0.90, method="linear"))
    bright = [row for row in rows if float(row["rgb_mean_luminance"]) >= q75 and int(row["gt_box_count"]) >= 2]
    dark = [row for row in rows if float(row["rgb_mean_luminance"]) <= q25 and int(row["gt_box_count"]) >= 2]
    crowded = [row for row in rows if int(row["gt_box_count"]) >= gt_q90]
    if not bright or not dark or not crowded:
        raise RuntimeError("A deterministic V85 scene bucket is empty")
    used: set[str] = set()
    selected = []
    for scene, bucket, score in (
        ("A", bright, lambda row, median=float(np.median([int(item["gt_box_count"]) for item in bright])): abs(int(row["gt_box_count"]) - median)),
        ("B", dark, lambda row, median=float(np.median([int(item["gt_box_count"]) for item in dark])): abs(int(row["gt_box_count"]) - median)),
        ("C", crowded, lambda row, median=float(np.median([float(item["rgb_mean_luminance"]) for item in crowded])): abs(float(row["rgb_mean_luminance"]) - median)),
    ):
        row = choose_ranked(bucket, score, used)
        row["selected_scene"] = scene
        used.add(str(row["component_id"]))
        selected.append(row)
    if len(used) != 3:
        raise RuntimeError("V85 scenes are not component-distinct")
    return selected, {"rgb_q25": q25, "rgb_q75": q75, "gt_count_q90": gt_q90}


def prediction_record(sample: dict[str, object], output: dict[str, torch.Tensor]) -> dict[str, object]:
    keep = output["scores"] >= DISPLAY_SCORE_THRESHOLD
    boxes = output["boxes"][keep][:MAX_DETECTIONS].detach().cpu().tolist()
    scores = output["scores"][keep][:MAX_DETECTIONS].detach().cpu().tolist()
    labels = output["labels"][keep][:MAX_DETECTIONS].detach().cpu().tolist()
    return {
        "sample_id": sample["sample_id"],
        "component_id": sample["component_id"],
        "boxes_xyxy": [[round(float(value), 5) for value in box] for box in boxes],
        "scores": [round(float(value), 7) for value in scores],
        "labels": [int(value) for value in labels],
        "count": len(boxes),
    }


def run_inference(dataset, selected, specs, device: torch.device) -> dict[str, list[dict[str, object]]]:
    images = [dataset[int(row["sample_index"])][0] for row in selected]
    results = {}
    for spec in specs:
        payload = torch.load(spec["checkpoint_path"], map_location=device, weights_only=False)
        cfg = payload.get("model_cfg", {})
        model = build_detector(
            spec["model_type"], model_name=cfg.get("model_name", "repvit_m0_9.dist_300e_in1k"),
            img_size=cfg.get("img_size", 640), num_classes=cfg.get("num_classes", 2),
            fpn_out_channels=cfg.get("fpn_out_channels", 128), score_thresh=DISPLAY_SCORE_THRESHOLD,
            nms_thresh=NMS_THRESHOLD, detections_per_img=MAX_DETECTIONS,
        )
        model.load_state_dict(payload["model_state"], strict=True)
        model.to(device).eval()
        with torch.inference_mode():
            outputs = model([image.to(device) for image in images])
        results[str(spec["display_name"])] = [prediction_record(sample, output) for sample, output in zip(selected, outputs)]
        del model, payload, outputs
        if device.type == "cuda":
            torch.cuda.empty_cache()
    return results


def to_uint8(array: np.ndarray) -> np.ndarray:
    return np.rint(np.clip(array, 0.0, 1.0) * 255.0).astype(np.uint8)


def shared_scale(array: np.ndarray, lower: float, upper: float) -> np.ndarray:
    if upper <= lower:
        return np.zeros_like(array, dtype=np.uint8)
    return to_uint8((array - lower) / (upper - lower))


def font_for(height: int):
    size = max(11, round(height / 45))
    for path in (Path("C:/Windows/Fonts/arial.ttf"), Path("C:/Windows/Fonts/calibri.ttf")):
        if path.is_file():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def overlay(rgb: np.ndarray, prediction: dict[str, object], color: tuple[int, int, int]) -> Image.Image:
    image = Image.fromarray(to_uint8(rgb))
    draw = ImageDraw.Draw(image)
    font = font_for(image.height)
    width = max(2, round(image.width / 320))
    for box, score in zip(prediction["boxes_xyxy"], prediction["scores"]):
        x1, y1, x2, y2 = (float(value) for value in box)
        draw.rectangle((x1, y1, x2, y2), outline=color, width=width)
        label = f"{float(score):.2f}"
        text_box = draw.textbbox((x1, y1), label, font=font, stroke_width=0)
        text_height = text_box[3] - text_box[1]
        top = max(0.0, y1 - text_height - 4)
        text_width = text_box[2] - text_box[0]
        draw.rectangle((x1, top, x1 + text_width + 4, top + text_height + 4), fill=color)
        draw.text((x1 + 2, top + 2), label, fill="white", font=font)
    return image


def render_outputs(dataset, selected, predictions, out: Path) -> dict[str, object]:
    panels = out / "panels"
    figure_dir = out / "figure"
    panels.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)
    arrays = [dataset[int(row["sample_index"])][0].permute(1, 2, 0).numpy() for row in selected]
    thermal_min = min(float(array[:, :, 3].min()) for array in arrays)
    thermal_max = max(float(array[:, :, 3].max()) for array in arrays)
    event_min = min(float(array[:, :, 4].min()) for array in arrays)
    event_max = max(float(array[:, :, 4].max()) for array in arrays)
    panel_paths: list[list[Path]] = []
    for scene, array in zip(("A", "B", "C"), arrays):
        rgb = array[:, :, :3]
        paths = [
            panels / f"scene_{scene}_rgb.png", panels / f"scene_{scene}_thermal.png",
            panels / f"scene_{scene}_event.png", panels / f"scene_{scene}_early.png",
            panels / f"scene_{scene}_gate.png",
        ]
        Image.fromarray(to_uint8(rgb)).save(paths[0])
        Image.fromarray(shared_scale(array[:, :, 3], thermal_min, thermal_max), mode="L").save(paths[1])
        Image.fromarray(shared_scale(array[:, :, 4], event_min, event_max), mode="L").save(paths[2])
        index = ord(scene) - ord("A")
        overlay(rgb, predictions["matched_early"][index], (0, 114, 178)).save(paths[3])
        overlay(rgb, predictions["dynamic_gate"][index], (213, 94, 0)).save(paths[4])
        panel_paths.append(paths)

    import matplotlib.pyplot as plt

    titles = ("(a) RGB", "(b) Thermal", "(c) Stored event representation", "(d) Matched early", "(e) Dynamic gate")
    row_names = ("Scene A: bright / ordinary", "Scene B: dark / low visible light", "Scene C: crowded / small target")
    fig, axes = plt.subplots(3, 5, figsize=(12.2, 7.0), constrained_layout=True)
    for row_index, paths in enumerate(panel_paths):
        for column_index, path in enumerate(paths):
            axes[row_index, column_index].imshow(Image.open(path), cmap="gray" if column_index in (1, 2) else None)
            axes[row_index, column_index].set_axis_off()
            if row_index == 0:
                axes[row_index, column_index].set_title(titles[column_index], fontsize=9, pad=5)
        axes[row_index, 0].text(
            -0.045, 0.5, row_names[row_index], transform=axes[row_index, 0].transAxes,
            rotation=90, ha="right", va="center", fontsize=8, clip_on=False,
        )
    png = figure_dir / "fig6_real_qualitative.png"
    pdf = figure_dir / "fig6_real_qualitative.pdf"
    fig.savefig(png, dpi=300, facecolor="white")
    fig.savefig(pdf, facecolor="white")
    plt.close(fig)
    rendered = np.asarray(Image.open(png).convert("L"))
    if rendered.std() < 5 or rendered.shape[0] < 1000 or rendered.shape[1] < 1500:
        raise RuntimeError("Rendered V85 figure failed nonblank/dimension validation")
    return {
        "thermal_shared_min": thermal_min, "thermal_shared_max": thermal_max,
        "event_shared_min": event_min, "event_shared_max": event_max,
        "figure_png_pixels": [int(rendered.shape[1]), int(rendered.shape[0])],
        "figure_png_sha256": sha256(png), "figure_pdf_sha256": sha256(pdf),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=r"D:\download\triair")
    parser.add_argument("--out", type=Path, default=Path("runs/v85_real_qualitative_figure"))
    parser.add_argument("--device", default="cuda")
    args = parser.parse_args()
    out = args.out if args.out.is_absolute() else PROJECT_ROOT / args.out
    for name in ("selection", "predictions", "provenance"):
        (out / name).mkdir(parents=True, exist_ok=True)
    if sha256(SPLIT) != EXPECTED_SPLIT_SHA256:
        raise RuntimeError("Frozen development-validation split SHA256 mismatch")
    dataset = DetectionTriAirDataset(args.data, split_file=str(SPLIT), mode="rgbte", train=False, modality_dropout=0.0)
    candidates = build_candidate_table(dataset, load_component_map())
    selected, thresholds = select_samples(candidates)
    write_csv(out / "selection/validation_candidate_table.csv", candidates)
    write_json(out / "selection/selected_samples.json", {"thresholds": thresholds, "samples": selected})
    (out / "selection/selection_protocol.md").write_text(
        "# V85 Deterministic Selection Protocol\n\n"
        "All 2,213 frozen development-validation samples are described before inference. Scene A uses RGB luminance "
        "at or above the linear 75th percentile and at least two GT boxes; Scene B uses luminance at or below the "
        "25th percentile and at least two boxes. Each minimizes distance to its bucket median GT count, then sample "
        "ID. Scene C uses GT count at or above the linear 90th percentile and minimizes distance to bucket median "
        "RGB luminance, then sample ID. Later scenes skip components already selected. No model output participates.\n",
        encoding="utf-8",
    )
    specs = load_checkpoint_specs()
    predictions = run_inference(dataset, selected, specs, torch.device(args.device))
    for name, rows in predictions.items():
        write_json(out / f"predictions/{name}_seed0_predictions.json", {
            "display_score_threshold": DISPLAY_SCORE_THRESHOLD, "nms_iou": NMS_THRESHOLD,
            "max_detections": MAX_DETECTIONS, "samples": rows,
        })
    identity = {spec["display_name"]: {
        "run_id": spec["run_id"], "seed": int(spec["seed"]), "model": spec["model_type"],
        "path": spec["checkpoint_path"], "sha256": spec["actual_sha256"],
        "selected_epoch": spec.get("selected_epoch"),
    } for spec in specs}
    write_json(out / "predictions/checkpoint_identity.json", identity)
    visualization = render_outputs(dataset, selected, predictions, out)
    visualization.update({
        "rgb_transform": "clip normalized stored channels 0:3 to [0,1], round to uint8",
        "thermal_transform": "shared min-max scaling over the three selected stored channel-3 arrays, grayscale",
        "event_transform": "shared min-max scaling over the three selected stored channel-4 arrays, grayscale",
        "display_score_threshold": DISPLAY_SCORE_THRESHOLD, "nms_iou": NMS_THRESHOLD,
        "max_detections": MAX_DETECTIONS, "early_box_rgb": [0, 114, 178], "gate_box_rgb": [213, 94, 0],
    })
    write_json(out / "provenance/visualization_parameters.json", visualization)
    command = f'{sys.executable} rarepdet/tools/build_v85_real_qualitative_figure.py --data "{args.data}" --device {args.device}'
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, text=True).strip()
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=PROJECT_ROOT, text=True).strip()
    sample_lines = "\n".join(
        f"- Scene {row['selected_scene']}: `{row['sample_id']}`, component `{row['component_id']}`, "
        f"GT boxes {row['gt_box_count']}, RGB mean {float(row['rgb_mean_luminance']):.6f}." for row in selected
    )
    checkpoint_lines = "\n".join(
        f"- {name}: `{item['path']}`, SHA256 `{item['sha256']}`, seed `{item['seed']}`." for name, item in identity.items()
    )
    (out / "provenance/qualitative_figure_provenance.md").write_text(
        "# V85 Qualitative Figure Provenance\n\n"
        f"Generated: {datetime.now().astimezone().isoformat(timespec='seconds')}\n\n"
        f"- Branch: `{branch}`; generation commit: `{commit}`.\n"
        f"- Validation manifest: `{SPLIT.relative_to(PROJECT_ROOT).as_posix()}`; SHA256 `{EXPECTED_SPLIT_SHA256}`; 2,213 rows.\n"
        "- Selection uses the frozen, model-independent protocol in `selection/selection_protocol.md`.\n"
        f"{sample_lines}\n\n## Checkpoints\n\n{checkpoint_lines}\n\n"
        "## Inference And Display\n\n"
        "- Preprocessing: `DetectionTriAirDataset`, five stored channels divided by 255, torchvision fixed-size 640 x 640 transform.\n"
        f"- One global display threshold `{DISPLAY_SCORE_THRESHOLD}`, NMS IoU `{NMS_THRESHOLD}`, maximum `{MAX_DETECTIONS}` detections.\n"
        f"- Thermal transform: {visualization['thermal_transform']}.\n"
        f"- Event transform: {visualization['event_transform']}; this is the stored event representation, not raw events.\n"
        "- Bounding boxes and scores are direct frozen-checkpoint outputs. They were not moved, resized, added, deleted, or relabeled manually.\n"
        "- No AI-generated, synthetic, reconstructed, or invented sensor imagery, prediction, box, score, or annotation is used.\n"
        "- The historical 837-image partition was not opened, rendered, scored, or used for selection.\n"
        f"- Generation command: `{command}`.\n",
        encoding="utf-8",
    )
    caption = (
        "Qualitative detections on deterministically selected TriAir component-disjoint development-validation samples. "
        "Columns show the RGB observation, thermal channel, stored event representation, matched early-fusion predictions, "
        "and dynamic-gate predictions from fixed seed-0 checkpoints. Samples are selected from predeclared image descriptors "
        "rather than model performance. Bounding boxes and confidence scores are direct checkpoint outputs under one fixed "
        "display threshold; no manual box editing is applied."
    )
    (out / "figure/fig6_caption.txt").write_text(caption + "\n", encoding="utf-8")
    counts = {name: [row["count"] for row in rows] for name, rows in predictions.items()}
    (out / "V85_QUALITATIVE_FIGURE_SUMMARY.md").write_text(
        "# V85 Real Qualitative Figure Summary\n\nStatus: `COMPLETE`\n\n"
        f"- Selected samples: `{', '.join(str(row['sample_id']) for row in selected)}` in three distinct components.\n"
        f"- Display detection counts by Scene A/B/C: `{json.dumps(counts, sort_keys=True)}`.\n"
        "- Both models use fixed seed 0 and identical score/NMS/maximum-detection settings.\n"
        "- Figure PNG/PDF passed nonblank and dimension checks.\n"
        "- All panels and boxes are real stored data or frozen-checkpoint outputs; no synthetic content was used.\n"
        "- The locked 837-image historical partition was not accessed.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "COMPLETE", "samples": [row["sample_id"] for row in selected], "counts": counts}, indent=2))


if __name__ == "__main__":
    main()
