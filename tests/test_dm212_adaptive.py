from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))

import data_mind_2_12_adaptive_grp619 as dm212


class DataMind212AdaptiveTests(unittest.TestCase):
    def test_portfolio_has_controlled_diversity(self):
        self.assertEqual(len(dm212.PORTFOLIO), 14)
        self.assertEqual(len(dm212.PORTFOLIO) * 2, 28)
        commands = [tuple(value) for value in dm212.PORTFOLIO.values()]
        self.assertEqual(len(commands), len(set(commands)))
        self.assertIn("default", dm212.PORTFOLIO)
        self.assertIn("sine_auto", dm212.PORTFOLIO)
        self.assertIn("auto_schedule", dm212.PORTFOLIO)
        self.assertIn("weight_kbo6", dm212.PORTFOLIO)
        self.assertIn("weight_lpo4", dm212.PORTFOLIO)
        self.assertIn("default_clausecap_250k", dm212.PORTFOLIO)

    def test_linear_slope(self):
        slope = dm212.linear_slope([(0.0, 100.0), (10.0, 200.0), (20.0, 300.0)])
        self.assertAlmostEqual(slope, 10.0)

    def test_predictive_trade_fires_before_hard_limit(self):
        gib = 1024 * 1024
        samples = [
            (0.0, 2.0 * gib),
            (10.0, 3.0 * gib),
            (20.0, 4.0 * gib),
        ]
        reason = dm212.predictive_trade_reason(
            samples=samples,
            current_rss_kib=4 * gib,
            mem_total_kib=16 * gib,
            hard_rss_fraction=0.65,
            min_rss_kib=3 * gib,
            min_slope_kib_per_second=24 * 1024,
            forecast_seconds=90,
        )
        self.assertIsNotNone(reason)
        self.assertEqual(reason["decision"], "predictive_strategy_trade")
        self.assertLess(reason["predicted_seconds_to_hard_limit"], 90)

    def test_predictive_trade_does_not_fire_on_flat_memory(self):
        gib = 1024 * 1024
        reason = dm212.predictive_trade_reason(
            samples=[(0.0, 3.1 * gib), (10.0, 3.1 * gib), (20.0, 3.1 * gib)],
            current_rss_kib=int(3.1 * gib),
            mem_total_kib=16 * gib,
            hard_rss_fraction=0.65,
            min_rss_kib=3 * gib,
            min_slope_kib_per_second=24 * 1024,
            forecast_seconds=90,
        )
        self.assertIsNone(reason)

    def test_search_efficiency_is_not_proof_credit(self):
        value = dm212.search_efficiency(
            processed_clauses=1000,
            generated_clauses=2500,
            peak_rss_kib=100 * 1024,
        )
        self.assertFalse(value["objective_is_proof_credit"])
        self.assertAlmostEqual(value["processed_clauses_per_peak_mib"], 10.0)
        self.assertAlmostEqual(value["generated_clauses_per_peak_mib"], 25.0)

    def test_candidate_order_interleaves_presentations(self):
        problems = {"reordered": Path("r.p"), "original": Path("o.p")}
        smoke = {
            "viable_strategies": [
                {"problem_form": form, "strategy": strategy}
                for strategy in dm212.PROFILE_ORDER
                for form in ("reordered", "original")
            ]
        }
        ordered = dm212.adaptive_ordered_viable(smoke, problems)
        self.assertEqual(ordered[0], {"problem_form": "reordered", "strategy": "default"})
        self.assertEqual(ordered[1], {"problem_form": "original", "strategy": "default"})
        self.assertEqual(len(ordered), 28)


if __name__ == "__main__":
    unittest.main()
