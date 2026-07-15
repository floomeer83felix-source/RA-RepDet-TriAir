"""Build and verify the CPU-only V53 MM-UAV feature-alignment preflight."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from datasets.mmuav_feature_alignment_dataset import MMUAVFeatureAlignmentDataset
from rarepdet.experimental.mmuav_feature_alignment_model import MMUAVFeatureAlignmentScaffold


V52 = ROOT / "runs/v52_mmuav_audit"
OUT = ROOT / "runs/v53_mmuav_feature_alignment_preflight"
MANIFESTS = OUT / "manifests"
START_COMMIT = "6cb8ba426432f0c590c937ac05dc017eb859582b"
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


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


def build_manifests() -> dict[str, object]:
    MANIFESTS.mkdir(parents=True, exist_ok=True)
    annotated = {}
    with (V52 / "manifests/annotated_only_sampled.txt").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            annotated[row["original_row_id"]] = row.get("common_track_ids", "")
    counts, sequences, hashes = {}, {}, {}
    fields = ["original_row_id", "split", "sequence", "frame_index", "rgb", "ir", "event", "gt_rgb", "gt_ir",
              "rgb_annotation_rows", "ir_annotation_rows", "source_annotation_state", "supervision_state", "common_track_ids"]
    for split in ("train", "devval"):
        source = V52 / f"manifests/{split}_sampled.txt"
        output = MANIFESTS / f"{split}_rgb_supervised.txt"
        selected = []
        with source.open(encoding="utf-8", newline="") as handle:
            for ordinal, row in enumerate(csv.DictReader(handle, delimiter="\t"), start=1):
                if int(row["rgb_annotation_rows"]) <= 0:
                    continue
                row_id = f"{split}:{ordinal:08d}"
                selected.append({
                    "original_row_id": row_id, "split": split, "sequence": row["sequence"],
                    "frame_index": row["frame_index"], "rgb": row["rgb"], "ir": row["ir"], "event": row["event"],
                    "gt_rgb": row["gt_rgb"], "gt_ir": row["gt_ir"], "rgb_annotation_rows": row["rgb_annotation_rows"],
                    "ir_annotation_rows": row["ir_annotation_rows"], "source_annotation_state": row["annotation_state"],
                    "supervision_state": "RGB_SOURCE_GT_PRESENT", "common_track_ids": annotated.get(row_id, ""),
                })
        with output.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
            writer.writeheader()
            writer.writerows(selected)
        counts[split] = len(selected)
        sequences[split] = len({row["sequence"] for row in selected})
        hashes[split] = sha256(output)
    if counts != {"train": 7187, "devval": 1845}:
        raise RuntimeError(f"RGB-supervised count mismatch: {counts}")
    if set(load_sequences("train")) & set(load_sequences("devval")):
        raise RuntimeError("Train/devval sequences overlap")
    return {"counts": counts | {"total": sum(counts.values())}, "sequence_counts": sequences,
            "hashes": hashes, "predicate": "rgb_annotation_rows > 0", "ir_only_excluded": 106,
            "unlabeled_excluded": 35898}


def load_sequences(split: str) -> set[str]:
    with (MANIFESTS / f"{split}_rgb_supervised.txt").open(encoding="utf-8", newline="") as handle:
        return {row["sequence"] for row in csv.DictReader(handle, delimiter="\t")}


def count_macs(model: torch.nn.Module, inputs: tuple[torch.Tensor, ...]) -> int:
    macs = 0
    hooks = []

    def conv_hook(module: torch.nn.Conv2d, values: tuple[torch.Tensor, ...], output: torch.Tensor) -> None:
        nonlocal macs
        kernel_ops = module.kernel_size[0] * module.kernel_size[1] * (module.in_channels // module.groups)
        macs += int(output.numel() * kernel_ops)

    def linear_hook(module: torch.nn.Linear, values: tuple[torch.Tensor, ...], output: torch.Tensor) -> None:
        nonlocal macs
        macs += int(output.numel() * module.in_features)

    for module in model.modules():
        if isinstance(module, torch.nn.Conv2d):
            hooks.append(module.register_forward_hook(conv_hook))
        elif isinstance(module, torch.nn.Linear):
            hooks.append(module.register_forward_hook(linear_hook))
    with torch.no_grad():
        model(*inputs)
    for hook in hooks:
        hook.remove()
    return macs


def run_preflight() -> dict[str, object]:
    torch.manual_seed(53)
    dataset = MMUAVFeatureAlignmentDataset(MANIFESTS / "train_rgb_supervised.txt", branch_size=128,
                                           validate_paths=True)
    sample = dataset[0]
    inputs = (sample["rgb"].unsqueeze(0), sample["ir"].unsqueeze(0), sample["event"].unsqueeze(0))
    results = {}
    for enabled in (False, True):
        model = MMUAVFeatureAlignmentScaffold(feature_channels=32, alignment_enabled=enabled, fusion_mode="equal")
        model.eval()
        with torch.no_grad():
            first = model(*inputs)
            second = model(*inputs)
        if not torch.isfinite(first["fused"]).all() or not torch.equal(first["fused"], second["fused"]):
            raise RuntimeError(f"Forward finite/determinism check failed: alignment_enabled={enabled}")
        results[f"alignment_{'on' if enabled else 'off'}"] = {
            "fused_shape": list(first["fused"].shape), "finite": True, "deterministic": True,
            "ir_theta": first["ir_theta"].tolist(), "event_theta": first["event_theta"].tolist(),
        }
    model = MMUAVFeatureAlignmentScaffold(feature_channels=32, alignment_enabled=True, fusion_mode="reliability")
    model.train()
    synthetic = (torch.randn(2, 3, 64, 64), torch.randn(2, 1, 64, 64), torch.randn(2, 1, 64, 64))
    output = model(*synthetic)
    output["fused"].square().mean().backward()
    align_grads = [parameter.grad for name, parameter in model.named_parameters() if "aligner" in name and parameter.requires_grad]
    if not align_grads or not all(gradient is not None and torch.isfinite(gradient).all() for gradient in align_grads):
        raise RuntimeError("Alignment gradient preflight failed")
    return {"device": "cpu", "cuda_probe_performed": False, "gpu_optimizer_steps": 0,
            "real_sample": {"original_row_id": sample["original_row_id"], "native_shapes": sample["modality_native_shapes"],
                            "branch_shapes": {key: list(sample[key].shape) for key in ("rgb", "ir", "event")},
                            "rgb_target_count": len(sample["target_rgb"]["boxes"])},
            "forward": results, "synthetic_backward": {"finite_alignment_gradients": True,
                                                         "alignment_parameter_tensors": len(align_grads)}}


def source_lock() -> dict[str, object]:
    changed = set(git("diff", "--name-only", START_COMMIT).splitlines())
    protected = {"rarepdet/train_early_fusion.py", "rarepdet/models/early_fusion_fcos.py",
                 "rarepdet/models/reliability_fusion_fcos.py", "datasets/triair_dataset.py"}
    historical = sorted(path for path in changed if path.startswith("runs/v52_mmuav_audit/"))
    manuscript = sorted(path for path in changed if path in {"main.tex", "main_sivp_snjnl.tex"} or
                        path.startswith("manuscript/") or path.startswith("submission/"))
    source_paths = [
        "datasets/mmuav_feature_alignment_dataset.py",
        "rarepdet/experimental/mmuav_feature_alignment.py",
        "rarepdet/experimental/mmuav_feature_alignment_model.py",
        "rarepdet/tools/prepare_v53_mmuav_feature_alignment.py",
        "tests/test_v53_mmuav_feature_alignment.py",
        "runs/v53_mmuav_feature_alignment_preflight/manifests/train_rgb_supervised.txt",
        "runs/v53_mmuav_feature_alignment_preflight/manifests/devval_rgb_supervised.txt",
    ]
    result = {"starting_commit": START_COMMIT, "protected_core_changed": sorted(protected & changed),
              "v52_evidence_changed": historical, "manuscript_changed": manuscript, "gpu_optimizer_steps": 0,
              "source_hashes": {path: sha256(ROOT / path) for path in source_paths}}
    if result["protected_core_changed"] or historical or manuscript:
        raise RuntimeError(f"Protected-path violation: {result}")
    return result


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    contract = build_manifests()
    preflight = run_preflight()
    equal = MMUAVFeatureAlignmentScaffold(32, True, "equal")
    reliability = MMUAVFeatureAlignmentScaffold(32, True, "reliability")
    estimate_inputs = (torch.zeros(1, 3, 320, 320), torch.zeros(1, 1, 320, 320), torch.zeros(1, 1, 320, 320))
    compute = {
        "classification": "CPU_SHAPE_BASED_ESTIMATE_NOT_MEASURED_GPU_USAGE", "input_branch_size": [320, 320],
        "equal_fusion_parameters": sum(p.numel() for p in equal.parameters()),
        "reliability_fusion_parameters": sum(p.numel() for p in reliability.parameters()),
        "equal_fusion_estimated_macs": count_macs(equal, estimate_inputs),
        "reliability_fusion_estimated_macs": count_macs(reliability, estimate_inputs),
        "estimated_rtx3090_risk": "LOW_FOR_SCAFFOLD_ONLY; detector/backbone integration is not measured and requires pilot monitoring",
    }
    lock = source_lock()
    hashes = {"generated_at": NOW, "source_v52_train_sha256": sha256(V52 / "manifests/train_sampled.txt"),
              "source_v52_devval_sha256": sha256(V52 / "manifests/devval_sampled.txt"),
              "train_rgb_supervised_sha256": contract["hashes"]["train"],
              "devval_rgb_supervised_sha256": contract["hashes"]["devval"]}
    write_json(OUT / "manifest_hashes.json", hashes)
    write_json(OUT / "rgb_target_contract.json", {"generated_at": NOW, **contract, "target_coordinate_system": "RGB",
                                                    "ir_role": "metadata_only", "event_target": None})
    write_json(OUT / "method_contract.json", {"generated_at": NOW, "mechanism": "STN_INSPIRED_RESIDUAL_AFFINE_FEATURE_ALIGNMENT",
                                               "reference": "RGB feature grid", "branches": ["rgb", "ir", "event"],
                                               "raw_channel_concatenation": False, "devval_gt_fitting": False,
                                               "alignment_enabled_switch": True, "production_builder_integration": False})
    write_json(OUT / "alignment_design.json", {"initialization": "exact identity via zero affine-residual head",
                                                "alignment_off": "deterministic bilinear feature-grid size matching only",
                                                "alignment_on": "learned residual affine_grid/grid_sample in feature space",
                                                "fusion_modes": ["equal", "reliability"], "pixel_calibration_claim": False})
    write_json(OUT / "compute_estimate.json", compute)
    write_json(OUT / "source_lock_v53.json", lock)
    write_json(OUT / "pilot_gate.json", {"locked": True, "gpu_optimizer_steps": 0,
                                          "reason": "V53_CPU_ONLY_PRE-REGISTRATION_AND_PREFLIGHT"})
    write_json(OUT / "preflight_result.json", preflight)

    (OUT / "rgb_target_contract.md").write_text(
        "# V53 RGB Target Contract\n\nOnly frozen rows with `rgb_annotation_rows > 0` are supervised: "
        "7,187 train + 1,845 devval = 9,032. RGB boxes are detector targets. IR boxes are metadata only; "
        "event has no target. The 106 IR-only and 35,898 unlabeled rows are excluded, never converted to negatives.\n", encoding="utf-8")
    (OUT / "manifest_integrity.md").write_text(
        f"# V53 Manifest Integrity\n\n- Train/devval/total: 7,187 / 1,845 / 9,032\n"
        f"- Train SHA256: `{hashes['train_rgb_supervised_sha256']}`\n"
        f"- Devval SHA256: `{hashes['devval_rgb_supervised_sha256']}`\n"
        "- Sequence overlap: 0\n- Media and RGB GT paths: validated\n- Synchronized numeric frame IDs: validated\n", encoding="utf-8")
    (OUT / "method_contract.md").write_text(
        "# V53 Method Contract\n\nThree native-modality branches feed independent stems. RGB defines the reference feature grid; "
        "IR and event are aligned only in feature space. This isolated scaffold is not connected to production builders and makes no pixel-calibration claim.\n",
        encoding="utf-8")
    (OUT / "alignment_design.md").write_text(
        "# V53 Alignment Design\n\nThe mechanism is STN-inspired residual affine feature alignment. A zero-initialized residual head "
        "makes the initial affine transform exactly identity. `alignment_enabled=False` provides the frozen no-alignment control. "
        "Equal and reliability-aware fusion interfaces share the same aligned features.\n", encoding="utf-8")
    (OUT / "ablation_contract.md").write_text(
        "# V53 Future Ablation Contract\n\n1. RGB-only detector.\n2. Three independent stems with alignment disabled.\n"
        "3. Learned feature alignment with fixed/equal fusion.\n4. Learned feature alignment with RA dynamic fusion.\n\n"
        "No experiment in this list was run in V53.\n", encoding="utf-8")
    (OUT / "source_lock_v53.md").write_text(
        f"# V53 Source Lock\n\nStarting commit: `{START_COMMIT}`. Protected core, V52 evidence, and manuscript changes: none. "
        "GPU optimizer steps: 0.\n", encoding="utf-8")
    (OUT / "preflight_commands.txt").write_text(
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe rarepdet/tools/prepare_v53_mmuav_feature_alignment.py\n"
        "C:\\Users\\xinnan\\.conda\\envs\\pytorch\\python.exe -m unittest discover -s tests -p test_v53_mmuav_feature_alignment.py -v\n",
        encoding="utf-8")
    print(json.dumps({"status": "V53_CPU_PREFLIGHT_READY_FOR_SEPARATE_GPU_AUTHORIZATION", **contract,
                      "compute": compute, "preflight": preflight}, indent=2))


if __name__ == "__main__":
    main()
