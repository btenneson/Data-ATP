from fractions import Fraction
import itertools
import unittest

from hilbert_theorem_search import (
    Budget,
    HilbertCurve,
    HilbertTheoremSearch,
    ProofCertificate,
    ToyFormula,
    a002260,
    a004736,
    exhaustive_direct_consequences,
    inference_address_line,
    make_toy_system,
    pair_positive,
    pair_tuple,
    premise_point,
    rational_cube_line,
    rational_cube_point,
    tenneson_r,
    tenneson_s,
    unit_rational,
    unit_rational_section,
    unpair_positive,
    unpair_tuple,
    wff_coordinate,
    wff_line_from_coordinate,
)


class TennesonAddressTests(unittest.TestCase):
    def test_sequence_coordinates(self):
        self.assertEqual([a002260(n) for n in range(1, 11)], [1,1,2,1,2,3,1,2,3,4])
        self.assertEqual([a004736(n) for n in range(1, 11)], [1,2,1,3,2,1,4,3,2,1])

    def test_r_and_s(self):
        samples = [
            Fraction(0), Fraction(1), Fraction(-1), Fraction(2,3),
            Fraction(-7,5), Fraction(13,11), Fraction(-19,23),
        ]
        for q in samples:
            self.assertEqual(tenneson_r(tenneson_s(q)), q)
            least = tenneson_s(q)
            self.assertTrue(all(tenneson_r(n) != q for n in range(1, least)))

    def test_pairing(self):
        for a in range(1, 20):
            for b in range(1, 20):
                self.assertEqual(unpair_positive(pair_positive(a,b)), (a,b))
        values = (3, 7, 2, 9)
        self.assertEqual(unpair_tuple(pair_tuple(values), len(values)), values)

    def test_unit_interval_section(self):
        samples = [Fraction(0), Fraction(1), Fraction(1,2), Fraction(2,3), Fraction(17,19)]
        for q in samples:
            line = unit_rational_section(q)
            self.assertEqual(unit_rational(line), q)
            self.assertTrue(all(unit_rational(n) != q for n in range(1, line)))

    def test_rational_cube_round_trip(self):
        point = (Fraction(0), Fraction(1,2), Fraction(7,9), Fraction(1))
        line = rational_cube_line(point)
        self.assertEqual(rational_cube_point(line, len(point)), point)

    def test_wff_coordinates_are_injective(self):
        coords = [wff_coordinate(g) for g in range(100)]
        self.assertEqual(len(coords), len(set(coords)))
        for g, q in enumerate(coords):
            self.assertEqual(wff_line_from_coordinate(q), g)


class HilbertTests(unittest.TestCase):
    def test_bijection_and_adjacency(self):
        for dimension in range(1, 6):
            for bits in range(0, 4):
                curve = HilbertCurve(dimension, bits)
                points = list(curve.points())
                self.assertEqual(len(points), curve.size)
                self.assertEqual(len(set(points)), curve.size)
                for distance, point in enumerate(points):
                    self.assertEqual(curve.distance_from_point(point), distance)
                for left, right in zip(points, points[1:]):
                    manhattan = sum(abs(a-b) for a,b in zip(left,right))
                    self.assertEqual(manhattan, 1)


class SearchTests(unittest.TestCase):
    def test_complete_epoch_matches_exhaustive_layer(self):
        system = make_toy_system(max_value=8)
        search = HilbertTheoremSearch(system)
        frozen = [record.formula for record in search.database.frozen_records()]
        expected = exhaustive_direct_consequences(system, frozen)
        report = search.run_epoch(Budget(1000, 1000, 1000))
        observed = {record.formula for record in search.database.frozen_records()}
        self.assertTrue(report.complete)
        self.assertEqual(observed, expected)
        expected_expansions = sum(len(frozen) ** rule.arity for rule in system.rules)
        self.assertEqual(report.expansions_used, expected_expansions)

    def test_every_valid_tuple_once(self):
        system = make_toy_system(max_value=5)
        search = HilbertTheoremSearch(system)
        m = len(search.database)
        report = search.run_epoch(Budget(1000, 1000, 1000))
        for coverage, rule in zip(report.rule_coverage, system.rules):
            self.assertEqual(coverage.valid_tuples_attempted, m ** rule.arity)
            self.assertEqual(
                coverage.cells_visited,
                coverage.valid_tuples_attempted + coverage.padding_cells_visited,
            )

    def test_partial_budget_is_reported(self):
        system = make_toy_system(max_value=8)
        search = HilbertTheoremSearch(system)
        report = search.run_epoch(Budget(3, 100, 100))
        self.assertFalse(report.complete)
        self.assertEqual(report.expansions_used, 3)
        self.assertTrue(report.log_chain_valid)

    def test_tampered_certificate_is_rejected(self):
        system = make_toy_system(max_value=5)
        search = HilbertTheoremSearch(system)
        known = search.database.known_by_line()
        bad = ProofCertificate(
            conclusion=ToyFormula(5),
            conclusion_line=5,
            rule_name="succ",
            premise_lines=(0,),
            premise_formulas=(ToyFormula(0),),
            inference_line=inference_address_line(0, (0,)),
        )
        self.assertFalse(search.verifier.verify(bad, known))

    def test_discovery_reaches_finite_closure(self):
        system = make_toy_system(max_value=10)
        search = HilbertTheoremSearch(system)
        reports = search.discover(Budget(50000, 100000, 50000), max_epochs=10)
        values = {record.formula.value for record in search.database.frozen_records()}
        self.assertEqual(values, set(range(11)))
        self.assertTrue(any(report.complete and not report.new_theorems for report in reports))


if __name__ == "__main__":
    unittest.main()
