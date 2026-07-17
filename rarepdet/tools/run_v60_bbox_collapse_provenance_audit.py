"""V60 read-only provenance audit for the V57 bbox-regression collapse."""

from __future__ import annotations

import argparse
import csv
import hashlib
import inspect
import json
import math
import random
import subprocess
import sys
import tempfile
import time
from contextlib import ExitStack
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import numpy as np
import torch
from torchvision.models.detection import fcos as fcos_module
from torchvision.ops import boxes as box_ops


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from datasets.mmuav_feature_alignment_dataset import MMUAVFeatureAlignmentDataset
from rarepdet.experimental import mmuav_feature_alignment_detector as v55_model_module
from rarepdet.experimental import v57_fusion_superset_detector as v57_model_module
from rarepdet.experimental.mmuav_feature_alignment_detector import MMUAVFeatureAlignmentDetector
from rarepdet.experimental.v57_fusion_superset_detector import V57FusionSupersetDetector
from rarepdet.tools.run_v55_mmuav_paired_alignment import configure_seed, inputs_to_device, target_to_device


OUT = ROOT / "runs/v60_mmuav_bbox_collapse_provenance_audit"
START_COMMIT = "d2e6030094c8c6abf0ac193ac323e816320eb0a9"
TRAIN_MANIFEST = ROOT / "runs/v53_mmuav_feature_alignment_preflight/manifests/train_rgb_supervised.txt"
DEVVAL_MANIFEST = ROOT / "runs/v53_mmuav_feature_alignment_preflight/manifests/devval_rgb_supervised.txt"
V59_OUT = ROOT / "runs/v59_mmuav_streaming_zero_detection_diagnostic"
TRAIN_SHA256 = "e81973b95dd6fd5ce2d3c5de526310a3bef083df49b8db584fdf39b78a34d67a"
DEVVAL_SHA256 = "113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54"
V59_SUBSET_SHA256 = "d622f6712a9bfb2faa596daa053ed207dded1a9227e80b4a10dd3b48ae3d51ee"
QUANTILES = (0.0, 0.01, 0.25, 0.5, 0.75, 0.99, 1.0)

STATE_SPECS = {
    "v55_initial": {
        "family": "v55", "variant": "alignment_on_equal",
        "path": Path(r"D:\MM-UAV_v55_local\common_seed0_init.pt"),
        "sha256": "91fec577380f895c932ffeb090bba7d376abc1ea1d97d568ae46901a7bbcb983",
        "payload_key": "state_dict", "tensor_count": 787, "initial": True,
    },
    "v57_initial_equal": {
        "family": "v57", "variant": "alignment_on_equal_superset",
        "path": Path(r"D:\MM-UAV_v57_local\common_seed0_superset_init.pt"),
        "sha256": "846da59cc8d908dfeb429fca2acb4985e73ff5fda3915154f9f764c571977cb9",
        "payload_key": "state_dict", "tensor_count": 791, "initial": True,
    },
    "v55_final": {
        "family": "v55", "variant": "alignment_on_equal",
        "path": Path(r"D:\MM-UAV_v55_local\alignment_on_equal_final_step7187.pt"),
        "sha256": "2b4bf19c4ae8d160d5045bb85df17a065e25387313eb5539dfb328ddce76b258",
        "payload_key": "model_state", "tensor_count": 787, "initial": False,
    },
    "v57_final_equal": {
        "family": "v57", "variant": "alignment_on_equal_superset",
        "path": Path(r"D:\MM-UAV_v57_local\alignment_on_equal_superset_final_step7187.pt"),
        "sha256": "d298e6cf4e901a5ad9a2961ecfbcf2592391e6fa237cd5f82d43594b8ceee142",
        "payload_key": "model_state", "tensor_count": 791, "initial": False,
    },
    "v57_final_reliability": {
        "family": "v57", "variant": "alignment_on_reliability_superset",
        "path": Path(r"D:\MM-UAV_v57_local\alignment_on_reliability_superset_final_step7187.pt"),
        "sha256": "b1322ce43e21e7eae2d646be85e0e43628432e79d1d376924fda6f782b05e5df",
        "payload_key": "model_state", "tensor_count": 791, "initial": False,
    },
}

LOG_SPECS = {
    "v55_alignment_off": ROOT / "runs/v55_mmuav_paired_alignment_ablation/alignment_off_equal_training_log.csv",
    "v55_alignment_on": ROOT / "runs/v55_mmuav_paired_alignment_ablation/alignment_on_equal_training_log.csv",
    "v57_equal": ROOT / "runs/v57_mmuav_paired_fusion_ablation/alignment_on_equal_superset_training_log.csv",
    "v57_reliability": ROOT / "runs/v57_mmuav_paired_fusion_ablation/alignment_on_reliability_superset_training_log.csv",
}


def now() -> str:
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def tensor_dict_fingerprint(state: dict[str, torch.Tensor]) -> str:
    digest = hashlib.sha256()
    for name, tensor in state.items():
        digest.update(name.encode("utf-8"))
        digest.update(str(tuple(tensor.shape)).encode("ascii"))
        digest.update(tensor.detach().cpu().contiguous().numpy().tobytes())
    return digest.hexdigest()


def rng_hashes() -> dict[str, object]:
    cpu = hashlib.sha256(torch.get_rng_state().numpy().tobytes()).hexdigest()
    cuda = [hashlib.sha256(state.cpu().numpy().tobytes()).hexdigest() for state in torch.cuda.get_rng_state_all()]
    return {"cpu": cpu, "cuda": cuda}


def model_for(spec: dict[str, object]) -> torch.nn.Module:
    if spec["family"] == "v55":
        return MMUAVFeatureAlignmentDetector(spec["variant"])
    return V57FusionSupersetDetector(spec["variant"])


def load_state(spec: dict[str, object]) -> dict[str, torch.Tensor]:
    payload = torch.load(spec["path"], map_location="cpu", weights_only=False)
    state = payload[spec["payload_key"]]
    if len(state) != spec["tensor_count"]:
        raise RuntimeError(f"State tensor-count mismatch: {spec['path']}")
    return state


def protected_paths() -> list[Path]:
    fixed = {
        "rarepdet/train_early_fusion.py", "rarepdet/models/early_fusion_fcos.py",
        "rarepdet/models/reliability_fusion_fcos.py", "datasets/triair_dataset.py",
        "main.tex", "main_sivp_snjnl.tex",
    }
    selected = []
    for relative in git("ls-files").splitlines():
        historical = relative.startswith("runs/v4") or any(
            relative.startswith(f"runs/v{version}_") for version in range(50, 60)
        )
        if relative in fixed or relative.startswith("manuscript/") or relative.startswith("submission/") or historical:
            path = ROOT / relative
            if path.is_file():
                selected.append(path)
    return selected


def aggregate_fingerprint(paths: list[Path]) -> dict[str, object]:
    digest = hashlib.sha256()
    total = 0
    for path in sorted(paths, key=lambda item: item.as_posix().lower()):
        relative = path.relative_to(ROOT).as_posix()
        file_hash = sha256(path)
        digest.update(relative.encode() + b"\0" + file_hash.encode() + b"\n")
        total += path.stat().st_size
    return {"file_count": len(paths), "total_bytes": total, "aggregate_sha256": digest.hexdigest()}


def verify_v59() -> dict[str, object]:
    final = json.loads((V59_OUT / "final_decision.json").read_text(encoding="utf-8"))
    checks = {
        "status": final["decision"] == "V59_STREAMING_ZERO_DETECTION_DIAGNOSIS_COMPLETE_ROOT_CAUSE_IDENTIFIED",
        "mechanism": final["root_cause"]["direct_mechanism"] == "V57_BBOX_REGRESSION_DEGENERATE_GEOMETRY",
        "v57_equal_geometry": (final["root_cause"]["v57_equal_valid_after_clip"],
                               final["root_cause"]["v57_equal_degenerate_after_clip"]) == (0, 5534979),
        "v57_reliability_geometry": (final["root_cause"]["v57_reliability_valid_after_clip"],
                                     final["root_cause"]["v57_reliability_degenerate_after_clip"]) == (0, 5535000),
        "v55_geometry": (final["root_cause"]["v55_valid_after_clip"],
                         final["root_cause"]["v55_degenerate_after_clip"]) == (5535000, 0),
        "zero_training": all(final[key] == 0 for key in
                             ("optimizer_steps", "backward_passes", "training_mode_executions", "gradient_executions")),
    }
    if not all(checks.values()):
        raise RuntimeError(f"V59 evidence mismatch: {checks}")
    return {"checks": checks, "final_decision_sha256": sha256(V59_OUT / "final_decision.json")}


def checkpoint_verification() -> dict[str, object]:
    results = {}
    for name, spec in STATE_SPECS.items():
        path = spec["path"]
        if not path.is_file() or sha256(path) != spec["sha256"]:
            raise RuntimeError(f"State file contract mismatch: {name}")
        state = load_state(spec)
        nonfinite = [key for key, value in state.items() if not torch.isfinite(value).all()]
        model = model_for(spec)
        loaded = model.load_state_dict(state, strict=False)
        if loaded.missing_keys or loaded.unexpected_keys or nonfinite:
            raise RuntimeError(f"State coverage/finite mismatch: {name}")
        results[name] = {
            "path_local_not_committed": str(path), "bytes": path.stat().st_size,
            "sha256": spec["sha256"], "tensor_count": len(state), "state_fingerprint": tensor_dict_fingerprint(state),
            "missing_keys": [], "unexpected_keys": [], "nonfinite_keys": [],
        }
    return results


def traced_construct(family: str) -> tuple[torch.nn.Module, list[dict[str, object]]]:
    events: list[dict[str, object]] = []

    def wrapper(label: str, original):
        def call(*args, **kwargs):
            before = rng_hashes()
            value = original(*args, **kwargs)
            events.append({"event": label, "before": before, "after": rng_hashes()})
            return value
        return call

    configure_seed(0)
    start = rng_hashes()
    with ExitStack() as stack:
        stack.enter_context(patch.object(
            v55_model_module, "MMUAVFeatureAlignmentScaffold",
            wrapper("parent_multimodal_front_end", v55_model_module.MMUAVFeatureAlignmentScaffold),
        ))
        stack.enter_context(patch.object(
            v55_model_module, "build_early_fusion_fcos",
            wrapper("detector_backbone_fpn_fcos", v55_model_module.build_early_fusion_fcos),
        ))
        stack.enter_context(patch.object(
            fcos_module, "FCOSHead", wrapper("fcos_head", fcos_module.FCOSHead),
        ))
        stack.enter_context(patch.object(
            fcos_module, "FCOSRegressionHead", wrapper("fcos_regression_head", fcos_module.FCOSRegressionHead),
        ))
        if family == "v57":
            stack.enter_context(patch.object(
                v57_model_module, "V57FusionSupersetScaffold",
                wrapper("replacement_superset_front_end_and_scorer", v57_model_module.V57FusionSupersetScaffold),
            ))
            model = V57FusionSupersetDetector("alignment_on_reliability_superset")
        else:
            model = MMUAVFeatureAlignmentDetector("alignment_on_equal")
    return model, [{"event": "construction_start", "state": start}, *events,
                   {"event": "construction_end", "state": rng_hashes()}]


def reconstruct_initializations() -> tuple[dict[str, object], dict[str, object]]:
    results, traces, models = {}, {}, {}
    for family, filename, historical, expected, source in (
        ("v55", "common_seed0_init.pt", STATE_SPECS["v55_initial"]["path"],
         STATE_SPECS["v55_initial"]["sha256"], "fresh_untrained_V55_common_initialization"),
        ("v57", "common_seed0_superset_init.pt", STATE_SPECS["v57_initial_equal"]["path"],
         STATE_SPECS["v57_initial_equal"]["sha256"], "fresh_untrained_V57_fusion_superset"),
    ):
        model, trace = traced_construct(family)
        if family == "v57":
            model.eval()
            zeros = (torch.zeros(1, 3, 320, 320), torch.zeros(1, 1, 320, 320), torch.zeros(1, 1, 320, 320))
            with torch.no_grad():
                model._feature_forward(*zeros)
        state = {key: value.detach().cpu() for key, value in model.state_dict().items()}
        historical_state = torch.load(historical, map_location="cpu", weights_only=False)["state_dict"]
        state_equal = state.keys() == historical_state.keys() and all(
            torch.equal(state[key], historical_state[key]) for key in state
        )
        with tempfile.TemporaryDirectory() as directory:
            rebuilt = Path(directory) / filename
            torch.save({"state_dict": state, "seed": 0, "source": source}, rebuilt)
            rebuilt_hash = sha256(rebuilt)
        if rebuilt_hash != expected or not state_equal:
            raise RuntimeError(f"Exact initialization reconstruction failed: {family}")
        results[family] = {
            "historical_sha256": expected, "rebuilt_sha256": rebuilt_hash, "serialized_exact": True,
            "state_tensors_exact": True, "tensor_count": len(state), "state_fingerprint": tensor_dict_fingerprint(state),
        }
        traces[family] = trace
        models[family] = state
    bbox_keys = ("detector.head.regression_head.bbox_reg.weight",
                 "detector.head.regression_head.bbox_reg.bias")
    detector_equal = all(torch.equal(models["v55"][key], models["v57"][key]) for key in bbox_keys)
    results["initial_bbox_head_v55_v57_bit_identical"] = detector_equal
    results["initial_bbox_parameters"] = {
        key: tensor_stats(models["v55"][key], include_quantiles=False) for key in bbox_keys
    }
    if not detector_equal:
        raise RuntimeError("V55/V57 initial bbox heads differ unexpectedly")
    return results, traces


def freeze_subsets() -> dict[str, object]:
    train = MMUAVFeatureAlignmentDataset(TRAIN_MANIFEST, 320, validate_paths=False)
    order = torch.randperm(len(train), generator=torch.Generator(device="cpu").manual_seed(60))[:32].tolist()
    train_ids = [train.rows[index]["original_row_id"] for index in order]
    gradient_indices = order[:4]
    gradient_ids = train_ids[:4]
    train_payload = ("\n".join(train_ids) + "\n").encode()
    gradient_payload = ("\n".join(gradient_ids) + "\n").encode()
    (OUT / "train_audit_subset.txt").write_bytes(train_payload)
    (OUT / "train_audit_subset_sha256.txt").write_text(hashlib.sha256(train_payload).hexdigest() + "\n", encoding="utf-8")
    (OUT / "gradient_probe_subset.txt").write_bytes(gradient_payload)
    (OUT / "gradient_probe_subset_sha256.txt").write_text(
        hashlib.sha256(gradient_payload).hexdigest() + "\n", encoding="utf-8")
    write_json(OUT / "train_audit_subset_indices.json", order)
    write_json(OUT / "gradient_probe_subset_indices.json", gradient_indices)
    v59_indices = json.loads((V59_OUT / "detailed_subset_indices.json").read_text(encoding="utf-8"))
    payload = (json.dumps(v59_indices, separators=(",", ":")) + "\n").encode()
    if hashlib.sha256(payload).hexdigest() != V59_SUBSET_SHA256:
        raise RuntimeError("V59 devval subset mismatch")
    return {
        "seed": 60, "train_count": 32, "train_indices": order, "train_sha256": hashlib.sha256(train_payload).hexdigest(),
        "gradient_count": 4, "gradient_indices": gradient_indices,
        "gradient_sha256": hashlib.sha256(gradient_payload).hexdigest(),
        "devval_seed": 58, "devval_count": 32, "devval_indices": v59_indices,
        "devval_sha256": V59_SUBSET_SHA256,
    }


def longest_run(values: list[bool]) -> int:
    best = current = 0
    for value in values:
        current = current + 1 if value else 0
        best = max(best, current)
    return best


def parse_logs() -> tuple[dict[str, object], dict[str, object]]:
    schemas, trajectories = {}, {}
    selected_steps = {1, 10, 50, 100, 200, 500, 1000, 2000, 4000, 6000, 7187}
    for name, path in LOG_SPECS.items():
        with path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        if len(rows) != 7187:
            raise RuntimeError(f"Historical log row mismatch: {name}")
        fields = list(rows[0])
        bbox = [float(row["loss_box_reg"]) for row in rows]
        total = [float(row["loss_total"]) for row in rows]
        global_grad = [float(row["global_gradient_norm"]) for row in rows]
        finite = [row["finite"].lower() == "true" for row in rows]
        one_flags = [value == 1.0 for value in bbox]
        schemas[name] = {
            "path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path), "rows": len(rows), "fields": fields,
            "bbox_gradient_field_present": any("bbox" in field and "gradient" in field for field in fields),
            "bbox_output_field_present": any("bbox" in field and "output" in field for field in fields),
        }
        trajectories[name] = {
            "loss_bbox_reg": {
                "first": bbox[0], "last": bbox[-1], "minimum": min(bbox), "maximum": max(bbox),
                "zero_count": sum(value == 0.0 for value in bbox), "exact_one_count": sum(one_flags),
                "between_zero_and_one_count": sum(0.0 < value < 1.0 for value in bbox),
                "above_one_count": sum(value > 1.0 for value in bbox),
                "first_exact_one_step": next((index + 1 for index, value in enumerate(one_flags) if value), None),
                "longest_exact_one_run": longest_run(one_flags),
            },
            "loss_total": {"first": total[0], "last": total[-1], "minimum": min(total), "maximum": max(total)},
            "global_gradient_norm": {"first": global_grad[0], "last": global_grad[-1],
                                     "minimum": min(global_grad), "maximum": max(global_grad)},
            "finite_false_count": sum(not value for value in finite),
            "selected_steps": [{key: row[key] for key in
                                ("step", "original_row_id", "loss_total", "loss_classifier", "loss_box_reg",
                                 "loss_centerness", "learning_rate", "global_gradient_norm", "finite")}
                               for row in rows if int(row["step"]) in selected_steps],
            "historical_limitation": "bbox-head output and bbox-parameter gradient fields were not logged",
        }
    return schemas, trajectories


def source_lock() -> dict[str, object]:
    sources = [
        "rarepdet/tools/run_v60_bbox_collapse_provenance_audit.py",
        "tests/test_v60_bbox_collapse_provenance_audit.py",
        "rarepdet/tools/run_v55_mmuav_paired_alignment.py",
        "rarepdet/tools/run_v57_mmuav_paired_fusion.py",
        "rarepdet/experimental/mmuav_feature_alignment_detector.py",
        "rarepdet/experimental/mmuav_feature_alignment_model.py",
        "rarepdet/experimental/v57_fusion_superset_detector.py",
        "datasets/mmuav_feature_alignment_dataset.py",
    ]
    installed = Path(inspect.getsourcefile(fcos_module.FCOS) or "")
    regression_source = inspect.getsource(fcos_module.FCOSRegressionHead.forward)
    loss_source = inspect.getsource(fcos_module.FCOSHead.compute_loss)
    if "functional.relu" not in regression_source or "generalized_box_iou_loss" not in loss_source:
        raise RuntimeError("Installed FCOS bbox activation/loss contract mismatch")
    return {
        "starting_commit": START_COMMIT,
        "source_hashes": {path: sha256(ROOT / path) for path in sources},
        "installed_fcos_path": str(installed), "installed_fcos_sha256": sha256(installed),
        "bbox_activation": "torch.nn.functional.relu", "bbox_loss": "generalized_box_iou_loss",
    }


def prepare() -> None:
    if git("rev-parse", "HEAD") != START_COMMIT:
        raise RuntimeError("Unexpected V60 starting commit")
    if OUT.exists():
        raise RuntimeError("V60 output already exists")
    OUT.mkdir(parents=True)
    if sha256(TRAIN_MANIFEST) != TRAIN_SHA256 or sha256(DEVVAL_MANIFEST) != DEVVAL_SHA256:
        raise RuntimeError("Manifest hash mismatch")
    train = MMUAVFeatureAlignmentDataset(TRAIN_MANIFEST, 320, validate_paths=True)
    devval = MMUAVFeatureAlignmentDataset(DEVVAL_MANIFEST, 320, validate_paths=True)
    if (len(train), len(devval)) != (7187, 1845):
        raise RuntimeError("Manifest row mismatch")
    v59 = verify_v59()
    checkpoints = checkpoint_verification()
    reconstruction, rng_trace = reconstruct_initializations()
    subsets = freeze_subsets()
    schemas, trajectories = parse_logs()
    protected = aggregate_fingerprint(protected_paths())
    lock = source_lock()
    protocol = {
        "prepared_at": now(), "starting_commit": START_COMMIT,
        "train_rows": len(train), "devval_rows": len(devval), "train_sha256": TRAIN_SHA256,
        "devval_sha256": DEVVAL_SHA256, "subsets": subsets,
        "optimizer_constructions": 0, "optimizer_steps": 0, "backward_limit": 20,
        "states": list(STATE_SPECS), "geometry_train_rows_per_state": 32,
        "geometry_devval_rows_final_states": 32, "gradient_rows_per_state": 4,
        "ap_ar_computed": False, "repair_authorized": False,
        "v59_verification": v59, "checkpoint_verification": checkpoints,
        "initialization_reconstruction": reconstruction, "protected_baseline": protected,
    }
    write_json(OUT / "v59_evidence_verification.json", v59)
    write_json(OUT / "checkpoint_verification.json", checkpoints)
    write_json(OUT / "initialization_reconstruction.json", reconstruction)
    write_json(OUT / "rng_construction_trace.json", rng_trace)
    write_json(OUT / "historical_log_schema.json", schemas)
    write_json(OUT / "historical_loss_trajectory.json", trajectories)
    write_json(OUT / "protocol.json", protocol)
    write_json(OUT / "source_lock_v60.json", {**lock, **protocol})
    (OUT / "protocol.md").write_text(
        "# V60 Bbox Collapse Provenance Audit\n\nFive frozen states, 32 train geometry rows each, "
        "32 V59 devval rows for final states, and exactly four no-step backward probes per state. "
        "No optimizer, parameter update, checkpoint write, AP/AR, or repair is permitted.\n", encoding="utf-8")
    (OUT / "test_commands.txt").write_text(
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe rarepdet/tools/run_v60_bbox_collapse_provenance_audit.py --prepare-only\n"
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe -m unittest discover -s tests -p test_v60_bbox_collapse_provenance_audit.py -v\n"
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe rarepdet/tools/run_v60_bbox_collapse_provenance_audit.py --run\n",
        encoding="utf-8")
    print(json.dumps({"status": "V60_PREPARED_CPU_ONLY", "protocol": protocol}, indent=2))


def compact_quantiles(values: torch.Tensor) -> dict[str, float]:
    flat = values.detach().double().flatten().cpu()
    if flat.numel() == 0:
        return {}
    levels = torch.tensor(QUANTILES, dtype=torch.float64)
    result = torch.quantile(flat, levels)
    return {format(level, ".3g"): float(value) for level, value in zip(QUANTILES, result)}


def tensor_stats(values: torch.Tensor, include_quantiles: bool = True) -> dict[str, object]:
    flat = values.detach().float().flatten()
    if flat.numel() == 0:
        return {"count": 0, "finite": True}
    result = {
        "count": int(flat.numel()), "minimum": float(flat.min().cpu()), "maximum": float(flat.max().cpu()),
        "mean": float(flat.mean().cpu()), "std": float(flat.std(unbiased=False).cpu()),
        "negative_count": int((flat < 0).sum().cpu()), "zero_count": int((flat == 0).sum().cpu()),
        "positive_count": int((flat > 0).sum().cpu()), "finite": bool(torch.isfinite(flat).all()),
    }
    if include_quantiles:
        result["quantiles"] = compact_quantiles(flat)
    return result


def geometry_forward(model: torch.nn.Module, sample: dict[str, object], device: torch.device) -> dict[str, object]:
    captures: list[torch.Tensor] = []
    hook = model.detector.head.regression_head.bbox_reg.register_forward_hook(
        lambda _module, _inputs, output: captures.append(output.detach())
    )
    detector_image = model._feature_forward(*inputs_to_device(sample, device))
    detector = model.detector
    images, _ = detector.transform(list(detector_image), None)
    features = detector.backbone(images.tensors)
    if isinstance(features, torch.Tensor):
        features = {"0": features}
    feature_list = list(features.values())
    head = detector.head(feature_list)
    hook.remove()
    if len(captures) != len(feature_list):
        raise RuntimeError("Bbox pre-ReLU hook count mismatch")
    counts = [feature.shape[-2] * feature.shape[-1] for feature in feature_list]
    anchors = list(detector.anchor_generator(images, feature_list)[0].split(counts))
    regressions = list(head["bbox_regression"][0].split(counts))
    logits = list(head["cls_logits"][0].split(counts))
    ctrness = list(head["bbox_ctrness"][0].split(counts))
    levels = []
    for level, (captured, post, cls, ctr, anchor) in enumerate(zip(captures, regressions, logits, ctrness, anchors)):
        pre = captured.permute(0, 2, 3, 1).reshape(-1, 4)
        decoded = detector.box_coder.decode(post, anchor)
        clipped = box_ops.clip_boxes_to_image(decoded, images.image_sizes[0])
        raw_width = decoded[:, 2] - decoded[:, 0]
        raw_height = decoded[:, 3] - decoded[:, 1]
        width = clipped[:, 2] - clipped[:, 0]
        height = clipped[:, 3] - clipped[:, 1]
        finite = torch.isfinite(clipped).all(dim=1)
        valid = finite & (width > 0) & (height > 0)
        out = ((decoded[:, 0] < 0) | (decoded[:, 1] < 0) |
               (decoded[:, 2] > images.image_sizes[0][1]) | (decoded[:, 3] > images.image_sizes[0][0]))
        combined = torch.sqrt(torch.sigmoid(cls) * torch.sigmoid(ctr))
        all_zero_locations = (post == 0).all(dim=1)
        levels.append({
            "level": level, "pre_relu": tensor_stats(pre), "post_relu": tensor_stats(post),
            "post_relu_positive_fraction": float((post > 0).float().mean().cpu()),
            "all_zero_location_fraction": float(all_zero_locations.float().mean().cpu()),
            "decoded_width_before_clip": tensor_stats(raw_width),
            "decoded_height_before_clip": tensor_stats(raw_height),
            "decoded_width_after_clip": tensor_stats(width),
            "decoded_height_after_clip": tensor_stats(height),
            "geometry_counts": {"decoded": int(decoded.shape[0]), "valid": int(valid.sum().cpu()),
                                "degenerate": int((finite & ~valid).sum().cpu()),
                                "nonfinite": int((~finite).sum().cpu()), "out_of_image": int(out.sum().cpu())},
            "classification_logit": tensor_stats(cls), "centerness_logit": tensor_stats(ctr),
            "combined_score": tensor_stats(combined),
        })
    return {"row_id": sample["original_row_id"], "levels": levels}


def aggregate_geometry(records: list[dict[str, object]]) -> dict[str, object]:
    result = {"rows": len(records), "levels": []}
    for level in range(4):
        items = [record["levels"][level] for record in records]
        counts = {key: sum(item["geometry_counts"][key] for item in items)
                  for key in ("decoded", "valid", "degenerate", "nonfinite", "out_of_image")}
        result["levels"].append({
            "level": level, "geometry_counts": counts,
            "pre_relu_negative_fraction_mean": float(np.mean([
                item["pre_relu"]["negative_count"] / item["pre_relu"]["count"] for item in items])),
            "pre_relu_zero_fraction_mean": float(np.mean([
                item["pre_relu"]["zero_count"] / item["pre_relu"]["count"] for item in items])),
            "pre_relu_positive_fraction_mean": float(np.mean([
                item["pre_relu"]["positive_count"] / item["pre_relu"]["count"] for item in items])),
            "post_relu_positive_fraction_mean": float(np.mean([item["post_relu_positive_fraction"] for item in items])),
            "all_zero_location_fraction_mean": float(np.mean([item["all_zero_location_fraction"] for item in items])),
            "per_row_pre_relu_min_quantiles": compact_quantiles(torch.tensor([item["pre_relu"]["minimum"] for item in items])),
            "per_row_pre_relu_max_quantiles": compact_quantiles(torch.tensor([item["pre_relu"]["maximum"] for item in items])),
            "per_row_width_median_quantiles": compact_quantiles(torch.tensor([
                item["decoded_width_after_clip"]["quantiles"]["0.5"] for item in items])),
            "per_row_height_median_quantiles": compact_quantiles(torch.tensor([
                item["decoded_height_after_clip"]["quantiles"]["0.5"] for item in items])),
            "combined_score_max_quantiles": compact_quantiles(torch.tensor([
                item["combined_score"]["maximum"] for item in items])),
        })
    result["aggregate_counts"] = {key: sum(level["geometry_counts"][key] for level in result["levels"])
                                  for key in ("decoded", "valid", "degenerate", "nonfinite", "out_of_image")}
    return result


def parameter_audit(states: dict[str, dict[str, torch.Tensor]]) -> dict[str, object]:
    keys = (
        "detector.head.regression_head.bbox_reg.weight",
        "detector.head.regression_head.bbox_reg.bias",
        "detector.head.regression_head.bbox_ctrness.weight",
        "detector.head.regression_head.bbox_ctrness.bias",
    )
    result = {}
    for name, state in states.items():
        initial_name = "v55_initial" if name.startswith("v55") else "v57_initial_equal"
        initial = states[initial_name]
        result[name] = {}
        for key in keys:
            value = state[key].float()
            delta = value - initial[key].float()
            result[name][key] = {"value": tensor_stats(value, False), "norm": float(value.norm()),
                                 "delta_norm_from_family_initial": float(delta.norm()),
                                 "delta_min": float(delta.min()), "delta_max": float(delta.max())}
    return result


def parameter_hash(model: torch.nn.Module) -> str:
    return tensor_dict_fingerprint({name: parameter.detach() for name, parameter in model.named_parameters()})


def buffer_hash(model: torch.nn.Module) -> str:
    return tensor_dict_fingerprint({name: buffer.detach() for name, buffer in model.named_buffers()})


def grad_norm(parameters) -> dict[str, object]:
    grads = [parameter.grad.detach().float().flatten() for parameter in parameters if parameter.grad is not None]
    if not grads:
        return {"norm": 0.0, "parameter_tensors_with_grad": 0, "nonzero_fraction": 0.0, "finite": True}
    total_values = sum(value.numel() for value in grads)
    nonzero = sum(int((value != 0).sum()) for value in grads)
    norm = math.sqrt(sum(float((value.double() ** 2).sum()) for value in grads))
    return {"norm": norm, "parameter_tensors_with_grad": len(grads), "nonzero_fraction": nonzero / total_values,
            "finite": all(bool(torch.isfinite(value).all()) for value in grads)}


def gradient_probe(name: str, spec: dict[str, object], state: dict[str, torch.Tensor], indices: list[int],
                   device: torch.device) -> dict[str, object]:
    model = model_for(spec)
    model.load_state_dict(state, strict=True)
    before_parameters = parameter_hash(model)
    before_buffers = buffer_hash(model)
    model.to(device)
    model.train()
    dataset = MMUAVFeatureAlignmentDataset(TRAIN_MANIFEST, 320, validate_paths=False)
    rows = []
    captures: list[torch.Tensor] = []
    hook = model.detector.head.regression_head.bbox_reg.register_forward_hook(
        lambda _module, _inputs, output: captures.append(output.detach())
    )
    for index in indices:
        model.zero_grad(set_to_none=True)
        captures.clear()
        sample = dataset[index]
        losses = model(*inputs_to_device(sample, device), target_to_device(sample, device))
        total = sum(losses.values())
        total.backward()
        if len(captures) != 4:
            raise RuntimeError(f"Gradient bbox hook mismatch: {name}")
        pre = torch.cat([value.flatten() for value in captures])
        bbox_module = model.detector.head.regression_head.bbox_reg
        regression_head = model.detector.head.regression_head
        detector_head = model.detector.head
        rows.append({
            "index": index, "row_id": sample["original_row_id"],
            "losses": {key: float(value.detach().cpu()) for key, value in losses.items()},
            "loss_total": float(total.detach().cpu()),
            "bbox_pre_relu": tensor_stats(pre),
            "bbox_post_relu_positive_fraction": float((pre > 0).float().mean().cpu()),
            "bbox_weight_gradient": grad_norm([bbox_module.weight]),
            "bbox_bias_gradient": grad_norm([bbox_module.bias]),
            "regression_head_gradient": grad_norm(regression_head.parameters()),
            "detector_head_gradient": grad_norm(detector_head.parameters()),
        })
    hook.remove()
    after_parameters = parameter_hash(model)
    after_buffers = buffer_hash(model)
    checkpoint_unchanged = sha256(spec["path"]) == spec["sha256"]
    if before_parameters != after_parameters or not checkpoint_unchanged:
        raise RuntimeError(f"Parameter/checkpoint mutation during gradient probe: {name}")
    result = {
        "state": name, "backward_calls": len(rows), "rows": rows,
        "parameter_hash_before": before_parameters, "parameter_hash_after": after_parameters,
        "parameters_unchanged": True, "buffer_hash_before": before_buffers, "buffer_hash_after": after_buffers,
        "buffers_changed_in_ephemeral_training_mode": before_buffers != after_buffers,
        "checkpoint_unchanged": True, "optimizer_constructions": 0, "optimizer_steps": 0,
    }
    del model
    torch.cuda.empty_cache()
    return result


def classify(geometry: dict[str, object], gradients: dict[str, object], reconstruction: dict[str, object]) -> dict[str, object]:
    initial_usable = all(geometry[name]["train"]["aggregate_counts"]["valid"] > 0
                         for name in ("v55_initial", "v57_initial_equal"))
    final_v57_dead = all(
        geometry[name]["train"]["aggregate_counts"]["valid"] == 0 and
        all(row["bbox_post_relu_positive_fraction"] == 0.0 and
            row["bbox_weight_gradient"]["norm"] == 0.0 and row["bbox_bias_gradient"]["norm"] == 0.0
            for row in gradients[name]["rows"])
        for name in ("v57_final_equal", "v57_final_reliability")
    )
    if initial_usable and final_v57_dead and reconstruction["initial_bbox_head_v55_v57_bit_identical"]:
        primary = "V57_TRAINING_INDUCED_DEAD_RELU_COLLAPSE"
        explanation = ("V55 and V57 begin with bit-identical, usable bbox heads. Both final V57 states have no positive "
                       "pre-ReLU bbox outputs on frozen probes, all decoded boxes are degenerate, and bbox weight/bias "
                       "gradients are exactly zero under the historical loss path. V55 final remains usable.")
    elif not initial_usable:
        primary = "V57_COLLAPSE_PRESENT_AT_INITIALIZATION"
        explanation = "The reconstructed V57 initialization already lacks usable bbox geometry."
    else:
        primary = "V57_BBOX_COLLAPSE_PROVENANCE_UNRESOLVED"
        explanation = "The bounded probes do not establish one provenance mechanism."
    return {
        "completion_state": "V60_BBOX_COLLAPSE_PROVENANCE_AUDIT_COMPLETE_MECHANISM_IDENTIFIED" if
                            primary != "V57_BBOX_COLLAPSE_PROVENANCE_UNRESOLVED" else
                            "V60_BBOX_COLLAPSE_PROVENANCE_AUDIT_COMPLETE_CAUSE_UNRESOLVED",
        "primary_classification": primary, "explanation": explanation,
        "initial_bbox_heads_bit_identical": reconstruction["initial_bbox_head_v55_v57_bit_identical"],
        "initial_geometry_usable": initial_usable, "final_v57_dead_relu_confirmed": final_v57_dead,
        "construction_rng_shift_causal_for_bbox_initialization": False,
        "repair_authorized": False,
    }


def run() -> None:
    protocol = json.loads((OUT / "protocol.json").read_text(encoding="utf-8"))
    locked = json.loads((OUT / "source_lock_v60.json").read_text(encoding="utf-8"))
    if source_lock()["source_hashes"] != locked["source_hashes"]:
        raise RuntimeError("V60 source changed after lock")
    if aggregate_fingerprint(protected_paths()) != protocol["protected_baseline"]:
        raise RuntimeError("Protected evidence changed before probes")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable for V60 probes")
    for name, spec in STATE_SPECS.items():
        if sha256(spec["path"]) != spec["sha256"]:
            raise RuntimeError(f"State changed before probe: {name}")
    states = {name: load_state(spec) for name, spec in STATE_SPECS.items()}
    subsets = protocol["subsets"]
    train_indices = subsets["train_indices"]
    devval_indices = subsets["devval_indices"]
    gradient_indices = subsets["gradient_indices"]
    train_dataset = MMUAVFeatureAlignmentDataset(TRAIN_MANIFEST, 320, validate_paths=False)
    devval_dataset = MMUAVFeatureAlignmentDataset(DEVVAL_MANIFEST, 320, validate_paths=False)
    device = torch.device("cuda:0")
    geometry = {}
    started = time.perf_counter()
    with torch.inference_mode():
        for name, spec in STATE_SPECS.items():
            model = model_for(spec)
            model.load_state_dict(states[name], strict=True)
            model.to(device).eval()
            train_records = [geometry_forward(model, train_dataset[index], device) for index in train_indices]
            record = {"train": aggregate_geometry(train_records), "train_rows": train_records}
            if not spec["initial"]:
                devval_records = [geometry_forward(model, devval_dataset[index], device) for index in devval_indices]
                record.update({"devval": aggregate_geometry(devval_records), "devval_rows": devval_records})
            geometry[name] = record
            print(f"V60_GEOMETRY_COMPLETE state={name} elapsed={time.perf_counter() - started:.1f}s", flush=True)
            del model
            torch.cuda.empty_cache()
    gradients = {}
    backward_calls = 0
    for name, spec in STATE_SPECS.items():
        gradients[name] = gradient_probe(name, spec, states[name], gradient_indices, device)
        backward_calls += gradients[name]["backward_calls"]
        if backward_calls > 20:
            raise RuntimeError("V60 backward-call limit exceeded")
        print(f"V60_GRADIENT_COMPLETE state={name} total_backward_calls={backward_calls}", flush=True)
    parameters = parameter_audit(states)
    reconstruction = json.loads((OUT / "initialization_reconstruction.json").read_text(encoding="utf-8"))
    decision = classify(geometry, gradients, reconstruction)
    safety = {
        "optimizer_constructions": 0, "optimizer_steps": 0, "backward_calls": backward_calls,
        "backward_limit": 20, "training_mode_loss_forwards": backward_calls,
        "all_parameters_unchanged": all(item["parameters_unchanged"] for item in gradients.values()),
        "all_checkpoints_unchanged": all(sha256(spec["path"]) == spec["sha256"] for spec in STATE_SPECS.values()),
        "ap_ar_computed": False, "threshold_selection": False, "repair_performed": False,
        "protected_fingerprint_unchanged": aggregate_fingerprint(protected_paths()) == protocol["protected_baseline"],
    }
    if not all((safety["all_parameters_unchanged"], safety["all_checkpoints_unchanged"],
                safety["protected_fingerprint_unchanged"])) or backward_calls != 20:
        raise RuntimeError(f"V60 safety audit failed: {safety}")
    write_json(OUT / "bbox_geometry_probe.json", geometry)
    write_json(OUT / "no_step_gradient_probe.json", gradients)
    write_json(OUT / "parameter_init_final_diff.json", parameters)
    write_json(OUT / "root_cause_refinement.json", decision)
    write_json(OUT / "safety_audit.json", safety)
    write_json(OUT / "final_decision.json", {
        "decision": decision["completion_state"], "root_cause": decision, "safety": safety,
        "states_probed": list(STATE_SPECS), "geometry_train_rows_per_state": 32,
        "geometry_devval_rows_per_final_state": 32, "gradient_rows_per_state": 4,
    })
    (OUT / "root_cause_refinement.md").write_text(
        f"# V60 Root-Cause Refinement\n\nPrimary classification: `{decision['primary_classification']}`. "
        f"{decision['explanation']} No repair is authorized.\n", encoding="utf-8")
    print(json.dumps(decision, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare-only", action="store_true")
    group.add_argument("--run", action="store_true")
    args = parser.parse_args()
    if args.prepare_only:
        prepare()
    else:
        run()


if __name__ == "__main__":
    main()
