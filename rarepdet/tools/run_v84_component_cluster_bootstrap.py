"""Compute V84 component-macro paired uncertainty with cluster bootstrap."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from datasets.triair_dataset import collate_fn
from rarepdet.coco_metrics import coco_detection_metrics
from rarepdet.data import DetectionTriAirDataset, get_sample_info
from rarepdet.models.early_fusion_fcos import build_detector


VARIANTS = ("matched_early", "ra_static_equal", "ra_stems_project", "ra_no_moddrop")
COMPARISONS = (
    ("ra_no_moddrop", "matched_early", "gate_no_dropout_minus_matched_early"),
    ("ra_no_moddrop", "ra_static_equal", "gate_no_dropout_minus_fixed_equal_stems"),
    ("ra_no_moddrop", "ra_stems_project", "gate_no_dropout_minus_learned_projection"),
)
METRICS = ("ap50_95", "ap50", "ap75", "ar100")
BOOTSTRAP_SEED = 8404
REPLICATES = 5000
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
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def registry() -> list[dict[str, object]]:
    source = PROJECT_ROOT / "runs/v48_complete_ablation/causal_ablation_summary.json"
    rows = json.loads(source.read_text(encoding="utf-8"))["per_run"]
    selected = [row for row in rows if row["variant"] in VARIANTS]
    if len(selected) != 12:
        raise RuntimeError(f"Expected 12 frozen checkpoints, found {len(selected)}")
    for row in selected:
        path = Path(row["weights"])
        if not path.is_file() or sha256(path) != row["checkpoint_sha256"]:
            raise RuntimeError(f"Checkpoint identity failure: {row['run_id']}")
    return sorted(selected, key=lambda row: (VARIANTS.index(row["variant"]), int(row["seed"])))


def component_membership(dataset: DetectionTriAirDataset) -> tuple[dict[int, str], dict[str, list[int]]]:
    path = PROJECT_ROOT / "reproducibility/v40_expanded_adjacency_component_split_v2/extended_graph/component_membership.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    # Final partition membership is defined by the frozen manifest. The source
    # table's v39_partition column predates V40's component-level reassignment.
    by_sample = {row["sample_id"]: row["component_id"] for row in rows}
    by_index, groups = {}, defaultdict(list)
    for index in range(len(dataset)):
        sample_id = Path(get_sample_info(dataset, index)["image_path"]).stem
        component = by_sample[sample_id]
        by_index[index] = component; groups[component].append(index)
    if len(groups) != 1298 or sum(map(len, groups.values())) != 2213:
        raise RuntimeError("Frozen validation component contract mismatch")
    return by_index, dict(groups)


def infer(model: torch.nn.Module, loader: DataLoader, device: torch.device) -> tuple[list[dict], list[dict]]:
    predictions, targets_cpu = [], []
    with torch.no_grad():
        for batch_index, (images, targets) in enumerate(loader, 1):
            outputs = model([image.to(device, non_blocking=True) for image in images])
            predictions.extend({key: value.detach().cpu() for key, value in output.items()} for output in outputs)
            targets_cpu.extend({key: value.detach().cpu() for key, value in target.items()} for target in targets)
            if batch_index == 1 or batch_index % 100 == 0 or batch_index == len(loader):
                print(f"inference batch {batch_index}/{len(loader)}", flush=True)
    return predictions, targets_cpu


def component_metrics(spec: dict[str, object], groups: dict[str, list[int]],
                      predictions: list[dict], targets: list[dict]) -> list[dict[str, object]]:
    rows = []
    for component_index, component in enumerate(sorted(groups), 1):
        indices = groups[component]
        metrics = coco_detection_metrics([predictions[index] for index in indices],
                                         [targets[index] for index in indices], score_thresh=0.0,
                                         max_detections=100)
        rows.append({"run_id": spec["run_id"], "variant": spec["variant"], "seed": int(spec["seed"]),
                     "component_id": component, "images": len(indices), "gt_boxes": int(metrics["gt_boxes"]),
                     "detections": int(metrics["detections"]),
                     **{metric: float(metrics[metric]) for metric in METRICS},
                     "checkpoint_sha256": spec["checkpoint_sha256"]})
        if component_index == 1 or component_index % 200 == 0 or component_index == len(groups):
            print(f"component metric {component_index}/{len(groups)}", flush=True)
    return rows


def bootstrap(rows: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    lookup = {(row["variant"], int(row["seed"]), row["component_id"]): row for row in rows}
    components = sorted({row["component_id"] for row in rows})
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    samples = rng.integers(0, len(components), size=(REPLICATES, len(components)), endpoint=False)
    summaries, replicates = [], []
    for minuend, subtrahend, label in COMPARISONS:
        for metric in METRICS:
            deltas = np.asarray([
                statistics.mean(float(lookup[(minuend, seed, component)][metric]) -
                                float(lookup[(subtrahend, seed, component)][metric]) for seed in (0, 1, 2))
                for component in components
            ], dtype=np.float64)
            values = deltas[samples].mean(axis=1)
            summaries.append({
                "comparison": label, "metric": metric, "estimand": "three-seed mean component-macro metric delta",
                "components": len(components), "seeds": 3, "replicates": REPLICATES,
                "bootstrap_seed": BOOTSTRAP_SEED, "observed_delta": float(deltas.mean()),
                "bootstrap_mean_delta": float(values.mean()),
                "percentile_95_low": float(np.quantile(values, 0.025)),
                "percentile_95_high": float(np.quantile(values, 0.975)),
                "fraction_delta_gt_zero": float((values > 0).mean()),
            })
            replicates.extend({"comparison": label, "metric": metric, "replicate": index,
                               "delta": float(value)} for index, value in enumerate(values))
    return summaries, replicates


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=r"D:\download\triair")
    parser.add_argument("--out", type=Path, default=Path("runs/v84_jei_critical_closure/component_cluster_bootstrap"))
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--batch-size", type=int, default=4)
    args = parser.parse_args()
    out = (PROJECT_ROOT / args.out).resolve() if not args.out.is_absolute() else args.out
    out.mkdir(parents=True, exist_ok=True); raw = out / "raw"; raw.mkdir(exist_ok=True)
    split = PROJECT_ROOT / SPLIT
    if sha256(split) != EXPECTED_SPLIT_HASH:
        raise RuntimeError("Frozen development-validation split hash mismatch")
    dataset = DetectionTriAirDataset(args.data, split_file=str(split), mode="rgbte", train=False, modality_dropout=0.0)
    _, groups = component_membership(dataset)
    device = torch.device(args.device)
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=False, num_workers=0,
                        collate_fn=collate_fn, pin_memory=device.type == "cuda")
    all_rows = []
    for spec in registry():
        result_path = raw / f"{spec['run_id']}__component_metrics.csv"
        if result_path.is_file():
            with result_path.open(encoding="utf-8", newline="") as handle:
                run_rows = list(csv.DictReader(handle))
            if len(run_rows) != len(groups) or run_rows[0]["checkpoint_sha256"] != spec["checkpoint_sha256"]:
                raise RuntimeError(f"Resume identity mismatch: {result_path}")
        else:
            checkpoint = torch.load(spec["weights"], map_location=device, weights_only=False)
            cfg = checkpoint.get("model_cfg", {})
            model = build_detector(spec["model"], model_name=cfg.get("model_name", "repvit_m0_9.dist_300e_in1k"),
                                   img_size=cfg.get("img_size", 640), num_classes=cfg.get("num_classes", 2),
                                   fpn_out_channels=cfg.get("fpn_out_channels", 128), score_thresh=0.001,
                                   nms_thresh=0.6, detections_per_img=100)
            model.load_state_dict(checkpoint["model_state"], strict=True); model.to(device).eval()
            predictions, targets = infer(model, loader, device)
            run_rows = component_metrics(spec, groups, predictions, targets)
            write_csv(result_path, run_rows)
            del model, checkpoint, predictions, targets; torch.cuda.empty_cache()
        all_rows.extend(run_rows)
        atomic_json(out / "run_status.json", {"state": "RUNNING", "completed_runs": len(all_rows) // len(groups),
                                                "required_runs": 12, "locked_holdout_accessed": False})
    write_csv(out / "per_component_metrics.csv", all_rows)
    summaries, replicates = bootstrap(all_rows)
    write_csv(out / "bootstrap_summary.csv", summaries)
    write_csv(out / "bootstrap_replicates.csv", replicates)
    (out / "analysis.md").write_text(
        "# V84 Component-Cluster Bootstrap\n\n"
        "The resampling unit is the 1,298-component identity from the leakage-aware validation split. For each "
        "checkpoint, COCO AP/AP50/AP75/AR100 is first computed separately within each component. The paired "
        "component difference is averaged across seeds 0, 1, and 2, and 5,000 bootstrap samples draw components "
        "with replacement using seed 8404.\n\n"
        "The estimand is explicitly the equally weighted component-macro metric, not the image-weighted headline "
        "COCO metric. Components without foreground boxes receive the project evaluator's zero local AP/AR and "
        "therefore do not independently penalize false positives; this is a limitation of the local component "
        "estimand. The interval is descriptive component-aware uncertainty, not a broad significance claim. The "
        "locked holdout was not accessed.\n",
        encoding="utf-8")
    atomic_json(out / "run_status.json", {"state": "COMPLETE", "completed_runs": 12, "required_runs": 12,
                                            "components": len(groups), "replicates": REPLICATES,
                                            "locked_holdout_accessed": False})


if __name__ == "__main__":
    main()
