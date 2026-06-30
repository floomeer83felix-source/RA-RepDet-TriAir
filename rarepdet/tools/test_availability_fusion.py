#!/usr/bin/env python
"""CPU-safe smoke tests for availability-conditioned reliability fusion."""

import hashlib
from pathlib import Path
import sys

import torch


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rarepdet.models.availability_reliability_fusion_fcos import build_availability_reliability_fcos


PROTECTED = [
    "rarepdet/train_early_fusion.py",
    "rarepdet/models/early_fusion_fcos.py",
    "rarepdet/models/reliability_fusion_fcos.py",
    "datasets/triair_dataset.py",
]


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check(condition, message, rows):
    status = "PASS" if bool(condition) else "FAIL"
    rows.append((status, message))
    if not condition:
        raise AssertionError(message)


def availability_case(name):
    mapping = {
        "full": torch.tensor([[1.0, 1.0, 1.0]]),
        "no_rgb": torch.tensor([[0.0, 1.0, 1.0]]),
        "no_thermal": torch.tensor([[1.0, 0.0, 1.0]]),
        "no_event": torch.tensor([[1.0, 1.0, 0.0]]),
    }
    return mapping[name]


def main():
    rows = []
    torch.manual_seed(0)
    model = build_availability_reliability_fcos(img_size=128, score_thresh=0.05).cpu()
    image = torch.rand(1, 5, 128, 128)

    model.eval()
    with torch.no_grad():
        _ = model.backbone(image, )

    for mode, absent_index in (("no_rgb", 0), ("no_thermal", 1), ("no_event", 2)):
        availability = availability_case(mode)
        model.backbone.set_availability(availability)
        with torch.no_grad():
            _ = model.backbone(image)
        alpha = model.backbone.last_alpha
        energy = model.backbone.last_post_stem_energy
        check(float(alpha[0, absent_index]) <= 1e-7, f"{mode} alpha absent modality <= 1e-7", rows)
        check(float(energy[0, absent_index]) == 0.0, f"{mode} post-stem absent modality energy is zero", rows)

    availability = availability_case("full")
    model.backbone.set_availability(availability)
    with torch.no_grad():
        _ = model.backbone(image)
    alpha = model.backbone.last_alpha
    check(torch.allclose(alpha.sum(dim=1), torch.ones(1), atol=1e-6), "full alpha sums to 1", rows)

    model.train()
    train_image = torch.rand(5, 128, 128)
    target = {
        "boxes": torch.tensor([[20.0, 20.0, 80.0, 80.0]], dtype=torch.float32),
        "labels": torch.tensor([1], dtype=torch.int64),
        "image_id": torch.tensor([0], dtype=torch.int64),
    }
    losses = model([train_image], [target], availability=availability)
    check(isinstance(losses, dict) and all(torch.isfinite(v).all() for v in losses.values()), "FCOS training loss works", rows)

    model.eval()
    with torch.no_grad():
        outputs = model([train_image], availability=availability)
    check(isinstance(outputs, list) and "boxes" in outputs[0], "FCOS inference output works", rows)

    for rel in PROTECTED:
        path = PROJECT_ROOT / rel
        digest = sha256(path) if path.exists() else "MISSING"
        rows.append(("INFO", f"{rel} sha256={digest}"))

    out_path = PROJECT_ROOT / "runs" / "acrf_smoke_test.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# ACRF Smoke Test",
        "",
        "| Status | Check |",
        "| --- | --- |",
    ]
    lines.extend(f"| {status} | {message} |" for status, message in rows)
    lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
