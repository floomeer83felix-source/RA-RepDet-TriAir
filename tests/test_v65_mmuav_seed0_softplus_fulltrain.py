"""CPU/source-lock and post-run contract tests for V65."""

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
from rarepdet.tools import run_v65_mmuav_seed0_softplus_fulltrain as audit


class V65ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not audit.OUT.is_dir():
            raise unittest.SkipTest("run V65 --prepare-only first")
        cls.protocol = json.loads((audit.OUT / "protocol.json").read_text(encoding="utf-8"))
        cls.lock = json.loads((audit.OUT / "source_lock_v65.json").read_text(encoding="utf-8"))
        audit.configure_helpers()

    def test_v63_v64_evidence_is_exact(self) -> None:
        self.assertEqual(audit.verify_prior_evidence(), self.protocol["prior_evidence"])
        self.assertTrue(all(record["checks"]["file_hashes"] for record in self.protocol["prior_evidence"].values()))

    def test_manifests_full_order_and_subsets_are_frozen(self) -> None:
        self.assertEqual(audit.sha256(audit.base.TRAIN_MANIFEST), audit.base.TRAIN_SHA256)
        self.assertEqual(audit.sha256(audit.DEVVAL_MANIFEST), audit.DEVVAL_SHA256)
        self.assertEqual(self.protocol["full_order"]["rows"], 7187)
        self.assertEqual(self.protocol["full_order"]["unique_rows"], 7187)
        self.assertEqual(self.protocol["full_order"]["sha256"], audit.base.ORDER_SHA256)
        self.assertTrue(all(self.protocol["subsets"]["checks"].values()))

    def test_seed0_initialization_is_exact_and_not_trained(self) -> None:
        record = self.protocol["initialization"]
        self.assertEqual(record["sha256"], audit.base.INIT_SHA256)
        self.assertFalse(record["trained_checkpoint_used"])
        self.assertTrue(all(record["checks"].values()))
        self.assertEqual(audit.sha256(audit.INIT_PATH), audit.base.INIT_SHA256)
        state = audit.load_initialization()
        self.assertEqual(len(state), 791)
        self.assertEqual(state[audit.base.BBOX_BIAS_KEY].tolist(), [0.0] * 4)

    def test_softplus_activation_is_exact_shared_and_parameter_free(self) -> None:
        native = inspect.getsource(audit.fcos_module.FCOSRegressionHead.forward)
        wrapper = Path(inspect.getsourcefile(V63BBoxActivationDetector) or "").read_text(encoding="utf-8")
        self.assertEqual(native.count("nn.functional.relu(self.bbox_reg(bbox_feature))"), 1)
        self.assertIn("F.softplus(pre_activation, beta=1.0, threshold=20.0)", wrapper)
        model = audit.build_model()
        head = model.detector.head.regression_head
        channels = head.bbox_reg.in_channels
        features = [torch.randn(1, channels, 4, 4), torch.randn(1, channels, 2, 2)]
        model.train(); train_bbox, _ = head(features)
        model.eval(); eval_bbox, _ = head(features)
        self.assertTrue(torch.equal(train_bbox, eval_bbox))
        self.assertTrue((train_bbox > 0).all())
        self.assertEqual(model.activation_counts(), {"forward_calls": 2, "activation_applications": 4})

    def test_step0_and_devval_target_contracts(self) -> None:
        identity = self.protocol["step0_contract"]["v63_seed0_identity"]
        self.assertTrue(all(identity["checks"].values()))
        self.assertTrue(all(self.protocol["step0_contract"]["feature_outputs_all_finite"].values()))
        gate = self.protocol["actual_devval_gate"]
        self.assertEqual(gate["row_id"], "devval:00005919")
        self.assertTrue(gate["trace_path_exact"])
        self.assertTrue(gate["historical_optimization_guard_rejects"])

    def test_evaluator_micro_fixture_is_deterministic_complete_and_perfect(self) -> None:
        fixture = audit.evaluator_micro_fixture()
        self.assertTrue(all(fixture["checks"].values()))
        self.assertEqual(fixture, self.protocol["evaluator_micro_fixture"])
        self.assertEqual(self.lock["coco_metrics_sha256"], audit.sha256(ROOT / "rarepdet/coco_metrics.py"))

    def test_budget_audit_recovery_and_final_eval_contract(self) -> None:
        self.assertEqual(self.protocol["optimizer_step_limit"], 7187)
        self.assertEqual(self.protocol["probe_backward_limit"], 40)
        self.assertEqual(list(audit.AUDIT_STEPS), [0, 15, 50, 200, 500, 1000, 2000, 4000, 6000, 7187])
        self.assertEqual(len(audit.SNAPSHOT_STEPS), 19)
        contract = json.loads((audit.OUT / "full_devval_evaluator_contract.json").read_text(encoding="utf-8"))
        self.assertTrue(contract["final_checkpoint_only"])
        self.assertEqual(contract["evaluation_attempt_limit"], 1)
        self.assertEqual(contract["max_detections"], [1, 10, 100])

    def test_source_and_protected_locks(self) -> None:
        self.assertEqual(audit.git("rev-parse", "HEAD"), audit.START_COMMIT)
        self.assertEqual(audit.source_lock(), self.lock)
        self.assertEqual(audit.protected_fingerprint(), self.protocol["protected_baseline"])

    def test_cuda_outputs_when_present(self) -> None:
        path = audit.OUT / "safety_audit.json"
        if not path.exists():
            self.skipTest("CUDA run not complete")
        safety = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(safety["optimizer_steps"], 7187)
        self.assertEqual(safety["unique_training_rows"], 7187)
        self.assertEqual(safety["probe_backward_calls"], 40)
        self.assertEqual(safety["verified_recovery_snapshots"], 19)
        self.assertEqual(safety["full_devval_rows"], 1845)
        self.assertEqual(safety["evaluation_attempts"], 1)
        self.assertTrue(safety["final_checkpoint_only"])
        self.assertTrue(safety["all_finite"])

    def test_no_heavy_artifacts_in_git_output(self) -> None:
        forbidden = {".pt", ".pth", ".ckpt", ".npy", ".npz", ".png", ".jpg", ".pkl"}
        files = [path for path in audit.OUT.rglob("*") if path.is_file()]
        self.assertTrue(files)
        self.assertFalse([path for path in files if path.suffix.lower() in forbidden])


if __name__ == "__main__":
    unittest.main()
