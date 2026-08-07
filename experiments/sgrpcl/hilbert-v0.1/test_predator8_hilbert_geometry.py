import unittest
from predator8_hilbert_geometry import HilbertCurve, blend_ranked_candidates


class GeometryTests(unittest.TestCase):
    def test_curve_bijection_and_adjacency(self):
        for d, bits in ((2,2), (4,1)):
            curve = HilbertCurve(d, bits)
            points = [curve.point_from_distance(i) for i in range(curve.size)]
            self.assertEqual(len(points), len(set(points)))
            for i, p in enumerate(points):
                self.assertEqual(curve.distance_from_point(p), i)
            for a,b in zip(points, points[1:]):
                self.assertEqual(sum(abs(x-y) for x,y in zip(a,b)), 1)

    def test_mix_zero_is_exact_control(self):
        ranked = [(3.0,("a",)), (2.0,("b",)), (1.0,("c",))]
        coords = [(0,0,0,0),(1,1,1,1),(2,2,2,2)]
        got, meta = blend_ranked_candidates(
            ranked, coords, hilbert_mix=0.0, seed=2301, context="goal"
        )
        self.assertEqual(got, ranked)
        self.assertEqual(meta, [])

    def test_hybrid_is_deterministic_and_preserves_items(self):
        ranked = [(4.0,("a",)), (3.0,("b",)), (2.0,("c",)), (1.0,("d",))]
        coords = [(0.1,0.2,1.0,2.0),(0.9,0.8,3.0,1.0),(0.2,0.9,2.0,4.0),(0.8,0.1,4.0,3.0)]
        a, ma = blend_ranked_candidates(ranked, coords, hilbert_mix=0.25, seed=2301, context="goal")
        b, mb = blend_ranked_candidates(ranked, coords, hilbert_mix=0.25, seed=2301, context="goal")
        self.assertEqual(a,b)
        self.assertEqual(ma,mb)
        self.assertEqual({x[1][0] for x in a}, {"a","b","c","d"})


if __name__ == "__main__":
    unittest.main()
