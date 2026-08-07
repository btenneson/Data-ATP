import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(ROOT, "src"))

from data_atp.metamath_hilbert import (
    HilbertCurve,
    LegalApplicationAddress,
    fair_cap,
    rank_legal_applications,
)


class HilbertCurveTests(unittest.TestCase):
    def test_bijection_and_adjacency(self):
        for dimension, bits in ((2, 2), (3, 2)):
            curve = HilbertCurve(dimension, bits)
            points = [curve.point_from_distance(i) for i in range(curve.size)]
            self.assertEqual(len(points), len(set(points)))
            for i, point in enumerate(points):
                self.assertEqual(curve.distance_from_point(point), i)
            for a, b in zip(points, points[1:]):
                self.assertEqual(sum(abs(x-y) for x, y in zip(a, b)), 1)


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.records = [
            {"assertion": "a", "coords": ("x", "u"), "score": 0.9, "id": "a1"},
            {"assertion": "a", "coords": ("y", "u"), "score": 0.7, "id": "a2"},
            {"assertion": "a", "coords": ("y", "v"), "score": 0.6, "id": "a3"},
            {"assertion": "b", "coords": ("p",), "score": 0.8, "id": "b1"},
            {"assertion": "b", "coords": ("q",), "score": 0.5, "id": "b2"},
        ]

    def kwargs(self):
        return dict(
            component_of=lambda r: r["assertion"],
            coordinates_of=lambda r: r["coords"],
            learned_score_of=lambda r: r["score"],
            identity_of=lambda r: r["id"],
            seed=2301,
        )

    def test_fingerprint_is_deterministic(self):
        a = LegalApplicationAddress("x", (1, "z"), "id", 0.4)
        b = LegalApplicationAddress("x", (1, "z"), "id", 99.0)
        self.assertEqual(a.fingerprint, b.fingerprint)

    def test_mix_zero_reproduces_learned_order(self):
        ranked = rank_legal_applications(self.records, hilbert_mix=0.0, **self.kwargs())
        self.assertEqual([x.record["id"] for x in ranked], ["a1", "b1", "a2", "a3", "b2"])

    def test_hilbert_metadata_is_reproducible(self):
        a = rank_legal_applications(self.records, hilbert_mix=0.25, **self.kwargs())
        b = rank_legal_applications(self.records, hilbert_mix=0.25, **self.kwargs())
        self.assertEqual(
            [(x.address.fingerprint, x.hilbert_distance) for x in a],
            [(x.address.fingerprint, x.hilbert_distance) for x in b],
        )

    def test_component_dimension_must_be_constant(self):
        bad = [
            {"assertion": "a", "coords": (1,), "score": 0.9, "id": "x"},
            {"assertion": "a", "coords": (1, 2), "score": 0.8, "id": "y"},
        ]
        with self.assertRaises(ValueError):
            rank_legal_applications(bad, hilbert_mix=0.25, **self.kwargs())

    def test_fair_cap_touches_components(self):
        ranked = rank_legal_applications(self.records, hilbert_mix=0.25, **self.kwargs())
        capped = fair_cap(ranked, 2, round_index=0)
        self.assertEqual({x.address.component for x in capped}, {"a", "b"})

    def test_fair_cap_rotates_first_component(self):
        ranked = rank_legal_applications(self.records, hilbert_mix=0.25, **self.kwargs())
        first0 = fair_cap(ranked, 1, round_index=0)[0].address.component
        first1 = fair_cap(ranked, 1, round_index=1)[0].address.component
        self.assertNotEqual(first0, first1)


if __name__ == "__main__":
    unittest.main()
