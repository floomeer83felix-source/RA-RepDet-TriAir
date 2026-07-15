import csv
import hashlib
import inspect
import json
from pathlib import Path
import subprocess
import unittest

import torch

from rarepdet.experimental.mmuav_feature_alignment_detector import MMUAVFeatureAlignmentDetector
from rarepdet.tools.run_v55_mmuav_paired_alignment import (
    COMMON_INIT,
    DEVVAL_MANIFEST,
    OUT,
    STEPS_PER_VARIANT,
    TOTAL_STEP_LIMIT,
    TRAIN_MANIFEST,
    VARIANTS,
    shared_config,
    variant_config,
)


ROOT = Path(__file__).resolve().parents[1]
START = "1dc5b48a4504e789bbe47e69153a71ac3b179532"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class V55MMUAVPairedAlignmentTests(unittest.TestCase):
    def test_exact_manifest_contract(self):
        hashes = json.loads((ROOT / "runs/v53_mmuav_feature_alignment_preflight/manifest_hashes.json").read_text())
        self.assertEqual(sha256(TRAIN_MANIFEST), hashes["train_rgb_supervised_sha256"])
        self.assertEqual(sha256(DEVVAL_MANIFEST), hashes["devval_rgb_supervised_sha256"])
        with TRAIN_MANIFEST.open(encoding="utf-8", newline="") as handle:
            train = list(csv.DictReader(handle, delimiter="\t"))
        with DEVVAL_MANIFEST.open(encoding="utf-8", newline="") as handle:
            devval = list(csv.DictReader(handle, delimiter="\t"))
        self.assertEqual((len(train), len(devval)), (7187, 1845))
        self.assertFalse({row["sequence"] for row in train} & {row["sequence"] for row in devval})

    def test_common_init_is_bit_identical_and_identity_aligned(self):
        protocol = json.loads((OUT / "protocol.json").read_text())
        self.assertEqual(sha256(COMMON_INIT), protocol["common_init"]["sha256"])
        common = torch.load(COMMON_INIT, map_location="cpu", weights_only=False)["state_dict"]
        models = [MMUAVFeatureAlignmentDetector(variant) for variant in VARIANTS]
        for model in models:
            model.load_state_dict(common, strict=True)
            self.assertTrue(all(torch.equal(value, common[key]) for key, value in model.state_dict().items()))
            self.assertTrue(torch.equal(model.feature_scaffold.ir_aligner.affine_residual.weight, torch.zeros_like(
                model.feature_scaffold.ir_aligner.affine_residual.weight)))
            self.assertTrue(torch.equal(model.feature_scaffold.event_aligner.affine_residual.bias, torch.zeros_like(
                model.feature_scaffold.event_aligner.affine_residual.bias)))
        self.assertTrue(all(torch.equal(models[0].state_dict()[key], models[1].state_dict()[key]) for key in common))

    def test_shared_order_is_full_unique_permutation(self):
        order = json.loads((OUT / "shared_sample_indices.json").read_text())
        self.assertEqual(len(order), STEPS_PER_VARIANT)
        self.assertEqual(len(set(order)), STEPS_PER_VARIANT)
        self.assertEqual(set(order), set(range(STEPS_PER_VARIANT)))
        stored = (OUT / "shared_sample_order_sha256.txt").read_text().strip()
        self.assertEqual(sha256(OUT / "shared_sample_order.txt"), stored)

    def test_only_alignment_enabled_is_scientific_difference(self):
        off, on = (variant_config(variant) for variant in VARIANTS)
        differences = {key for key in off if off[key] != on[key]}
        self.assertEqual(differences, {"variant", "alignment_enabled", "final_checkpoint"})
        self.assertFalse(off["alignment_enabled"])
        self.assertTrue(on["alignment_enabled"])
        self.assertEqual(shared_config()["fusion"], "equal")

    def test_step_caps_and_no_devval_optimization(self):
        self.assertEqual(STEPS_PER_VARIANT, 7187)
        self.assertEqual(TOTAL_STEP_LIMIT, 14374)
        config = shared_config()
        self.assertFalse(config["devval_optimization"])
        self.assertEqual(config["train_manifest"], str(TRAIN_MANIFEST))
        self.assertEqual(config["run_order"], ["alignment_off_equal", "alignment_on_equal"])
        self.assertFalse(config["early_stopping"])
        self.assertFalse(config["checkpoint_selection"])

    def test_frozen_final_checkpoint_evaluation_contract(self):
        evaluation = json.loads((OUT / "evaluation_protocol.json").read_text())
        self.assertEqual(evaluation["rows"], 1845)
        self.assertEqual(evaluation["checkpoint"], "final_step7187_only")
        self.assertEqual(evaluation["evaluation_count_per_variant"], 1)
        self.assertEqual(evaluation["metrics"], ["ap50_95", "ap50", "ap75", "ar100"])

    def test_no_raw_concat_reliability_training_or_v54_initialization(self):
        detector_source = inspect.getsource(MMUAVFeatureAlignmentDetector)
        runner_source = (ROOT / "rarepdet/tools/run_v55_mmuav_paired_alignment.py").read_text()
        self.assertNotIn("torch.cat", detector_source)
        self.assertNotIn("alignment_on_reliability", runner_source)
        self.assertNotIn("alignment_on_equal_step200.pt", runner_source)
        self.assertNotIn("best.pt", runner_source)

    def test_heavy_outputs_are_local_and_protected_paths_unchanged(self):
        protocol = json.loads((OUT / "protocol.json").read_text())
        self.assertTrue(Path(protocol["common_init"]["path_local_not_committed"]).drive.upper().startswith("D:"))
        self.assertEqual(list(OUT.rglob("*.pt")), [])
        changed = subprocess.check_output(["git", "diff", "--name-only", START], cwd=ROOT, text=True).splitlines()
        forbidden = [path for path in changed if (path.startswith("runs/v5") and not path.startswith(
            "runs/v55_mmuav_paired_alignment_ablation/")) or path.startswith("manuscript/") or
            path.startswith("submission/") or path in {"datasets/triair_dataset.py", "rarepdet/train_early_fusion.py",
                                                       "main.tex", "main_sivp_snjnl.tex"}]
        self.assertEqual(forbidden, [])


if __name__ == "__main__":
    unittest.main()
