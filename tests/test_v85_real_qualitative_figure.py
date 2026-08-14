import unittest

from rarepdet.tools.build_v85_real_qualitative_figure import select_samples


class V85SelectionTest(unittest.TestCase):
    def make_rows(self):
        return [
            {"sample_id": f"frame_{index:05d}", "component_id": f"c{index}",
             "gt_box_count": index % 7, "rgb_mean_luminance": index / 99, "selected_scene": ""}
            for index in range(100)
        ]

    def test_selection_is_deterministic_and_component_distinct(self):
        first, thresholds = select_samples(self.make_rows())
        second, _ = select_samples(self.make_rows())
        self.assertEqual([row["sample_id"] for row in first], [row["sample_id"] for row in second])
        self.assertEqual(len({row["component_id"] for row in first}), 3)
        self.assertEqual([row["selected_scene"] for row in first], ["A", "B", "C"])
        self.assertLess(thresholds["rgb_q25"], thresholds["rgb_q75"])

    def test_later_scene_skips_used_component(self):
        rows = self.make_rows()
        for row in rows:
            if row["sample_id"] in {"frame_00082", "frame_00019"}:
                row["component_id"] = "shared"
        selected, _ = select_samples(rows)
        self.assertEqual(len({row["component_id"] for row in selected}), 3)


if __name__ == "__main__":
    unittest.main()
