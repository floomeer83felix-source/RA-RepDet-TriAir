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


if __name__ == "__main__":
    unittest.main()
