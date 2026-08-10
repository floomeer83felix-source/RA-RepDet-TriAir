"""Run the frozen V84 2x2 gate-by-dropout channel-removal evaluation."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
import sys
import time
from pathlib import Path

import torch
from torch.utils.data import DataLoader


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from datasets.triair_dataset import collate_fn
from rarepdet.coco_metrics import coco_detection_metrics
from rarepdet.data import DetectionTriAirDataset
from rarepdet.models.early_fusion_fcos import build_detector


VARIANTS = ("matched_early", "early_moddrop", "ra_no_moddrop", "ra_full_p015")
CONDITIONS = ("full", "no_rgb", "no_thermal", "no_event")
METRICS = ("ap50_95", "ap50", "ap75", "ar100")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def apply_condition(image: torch.Tensor, condition: str) -> torch.Tensor:
    result = image.clone()
    if condition == "no_rgb":
        result[0:3].zero_()
    elif condition == "no_thermal":
        result[3:4].zero_()
    elif condition == "no_event":
        result[4:5].zero_()
    elif condition != "full":
        raise ValueError(f"Unknown condition: {condition}")
    return result


def atomic_json(path: Path, payload: object) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def registry() -> list[dict[str, object]]:
    source = PROJECT_ROOT / "runs/v48_complete_ablation/causal_ablation_summary.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    rows = [row for row in payload["per_run"] if row["variant"] in VARIANTS]
    if len(rows) != 12:
        raise RuntimeError(f"Expected 12 frozen 2x2 checkpoints, found {len(rows)}")
    for row in rows:
        path = Path(row["weights"])
        if not path.is_file() or sha256(path) != row["checkpoint_sha256"]:
            raise RuntimeError(f"Checkpoint identity failure: {row['run_id']}")
    return sorted(rows, key=lambda row: (VARIANTS.index(row["variant"]), int(row["seed"])))


def evaluate(model: torch.nn.Module, loader: DataLoader, device: torch.device, condition: str) -> dict[str, object]:
    predictions, targets_cpu = [], []
    started = time.time()
    with torch.no_grad():
        for batch_index, (images, targets) in enumerate(loader, 1):
            inputs = [apply_condition(image, condition).to(device, non_blocking=True) for image in images]
            outputs = model(inputs)
            predictions.extend({key: value.detach().cpu() for key, value in output.items()} for output in outputs)
            targets_cpu.extend({key: value.detach().cpu() for key, value in target.items()} for target in targets)
            if batch_index == 1 or batch_index % 100 == 0 or batch_index == len(loader):
                print(f"{condition}: batch {batch_index}/{len(loader)}", flush=True)
    metrics = coco_detection_metrics(predictions, targets_cpu, score_thresh=0.0, max_detections=100)
    return {
        "images": len(targets_cpu), "ap50_95": float(metrics["ap50_95"]),
        "ap50": float(metrics["ap50"]), "ap75": float(metrics["ap75"]),
        "ar100": float(metrics["ar100"]), "gt_boxes": int(metrics["gt_boxes"]),
        "detections": int(metrics["detections"]), "runtime_seconds": time.time() - started,
    }


def write_csv(path: Path, rows: list[dict[str, object]], fields: tuple[str, ...]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    by_key = {(row["variant"], int(row["seed"]), row["condition"]): row for row in rows}
    summary = []
    for variant in VARIANTS:
        for condition in CONDITIONS:
            group = [by_key[(variant, seed, condition)] for seed in (0, 1, 2)]
            record = {"variant": variant, "condition": condition, "n": 3}
            for metric in METRICS:
                values = [float(row[metric]) for row in group]
                record[f"{metric}_mean"] = statistics.mean(values)
                record[f"{metric}_sample_sd"] = statistics.stdev(values)
            summary.append(record)

    deltas = []
    for seed in (0, 1, 2):
        for condition in CONDITIONS:
            e0 = by_key[("matched_early", seed, condition)]
            e1 = by_key[("early_moddrop", seed, condition)]
            g0 = by_key[("ra_no_moddrop", seed, condition)]
            g1 = by_key[("ra_full_p015", seed, condition)]
            for metric in METRICS:
                gate = ((float(g0[metric]) - float(e0[metric])) +
                        (float(g1[metric]) - float(e1[metric]))) / 2
                dropout = ((float(e1[metric]) - float(e0[metric])) +
                           (float(g1[metric]) - float(g0[metric]))) / 2
                interaction = ((float(g1[metric]) - float(g0[metric])) -
                               (float(e1[metric]) - float(e0[metric])))
                deltas.extend((
                    {"effect": "dynamic_gate_main", "seed": seed, "condition": condition,
                     "metric": metric, "delta": gate},
                    {"effect": "modality_dropout_main", "seed": seed, "condition": condition,
                     "metric": metric, "delta": dropout},
                    {"effect": "gate_x_dropout_interaction", "seed": seed, "condition": condition,
                     "metric": metric, "delta": interaction},
                ))
        for variant in VARIANTS:
            full = by_key[(variant, seed, "full")]
            for condition in CONDITIONS[1:]:
                removed = by_key[(variant, seed, condition)]
                for metric in METRICS:
                    deltas.append({"effect": "removal_minus_full", "variant": variant, "seed": seed,
                                   "condition": condition, "metric": metric,
                                   "delta": float(removed[metric]) - float(full[metric])})
    return summary, deltas


def finalize(out: Path, rows: list[dict[str, object]]) -> None:
    summary, deltas = summarize(rows)
    per_fields = ("run_id", "variant", "model", "seed", "training_modality_dropout", "condition",
                  *METRICS, "images", "gt_boxes", "detections", "runtime_seconds", "checkpoint_sha256",
                  "weights", "split_sha256", "removal_operator")
    summary_fields = tuple(summary[0])
    delta_fields = ("effect", "variant", "seed", "condition", "metric", "delta")
    write_csv(out / "per_run.csv", rows, per_fields)
    write_csv(out / "summary.csv", summary, summary_fields)
    write_csv(out / "paired_deltas.csv", deltas, delta_fields)

    effects = {}
    for effect in ("dynamic_gate_main", "modality_dropout_main", "gate_x_dropout_interaction"):
        effects[effect] = {}
        for condition in CONDITIONS:
            effects[effect][condition] = {}
            for metric in METRICS:
                values = [float(row["delta"]) for row in deltas if row["effect"] == effect and
                          row["condition"] == condition and row["metric"] == metric]
                effects[effect][condition][metric] = {"mean": statistics.mean(values),
                                                       "sample_sd": statistics.stdev(values), "n": len(values)}
    atomic_json(out / "factorial_effects.json", effects)
    (out / "analysis.md").write_text(
        "# V84 Matched Channel-Removal Analysis\n\n"
        "This is a seed-matched 2x2 gate-by-training-modality-dropout analysis on the frozen 2,213-image "
        "development-validation split. At inference, removal deterministically sets RGB channels 0:3, thermal "
        "channel 3, or event channel 4 to zero; all other channels and evaluator settings are unchanged.\n\n"
        "`factorial_effects.json` reports the gate and dropout main effects as averages over the opposite factor, "
        "plus the difference-in-differences interaction. `paired_deltas.csv` also records every seed-level effect "
        "and modality-specific removal-minus-full degradation. Interpret robustness attribution from these matched "
        "effects rather than from an unmatched pair. This analysis is development-validation evidence only. The "
        "locked holdout was not accessed.\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=r"D:\download\triair")
    parser.add_argument("--split", default="reproducibility/v40_expanded_adjacency_component_split_v2/manifests/v40_expanded_adjacency_component_disjoint_val.txt")
    parser.add_argument("--out", type=Path, default=Path("runs/v84_jei_critical_closure/channel_removal_2x2"))
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--num-workers", type=int, default=0)
    args = parser.parse_args()
    out = (PROJECT_ROOT / args.out).resolve() if not args.out.is_absolute() else args.out
    out.mkdir(parents=True, exist_ok=True)
    raw = out / "raw"
    raw.mkdir(exist_ok=True)
    split = (PROJECT_ROOT / args.split).resolve()
    split_hash = sha256(split)
    source_lock = json.loads((PROJECT_ROOT / "runs/v48_complete_ablation/source_lock_v48.json").read_text(encoding="utf-8"))
    if split_hash != source_lock["manifests"]["devval"]["sha256"]:
        raise RuntimeError("Frozen development-validation split hash mismatch")
    device = torch.device(args.device)
    dataset = DetectionTriAirDataset(args.data, split_file=str(split), mode="rgbte", train=False, modality_dropout=0.0)
    if len(dataset) != 2213:
        raise RuntimeError("Frozen development-validation row count mismatch")
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=False, num_workers=args.num_workers,
                        collate_fn=collate_fn, pin_memory=device.type == "cuda")
    rows = []
    for spec in registry():
        checkpoint = torch.load(spec["weights"], map_location=device, weights_only=False)
        cfg = checkpoint.get("model_cfg", {})
        model = build_detector(model_type=spec["model"], model_name=cfg.get("model_name", "repvit_m0_9.dist_300e_in1k"),
                               img_size=cfg.get("img_size", 640), num_classes=cfg.get("num_classes", 2),
                               fpn_out_channels=cfg.get("fpn_out_channels", 128), score_thresh=0.001,
                               nms_thresh=0.6, detections_per_img=100)
        model.load_state_dict(checkpoint["model_state"], strict=True)
        model.to(device).eval()
        for condition in CONDITIONS:
            result_path = raw / f"{spec['run_id']}__{condition}.json"
            if result_path.is_file():
                result = json.loads(result_path.read_text(encoding="utf-8"))
                if result["checkpoint_sha256"] != spec["checkpoint_sha256"] or result["split_sha256"] != split_hash:
                    raise RuntimeError(f"Resume identity mismatch: {result_path}")
            else:
                result = evaluate(model, loader, device, condition)
                result.update(run_id=spec["run_id"], variant=spec["variant"], model=spec["model"],
                              seed=int(spec["seed"]), training_modality_dropout=float(spec["modality_dropout"]),
                              condition=condition, checkpoint_sha256=spec["checkpoint_sha256"],
                              weights=spec["weights"], split_sha256=split_hash,
                              removal_operator="zero RGB[0:3], thermal[3:4], or event[4:5]")
                atomic_json(result_path, result)
            rows.append(result)
            atomic_json(out / "run_status.json", {"state": "RUNNING", "completed": len(rows), "required": 48,
                                                    "locked_holdout_accessed": False})
        del model, checkpoint
        if device.type == "cuda":
            torch.cuda.empty_cache()
    finalize(out, rows)
    atomic_json(out / "run_status.json", {"state": "COMPLETE", "completed": 48, "required": 48,
                                            "locked_holdout_accessed": False})


if __name__ == "__main__":
    main()
