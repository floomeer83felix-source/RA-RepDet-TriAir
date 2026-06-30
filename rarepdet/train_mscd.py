#!/usr/bin/env python
"""Train Modality-Subset Consistency Distillation for Reliability RepViT-FCOS."""

import argparse
import random
from collections import OrderedDict
from pathlib import Path
import subprocess
import sys
import time

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from datasets.triair_dataset import collate_fn
from rarepdet.data import DetectionTriAirDataset
from rarepdet.metrics import detection_metrics, format_metrics
from rarepdet.models.early_fusion_fcos import build_detector


MSCD_LEVELS = ("0", "1", "2")


def resolve_path(path):
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def log_line(message, log_file=None):
    print(message)
    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with log_file.open("a", encoding="utf-8") as f:
            f.write(message + "\n")


class MSCDTriAirDataset(Dataset):
    """Return full input for the teacher and modality-dropped input for student."""

    def __init__(self, data_root, split_file=None, train=False, modality_dropout=0.0):
        self.dataset = DetectionTriAirDataset(
            data_root,
            split_file=split_file,
            mode="rgbte",
            train=False,
            modality_dropout=0.0,
        )
        self.train = train
        self.modality_dropout = float(modality_dropout)
        if self.modality_dropout < 0.0 or self.modality_dropout >= 1.0:
            raise ValueError("--modality-dropout must be in [0, 1)")

    def __len__(self):
        return len(self.dataset)

    def _apply_modality_dropout(self, image):
        if not self.train or self.modality_dropout <= 0.0:
            return image

        original = image.clone()
        dropped = []
        # Same group convention as E2: RGB, thermal, event. Never drop all three.
        if random.random() < self.modality_dropout:
            image[0:3] = 0
            dropped.append("rgb")
        if random.random() < self.modality_dropout:
            image[3:4] = 0
            dropped.append("thermal")
        if random.random() < self.modality_dropout:
            image[4:5] = 0
            dropped.append("event")
        if len(dropped) == 3:
            keep = random.choice(("rgb", "thermal", "event"))
            if keep == "rgb":
                image[0:3] = original[0:3]
            elif keep == "thermal":
                image[3:4] = original[3:4]
            else:
                image[4:5] = original[4:5]
        return image

    def __getitem__(self, index):
        full_image, target = self.dataset[index]
        student_image = self._apply_modality_dropout(full_image.clone())
        return full_image, student_image, target


def mscd_collate(batch):
    full_images, student_images, targets = zip(*batch)
    full_images, targets = collate_fn(list(zip(full_images, targets)))
    student_images, _ = collate_fn(list(zip(student_images, targets)))
    return full_images, student_images, targets


def move_targets_to_device(targets, device):
    return [{key: value.to(device) for key, value in target.items()} for target in targets]


def count_params(model):
    return sum(parameter.numel() for parameter in model.parameters())


def is_cuda_oom(exc):
    message = str(exc).lower()
    return "out of memory" in message or "cuda error: out of memory" in message


def current_batch_size_from_argv(default=4):
    if "--batch-size" not in sys.argv:
        return default
    index = sys.argv.index("--batch-size")
    if index + 1 >= len(sys.argv):
        return default
    try:
        return int(sys.argv[index + 1])
    except ValueError:
        return default


def argv_with_batch_size(batch_size):
    args = sys.argv[1:]
    if "--batch-size" in args:
        index = args.index("--batch-size")
        if index + 1 < len(args):
            args[index + 1] = str(batch_size)
        else:
            args.append(str(batch_size))
    else:
        args.extend(["--batch-size", str(batch_size)])
    return args


def build_reliability_model(img_size=640, score_thresh=0.2):
    return build_detector(
        model_type="reliability",
        model_name="repvit_m0_9.dist_300e_in1k",
        img_size=img_size,
        num_classes=2,
        fpn_out_channels=128,
        score_thresh=score_thresh,
    )


def load_teacher(weights, img_size, device):
    checkpoint = torch.load(resolve_path(weights), map_location=device)
    teacher = build_reliability_model(img_size=img_size, score_thresh=0.2)
    teacher.load_state_dict(checkpoint["model_state"], strict=True)
    teacher.to(device)
    teacher.eval()
    for parameter in teacher.parameters():
        parameter.requires_grad_(False)
    return teacher


class FPNFeatureHook:
    """Non-invasive hook that stores FPN outputs from a detector forward."""

    def __init__(self, model):
        self.features = None
        self.handle = model.backbone.fpn.register_forward_hook(self._hook)

    def _hook(self, module, inputs, output):
        self.features = OrderedDict((key, value) for key, value in output.items())

    def clear(self):
        self.features = None

    def close(self):
        self.handle.remove()


def select_mscd_features(features, levels=MSCD_LEVELS):
    if features is None:
        raise RuntimeError("FPN features were not captured.")
    selected = OrderedDict()
    keys = list(features.keys())
    for level in levels:
        if level not in features:
            raise RuntimeError(f"Missing FPN level {level}; available levels: {keys}")
        selected[level] = features[level]
    return selected


def transformed_backbone_features(model, images, hook, levels=MSCD_LEVELS):
    """Run the detector transform and backbone only, then return hooked FPN levels."""

    hook.clear()
    image_list, _ = model.transform(images, None)
    _ = model.backbone(image_list.tensors)
    return select_mscd_features(hook.features, levels)


def feature_consistency_loss(student_features, teacher_features, levels=MSCD_LEVELS):
    student_selected = select_mscd_features(student_features, levels)
    teacher_selected = select_mscd_features(teacher_features, levels)
    losses = []
    for level in levels:
        student = student_selected[level]
        teacher = teacher_selected[level].detach()
        if student.shape != teacher.shape:
            raise RuntimeError(f"FPN feature shape mismatch at level {level}: {student.shape} vs {teacher.shape}")
        student = F.normalize(student, p=2, dim=1)
        teacher = F.normalize(teacher, p=2, dim=1)
        losses.append(F.smooth_l1_loss(student, teacher))
    return torch.stack(losses).mean()


def lambda_cons_for_epoch(epoch, warmup_epochs, ramp_end_epoch, lambda_max):
    if epoch <= warmup_epochs:
        return 0.0
    if epoch >= ramp_end_epoch:
        return float(lambda_max)
    span = max(ramp_end_epoch - warmup_epochs, 1)
    return float(lambda_max) * float(epoch - warmup_epochs) / float(span)


def get_alpha(model):
    alpha = getattr(model.backbone, "last_alpha", None)
    if alpha is None:
        return None
    return alpha.detach().float().mean(dim=0).cpu().tolist()


def loss_is_finite(*losses):
    return all(torch.isfinite(loss).all() for loss in losses)


def save_checkpoint(path, model, optimizer, epoch, args, best_ap50, metrics):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint = {
        "epoch": epoch,
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "best_ap50": best_ap50,
        "metrics": metrics,
        "model_cfg": {
            "model_type": "reliability",
            "training_method": "mscd",
            "model_name": "repvit_m0_9.dist_300e_in1k",
            "in_chans": 5,
            "img_size": args.img_size,
            "num_classes": 2,
            "fpn_out_channels": 128,
        },
        "train_args": vars(args),
    }
    tmp_path = path.with_name(f".{path.name}.tmp")
    if tmp_path.exists():
        tmp_path.unlink()
    try:
        torch.save(checkpoint, tmp_path)
        if tmp_path.stat().st_size == 0:
            raise RuntimeError(f"Checkpoint write produced an empty file: {tmp_path}")
        tmp_path.replace(path)
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink()
        raise


def load_checkpoint_safely(path, map_location, log_file=None):
    try:
        return torch.load(path, map_location=map_location)
    except Exception as exc:
        log_line(f"WARNING: could not load checkpoint {path}: {exc}", log_file)
        return None


def evaluate(model, loader, device, score_thresh=0.05):
    model.eval()
    predictions = []
    targets_cpu = []
    image_count = 0
    start = time.time()
    with torch.no_grad():
        for full_images, _, targets in loader:
            images = [image.to(device, non_blocking=True) for image in full_images]
            outputs = model(images)
            predictions.extend([{key: value.detach().cpu() for key, value in output.items()} for output in outputs])
            targets_cpu.extend([{key: value.detach().cpu() for key, value in target.items()} for target in targets])
            image_count += len(images)
    metrics = detection_metrics(predictions, targets_cpu, score_thresh=score_thresh)
    metrics["eval_fps"] = image_count / max(time.time() - start, 1e-6)
    return metrics


def write_config(path, args, model, teacher, train_len, val_len):
    with path.open("w", encoding="utf-8") as f:
        f.write("MSCD RarePDet experiment config\n")
        f.write("================================\n")
        for key, value in sorted(vars(args).items()):
            f.write(f"{key}: {value}\n")
        f.write(f"train_samples: {train_len}\n")
        f.write(f"val_samples: {val_len}\n")
        f.write(f"params: {count_params(model)}\n")
        f.write(f"teacher_params: {count_params(teacher)}\n")
        f.write("extra_inference_params: 0\n")


def train_one_epoch(model, teacher, teacher_hook, student_hook, loader, optimizer, device, epoch, args, log_file):
    model.train()
    teacher.eval()
    running_total = 0.0
    running_det = 0.0
    running_cons = 0.0
    lambda_cons = lambda_cons_for_epoch(
        epoch,
        args.cons_warmup_epochs,
        args.cons_ramp_end_epoch,
        args.lambda_cons_max,
    )

    for iteration, (full_images, student_images, targets) in enumerate(loader, 1):
        full_images = [image.to(device, non_blocking=True) for image in full_images]
        student_images = [image.to(device, non_blocking=True) for image in student_images]
        targets = move_targets_to_device(targets, device)

        teacher_hook.clear()
        with torch.no_grad():
            teacher_features = transformed_backbone_features(teacher, full_images, teacher_hook)

        student_hook.clear()
        optimizer.zero_grad(set_to_none=True)
        loss_dict = model(student_images, targets)
        detector_loss = sum(loss_dict.values())
        consistency_loss = feature_consistency_loss(student_hook.features, teacher_features)
        total_loss = detector_loss + lambda_cons * consistency_loss

        if not loss_is_finite(detector_loss, consistency_loss, total_loss):
            log_line("ERROR: NaN or Inf loss detected. Stopping training.", log_file)
            raise SystemExit(1)

        total_loss.backward()
        optimizer.step()

        total_value = float(total_loss.detach().cpu())
        det_value = float(detector_loss.detach().cpu())
        cons_value = float(consistency_loss.detach().cpu())
        running_total += total_value
        running_det += det_value
        running_cons += cons_value

        if iteration == 1 or iteration % 20 == 0 or iteration == len(loader):
            parts = ", ".join(f"{key}={float(value.detach().cpu()):.4f}" for key, value in loss_dict.items())
            log_line(
                f"epoch {epoch}/{args.epochs} iter {iteration}/{len(loader)} "
                f"loss={total_value:.4f} detector={det_value:.4f} cons={cons_value:.4f} "
                f"lambda_cons={lambda_cons:.5f} mean_loss={running_total / iteration:.4f} "
                f"mean_detector={running_det / iteration:.4f} mean_cons={running_cons / iteration:.4f} {parts}",
                log_file,
            )

        if iteration % 50 == 0:
            alpha = get_alpha(model)
            if alpha is not None:
                log_line(
                    f"epoch {epoch} iter {iteration} alpha_rgb={alpha[0]:.4f} "
                    f"alpha_thermal={alpha[1]:.4f} alpha_event={alpha[2]:.4f}",
                    log_file,
                )


def main():
    parser = argparse.ArgumentParser(description="Train MSCD Reliability RepViT-FCOS on TriAir.")
    parser.add_argument("--data", default=r"D:\download\triair")
    parser.add_argument("--train-split", default=r"D:\download\triair\splits\train.txt")
    parser.add_argument("--val-split", default=r"D:\download\triair\splits\val.txt")
    parser.add_argument("--teacher-weights", default="runs/E2_reliability_dropout015_repvit_fcos_e50/weights/best.pt")
    parser.add_argument("--epochs", default=50, type=int)
    parser.add_argument("--batch-size", default=4, type=int)
    parser.add_argument("--img-size", default=640, type=int)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--lr", default=1e-4, type=float)
    parser.add_argument("--num-workers", default=0, type=int)
    parser.add_argument("--modality-dropout", default=0.15, type=float)
    parser.add_argument("--lambda-cons-max", default=0.05, type=float)
    parser.add_argument("--cons-warmup-epochs", default=5, type=int)
    parser.add_argument("--cons-ramp-end-epoch", default=15, type=int)
    parser.add_argument("--out", default="runs/E6_mscd_dropout015_repvit_fcos_e50")
    args = parser.parse_args()

    out_dir = resolve_path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    weights_dir = out_dir / "weights"
    weights_dir.mkdir(parents=True, exist_ok=True)
    log_file = out_dir / "train_log.txt"
    resume_path = weights_dir / "last.pt"
    resume_available = resume_path.exists()
    if log_file.exists() and not resume_available:
        log_file.unlink()

    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        log_line("WARNING: CUDA requested but unavailable. Falling back to CPU.", log_file)
        device = torch.device("cpu")
    log_line(f"Using device: {device}", log_file)

    train_dataset = MSCDTriAirDataset(
        args.data,
        split_file=args.train_split,
        train=True,
        modality_dropout=args.modality_dropout,
    )
    val_dataset = MSCDTriAirDataset(args.data, split_file=args.val_split, train=False, modality_dropout=0.0)
    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.num_workers,
        collate_fn=mscd_collate,
        pin_memory=(device.type == "cuda"),
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        collate_fn=mscd_collate,
        pin_memory=(device.type == "cuda"),
    )

    teacher = load_teacher(args.teacher_weights, args.img_size, device)
    model = build_reliability_model(img_size=args.img_size).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    best_ap50 = -1.0
    start_epoch = 1

    if resume_available:
        checkpoint = torch.load(resume_path, map_location=device)
        model.load_state_dict(checkpoint["model_state"], strict=True)
        optimizer.load_state_dict(checkpoint["optimizer_state"])
        best_ap50 = float(checkpoint.get("best_ap50", -1.0))
        checkpoint_epoch = int(checkpoint.get("epoch", 0))
        start_epoch = int(checkpoint.get("epoch", 0)) + 1
        best_path = weights_dir / "best.pt"
        best_checkpoint = None
        if best_path.exists():
            best_checkpoint = load_checkpoint_safely(best_path, map_location="cpu", log_file=log_file)
        if best_checkpoint is not None:
            best_metrics = best_checkpoint.get("metrics", {})
            best_ap50 = max(
                best_ap50,
                float(best_checkpoint.get("best_ap50", -1.0)),
                float(best_metrics.get("ap50", -1.0)),
            )
        else:
            checkpoint_metrics = checkpoint.get("metrics", {})
            checkpoint_ap50 = float(checkpoint_metrics.get("ap50", -1.0))
            if checkpoint_ap50 >= 0.0 and checkpoint_ap50 >= best_ap50 - 1e-12:
                save_checkpoint(best_path, model, optimizer, checkpoint_epoch, args, best_ap50, checkpoint_metrics)
                log_line(f"Repaired best checkpoint from last checkpoint: {best_path}", log_file)
        log_line(f"Resuming from checkpoint: {resume_path} at epoch {start_epoch}", log_file)

    write_config(out_dir / "config.txt", args, model, teacher, len(train_dataset), len(val_dataset))
    log_line(f"train samples: {len(train_dataset)}", log_file)
    log_line(f"val samples: {len(val_dataset)}", log_file)
    log_line(f"params: {count_params(model)}", log_file)
    log_line(f"teacher params: {count_params(teacher)}", log_file)
    log_line("extra inference params: 0", log_file)
    log_line(f"total train iterations per epoch: {len(train_loader)}", log_file)

    if start_epoch > args.epochs:
        log_line(f"Checkpoint already reached epoch {start_epoch - 1}; nothing to train.", log_file)
        return

    teacher_hook = FPNFeatureHook(teacher)
    student_hook = FPNFeatureHook(model)
    try:
        for epoch in range(start_epoch, args.epochs + 1):
            epoch_start = time.time()
            train_one_epoch(model, teacher, teacher_hook, student_hook, train_loader, optimizer, device, epoch, args, log_file)
            metrics = evaluate(model, val_loader, device)
            elapsed = time.time() - epoch_start
            log_line(
                f"epoch {epoch} validation {format_metrics(metrics)} "
                f"eval_fps={metrics['eval_fps']:.2f} epoch_time_sec={elapsed:.1f}",
                log_file,
            )

            is_best = metrics["ap50"] > best_ap50
            if is_best:
                best_ap50 = metrics["ap50"]

            last_path = weights_dir / "last.pt"
            save_checkpoint(last_path, model, optimizer, epoch, args, best_ap50, metrics)
            log_line(f"saved checkpoint: {last_path}", log_file)
            if is_best:
                best_path = weights_dir / "best.pt"
                save_checkpoint(best_path, model, optimizer, epoch, args, best_ap50, metrics)
                log_line(f"new best AP50={best_ap50:.4f}; saved checkpoint: {best_path}", log_file)
    finally:
        teacher_hook.close()
        student_hook.close()

    log_line("Training complete.", log_file)


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        if is_cuda_oom(exc) and current_batch_size_from_argv(default=4) > 2:
            print("CUDA out of memory detected. Automatically retrying with --batch-size 2.")
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            raise SystemExit(subprocess.call([sys.executable, sys.argv[0], *argv_with_batch_size(2)]))
        raise
