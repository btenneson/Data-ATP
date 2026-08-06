import math
import unittest

from data_atp import (
    completed_level_for_budget,
    coverage_defect_bound,
    cumulative_nominal_length,
    hierarchical_atp_defect,
    nominal_stage_length,
)


class CoverageTests(unittest.TestCase):
    def test_stage_length_matches_counting(self):
        for dimension in range(2, 7):
            for level in range(0, 7):
                L = 3.0
                cells = 2 ** (level * dimension)
                h = L / 2 ** level
                expected = (cells - 1) * h
                self.assertAlmostEqual(
                    nominal_stage_length(dimension, level, L), expected, places=7
                )

    def test_cumulative_formula(self):
        for dimension in range(2, 6):
            for level in range(0, 7):
                explicit = sum(
                    nominal_stage_length(dimension, j, 2.5) for j in range(level + 1)
                )
                self.assertTrue(math.isclose(
                    cumulative_nominal_length(dimension, level, 2.5),
                    explicit,
                    rel_tol=1e-12,
                    abs_tol=1e-8,
                ))

    def test_completed_level_and_defect(self):
        budget = cumulative_nominal_length(3, 3, 10.0)
        self.assertEqual(completed_level_for_budget(3, budget, 10.0), 3)
        self.assertAlmostEqual(coverage_defect_bound(3, 3, 10.0), math.sqrt(3)*10/16)

    def test_atp_defect_contracts(self):
        self.assertEqual(hierarchical_atp_defect(1.0, 4, 0.5), 1/16)


if __name__ == "__main__":
    unittest.main()
