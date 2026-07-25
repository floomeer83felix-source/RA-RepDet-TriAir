"""Contract tests for the CPU-only V68 manuscript-evidence audit."""

from __future__ import annotations

import csv
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rarepdet.tools import run_v68_mmuav_manuscript_evidence_audit as audit


class V68EvidenceAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not audit.OUT.is_dir():
            raise unittest.SkipTest("run V68 generator first")
        cls.final = json.loads((audit.OUT / "final_decision.json").read_text(encoding="utf-8"))
        cls.verification = json.loads(
            (audit.OUT / "v65_v66_v67_hash_verification.json").read_text(encoding="utf-8")
        )

    def test_frozen_hashes_decisions_and_safety_match(self) -> None:
        self.assertTrue(all(record["match"] for record in self.verification["records"].values()))
        self.assertTrue(all(self.verification["decisions"].values()))
        self.assertTrue(all(self.verification["safety"].values()))
        self.assertTrue(all(self.verification["checks"].values()))

    def test_exact_table_has_all_required_rows_and_metrics(self) -> None:
        with (audit.OUT / "matched_metrics_table.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 11)
        self.assertEqual({row["row_type"] for row in rows}, {
            "seed", "mean", "sample_std", "matched_delta", "mean_matched_delta"
        })
        self.assertEqual(
            set(rows[0]),
            {"row_type", "method", "seed", "AP", "AP50", "AP75", "AR@1", "AR@10", "AR@100"},
        )
        seed0_delta = next(
            row for row in rows if row["row_type"] == "matched_delta" and row["seed"] == "0"
        )
        seed1_delta = next(
            row for row in rows if row["row_type"] == "matched_delta" and row["seed"] == "1"
        )
        self.assertEqual(seed0_delta["AP"], "+0.0041719276")
        self.assertEqual(seed1_delta["AP"], "-0.0004533834")

    def test_independent_arithmetic_path_matches_frozen_summary(self) -> None:
        arithmetic = json.loads((audit.OUT / "arithmetic_verification.json").read_text(encoding="utf-8"))
        self.assertTrue(arithmetic["frozen_v67_comparison_matched"])
        equal = arithmetic["numeric"]["methods"]["equal"]
        reliability = arithmetic["numeric"]["methods"]["reliability"]
        self.assertAlmostEqual(equal["mean"]["ap50_95"], 0.0196700860)
        self.assertAlmostEqual(equal["sample_std"]["ap50_95"], 0.0235244622)
        self.assertAlmostEqual(reliability["mean"]["ap50_95"], 0.0215293581)
        self.assertAlmostEqual(reliability["sample_std"]["ap50_95"], 0.0267950511)
        self.assertAlmostEqual(arithmetic["numeric"]["deltas"]["mean"]["ap50_95"], 0.0018592721)

    def test_fusion_summary_is_finite_nonuniform_and_not_calibration(self) -> None:
        fusion = json.loads((audit.OUT / "fusion_weight_summary.json").read_text(encoding="utf-8"))
        self.assertTrue(all(fusion["checks"].values()))
        self.assertIn("not calibrated", fusion["interpretation_boundary"])
        self.assertAlmostEqual(fusion["seed0"]["per_modality"]["rgb"]["mean"], 0.5550344586)
        self.assertAlmostEqual(fusion["seed1"]["per_modality"]["rgb"]["mean"], 0.5600358248)

    def test_rights_gate_fails_closed(self) -> None:
        rights = json.loads((audit.OUT / "data_rights_status.json").read_text(encoding="utf-8"))
        self.assertIsNone(rights["dataset_license"])
        self.assertEqual(rights["provider"], "unresolved")
        self.assertEqual(rights["research_use_permission"], "unresolved")
        self.assertEqual(rights["aggregate_reporting_permission"], "unresolved")
        self.assertFalse(rights["submission_gate_passed"])

    def test_decision_is_unique_blocked_state_and_no_draft_exists(self) -> None:
        self.assertEqual(self.final["decision"], "V68_BLOCKED_DATA_RIGHTS_OR_CITATION_INCOMPLETE")
        self.assertTrue(self.final["scientific_evidence_valid"])
        self.assertFalse(self.final["rights_and_citation_gate_passed"])
        self.assertFalse(self.final["appendix_draft_created"])
        self.assertFalse((ROOT / "manuscript/v68_mmuav_extension_draft").exists())

    def test_claim_and_protocol_boundaries_are_explicit(self) -> None:
        claims = (audit.OUT / "claim_matrix.md").read_text(encoding="utf-8")
        protocol = (audit.OUT / "protocol_difference_matrix.md").read_text(encoding="utf-8")
        self.assertIn("consistently improves MM-UAV | Disallowed", claims)
        self.assertIn("measure sensor health or calibrated reliability | Disallowed", claims)
        self.assertIn("320 x 320", protocol)
        self.assertIn("640 x 640", protocol)
        self.assertIn("One ordered pass", protocol)
        self.assertIn("50 epochs", protocol)

    def test_protected_files_match_generation_baseline(self) -> None:
        post = json.loads((audit.OUT / "protected_postcheck.json").read_text(encoding="utf-8"))
        baseline = json.loads((audit.OUT / "protected_baseline.json").read_text(encoding="utf-8"))
        self.assertEqual(post["fingerprint"], baseline)
        self.assertTrue(post["checks"]["baseline_equals_post_generation"])
        self.assertTrue(post["checks"]["main_tex_unchanged"])
        self.assertTrue(post["checks"]["main_sivp_unchanged"])
        self.assertTrue(post["checks"]["no_cuda_or_evaluation_work_performed"])

    def test_no_raw_or_heavy_artifacts_or_local_paths(self) -> None:
        forbidden_suffixes = {".pt", ".pth", ".ckpt", ".npy", ".npz", ".png", ".jpg", ".pkl"}
        files = [path for path in audit.OUT.rglob("*") if path.is_file()]
        self.assertTrue(files)
        self.assertFalse([path for path in files if path.suffix.lower() in forbidden_suffixes])
        for path in files:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("E:\\MM-UAV", text)
            self.assertNotIn("D:\\MM-UAV", text)


if __name__ == "__main__":
    unittest.main()
