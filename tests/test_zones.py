import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from rp_why_core import calculate_adt_zone, estimate_tm_tier


class ZoneTests(unittest.TestCase):
    def test_tier_5_and_up(self):
        self.assertEqual(calculate_adt_zone(3.0, 5), "Frontier")
        self.assertEqual(calculate_adt_zone(2.6, 6), "Frontier")
        self.assertEqual(calculate_adt_zone(2.2, 5, compression_pct=10.0), "Leveraging")
        self.assertEqual(calculate_adt_zone(2.2, 5, compression_pct=9.9), "Underutilizing")
        self.assertEqual(calculate_adt_zone(2.2, 5), "Underutilizing")
        self.assertEqual(calculate_adt_zone(1.9, 5), "Overpowered")

    def test_tier_3_and_4(self):
        self.assertEqual(calculate_adt_zone(3.0, 3), "Frontier")
        self.assertEqual(calculate_adt_zone(2.5, 4), "Growing")
        self.assertEqual(calculate_adt_zone(2.0, 4), "Expected")
        self.assertEqual(calculate_adt_zone(2.2, 4, compression_pct=50.0), "Expected")
        self.assertEqual(calculate_adt_zone(1.5, 3), "Overpowered")

    def test_tier_1_and_2(self):
        self.assertEqual(calculate_adt_zone(2.5, 2), "Thinking Ahead")
        self.assertEqual(calculate_adt_zone(3.5, 1), "Thinking Ahead")
        self.assertEqual(calculate_adt_zone(2.0, 2), "Growing")
        self.assertEqual(calculate_adt_zone(1.0, 1), "Expected")

    def test_improving_trajectory_moves_up_one_step(self):
        self.assertEqual(calculate_adt_zone(1.9, 5, trajectory="improving"), "Underutilizing")
        self.assertEqual(calculate_adt_zone(2.2, 5, trajectory="improving"), "Leveraging")
        self.assertEqual(calculate_adt_zone(2.0, 4, trajectory="improving"), "Growing")
        self.assertEqual(calculate_adt_zone(2.5, 4, trajectory="improving"), "Frontier")
        self.assertEqual(calculate_adt_zone(1.0, 1, trajectory="improving"), "Growing")

    def test_improving_trajectory_leaves_top_zones(self):
        self.assertEqual(calculate_adt_zone(3.0, 5, trajectory="improving"), "Frontier")
        self.assertEqual(calculate_adt_zone(2.5, 2, trajectory="improving"), "Thinking Ahead")
        self.assertEqual(calculate_adt_zone(2.2, 5, trajectory="improving", compression_pct=10.0), "Leveraging")


class TierTests(unittest.TestCase):
    def tier(self, **kw):
        return estimate_tm_tier({"has_subagents": False, "prompt_count": 0, "unique_tools": 0, **kw})

    def test_tiers(self):
        self.assertEqual(self.tier(has_subagents=True, prompt_count=51), 5)
        self.assertEqual(self.tier(has_subagents=True, prompt_count=50), 4)
        self.assertEqual(self.tier(unique_tools=6, prompt_count=21), 4)
        self.assertEqual(self.tier(unique_tools=4, prompt_count=11), 3)
        self.assertEqual(self.tier(prompt_count=4), 2)
        self.assertEqual(self.tier(prompt_count=3), 1)


if __name__ == "__main__":
    unittest.main()
