from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "runs/v71_mmuav_existing_devval_triair_zero_shot_external_domain_validation"


def load(name: str):
    return json.loads((RUN / name).read_text(encoding="utf-8"))


class V71ZeroShotExternalDomainTests(unittest.TestCase):
    def test_manifest_is_exactly_frozen_exposed_devval(self):
        value = load("devval_manifest_lock.json")
        self.assertEqual(value["rows"], 1845)
        self.assertEqual(
            value["manifest_sha256"],
            "113c304794cb32232ca4121edcd8fd8f40dab5a540b2d52b1f165ac4adb37a54",
        )
        self.assertTrue(value["row_order_preserved"])
        self.assertTrue(value["previously_exposed"])

    def test_all_six_authoritative_checkpoints_strictly_load(self):
        manifest = load("triair_checkpoint_manifest.json")
        verification = load("triair_checkpoint_verification.json")
        self.assertEqual(manifest["count"], 6)
        self.assertEqual(len({(item["method"], item["seed"]) for item in manifest["entries"]}), 6)
        self.assertTrue(all(item["strict_load"] for item in verification["entries"]))
        self.assertFalse(verification["mmuav_trained_checkpoints_used"])
        self.assertFalse(verification["softplus_wrapper_used"])

    def test_adapter_blocks_without_raw_grid_registration(self):
        value = load("mmuav_to_triair_adapter_spec.json")
        self.assertEqual(value["status"], "BLOCKED_NO_DEFENSIBLE_PARAMETER_FREE_SPATIAL_REGISTRATION")
        self.assertFalse(value["parameter_free_adapter_frozen"])
        self.assertFalse(value["deterministic_raw_grid_transform_found"])
        self.assertFalse(value["pixel_alignment_established"])
        self.assertFalse(value["raw_channel_concatenation_authorized"])

    def test_no_adapter_or_learned_alignment_path_was_added(self):
        value = load("adapter_source_lock.json")
        self.assertEqual(value["status"], "NO_ADAPTER_IMPLEMENTED")
        self.assertFalse((ROOT / "rarepdet/models/reliability_fusion_fcos.py").exists())

    def test_frozen_requested_evaluator_settings_are_recorded_but_inactive(self):
        value = load("zero_shot_evaluator_contract.json")
        settings = value["frozen_requested_settings"]
        self.assertEqual(settings["score_threshold"], 0.001)
        self.assertEqual(settings["nms_threshold"], 0.6)
        self.assertEqual(settings["maximum_detections"], 100)
        self.assertEqual(value["evaluation_attempts"], 0)

    def test_no_smoke_inference_or_metrics_occurred(self):
        smoke = load("smoke_test_summary.json")
        decision = load("final_decision.json")
        self.assertEqual(smoke["model_forward_calls"], 0)
        self.assertEqual(decision["evaluation_attempts"], 0)
        self.assertFalse(decision["metrics_computed"])
        with (RUN / "per_checkpoint_metrics.csv").open(encoding="utf-8", newline="") as handle:
            self.assertEqual(len(list(csv.reader(handle))), 1)

    def test_claim_boundary_is_exposed_not_blind(self):
        value = load("exposure_and_claim_boundary.json")
        self.assertTrue(value["previously_exposed"])
        self.assertFalse(value["independent_external_validation"])
        self.assertFalse(value["blind_external_test"])
        self.assertIn("exposed MM-UAV devval", value["label"])

    def test_decision_matches_fail_closed_adapter_state(self):
        value = load("final_decision.json")
        self.assertEqual(value["decision"], "V71_BLOCKED_ADAPTER_OR_ONTOLOGY_CONTRACT")
        self.assertEqual(value["manifest_gate"], "PASS")
        self.assertEqual(value["checkpoint_gate"], "PASS_6_OF_6")
        self.assertEqual(value["adapter_gate"], "BLOCKED")

    def test_no_cuda_training_tuning_or_rerun(self):
        decision = load("final_decision.json")
        memory = load("memory_timing_summary.json")
        self.assertFalse(decision["gpu_used"])
        self.assertFalse(decision["training_fine_tuning_adaptation_or_tuning"])
        self.assertEqual(memory["gpu_evaluation_seconds"], 0)
        self.assertEqual(memory["evaluation_attempts"], 0)

    def test_outputs_are_compact_and_private_safe(self):
        forbidden = {".pt", ".pth", ".ckpt", ".npy", ".npz", ".pkl", ".pickle", ".jpg", ".png", ".mp4"}
        for path in RUN.rglob("*"):
            if not path.is_file():
                continue
            self.assertNotIn(path.suffix.lower(), forbidden)
            self.assertLess(path.stat().st_size, 1024 * 1024)
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("E:\\\\", text)
            self.assertNotIn("D:\\\\", text)


if __name__ == "__main__":
    unittest.main()
