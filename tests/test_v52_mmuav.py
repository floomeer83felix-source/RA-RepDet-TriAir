import csv
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "runs/v52_mmuav_audit"


class V52ArchiveAuditTests(unittest.TestCase):
    def test_extracted_audit_freezes_interval20(self):
        audit = json.loads((OUTPUT / "dataset_audit.json").read_text(encoding="utf-8"))
        protocol = json.loads((OUTPUT / "sampling_protocol.json").read_text(encoding="utf-8"))
        self.assertEqual(audit["status"], "INTERVAL20_FROZEN_SUPERVISED_LABEL_CONTRACT_BLOCKED")
        self.assertEqual(audit["complete_train_sequences"], 424)
        self.assertEqual(protocol["interval"], 20)
        self.assertEqual(protocol["index_origin"], 1)
        self.assertEqual(protocol["total_samples"], 45036)
        self.assertGreater(protocol["samples_with_unresolved_annotation_state"], 0)

    def test_pilot_gate_is_locked_without_gpu_steps(self):
        gate = json.loads((OUTPUT / "pilot_gate.json").read_text(encoding="utf-8"))
        benchmark = json.loads((OUTPUT / "loader_benchmark.json").read_text(encoding="utf-8"))
        self.assertTrue(gate["locked"])
        self.assertEqual(benchmark["status"], "PASS_CPU_ONLY")
        self.assertFalse(benchmark["gpu_used"])

    def test_sequence_disjoint_manifests_exist(self):
        train = OUTPUT / "manifests/train_sampled.txt"
        devval = OUTPUT / "manifests/devval_sampled.txt"
        self.assertTrue(train.is_file())
        self.assertTrue(devval.is_file())
        with train.open(encoding="utf-8", newline="") as handle:
            train_sequences = {row["sequence"] for row in csv.DictReader(handle, delimiter="\t")}
        with devval.open(encoding="utf-8", newline="") as handle:
            devval_sequences = {row["sequence"] for row in csv.DictReader(handle, delimiter="\t")}
        self.assertTrue(train_sequences)
        self.assertTrue(devval_sequences)
        self.assertFalse(train_sequences & devval_sequences)

    def test_geometry_requires_alignment(self):
        geometry = json.loads((OUTPUT / "geometry_audit.json").read_text(encoding="utf-8"))
        self.assertEqual(geometry["status"], "ALIGNMENT_MODULE_REQUIRED")
        self.assertGreaterEqual(geometry["sample_frames"], 100)
        self.assertGreaterEqual(geometry["sample_sequences"], 20)

    def test_unlabeled_rows_are_not_silently_empty(self):
        with (OUTPUT / "manifests/train_sampled.txt").open(encoding="utf-8", newline="") as handle:
            states = {row["annotation_state"] for row in csv.DictReader(handle, delimiter="\t")}
        self.assertIn("SOURCE_GT_ROW_PRESENT", states)
        self.assertIn("UNLABELED_OR_EMPTY_UNRESOLVED", states)

    def test_annotated_only_contract_reproduces_exactly(self):
        protocol = json.loads((OUTPUT / "annotated_only_protocol.json").read_text(encoding="utf-8"))
        self.assertEqual(protocol["included"], 9138)
        self.assertEqual(protocol["excluded_unlabeled"], 35898)
        self.assertEqual(protocol["empty_target_assignments"], 0)
        self.assertEqual(protocol["excluded_state"], "UNLABELED")

    def test_evidence_inventory_is_traceable(self):
        with (OUTPUT / "provider_evidence_inventory.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertGreaterEqual(len(rows), 10)
        for row in rows:
            self.assertTrue(row["path_or_url"])
            self.assertEqual(len(row["sha256"]), 64)
            self.assertTrue(row["source"])
            self.assertTrue(row["evidence_classification"])
        audit = json.loads((OUTPUT / "provider_contract_audit.json").read_text(encoding="utf-8"))
        self.assertTrue(audit["download_inventory"]["below_limit"])
        self.assertLess(audit["download_inventory"]["total_downloaded_material_bytes_including_git"], 1_000_000_000)
        self.assertEqual(audit["local_search"]["complete_sequences"], 424)
        self.assertEqual(audit["local_search"]["provider_nonmedia_files_searched"], 1696)

    def test_non_pixel_alignment_cannot_unlock_verification(self):
        audit = json.loads((OUTPUT / "alignment_source_audit.json").read_text(encoding="utf-8"))
        verification = json.loads((OUTPUT / "official_alignment_verification.json").read_text(encoding="utf-8"))
        forbidden_promotions = {"LEARNED_FEATURE_ALIGNMENT", "TEMPORAL_SYNCHRONIZATION_ONLY",
                                "VISUALIZATION_ONLY", "FIXED_PREPROCESSING_WITHOUT_CALIBRATION"}
        self.assertFalse(audit["deterministic_raw_grid_transform_found"])
        self.assertTrue(any(c["classification"] in forbidden_promotions for c in audit["candidates"]))
        self.assertEqual(verification["status"], "NOT_RUN_NO_OFFICIAL_DETERMINISTIC_TRANSFORM")
        self.assertFalse(verification["devval_gt_fitting"])

    def test_final_gate_and_source_lock(self):
        gate = json.loads((OUTPUT / "pilot_gate.json").read_text(encoding="utf-8"))
        lock = json.loads((OUTPUT / "provider_audit_source_lock.json").read_text(encoding="utf-8"))
        decision = json.loads((OUTPUT / "feasibility_decision.json").read_text(encoding="utf-8"))
        self.assertTrue(gate["locked"])
        self.assertEqual(gate["gpu_optimizer_steps"], 0)
        self.assertEqual(decision["outcome"], "OFFICIAL_LEARNED_ALIGNMENT_ONLY_DIRECT_FUSION_NO_GO")
        self.assertEqual(lock["protected_core_changed"], [])
        self.assertEqual(lock["manuscript_changed"], [])


if __name__ == "__main__":
    unittest.main()
