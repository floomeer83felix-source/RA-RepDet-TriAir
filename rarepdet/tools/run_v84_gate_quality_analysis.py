"""Evaluate V84 gate weights against clean descriptors and controlled corruption."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from datasets.triair_dataset import collate_fn
from rarepdet.coco_metrics import coco_detection_metrics
from rarepdet.data import DetectionTriAirDataset, get_sample_info
from rarepdet.models.early_fusion_fcos import build_detector


MODALITIES = ("rgb", "thermal", "event")
LEVELS = (0, 1, 2, 3)
SPLIT = Path("reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt")
EXPECTED_SPLIT_HASH = "722efc6f74a7615aa70fad30275e9e617b3a1866bbc63eadbebce60a9a23fe8f"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, payload: object) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def component_map() -> dict[str, str]:
    path = PROJECT_ROOT / "reproducibility/v40_expanded_adjacency_component_split_v2/extended_graph/component_membership.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return {row["sample_id"]: row["component_id"] for row in rows if row["v39_partition"] == "VALIDATION"}


def checkpoints() -> list[dict[str, object]]:
    source = PROJECT_ROOT / "runs/v48_complete_ablation/causal_ablation_summary.json"
    rows = json.loads(source.read_text(encoding="utf-8"))["per_run"]
    selected = sorted((row for row in rows if row["variant"] == "ra_no_moddrop"), key=lambda row: int(row["seed"]))
    if [int(row["seed"]) for row in selected] != [0, 1, 2]:
        raise RuntimeError("Frozen gate-no-dropout seed family is incomplete")
    for row in selected:
        path = Path(row["weights"])
        if not path.is_file() or sha256(path) != row["checkpoint_sha256"]:
            raise RuntimeError(f"Checkpoint identity failure: {row['run_id']}")
    return selected


def entropy(channel: torch.Tensor, bins: int = 32) -> float:
    hist = torch.histc(channel.float().clamp(0, 1), bins=bins, min=0.0, max=1.0)
    probabilities = hist / hist.sum().clamp_min(1)
    nonzero = probabilities[probabilities > 0]
    return float((-(nonzero * torch.log2(nonzero)).sum() / math.log2(bins)).item())


def build_descriptors(dataset: DetectionTriAirDataset, components: dict[str, str]) -> list[dict[str, object]]:
    rows = []
    for index in range(len(dataset)):
        image, _ = dataset[index]
        info = get_sample_info(dataset, index)
        sample_id = Path(info["image_path"]).stem
        rgb = 0.299 * image[0] + 0.587 * image[1] + 0.114 * image[2]
        thermal, event = image[3], image[4]
        rows.append({
            "sample_index": index, "sample_id": sample_id, "component_id": components[sample_id],
            "rgb_mean_luminance": float(rgb.mean()), "rgb_std_luminance": float(rgb.std(unbiased=False)),
            "rgb_entropy32_normalized": entropy(rgb), "thermal_mean": float(thermal.mean()),
            "thermal_std": float(thermal.std(unbiased=False)),
            "thermal_entropy32_normalized": entropy(thermal),
            "event_nonzero_fraction": float((event != 0).float().mean()),
            "event_mean_magnitude": float(event.abs().mean()),
            "event_entropy32_normalized": entropy(event),
        })
    return rows


def corrupt(image: torch.Tensor, modality: str | None, level: int) -> torch.Tensor:
    result = image.clone()
    if level == 0:
        return result
    if modality in {"rgb", "thermal"}:
        channels = slice(0, 3) if modality == "rgb" else slice(3, 4)
        kernel = (3, 7, 11)[level - 1]
        padding = kernel // 2
        result[channels] = F.avg_pool2d(result[channels].unsqueeze(0), kernel, stride=1,
                                        padding=padding).squeeze(0)
    elif modality == "event":
        result[4:5].mul_((0.75, 0.50, 0.25)[level - 1])
    else:
        raise ValueError(f"Unknown modality: {modality}")
    return result


def evaluate(model: torch.nn.Module, loader: DataLoader, device: torch.device,
             modality: str | None, level: int, descriptors: list[dict[str, object]]) -> tuple[dict[str, object], list[dict[str, object]]]:
    predictions, targets_cpu, sample_weights = [], [], []
    alpha_sum = torch.zeros(3, dtype=torch.float64)
    count = 0
    started = time.time()
    with torch.no_grad():
        for batch_index, (images, targets) in enumerate(loader, 1):
            inputs = [corrupt(image, modality, level).to(device, non_blocking=True) for image in images]
            outputs = model(inputs)
            alpha = model.backbone.last_alpha.detach().cpu().to(torch.float64)
            if alpha.shape != (len(images), 3):
                raise RuntimeError(f"Unexpected gate shape: {tuple(alpha.shape)}")
            alpha_sum += alpha.sum(0)
            count += len(images)
            predictions.extend({key: value.detach().cpu() for key, value in output.items()} for output in outputs)
            targets_cpu.extend({key: value.detach().cpu() for key, value in target.items()} for target in targets)
            if modality is None and level == 0:
                for target, weights in zip(targets, alpha):
                    index = int(target["image_id"].item())
                    descriptor = descriptors[index]
                    sample_weights.append({
                        "sample_index": index, "sample_id": descriptor["sample_id"],
                        "component_id": descriptor["component_id"], "rgb_weight": float(weights[0]),
                        "thermal_weight": float(weights[1]), "event_weight": float(weights[2]),
                    })
            if batch_index == 1 or batch_index % 100 == 0 or batch_index == len(loader):
                label = "clean" if modality is None else f"{modality}_level{level}"
                print(f"{label}: batch {batch_index}/{len(loader)}", flush=True)
    metrics = coco_detection_metrics(predictions, targets_cpu, score_thresh=0.0, max_detections=100)
    means = alpha_sum / count
    return ({
        "modality": modality or "clean", "severity": level,
        "operator": "none" if level == 0 else (f"box_blur_kernel_{(3, 7, 11)[level - 1]}" if modality != "event"
                                                 else f"attenuation_{(0.75, 0.50, 0.25)[level - 1]:.2f}"),
        "rgb_weight_mean": float(means[0]), "thermal_weight_mean": float(means[1]),
        "event_weight_mean": float(means[2]), "ap50_95": float(metrics["ap50_95"]),
        "ap50": float(metrics["ap50"]), "ap75": float(metrics["ap75"]),
        "ar100": float(metrics["ar100"]), "runtime_seconds": time.time() - started,
    }, sample_weights)


def correlations(descriptors: list[dict[str, object]], weights: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    descriptors_by_id = {row["sample_id"]: row for row in descriptors}
    descriptor_names = [key for key in descriptors[0] if key not in {"sample_index", "sample_id", "component_id"}]
    correlation_rows, bin_rows = [], []
    for seed in (0, 1, 2):
        seed_weights = [row for row in weights if int(row["seed"]) == seed]
        for descriptor_name in descriptor_names:
            modality = descriptor_name.split("_")[0]
            weight_name = f"{modality}_weight"
            x = np.asarray([descriptors_by_id[row["sample_id"]][descriptor_name] for row in seed_weights], dtype=float)
            y = np.asarray([row[weight_name] for row in seed_weights], dtype=float)
            pearson = float(np.corrcoef(x, y)[0, 1]) if x.std() > 0 and y.std() > 0 else 0.0
            correlation_rows.append({"seed": seed, "descriptor": descriptor_name,
                                     "gate_weight": weight_name, "pearson_r": pearson, "n": len(x)})
            order = np.argsort(x, kind="stable")
            for bin_index, indices in enumerate(np.array_split(order, 5), 1):
                bin_rows.append({"seed": seed, "descriptor": descriptor_name, "gate_weight": weight_name,
                                 "quantile_bin": bin_index, "descriptor_mean": float(x[indices].mean()),
                                 "weight_mean": float(y[indices].mean()), "n": len(indices)})
    return correlation_rows, bin_rows


def figures(out: Path, corruption: list[dict[str, object]], weights: list[dict[str, object]], bins: list[dict[str, object]]) -> None:
    import matplotlib.pyplot as plt

    figure_dir = out / "figures"
    figure_dir.mkdir(exist_ok=True)
    values = [[float(row[f"{modality}_weight"]) for row in weights] for modality in MODALITIES]
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    ax.boxplot(values, tick_labels=MODALITIES, showfliers=False)
    ax.set_ylabel("Task-driven gate weight")
    fig.tight_layout(); fig.savefig(figure_dir / "clean_weight_distribution.png", dpi=200); plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.0))
    for modality in MODALITIES:
        rows = [row for row in corruption if row["modality"] in {"clean", modality}]
        grouped = []
        for level in LEVELS:
            selected = [row for row in rows if int(row["severity"]) == level and
                        (level == 0 or row["modality"] == modality)]
            grouped.append(statistics.mean(float(row[f"{modality}_weight_mean"]) for row in selected))
        axes[0].plot(LEVELS, grouped, marker="o", label=modality)
        ap = [statistics.mean(float(row["ap50_95"]) for row in rows if int(row["severity"]) == level and
                              (level == 0 or row["modality"] == modality)) for level in LEVELS]
        axes[1].plot(LEVELS, ap, marker="o", label=modality)
    axes[0].set(xlabel="Corruption severity", ylabel="Corrupted-modality gate weight", xticks=LEVELS)
    axes[1].set(xlabel="Corruption severity", ylabel="COCO AP", xticks=LEVELS)
    axes[0].legend(); axes[1].legend(); fig.tight_layout()
    fig.savefig(figure_dir / "corruption_response.png", dpi=200); plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    primary = {"rgb": "rgb_std_luminance", "thermal": "thermal_std", "event": "event_nonzero_fraction"}
    for modality, descriptor in primary.items():
        rows = [row for row in bins if row["descriptor"] == descriptor]
        x = sorted(set(int(row["quantile_bin"]) for row in rows))
        y = [statistics.mean(float(row["weight_mean"]) for row in rows if int(row["quantile_bin"]) == value) for value in x]
        ax.plot(x, y, marker="o", label=modality)
    ax.set(xlabel="Descriptor quantile bin", ylabel="Mean matched gate weight", xticks=range(1, 6))
    ax.legend(); fig.tight_layout(); fig.savefig(figure_dir / "descriptor_binned_trends.png", dpi=200); plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=r"D:\download\triair")
    parser.add_argument("--out", type=Path, default=Path("runs/v84_jei_critical_closure/gate_quality_analysis"))
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--batch-size", type=int, default=4)
    args = parser.parse_args()
    out = (PROJECT_ROOT / args.out).resolve() if not args.out.is_absolute() else args.out
    out.mkdir(parents=True, exist_ok=True)
    split = PROJECT_ROOT / SPLIT
    if sha256(split) != EXPECTED_SPLIT_HASH:
        raise RuntimeError("Frozen development-validation split hash mismatch")
    dataset = DetectionTriAirDataset(args.data, split_file=str(split), mode="rgbte", train=False, modality_dropout=0.0)
    descriptors_path = out / "quality_descriptors.csv"
    if descriptors_path.is_file():
        with descriptors_path.open(encoding="utf-8", newline="") as handle:
            descriptors = list(csv.DictReader(handle))
    else:
        descriptors = build_descriptors(dataset, component_map())
        write_csv(descriptors_path, descriptors)
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=False, num_workers=0,
                        collate_fn=collate_fn, pin_memory=args.device.startswith("cuda"))
    device = torch.device(args.device)
    corruption_rows, clean_weights = [], []
    raw = out / "raw"; raw.mkdir(exist_ok=True)
    conditions = [(None, 0)] + [(modality, level) for modality in MODALITIES for level in LEVELS[1:]]
    for spec in checkpoints():
        checkpoint = torch.load(spec["weights"], map_location=device, weights_only=False)
        cfg = checkpoint.get("model_cfg", {})
        model = build_detector("reliability", model_name=cfg.get("model_name", "repvit_m0_9.dist_300e_in1k"),
                               img_size=cfg.get("img_size", 640), num_classes=cfg.get("num_classes", 2),
                               fpn_out_channels=cfg.get("fpn_out_channels", 128), score_thresh=0.001,
                               nms_thresh=0.6, detections_per_img=100)
        model.load_state_dict(checkpoint["model_state"], strict=True); model.to(device).eval()
        for modality, level in conditions:
            label = "clean" if modality is None else f"{modality}_level{level}"
            result_path = raw / f"seed{spec['seed']}__{label}.json"
            weights_path = raw / f"seed{spec['seed']}__clean_weights.csv"
            if result_path.is_file():
                result = json.loads(result_path.read_text(encoding="utf-8"))
                if result["checkpoint_sha256"] != spec["checkpoint_sha256"]:
                    raise RuntimeError(f"Resume checkpoint mismatch: {result_path}")
                sample_weights = []
            else:
                result, sample_weights = evaluate(model, loader, device, modality, level, descriptors)
                result.update(seed=int(spec["seed"]), run_id=spec["run_id"],
                              checkpoint_sha256=spec["checkpoint_sha256"], split_sha256=EXPECTED_SPLIT_HASH)
                atomic_json(result_path, result)
                if sample_weights:
                    for row in sample_weights: row["seed"] = int(spec["seed"])
                    write_csv(weights_path, sample_weights)
            corruption_rows.append(result)
            if modality is None:
                with weights_path.open(encoding="utf-8", newline="") as handle:
                    clean_weights.extend(csv.DictReader(handle))
            atomic_json(out / "run_status.json", {"state": "RUNNING", "completed": len(corruption_rows),
                                                    "required": 30, "locked_holdout_accessed": False})
        del model, checkpoint; torch.cuda.empty_cache()
    write_csv(out / "clean_sample_weights.csv", clean_weights)
    write_csv(out / "corruption_results.csv", corruption_rows)
    correlation_rows, bin_rows = correlations(descriptors, clean_weights)
    write_csv(out / "descriptor_correlations.csv", correlation_rows)
    write_csv(out / "descriptor_binned_trends.csv", bin_rows)
    figures(out, corruption_rows, clean_weights, bin_rows)
    monotonic = {}
    for modality in MODALITIES:
        means = []
        for level in LEVELS:
            selected = [row for row in corruption_rows if int(row["severity"]) == level and
                        (level == 0 or row["modality"] == modality)]
            means.append(statistics.mean(float(row[f"{modality}_weight_mean"]) for row in selected))
        monotonic[modality] = {"severity_means": means,
                               "nonincreasing": all(right <= left for left, right in zip(means, means[1:]))}
    (out / "analysis.md").write_text(
        "# V84 Gate-Quality Analysis\n\n"
        "The primary model family is dynamic gate without training-time modality dropout (seeds 0, 1, and 2). "
        "Clean descriptors use 32-bin normalized Shannon entropy, intensity mean/standard deviation, and event "
        "nonzero activity. Controlled RGB and thermal corruption is deterministic box blur (kernels 3, 7, 11); "
        "event corruption is deterministic attenuation (0.75, 0.50, 0.25). Only one modality changes at a time.\n\n"
        f"Mean corrupted-modality weights by severity and monotonic checks: `{json.dumps(monotonic, sort_keys=True)}`.\n\n"
        "The weights are learned task-driven fusion weights, not calibrated physical sensor-health probabilities. "
        "Results use exposed development-validation labels; no day/night labels were invented and the locked holdout "
        "was not accessed.\n",
        encoding="utf-8")
    atomic_json(out / "run_status.json", {"state": "COMPLETE", "completed": 30, "required": 30,
                                            "locked_holdout_accessed": False, "monotonic": monotonic})


if __name__ == "__main__":
    main()
