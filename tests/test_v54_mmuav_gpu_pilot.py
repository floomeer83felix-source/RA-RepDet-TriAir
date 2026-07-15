import csv
import hashlib
import inspect
import json
from pathlib import Path
import subprocess
import unittest

import torch

from datasets.mmuav_feature_alignment_dataset import MMUAVFeatureAlignmentDataset, transform_rgb_boxes
from rarepdet.experimental.mmuav_feature_alignment_detector import MMUAVFeatureAlignmentDetector, VARIANTS
from rarepdet.tools.run_v54_mmuav_gpu_pilot import (
    MAX_STEPS,
    TRAIN_FIELDS,
    assert_step_allowed,
    frozen_config,
    losses_are_finite,
)


ROOT = Path(__file__).resolve().parents[1]
V53 = ROOT / "runs/v53_mmuav_feature_alignment_preflight"
TRAIN = V53 / "manifests/train_rgb_supervised.txt"
DEVVAL = V53 / "manifests/devval_rgb_supervised.txt"
START = "e00f4f829445216fd778f0dc842623793a93b93f"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class V54MMUAVGpuPilotTests(unittest.TestCase):
    def test_v53_manifest_hashes_and_counts_are_exact(self):
        expected = json.loads((V53 / "manifest_hashes.json").read_text(encoding="utf-8"))
        self.assertEqual(sha256(TRAIN), expected["train_rgb_supervised_sha256"])
        self.assertEqual(sha256(DEVVAL), expected["devval_rgb_supervised_sha256"])
        with TRAIN.open(encoding="utf-8", newline="") as handle:
            train = list(csv.DictReader(handle, delimiter="\t"))
        with DEVVAL.open(encoding="utf-8", newline="") as handle:
            devval = list(csv.DictReader(handle, delimiter="\t"))
        self.assertEqual((len(train), len(devval), len(train) + len(devval)), (7187, 1845, 9032))
        self.assertTrue(all(row["split"] == "train" and row["original_row_id"].startswith("train:") for row in train))
        self.assertFalse({row["sequence"] for row in train} & {row["sequence"] for row in devval})

    def test_batch_contract_uses_rgb_transform_and_train_only(self):
        dataset = MMUAVFeatureAlignmentDataset(TRAIN, 128, validate_paths=False)
        sample = dataset[0]
        self.assertEqual(sample["split"], "train")
        self.assertTrue(sample["rgb_gt_present"])
        transforms = sample["modality_transforms"]
        box = torch.tensor([[10.0, 20.0, 30.0, 40.0]])
        self.assertFalse(torch.equal(transform_rgb_boxes(box, transforms["rgb"]),
                                     transform_rgb_boxes(box, transforms["ir"])))

    def test_independent_branches_and_no_raw_concat_detector_path(self):
        model = MMUAVFeatureAlignmentDetector("alignment_on_equal", image_size=128)
        scaffold = model.feature_scaffold
        self.assertIsNot(scaffold.rgb_stem, scaffold.ir_stem)
        self.assertIsNot(scaffold.ir_stem, scaffold.event_stem)
        self.assertEqual((scaffold.rgb_stem[0].in_channels, scaffold.ir_stem[0].in_channels,
                          scaffold.event_stem[0].in_channels), (3, 1, 1))
        source = inspect.getsource(MMUAVFeatureAlignmentDetector)
        self.assertNotIn("torch.cat", source)

    def test_alignment_off_and_on_detector_cpu_outputs_are_finite(self):
        inputs = (torch.rand(1, 3, 128, 128), torch.rand(1, 1, 128, 128), torch.rand(1, 1, 128, 128))
        for variant in ("alignment_off_equal", "alignment_on_equal"):
            model = MMUAVFeatureAlignmentDetector(variant, image_size=128).eval()
            with torch.no_grad():
                output = model(*inputs)[0]
            self.assertTrue(all(torch.isfinite(value).all() for value in output.values()))
            self.assertEqual(output["boxes"].shape[-1], 4)

    def test_identity_initialization_and_smoke_variants(self):
        identity = torch.tensor([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
        model = MMUAVFeatureAlignmentDetector("alignment_on_equal", image_size=128)
        self.assertTrue(torch.equal(model.feature_scaffold.ir_aligner.identity_theta, identity))
        self.assertTrue(torch.equal(model.feature_scaffold.event_aligner.identity_theta, identity))
        self.assertEqual(set(VARIANTS), {"rgb_only", "alignment_off_equal", "alignment_on_equal",
                                         "alignment_on_reliability"})
        self.assertEqual(frozen_config()["primary_variant"], "alignment_on_equal")

    def test_step_limit_and_nonfinite_fail_closed(self):
        self.assertEqual(MAX_STEPS, 200)
        assert_step_allowed(199)
        with self.assertRaises(RuntimeError):
            assert_step_allowed(200)
        self.assertTrue(losses_are_finite({"classification": torch.tensor(1.0)}))
        self.assertFalse(losses_are_finite({"classification": torch.tensor(float("nan"))}))
        runner = (ROOT / "rarepdet/tools/run_v54_mmuav_gpu_pilot.py").read_text(encoding="utf-8")
        self.assertIn("except torch.OutOfMemoryError", runner)
        self.assertNotIn("retry", runner.lower())

    def test_config_and_required_log_fields_are_frozen(self):
        config = frozen_config()
        self.assertEqual(config["batch_size"], 1)
        self.assertEqual(config["branch_input_size"], [320, 320])
        self.assertFalse(config["amp_enabled"])
        self.assertEqual(config["scheduler"], "none")
        self.assertFalse(config["automatic_oom_fallback"])
        required = {"step", "original_row_id", "loss_total", "global_gradient_norm",
                    "ir_alignment_gradient_norm", "event_alignment_gradient_norm", "ir_theta_mean",
                    "event_theta_mean", "ir_grid_oob_fraction", "event_grid_oob_fraction",
                    "cuda_allocated_bytes", "cuda_reserved_bytes", "step_time_sec"}
        self.assertTrue(required <= set(TRAIN_FIELDS))
        self.assertTrue(Path(config["checkpoint_local_only"]).drive.upper().startswith("D:"))

    def test_protected_paths_unchanged_before_cuda(self):
        changed = subprocess.check_output(["git", "diff", "--name-only", START], cwd=ROOT, text=True).splitlines()
        forbidden = [path for path in changed if path.startswith("runs/v53_mmuav_feature_alignment_preflight/") or
                     path.startswith("runs/v52_mmuav_audit/") or path.startswith("manuscript/") or
                     path.startswith("submission/") or path in {"datasets/triair_dataset.py", "rarepdet/train_early_fusion.py",
                                                                  "main.tex", "main_sivp_snjnl.tex"}]
        self.assertEqual(forbidden, [])


if __name__ == "__main__":
    unittest.main()
