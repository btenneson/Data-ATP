#!/usr/bin/env python3
"""Deterministic Hilbert reordering for already-ranked legal proof actions.

Predator remains responsible for legality, learned scoring, creativity, proof
state construction, and certificate verification.  This module only changes
the order in which an existing ranked list is visited.
"""

from __future__ import annotations

import hashlib
import json
from typing import Sequence


class HilbertCurve:
    """Discrete Skilling-style Hilbert index <-> point map."""

    def __init__(self, dimension: int, bits: int) -> None:
        if dimension < 1:
            raise ValueError("dimension must be positive")
        if bits < 0:
            raise ValueError("bits must be nonnegative")
        self.dimension = dimension
        self.bits = bits
        self.side = 1 << bits
        self.size = 1 << (bits * dimension)

    def _integer_to_transpose(self, distance: int) -> list[int]:
        if self.bits == 0:
            return [0] * self.dimension
        text = format(distance, f"0{self.bits * self.dimension}b")
        return [int(text[axis :: self.dimension], 2) for axis in range(self.dimension)]

    def _transpose_to_integer(self, coordinates: Sequence[int]) -> int:
        if self.bits == 0:
            return 0
        words = [format(value, f"0{self.bits}b") for value in coordinates]
        text = "".join(
            words[axis][bit]
            for bit in range(self.bits)
            for axis in range(self.dimension)
        )
        return int(text, 2)

    def point_from_distance(self, distance: int) -> tuple[int, ...]:
        if distance < 0 or distance >= self.size:
            raise ValueError("distance outside Hilbert grid")
        if self.bits == 0:
            return (0,) * self.dimension
        x = self._integer_to_transpose(distance)
        t = x[self.dimension - 1] >> 1
        for axis in range(self.dimension - 1, 0, -1):
            x[axis] ^= x[axis - 1]
        x[0] ^= t
        q = 2
        limit = 1 << self.bits
        while q != limit:
            p = q - 1
            for axis in range(self.dimension - 1, -1, -1):
                if x[axis] & q:
                    x[0] ^= p
                else:
                    t = (x[0] ^ x[axis]) & p
                    x[0] ^= t
                    x[axis] ^= t
            q <<= 1
        return tuple(x)

    def distance_from_point(self, point: Sequence[int]) -> int:
        if len(point) != self.dimension:
            raise ValueError("point has wrong dimension")
        if any(value < 0 or value >= self.side for value in point):
            raise ValueError("point outside Hilbert grid")
        if self.bits == 0:
            return 0
        x = list(point)
        q = 1 << (self.bits - 1)
        while q > 1:
            p = q - 1
            for axis in range(self.dimension):
                if x[axis] & q:
                    x[0] ^= p
                else:
                    t = (x[0] ^ x[axis]) & p
                    x[0] ^= t
                    x[axis] ^= t
            q >>= 1
        for axis in range(1, self.dimension):
            x[axis] ^= x[axis - 1]
        t = 0
        q = 1 << (self.bits - 1)
        while q > 1:
            if x[self.dimension - 1] & q:
                t ^= q - 1
            q >>= 1
        for axis in range(self.dimension):
            x[axis] ^= t
        return self._transpose_to_integer(x)


def _stable(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _percentile(rank: int, count: int) -> float:
    return 0.0 if count <= 1 else rank / (count - 1)


def blend_ranked_candidates(
    ranked: Sequence[tuple[float, object]],
    coordinates: Sequence[Sequence[float]],
    *,
    hilbert_mix: float,
    seed: int,
    context: str,
):
    """Blend existing candidate rank with Hilbert rank in structural feature space.

    ``ranked`` must already be in the prover's preferred order.  ``coordinates``
    supplies one structural point for each corresponding candidate.  The
    function returns ``(reordered, metadata)``.  Candidate scores themselves are
    not changed; only visitation order changes.
    """
    if not 0.0 <= hilbert_mix <= 1.0:
        raise ValueError("hilbert_mix must lie in [0,1]")
    if len(ranked) != len(coordinates):
        raise ValueError("candidate/coordinate length mismatch")
    if len(ranked) <= 1 or hilbert_mix == 0.0:
        return list(ranked), []

    dimension = len(coordinates[0])
    if dimension < 1 or any(len(row) != dimension for row in coordinates):
        raise ValueError("coordinates must have one positive common dimension")

    axis_maps = []
    for axis in range(dimension):
        atoms = sorted({_stable(row[axis]) for row in coordinates})
        axis_maps.append({atom: i for i, atom in enumerate(atoms)})
    side_needed = max(1, *(len(mapping) for mapping in axis_maps))
    bits = max(0, (side_needed - 1).bit_length())
    curve = HilbertCurve(dimension, bits)

    digest = hashlib.sha256(f"{seed}|{context}".encode("utf-8")).digest()
    offset = int.from_bytes(digest[:8], "big") % curve.size

    rows = []
    for original_rank, ((score, item), coord) in enumerate(zip(ranked, coordinates)):
        point = tuple(
            axis_maps[axis][_stable(coord[axis])]
            for axis in range(dimension)
        )
        raw_distance = curve.distance_from_point(point)
        distance = (raw_distance - offset) % curve.size
        label = item[0] if isinstance(item, tuple) and item else repr(item)
        rows.append({
            "score": score,
            "item": item,
            "label": str(label),
            "original_rank": original_rank,
            "point": point,
            "distance": distance,
            "curve_size": curve.size,
        })

    hilbert_sorted = sorted(rows, key=lambda row: (row["distance"], row["label"]))
    hilbert_rank = {id(row): rank for rank, row in enumerate(hilbert_sorted)}
    count = len(rows)
    for row in rows:
        hrank = hilbert_rank[id(row)]
        row["hilbert_rank"] = hrank
        row["priority"] = (
            (1.0 - hilbert_mix) * _percentile(row["original_rank"], count)
            + hilbert_mix * _percentile(hrank, count)
        )

    rows.sort(key=lambda row: (
        row["priority"], row["original_rank"], row["hilbert_rank"], row["label"]
    ))
    reordered = [(row["score"], row["item"]) for row in rows]
    metadata = [
        {
            "label": row["label"],
            "original_rank": row["original_rank"] + 1,
            "hilbert_rank": row["hilbert_rank"] + 1,
            "grid_point": list(row["point"]),
            "hilbert_distance": row["distance"],
            "hilbert_curve_size": row["curve_size"],
            "blended_priority": row["priority"],
        }
        for row in rows
    ]
    return reordered, metadata
