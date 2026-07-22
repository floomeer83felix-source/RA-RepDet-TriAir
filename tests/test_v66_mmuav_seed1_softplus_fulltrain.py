"""CPU/source-lock and post-run contract tests for V66."""

from __future__ import annotations

import inspect
import json
import sys
import unittest
from pathlib import Path

import torch


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rarepdet.experimental.v63_bbox_activation_detector import V63BBoxActivationDetector
from rarepdet.tools import run_v66_mmuav_seed1_softplus_fulltrain as audit


class V66ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not audit.OUT.is_dir():
            raise unittest.SkipTest("run V66 --prepare-only first")
        audit.configure_runtime()
        cls.protocol = json.loads((audit.OUT / "protocol.json").read_text(encoding="utf-8"))
        cls.lock = json.loads((audit.OUT / "source_lock_v66.json").read_text(encoding="utf-8"))

    def test_v65_evidence_is_exact_and_immutable(self) -> None:
        self.assertEqual(audit.verify_v65(), self.protocol["v65_evidence"])
        self.assertTrue(all(self.protocol["v65_evidence"]["checks"].values()))

    def test_seed1_initialization_is_exact_and_not_trained(self) -> None:
        record = self.protocol["initialization"]
        self.assertEqual(record["seed"], 1)
        self.assertEqual(record["sha256"], audit.INIT_SHA256)
        self.assertFalse(record["trained_checkpoint_used"])
        self.assertEqual(record["alternative_candidates_generated"], 0)
        self.assertTrue(all(record["checks"].values()))
        self.assertEqual(audit.sha256(audit.INIT_PATH), audit.INIT_SHA256)

    def test_data_order_and_subsets_match_v65(self) -> None:
        self.assertEqual(self.protocol["train_manifest"]["sha256"], audit.base.TRAIN_SHA256)
        self.assertEqual(self.protocol["devval_manifest"]["sha256"], audit.v65.DEVVAL_SHA256)
        self.assertEqual(self.protocol["full_order"]["rows"], 7187)
        self.assertEqual(self.protocol["full_order"]["unique_rows"], 7187)
        self.assertEqual(self.protocol["full_order"]["sha256"], audit.base.ORDER_SHA256)
        self.assertTrue(all(self.protocol["subsets"]["checks"].values()))

    def test_softplus_and_step0_contracts(self) -> None:
        native = inspect.getsource(audit.fcos_module.FCOSRegressionHead.forward)
        wrapper = Path(inspect.getsourcefile(V63BBoxActivationDetector) or "").read_text(encoding="utf-8")
        self.assertEqual(native.count("nn.functional.relu(self.bbox_reg(bbox_feature))"), 1)
        self.assertIn("F.softplus(pre_activation, beta=1.0, threshold=20.0)", wrapper)
        identity = self.protocol["step0_contract"]["v63_seed0_identity"]
        self.assertTrue(all(identity["checks"].values()))
        self.assertTrue(all(self.protocol["step0_contract"]["feature_outputs_all_finite"].values()))
        model = audit.build_model()
        channels = model.detector.head.regression_head.bbox_reg.in_channels
        features = [torch.randn(1, channels, 4, 4), torch.randn(1, channels, 2, 2)]
        model.train(); train_bbox, _ = model.detector.head.regression_head(features)
        model.eval(); eval_bbox, _ = model.detector.head.regression_head(features)
        self.assertTrue(torch.equal(train_bbox, eval_bbox))
        self.assertTrue((train_bbox > 0).all())

    def test_evaluator_and_budget_match_v65(self) -> None:
        fixture = audit.v65.evaluator_micro_fixture()
        self.assertEqual(fixture, self.protocol["evaluator_micro_fixture"])
        self.assertTrue(all(fixture["checks"].values()))
        self.assertEqual(self.protocol["optimizer_step_limit"], 7187)
        self.assertEqual(self.protocol["probe_backward_limit"], 40)
        self.assertEqual(len(audit.v65.SNAPSHOT_STEPS), 19)
        contract = json.loads((audit.OUT / "full_devval_evaluator_contract.json").read_text(encoding="utf-8"))
        self.assertTrue(contract["identical_to_v65"])
        self.assertTrue(contract["final_checkpoint_only"])

    def test_actual_devval_target_path_is_exact(self) -> None:
        gate = self.protocol["actual_devval_gate"]
        self.assertEqual(gate["row_id"], "devval:00005919")
        self.assertTrue(gate["trace_path_exact"])
        self.assertTrue(gate["historical_optimization_guard_rejects"])

    def test_source_and_protected_locks(self) -> None:
        self.assertEqual(audit.git("rev-parse", "HEAD"), audit.START_COMMIT)
        self.assertEqual(audit.source_lock(), self.lock)
        self.assertEqual(audit.protected_fingerprint(), self.protocol["protected_baseline"])

    def test_two_seed_summary_math(self) -> None:
        values = {key: float(index + 1) / 100 for index, key in enumerate(audit.METRIC_KEYS)}
        summary = audit.two_seed_summary(values)
        self.assertTrue(summary["descriptive_only"])
        self.assertEqual(summary["n"], 2)
        self.assertFalse(summary["selection_or_rerun_trigger"])
        for key in audit.METRIC_KEYS:
            row = summary["metrics"][key]
            self.assertAlmostEqual(row["mean"], (row["v65_seed0"] + row["v66_seed1"]) / 2)
            self.assertAlmostEqual(row["absolute_seed_difference"], abs(row["v66_seed1"] - row["v65_seed0"]))

    def test_cuda_outputs_when_present(self) -> None:
        path = audit.OUT / "safety_audit.json"
        if not path.exists():
            self.skipTest("CUDA run not complete")
        safety = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(safety["optimizer_steps"], 7187)
        self.assertEqual(safety["probe_backward_calls"], 40)
        self.assertEqual(safety["verified_recovery_snapshots"], 19)
        self.assertEqual(safety["full_devval_rows"], 1845)
        self.assertTrue(safety["all_finite"])
        summary = json.loads((audit.OUT / "two_seed_equal_fusion_summary.json").read_text(encoding="utf-8"))
        self.assertEqual(set(summary["metrics"]), set(audit.METRIC_KEYS))

    def test_no_heavy_artifacts_in_git_output(self) -> None:
        forbidden = {".pt", ".pth", ".ckpt", ".npy", ".npz", ".png", ".jpg", ".pkl"}
        files = [path for path in audit.OUT.rglob("*") if path.is_file()]
        self.assertTrue(files)
        self.assertFalse([path for path in files if path.suffix.lower() in forbidden])


if __name__ == "__main__":
    unittest.main()
