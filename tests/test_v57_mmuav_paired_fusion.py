import csv
import hashlib
import inspect
import json
from pathlib import Path
import subprocess
import unittest

import torch

from rarepdet.experimental.v57_fusion_superset_detector import VARIANTS, V57FusionSupersetDetector
from rarepdet.tools.run_v57_mmuav_paired_fusion import (
    COMMON_INIT,
    DEVVAL_MANIFEST,
    OUT,
    START_COMMIT,
    STEPS_PER_VARIANT,
    TOTAL_STEP_LIMIT,
    TRAIN_MANIFEST,
    V56_EXPECTED,
    parameter_signature,
    shared_config,
    variant_config,
)


ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class V57MMUAVPairedFusionTests(unittest.TestCase):
    def test_exact_manifest_contract(self):
        self.assertEqual(sha256(TRAIN_MANIFEST), "e81973b95dd6fd5ce2d3c5de526310a3bef083df49b8db584fdf39b78a34d67a")
        self.assertEqual(sha256(DEVVAL_MANIFEST), "113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54")
        with TRAIN_MANIFEST.open(encoding="utf-8", newline="") as handle:
            train = list(csv.DictReader(handle, delimiter="\t"))
        with DEVVAL_MANIFEST.open(encoding="utf-8", newline="") as handle:
            devval = list(csv.DictReader(handle, delimiter="\t"))
        self.assertEqual((len(train), len(devval)), (7187, 1845))
        self.assertFalse({row["sequence"] for row in train} & {row["sequence"] for row in devval})

    def test_v56_evidence_exact_without_execution(self):
        evidence = json.loads((OUT / "v56_evidence_verification.json").read_text())
        self.assertFalse(evidence["executed_v55_or_v56"])
        for key, value in V56_EXPECTED.items():
            self.assertEqual(evidence[key], value)

    def test_superset_signatures_and_common_init_identical(self):
        common = torch.load(COMMON_INIT, map_location="cpu", weights_only=False)["state_dict"]
        models = [V57FusionSupersetDetector(variant) for variant in VARIANTS]
        self.assertEqual(parameter_signature(models[0]), parameter_signature(models[1]))
        for model in models:
            model.load_state_dict(common, strict=True)
            self.assertTrue(all(torch.equal(value, common[key]) for key, value in model.state_dict().items()))
        self.assertEqual(list(models[0].state_dict()), list(models[1].state_dict()))

    def test_alignment_and_uniform_initialization(self):
        common = torch.load(COMMON_INIT, map_location="cpu", weights_only=False)["state_dict"]
        inputs = (torch.zeros(1, 3, 320, 320), torch.zeros(1, 1, 320, 320), torch.zeros(1, 1, 320, 320))
        outputs = []
        for variant in VARIANTS:
            model = V57FusionSupersetDetector(variant)
            model.load_state_dict(common, strict=True)
            self.assertTrue(model.feature_scaffold.alignment_enabled)
            self.assertTrue(torch.equal(model.feature_scaffold.ir_aligner.affine_residual.weight,
                                        torch.zeros_like(model.feature_scaffold.ir_aligner.affine_residual.weight)))
            self.assertTrue(torch.equal(model.feature_scaffold.reliability_scorer[-1].weight,
                                        torch.zeros_like(model.feature_scaffold.reliability_scorer[-1].weight)))
            model.eval()
            with torch.no_grad():
                model._feature_forward(*inputs)
            weights = model.last_feature_outputs["fusion_weights"]
            self.assertTrue(torch.equal(weights, torch.full_like(weights, 1.0 / 3.0)))
            outputs.append(model.last_feature_outputs["fused"])
        self.assertTrue(torch.equal(outputs[0], outputs[1]))

    def test_shared_order_full_unique(self):
        order = json.loads((OUT / "shared_sample_indices.json").read_text())
        self.assertEqual(len(order), STEPS_PER_VARIANT)
        self.assertEqual(set(order), set(range(STEPS_PER_VARIANT)))
        stored = (OUT / "shared_sample_order_sha256.txt").read_text().strip()
        self.assertEqual(sha256(OUT / "shared_sample_order.txt"), stored)

    def test_only_fusion_behavior_differs(self):
        equal, reliability = (variant_config(variant) for variant in VARIANTS)
        differences = {key for key in equal if equal[key] != reliability[key]}
        self.assertEqual(differences, {"variant", "fusion_behavior", "final_checkpoint"})
        self.assertTrue(equal["alignment_enabled"] and reliability["alignment_enabled"])
        self.assertTrue(equal["superset_reliability_scorer_present"])

    def test_caps_and_no_devval_optimization(self):
        config = shared_config()
        self.assertEqual(STEPS_PER_VARIANT, 7187)
        self.assertEqual(TOTAL_STEP_LIMIT, 14374)
        self.assertEqual(config["run_order"], list(VARIANTS))
        self.assertFalse(config["devval_optimization"])
        self.assertFalse(config["early_stopping"])
        self.assertFalse(config["checkpoint_selection"])

    def test_frozen_evaluation_contract(self):
        evaluation = json.loads((OUT / "evaluation_protocol.json").read_text())
        self.assertEqual(evaluation["rows"], 1845)
        self.assertEqual(evaluation["evaluation_count_per_variant"], 1)
        self.assertEqual(evaluation["checkpoint"], "final_step7187_only")

    def test_no_raw_concat_or_trained_initialization(self):
        source = inspect.getsource(V57FusionSupersetDetector)
        runner = (ROOT / "rarepdet/tools/run_v57_mmuav_paired_fusion.py").read_text()
        self.assertNotIn("alignment_off", source)
        self.assertNotIn("best.pt", runner)
        self.assertNotIn("alignment_on_equal_final_step7187.pt", runner)

    def test_heavy_outputs_local_and_protected_unchanged(self):
        self.assertEqual(COMMON_INIT.drive.upper(), "D:")
        self.assertEqual(list(OUT.rglob("*.pt")), [])
        changed = subprocess.check_output(["git", "diff", "--name-only", START_COMMIT], cwd=ROOT, text=True).splitlines()
        forbidden = [path for path in changed if (path.startswith("runs/v5") and not path.startswith(
            "runs/v57_mmuav_paired_fusion_ablation/")) or path.startswith("manuscript/") or
            path.startswith("submission/") or path in {"datasets/triair_dataset.py", "rarepdet/train_early_fusion.py",
            "rarepdet/models/early_fusion_fcos.py", "rarepdet/models/reliability_fusion_fcos.py",
            "main.tex", "main_sivp_snjnl.tex"}]
        self.assertEqual(forbidden, [])


if __name__ == "__main__":
    unittest.main()
