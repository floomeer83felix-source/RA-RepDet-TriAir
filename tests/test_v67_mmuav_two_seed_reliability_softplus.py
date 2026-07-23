"""CPU/source-lock and post-run contract tests for V67."""

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
from rarepdet.experimental.v67_reliability_softplus_detector import V67ReliabilitySoftplusDetector
from rarepdet.tools import run_v67_mmuav_two_seed_reliability_softplus as audit


class V67ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not audit.OUT.is_dir():
            raise unittest.SkipTest("run V67 --prepare-only first")
        audit.configure_helpers(0)
        cls.protocol = json.loads((audit.OUT / "protocol.json").read_text(encoding="utf-8"))
        cls.lock = json.loads((audit.OUT / "source_lock_v67.json").read_text(encoding="utf-8"))

    def test_prior_evidence_is_exact_and_immutable(self) -> None:
        self.assertEqual(audit.verify_prior_evidence(), self.protocol["prior_evidence"])
        for record in self.protocol["prior_evidence"].values():
            self.assertTrue(all(record["checks"].values()))

    def test_two_initializations_are_exact_state_identical_and_untrained(self) -> None:
        for seed in audit.SEEDS:
            record = self.protocol["initializations"][str(seed)]
            self.assertEqual(record["sha256"], audit.INIT_HASHES[seed])
            self.assertFalse(record["trained_checkpoint_used"])
            self.assertTrue(all(record["checks"].values()))
            self.assertEqual(audit.sha256(audit.init_path(seed)), audit.INIT_HASHES[seed])

    def test_data_order_and_subsets_are_frozen(self) -> None:
        self.assertEqual(self.protocol["train_sha256"], audit.base.TRAIN_SHA256)
        self.assertEqual(self.protocol["devval_sha256"], audit.v65.DEVVAL_SHA256)
        self.assertEqual(self.protocol["full_order"]["rows"], 7187)
        self.assertEqual(self.protocol["full_order"]["unique_rows"], 7187)
        self.assertEqual(self.protocol["full_order"]["sha256"], audit.base.ORDER_SHA256)
        self.assertTrue(all(self.protocol["subsets"]["checks"].values()))

    def test_step0_identity_and_scorer_gradient_gate(self) -> None:
        for record in self.protocol["step0_identity_and_scorer_gradient_gate"].values():
            self.assertTrue(all(record["checks"].values()))
            self.assertGreater(record["scorer_gradient_norm"], 0.0)
            weights = torch.tensor(record["weights"], dtype=torch.float32)
            self.assertTrue(torch.equal(weights, torch.full_like(weights, 1.0 / 3.0)))

    def test_sole_switch_and_parameter_superset(self) -> None:
        equal = V63BBoxActivationDetector("softplus_b1_t20")
        reliability = V67ReliabilitySoftplusDetector()
        self.assertEqual(list(equal.state_dict()), list(reliability.state_dict()))
        self.assertTrue(callable(reliability.fusion_diagnostics))
        self.assertFalse(hasattr(reliability.feature_scaffold, "fusion_diagnostics"))
        self.assertEqual(
            reliability.variant,
            "alignment_on_reliability_superset",
        )
        self.assertEqual(
            self.lock["sole_behavior_switch"],
            "alignment_on_reliability_superset versus alignment_on_equal_superset",
        )

    def test_softplus_source_parameters_and_call_count(self) -> None:
        native = inspect.getsource(audit.fcos_module.FCOSRegressionHead.forward)
        wrapper = Path(inspect.getsourcefile(V67ReliabilitySoftplusDetector) or "").read_text(encoding="utf-8")
        inherited = ROOT / "rarepdet/experimental/v63_bbox_activation_detector.py"
        self.assertEqual(native.count("nn.functional.relu(self.bbox_reg(bbox_feature))"), 1)
        self.assertIn("_softplus_regression_forward", wrapper)
        self.assertIn("F.softplus(pre_activation, beta=1.0, threshold=20.0)", inherited.read_text(encoding="utf-8"))
        model = V67ReliabilitySoftplusDetector()
        head = model.detector.head.regression_head
        channels = head.bbox_reg.in_channels
        features = [torch.randn(1, channels, 4, 4), torch.randn(1, channels, 2, 2)]
        model.train(); train_bbox, _ = head(features)
        model.eval(); eval_bbox, _ = head(features)
        self.assertTrue(torch.equal(train_bbox, eval_bbox))
        self.assertTrue((train_bbox > 0).all())
        self.assertEqual(model.activation_counts(), {"forward_calls": 2, "activation_applications": 4})

    def test_evaluator_budget_audits_and_recovery_contract(self) -> None:
        fixture = audit.v65.evaluator_micro_fixture()
        self.assertEqual(fixture, self.protocol["evaluator_micro_fixture"])
        self.assertTrue(all(fixture["checks"].values()))
        self.assertEqual(self.protocol["total_optimizer_step_limit"], 14374)
        self.assertEqual(self.protocol["total_probe_backward_limit"], 80)
        self.assertEqual(list(audit.v65.AUDIT_STEPS), [0, 15, 50, 200, 500, 1000, 2000, 4000, 6000, 7187])
        self.assertEqual(len(audit.v65.SNAPSHOT_STEPS), 19)
        contract = json.loads((audit.OUT / "evaluator_contract.json").read_text(encoding="utf-8"))
        self.assertTrue(contract["final_checkpoint_only"])
        self.assertEqual(contract["evaluation_attempts_per_seed"], 1)

    def test_source_and_protected_locks(self) -> None:
        self.assertEqual(audit.git("rev-parse", "HEAD"), audit.START_COMMIT)
        self.assertEqual(audit.source_lock(), self.lock)
        self.assertEqual(audit.protected_fingerprint(), self.protocol["protected_baseline"])

    def test_matched_summary_math(self) -> None:
        reliability = {
            seed: {**{key: float(seed + index + 1) / 100 for index, key in enumerate(audit.METRIC_KEYS)},
                   "fusion_diagnostics": {"seed": seed}}
            for seed in audit.SEEDS
        }
        summary = audit.matched_summary(self.protocol["prior_evidence"], reliability)
        self.assertTrue(summary["descriptive_only"])
        self.assertEqual(summary["n"], 2)
        self.assertTrue(summary["no_independent_test"])
        self.assertTrue(summary["no_significance_claim"])
        self.assertFalse(summary["selection_or_rerun_trigger"])
        for key in audit.METRIC_KEYS:
            deltas = [summary["per_seed"][str(seed)][key]["reliability_minus_equal"] for seed in audit.SEEDS]
            self.assertAlmostEqual(summary["matched_delta_two_seed"][key]["mean"], sum(deltas) / 2)

    def test_cuda_outputs_when_present_and_no_heavy_git_artifacts(self) -> None:
        forbidden = {".pt", ".pth", ".ckpt", ".npy", ".npz", ".png", ".jpg", ".pkl"}
        files = [path for path in audit.OUT.rglob("*") if path.is_file()]
        self.assertTrue(files)
        self.assertFalse([path for path in files if path.suffix.lower() in forbidden])
        safety_path = audit.OUT / "safety_audit.json"
        if not safety_path.exists():
            self.skipTest("CUDA run not complete")
        safety = json.loads(safety_path.read_text(encoding="utf-8"))
        self.assertEqual(safety["optimizer_steps"], 14374)
        self.assertEqual(safety["probe_backward_calls"], 80)
        self.assertEqual(safety["verified_recovery_snapshots"], 38)
        self.assertEqual(safety["full_devval_rows_per_seed"], 1845)
        self.assertEqual(safety["evaluation_attempts_per_seed"], 1)
        self.assertTrue(safety["all_finite"])


if __name__ == "__main__":
    unittest.main()
