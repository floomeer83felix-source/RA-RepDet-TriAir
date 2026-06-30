#!/usr/bin/env python
"""Smoke tests for Phase 4B seeded training reproducibility controls."""

import argparse
import csv
import hashlib
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace

import torch


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rarepdet.models.early_fusion_fcos import build_detector  # noqa: E402
from rarepdet.train_early_fusion import (  # noqa: E402
    configure_reproducibility,
    count_params,
    log_line,
    make_train_generator,
    reproducibility_lines,
    write_config,
)


EXPECTED = {
    "train": 7439,
    "val": 2213,
    "guard": 837,
    "exact_rgb_matched_val_images": 0,
    "exact_rgb_matched_train_images": 0,
    "exact_rgb_group_count": 0,
    "id_guard_violations": 0,
}


def resolve_path(path):
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def model_state_sha(seed, model_type="early"):
    configure_reproducibility(seed)
    model = build_detector(
        model_type=model_type,
        model_name="repvit_m0_9.dist_300e_in1k",
        img_size=640,
        num_classes=2,
        fpn_out_channels=128,
    )
    digest = hashlib.sha256()
    for key, value in sorted(model.state_dict().items()):
        tensor = value.detach().cpu().contiguous()
        digest.update(key.encode("utf-8"))
        digest.update(str(tensor.dtype).encode("utf-8"))
        digest.update(",".join(str(dim) for dim in tensor.shape).encode("utf-8"))
        digest.update(tensor.numpy().tobytes(order="C"))
    params = count_params(model)
    del model
    return digest.hexdigest(), params


def first_shuffle_indices(seed, length=7439, n=32):
    generator = make_train_generator(seed, torch.device("cpu"))
    return torch.randperm(length, generator=generator).tolist()[:n]


def read_list_count(path):
    return len([line for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()])


def read_candidate_row(path, candidate):
    with Path(path).open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("candidate") == candidate:
                return row
    raise RuntimeError(f"Missing candidate {candidate} in {path}")


def check_config_and_log(seed):
    configure_reproducibility(seed)
    model = build_detector(
        model_type="early",
        model_name="repvit_m0_9.dist_300e_in1k",
        img_size=640,
        num_classes=2,
        fpn_out_channels=128,
    )
    args = SimpleNamespace(
        model="early",
        data=r"D:\download\triair",
        train_split=str(PROJECT_ROOT / "runs" / "blocked_split_candidates" / "block64_guard16_seed0_train.txt"),
        val_split=str(PROJECT_ROOT / "runs" / "blocked_split_candidates" / "block64_guard16_seed0_val.txt"),
        epochs=50,
        batch_size=4,
        img_size=640,
        device="cuda",
        lr=1e-4,
        num_workers=0,
        out="runs/seed_smoke_tmp",
        modality_dropout=0.0,
        seed=seed,
    )
    settings = configure_reproducibility(seed)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        config_path = tmp_path / "config.txt"
        log_path = tmp_path / "train_log.txt"
        write_config(config_path, args, model, 7439, 2213, settings)
        for line in reproducibility_lines(args, settings):
            log_line(line, log_path)
        config_text = config_path.read_text(encoding="utf-8")
        log_text = log_path.read_text(encoding="utf-8")
    del model
    return "seed: 0" in config_text and "requested_seed: 0" in config_text and "requested_seed: 0" in log_text


def check_split_integrity(train_path, val_path, guard_path, summary_path):
    row = read_candidate_row(summary_path, "block64_guard16_seed0")
    checks = {
        "train_count": read_list_count(train_path) == EXPECTED["train"],
        "val_count": read_list_count(val_path) == EXPECTED["val"],
        "guard_count": read_list_count(guard_path) == EXPECTED["guard"],
    }
    for key in ("exact_rgb_matched_val_images", "exact_rgb_matched_train_images", "exact_rgb_group_count", "id_guard_violations"):
        checks[key] = int(row[key]) == EXPECTED[key]
    return checks


def pass_fail(value):
    return "pass" if value else "fail"


def main():
    parser = argparse.ArgumentParser(description="Run Phase 4B seed reproducibility smoke tests.")
    parser.add_argument("--train-list", default="runs/blocked_split_candidates/block64_guard16_seed0_train.txt")
    parser.add_argument("--val-list", default="runs/blocked_split_candidates/block64_guard16_seed0_val.txt")
    parser.add_argument("--guard-list", default="runs/blocked_split_candidates/block64_guard16_seed0_guard.txt")
    parser.add_argument("--summary", default="runs/blocked_split_proposal_summary.csv")
    parser.add_argument("--out", default="runs/seed_reproducibility_smoke.md")
    args = parser.parse_args()

    train_path = resolve_path(args.train_list)
    val_path = resolve_path(args.val_list)
    guard_path = resolve_path(args.guard_list)
    summary_path = resolve_path(args.summary)
    out_path = resolve_path(args.out)

    sha0_a, early_params_a = model_state_sha(0, "early")
    sha0_b, early_params_b = model_state_sha(0, "early")
    sha2, early_params_2 = model_state_sha(2, "early")
    _, reliability_params = model_state_sha(0, "reliability")

    shuffle0_a = first_shuffle_indices(0)
    shuffle0_b = first_shuffle_indices(0)
    shuffle2 = first_shuffle_indices(2)
    split_checks = check_split_integrity(train_path, val_path, guard_path, summary_path)
    config_log_ok = check_config_and_log(0)
    legacy_ok = configure_reproducibility(None)["deterministic_algorithms"] == "legacy_unseeded" and make_train_generator(None, torch.device("cpu")) is None

    checks = {
        "same_seed_initial_state_identical": sha0_a == sha0_b,
        "different_seed_initial_state_differs": sha0_a != sha2,
        "same_seed_first_32_shuffle_identical": shuffle0_a == shuffle0_b,
        "different_seed_first_32_shuffle_differs": shuffle0_a != shuffle2,
        "config_and_log_record_seed": config_log_ok,
        "early_param_count_unchanged": early_params_a == early_params_b == early_params_2 == 6591609,
        "reliability_param_count_unchanged": reliability_params == 6593293,
        "legacy_unseeded_path_preserved": legacy_ok,
    }
    checks.update(split_checks)
    all_pass = all(checks.values())

    lines = [
        "# Seed Reproducibility Smoke Test",
        "",
        f"Overall: **{pass_fail(all_pass)}**",
        "",
        "## Checks",
        "",
        "| Check | Result |",
        "| --- | --- |",
    ]
    for key, value in checks.items():
        lines.append(f"| {key} | {pass_fail(value)} |")
    lines.extend(
        [
            "",
            "## Initial Model SHA256",
            "",
            f"- seed 0 run A: `{sha0_a}`",
            f"- seed 0 run B: `{sha0_b}`",
            f"- seed 2: `{sha2}`",
            "",
            "## First 32 Shuffled Training Indices",
            "",
            f"- seed 0 run A: `{shuffle0_a}`",
            f"- seed 0 run B: `{shuffle0_b}`",
            f"- seed 2: `{shuffle2}`",
            "",
            "## Clean Split Integrity",
            "",
            f"- train list: `{train_path}`",
            f"- val list: `{val_path}`",
            f"- guard list: `{guard_path}`",
            f"- train/val/guard counts: {EXPECTED['train']} / {EXPECTED['val']} / {EXPECTED['guard']}",
            "- exact RGB train/validation matches: 0",
            "- same-family guard violations: 0",
            "",
        ]
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved: {out_path}")
    print(f"Overall: {pass_fail(all_pass)}")
    if not all_pass:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
