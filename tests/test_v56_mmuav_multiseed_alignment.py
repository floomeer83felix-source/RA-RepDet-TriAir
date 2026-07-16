import csv
import hashlib
import inspect
import json
from pathlib import Path
import subprocess
import unittest

import torch

from rarepdet.experimental.mmuav_feature_alignment_detector import MMUAVFeatureAlignmentDetector
from rarepdet.tools.run_v56_mmuav_multiseed_alignment import (
    DEVVAL_MANIFEST,
    METRIC_KEYS,
    OUT,
    RUN_ORDER,
    SEEDS,
    START_COMMIT,
    STEPS_PER_RUN,
    TOTAL_STEP_LIMIT,
    TRAIN_MANIFEST,
    V55_EXPECTED,
    VARIANTS,
    common_init_path,
    shared_config,
    variant_config,
)


ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class V56MMUAVMultiseedAlignmentTests(unittest.TestCase):
    def test_exact_manifest_contract(self):
        self.assertEqual(sha256(TRAIN_MANIFEST), "e81973b95dd6fd5ce2d3c5de526310a3bef083df49b8db584fdf39b78a34d67a")
        self.assertEqual(sha256(DEVVAL_MANIFEST), "113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54")
        with TRAIN_MANIFEST.open(encoding="utf-8", newline="") as handle:
            train = list(csv.DictReader(handle, delimiter="\t"))
        with DEVVAL_MANIFEST.open(encoding="utf-8", newline="") as handle:
            devval = list(csv.DictReader(handle, delimiter="\t"))
        self.assertEqual((len(train), len(devval)), (7187, 1845))
        self.assertFalse({row["sequence"] for row in train} & {row["sequence"] for row in devval})

    def test_v55_seed0_evidence_is_exact_and_not_executed(self):
        imported = json.loads((OUT / "v55_seed0_evidence_verification.json").read_text())
        self.assertFalse(imported["executed_seed0"])
        self.assertEqual(imported["common_init_sha256"], V55_EXPECTED["common_init_sha256"])
        self.assertEqual(imported["sample_order_sha256"], V55_EXPECTED["sample_order_sha256"])
        for variant in VARIANTS:
            for key in METRIC_KEYS:
                self.assertEqual(imported["metrics"][variant][key], V55_EXPECTED[variant][key])

    def test_seed_specific_common_init_and_identity(self):
        hashes = []
        for seed in SEEDS:
            metadata = json.loads((OUT / f"seed{seed}_common_init_metadata.json").read_text())
            self.assertEqual(sha256(common_init_path(seed)), metadata["sha256"])
            common = torch.load(common_init_path(seed), map_location="cpu", weights_only=False)["state_dict"]
            models = [MMUAVFeatureAlignmentDetector(variant) for variant in VARIANTS]
            for model in models:
                model.load_state_dict(common, strict=True)
                self.assertTrue(all(torch.equal(value, common[key]) for key, value in model.state_dict().items()))
                self.assertTrue(torch.equal(model.feature_scaffold.ir_aligner.affine_residual.weight,
                                            torch.zeros_like(model.feature_scaffold.ir_aligner.affine_residual.weight)))
                self.assertTrue(torch.equal(model.feature_scaffold.event_aligner.affine_residual.bias,
                                            torch.zeros_like(model.feature_scaffold.event_aligner.affine_residual.bias)))
            hashes.append(metadata["sha256"])
        self.assertEqual(len(set(hashes)), 2)

    def test_seed_orders_are_full_and_pair_shared(self):
        hashes = []
        for seed in SEEDS:
            order = json.loads((OUT / f"seed{seed}_shared_sample_indices.json").read_text())
            self.assertEqual(len(order), STEPS_PER_RUN)
            self.assertEqual(set(order), set(range(STEPS_PER_RUN)))
            stored = (OUT / f"seed{seed}_shared_sample_order_sha256.txt").read_text().strip()
            self.assertEqual(sha256(OUT / f"seed{seed}_shared_sample_order.txt"), stored)
            hashes.append(stored)
        self.assertEqual(len(set(hashes)), 2)

    def test_only_alignment_enabled_differs_within_pair(self):
        for seed in SEEDS:
            off, on = (variant_config(seed, variant) for variant in VARIANTS)
            differences = {key for key in off if off[key] != on[key]}
            self.assertEqual(differences, {"variant", "alignment_enabled", "final_checkpoint"})
            self.assertFalse(off["alignment_enabled"])
            self.assertTrue(on["alignment_enabled"])
            self.assertEqual(shared_config(seed)["fusion"], "equal")

    def test_exact_order_caps_and_no_devval_optimization(self):
        self.assertEqual(RUN_ORDER, ((1, "alignment_off_equal"), (1, "alignment_on_equal"),
                                     (2, "alignment_off_equal"), (2, "alignment_on_equal")))
        self.assertEqual(STEPS_PER_RUN, 7187)
        self.assertEqual(TOTAL_STEP_LIMIT, 28748)
        for seed in SEEDS:
            config = shared_config(seed)
            self.assertFalse(config["devval_optimization"])
            self.assertFalse(config["early_stopping"])
            self.assertFalse(config["checkpoint_selection"])

    def test_frozen_evaluation_and_aggregation_contract(self):
        evaluation = json.loads((OUT / "evaluation_protocol.json").read_text())
        self.assertEqual(evaluation["rows"], 1845)
        self.assertEqual(evaluation["checkpoint"], "final_step7187_only")
        self.assertEqual(evaluation["evaluation_count_per_run"], 1)
        self.assertEqual(evaluation["metrics"], list(METRIC_KEYS))
        protocol = json.loads((OUT / "protocol.json").read_text())
        self.assertEqual(protocol["seeds"], [1, 2])
        self.assertFalse(protocol["v55_seed0_evidence"]["executed_seed0"])

    def test_no_raw_concat_reliability_or_trained_initialization(self):
        detector_source = inspect.getsource(MMUAVFeatureAlignmentDetector)
        runner_source = (ROOT / "rarepdet/tools/run_v56_mmuav_multiseed_alignment.py").read_text()
        self.assertNotIn("torch.cat", detector_source)
        self.assertNotIn("alignment_on_reliability", runner_source)
        self.assertNotIn("alignment_on_equal_step200.pt", runner_source)
        self.assertNotIn("best.pt", runner_source)

    def test_heavy_outputs_local_and_protected_paths_unchanged(self):
        for seed in SEEDS:
            self.assertEqual(common_init_path(seed).drive.upper(), "D:")
        self.assertEqual(list(OUT.rglob("*.pt")), [])
        changed = subprocess.check_output(["git", "diff", "--name-only", START_COMMIT], cwd=ROOT, text=True).splitlines()
        forbidden = [path for path in changed if (path.startswith("runs/v5") and not path.startswith(
            "runs/v56_mmuav_multiseed_alignment_confirmation/")) or path.startswith("manuscript/") or
            path.startswith("submission/") or path in {"datasets/triair_dataset.py", "rarepdet/train_early_fusion.py",
            "rarepdet/models/early_fusion_fcos.py", "rarepdet/models/reliability_fusion_fcos.py",
            "main.tex", "main_sivp_snjnl.tex"}]
        self.assertEqual(forbidden, [])


if __name__ == "__main__":
    unittest.main()
