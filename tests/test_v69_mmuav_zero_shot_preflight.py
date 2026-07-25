"""Contract tests for the metadata-only V69 MM-UAV preflight."""

from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rarepdet.tools import run_v69_mmuav_zero_shot_preflight as audit


class V69ZeroShotPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not audit.OUT.is_dir():
            raise unittest.SkipTest("run V69 preflight first")
        cls.final = json.loads((audit.OUT / "final_decision.json").read_text(encoding="utf-8"))

    def test_source_evidence_is_frozen(self) -> None:
        evidence = json.loads((audit.OUT / "source_evidence_verification.json").read_text(encoding="utf-8"))
        self.assertTrue(all(record["match"] for record in evidence["records"].values()))
        self.assertTrue(all(evidence["checks"].values()))

    def test_complete_sample_and_sequence_ledger(self) -> None:
        ledger = json.loads((audit.OUT / "historical_exposure_ledger_summary.json").read_text(encoding="utf-8"))
        sequence = json.loads(
            (audit.OUT / "sequence_component_independence_audit.json").read_text(encoding="utf-8")
        )
        self.assertEqual(ledger["rows"], 897578)
        self.assertEqual(sum(ledger["direct_exposure_counts"].values()), 897578)
        self.assertEqual(ledger["direct_exposure_counts"]["DEVELOPMENT_USED"], 9032)
        self.assertEqual(ledger["direct_exposure_counts"]["CONTENT_EXPOSED"], 36004)
        self.assertEqual(ledger["direct_exposure_counts"]["IDENTITY_ONLY"], 852542)
        self.assertEqual(ledger["blind_eligible_rows"], 0)
        self.assertEqual(sequence["provider_train_sequences"], 424)
        self.assertEqual(sequence["v52_sampled_sequences"], 424)
        self.assertEqual(sequence["v53_v67_development_used_sequences"], 424)
        self.assertEqual(sequence["eligible_sequences"], 0)
        self.assertTrue(all(sequence["checks"].values()))

    def test_local_ledger_hash_and_privacy_contract(self) -> None:
        ledger = json.loads((audit.OUT / "historical_exposure_ledger_summary.json").read_text(encoding="utf-8"))
        self.assertTrue(audit.LOCAL_LEDGER.is_file())
        self.assertEqual(audit.sha256(audit.LOCAL_LEDGER), ledger["sha256"])
        self.assertFalse(ledger["committed"])
        self.assertFalse(ledger["contains_absolute_paths"])
        self.assertFalse(ledger["contains_media_or_labels"])

    def test_no_official_or_unexposed_candidate_exists(self) -> None:
        inventory = json.loads((audit.OUT / "full_inventory_metadata.json").read_text(encoding="utf-8"))
        discovery = json.loads(
            (audit.OUT / "candidate_partition_discovery.json").read_text(encoding="utf-8")
        )
        self.assertEqual(inventory["provider_split_names_present"], ["train"])
        self.assertTrue(all(inventory["checks"].values()))
        self.assertFalse(discovery["official_test_split_present"])
        self.assertEqual(discovery["wholly_unexposed_sequence_components"], 0)
        self.assertEqual(discovery["eligible_candidate_rows"], 0)
        self.assertFalse(discovery["candidate_selected"])

    def test_candidate_content_labels_predictions_and_metrics_untouched(self) -> None:
        discovery = json.loads(
            (audit.OUT / "candidate_partition_discovery.json").read_text(encoding="utf-8")
        )
        seal = json.loads((audit.OUT / "label_seal_record.json").read_text(encoding="utf-8"))
        duplicate = json.loads(
            (audit.OUT / "exact_and_near_duplicate_audit.json").read_text(encoding="utf-8")
        )
        self.assertFalse(discovery["labels_read"])
        self.assertFalse(discovery["media_opened"])
        self.assertFalse(discovery["predictions_generated"])
        self.assertFalse(discovery["metrics_computed"])
        self.assertFalse(seal["candidate_labels_parsed"])
        self.assertFalse(seal["seal_created"])
        self.assertFalse(duplicate["candidate_content_hashed_or_decoded"])

    def test_downstream_checkpoint_adapter_and_evaluator_gates_not_attempted(self) -> None:
        checkpoints = json.loads(
            (audit.OUT / "triair_checkpoint_verification.json").read_text(encoding="utf-8")
        )
        adapter = json.loads(
            (audit.OUT / "mmuav_to_triair_adapter_spec.json").read_text(encoding="utf-8")
        )
        evaluator = json.loads(
            (audit.OUT / "zero_shot_evaluator_contract.json").read_text(encoding="utf-8")
        )
        self.assertEqual(checkpoints["checkpoint_files_opened"], 0)
        self.assertEqual(checkpoints["strict_load_attempts"], 0)
        self.assertFalse(adapter["parameter_free_adapter_frozen"])
        self.assertFalse(adapter["candidate_informed_choices"])
        self.assertFalse(evaluator["evaluator_frozen"])
        self.assertEqual(evaluator["candidate_inference_attempts"], 0)
        self.assertEqual(evaluator["candidate_metric_computations"], 0)

    def test_blocked_decision_and_independent_rights_status(self) -> None:
        self.assertEqual(self.final["decision"], "V69_BLOCKED_NO_UNUSED_MMUAV_PARTITION")
        self.assertFalse(self.final["internal_scientific_protocol_ready"])
        self.assertFalse(self.final["manuscript_reporting_ready"])
        self.assertFalse(self.final["candidate_partition_exists"])
        self.assertEqual(self.final["counts"]["eligible_sequences"], 0)
        self.assertEqual(self.final["counts"]["eligible_rows"], 0)
        self.assertTrue(all(self.final["checks"].values()))

    def test_protected_files_are_unchanged(self) -> None:
        protected = json.loads((audit.OUT / "protected_file_audit.json").read_text(encoding="utf-8"))
        self.assertEqual(protected["baseline"], protected["post"])
        self.assertTrue(all(protected["checks"].values()))
        self.assertEqual(audit.protected_fingerprint(), protected["baseline"])

    def test_git_outputs_are_compact_private_safe_and_have_no_heavy_artifacts(self) -> None:
        forbidden = {".pt", ".pth", ".ckpt", ".npy", ".npz", ".png", ".jpg", ".jpeg", ".pkl"}
        files = [path for path in audit.OUT.rglob("*") if path.is_file()]
        self.assertTrue(files)
        self.assertFalse([path for path in files if path.suffix.lower() in forbidden])
        self.assertFalse((audit.OUT / "historical_exposure_ledger.csv").exists())
        for path in files:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("E:\\MM-UAV", text)
            self.assertNotIn("D:\\MM-UAV", text)
            self.assertIsNone(re.search(r"[A-Za-z]:\\", text), path)


if __name__ == "__main__":
    unittest.main()
