import csv
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "runs/v52_mmuav_audit"


class V52ArchiveAuditTests(unittest.TestCase):
    def test_archive_audit_is_explicitly_blocked(self):
        audit = json.loads((OUTPUT / "dataset_audit.json").read_text(encoding="utf-8"))
        self.assertEqual(audit["status"], "BLOCKED_ARCHIVE_ONLY_INSUFFICIENT_EXTRACTION_SPACE")
        self.assertEqual(audit["zip64"]["total_entries"], 8460602)
        self.assertEqual(audit["central_directory_entries_parsed"], 8460602)
        self.assertLess(audit["free_minus_archive_bytes"], 0)
        self.assertGreater(audit["central_total_uncompressed_bytes"], 0)

    def test_pilot_gate_is_locked_without_gpu_steps(self):
        gate = json.loads((OUTPUT / "pilot_gate.json").read_text(encoding="utf-8"))
        benchmark = json.loads((OUTPUT / "loader_benchmark.json").read_text(encoding="utf-8"))
        self.assertTrue(gate["locked"])
        self.assertEqual(benchmark["status"], "NOT_RUN")
        self.assertFalse(benchmark["gpu_used"])

    def test_sequence_inventory_has_all_three_modalities(self):
        with (OUTPUT / "sequence_alignment.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertTrue(rows)
        self.assertTrue(any(int(row["rgb_count"]) > 0 for row in rows))
        self.assertTrue(any(int(row["ir_count"]) > 0 for row in rows))
        self.assertTrue(any(int(row["event_count"]) > 0 for row in rows))

    def test_sampling_manifest_was_not_fabricated(self):
        protocol = json.loads((OUTPUT / "sampling_protocol.json").read_text(encoding="utf-8"))
        self.assertFalse(protocol["manifests_created"])
        self.assertFalse((OUTPUT / "manifests/train_sampled.txt").exists())
        self.assertFalse((OUTPUT / "manifests/devval_sampled.txt").exists())


if __name__ == "__main__":
    unittest.main()
