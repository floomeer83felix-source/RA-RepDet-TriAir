#!/usr/bin/env python
"""CPU-safe smoke tests for Modality-Subset Consistency Distillation."""

import hashlib
from pathlib import Path
import sys

import torch


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rarepdet.train_mscd import (
    FPNFeatureHook,
    build_reliability_model,
    feature_consistency_loss,
    load_teacher,
    select_mscd_features,
    transformed_backbone_features,
)


PROTECTED = [
    "rarepdet/train_early_fusion.py",
    "rarepdet/models/early_fusion_fcos.py",
    "rarepdet/models/reliability_fusion_fcos.py",
    "datasets/triair_dataset.py",
    "rarepdet/train_availability_fusion.py",
    "rarepdet/models/availability_reliability_fusion_fcos.py",
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


def nonzero_grad(parameters):
    for parameter in parameters:
        if parameter.grad is not None and torch.isfinite(parameter.grad).all() and float(parameter.grad.abs().sum()) > 0:
            return True
    return False


def target_for_smoke():
    return {
        "boxes": torch.tensor([[20.0, 20.0, 80.0, 80.0]], dtype=torch.float32),
        "labels": torch.tensor([1], dtype=torch.int64),
        "image_id": torch.tensor([0], dtype=torch.int64),
    }


def main():
    rows = []
    torch.manual_seed(0)
    teacher_weights = PROJECT_ROOT / "runs" / "E2_reliability_dropout015_repvit_fcos_e50" / "weights" / "best.pt"
    img_size = 128

    teacher = load_teacher(teacher_weights, img_size=img_size, device=torch.device("cpu"))
    student = build_reliability_model(img_size=img_size, score_thresh=0.05).cpu()
    reference = build_reliability_model(img_size=img_size, score_thresh=0.05).cpu()
    check(sum(p.numel() for p in student.parameters()) == sum(p.numel() for p in reference.parameters()), "Parameter count of student equals E2 exactly", rows)

    teacher_hook = FPNFeatureHook(teacher)
    student_hook = FPNFeatureHook(student)
    try:
        full = torch.rand(1, 5, img_size, img_size)
        missing = full.clone()
        missing[:, 3:4] = 0.0
        image = full[0]
        missing_image = missing[0]
        target = target_for_smoke()

        teacher.eval()
        student.train()
        with torch.no_grad():
            teacher_features = transformed_backbone_features(teacher, [image], teacher_hook)

        student.zero_grad(set_to_none=True)
        losses = student([missing_image], [target])
        student_features = select_mscd_features(student_hook.features)
        check(
            [tuple(student_features[k].shape) for k in student_features] == [tuple(teacher_features[k].shape) for k in teacher_features],
            "Hooks capture matching P3/P4/P5 shapes for teacher and student",
            rows,
        )
        detector_loss = sum(losses.values())
        detector_loss.backward()
        check(nonzero_grad(student.parameters()), "Student parameters receive gradients from detector loss", rows)

        student.zero_grad(set_to_none=True)
        student_hook.clear()
        student_features = transformed_backbone_features(student, [missing_image], student_hook)
        cons_loss = feature_consistency_loss(student_features, teacher_features)
        check(torch.isfinite(cons_loss), "Consistency loss is finite for one missing-modality synthetic batch", rows)
        cons_loss.backward()
        check(not nonzero_grad(teacher.parameters()), "Teacher parameters receive no gradients", rows)
        check(nonzero_grad(student.parameters()), "Student parameters receive gradients from consistency loss", rows)

        student.zero_grad(set_to_none=True)
        teacher_hook.clear()
        student_hook.clear()
        with torch.no_grad():
            teacher_full_features = transformed_backbone_features(teacher, [image], teacher_hook)
        _ = student([image], [target])
        student_full_features = select_mscd_features(student_hook.features)
        full_cons = feature_consistency_loss(student_full_features, teacher_full_features)
        check(torch.isfinite(full_cons), "Consistency loss is finite for full-modality synthetic batch", rows)

        student.eval()
        with torch.no_grad():
            output = student([image])
        check(
            isinstance(output, list) and {"boxes", "labels", "scores"}.issubset(output[0].keys()),
            "Inference output of the student is unchanged in structure relative to E2",
            rows,
        )
    finally:
        teacher_hook.close()
        student_hook.close()

    for rel in PROTECTED:
        path = PROJECT_ROOT / rel
        digest = sha256(path) if path.exists() else "MISSING"
        rows.append(("INFO", f"{rel} sha256={digest}"))

    out_path = PROJECT_ROOT / "runs" / "mscd_smoke_test.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# MSCD Smoke Test",
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
