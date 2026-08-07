"""Hilbert ordering adapter for legal Metamath applications.

This module does not decide legality and does not verify proofs.  It accepts
already-legal candidate applications from a prover such as Predator and gives
them reproducible Hilbert-style coverage coordinates.  A learned score may be
blended with the Hilbert order so density-trained guidance remains in control
while geometric coverage changes where ties/near-ties are explored first.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from typing import Any, Callable, Hashable, Iterable, Sequence, TypeVar

RecordT = TypeVar("RecordT")
Scalar = Hashable


def _stable_atom(value: Any) -> str:
    """Return a deterministic text key for a coordinate or identity value."""
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    except TypeError:
        return repr(value)


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
        bit_string = format(distance, f"0{self.bits * self.dimension}b")
        return [
            int(bit_string[axis :: self.dimension], 2)
            for axis in range(self.dimension)
        ]

    def _transpose_to_integer(self, coordinates: Sequence[int]) -> int:
        if self.bits == 0:
            return 0
        words = [format(value, f"0{self.bits}b") for value in coordinates]
        interleaved = "".join(
            words[axis][bit]
            for bit in range(self.bits)
            for axis in range(self.dimension)
        )
        return int(interleaved, 2)

    def point_from_distance(self, distance: int) -> tuple[int, ...]:
        if distance < 0 or distance >= self.size:
            raise ValueError(f"distance must lie in [0, {self.size})")
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
            raise ValueError("point has the wrong dimension")
        if any(value < 0 or value >= self.side for value in point):
            raise ValueError(f"coordinates must lie in [0, {self.side})")
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


@dataclass(frozen=True, slots=True)
class LegalApplicationAddress:
    """Geometry/logging metadata for one already-legal prover application."""

    component: str
    coordinates: tuple[Scalar, ...]
    identity: str
    learned_score: float

    def canonical_bytes(self) -> bytes:
        data = {
            "component": self.component,
            "coordinates": [_stable_atom(x) for x in self.coordinates],
            "identity": self.identity,
        }
        return json.dumps(
            data, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("ascii")

    @property
    def fingerprint(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True, slots=True)
class RankedApplication:
    """One legal candidate plus reproducible Hilbert ranking metadata."""

    record: Any
    address: LegalApplicationAddress
    grid_point: tuple[int, ...]
    hilbert_distance: int
    hilbert_size: int
    learned_rank: int
    hilbert_rank: int
    blended_priority: float


def _bits_for_side(side: int) -> int:
    if side < 1:
        raise ValueError("side must be positive")
    return max(0, (side - 1).bit_length())


def _rank_percentile(rank: int, count: int) -> float:
    return 0.0 if count <= 1 else rank / (count - 1)


def _component_hilbert_metadata(
    addresses: Sequence[LegalApplicationAddress],
    *,
    seed: int,
) -> dict[str, tuple[tuple[int, ...], int, int]]:
    """Map fingerprint -> (grid point, rotated Hilbert distance, curve size)."""
    if not addresses:
        return {}

    dimensions = {len(a.coordinates) for a in addresses}
    if len(dimensions) != 1:
        raise ValueError("one assertion component must have one coordinate dimension")
    raw_dimension = dimensions.pop()
    dimension = max(1, raw_dimension)

    effective_coordinates = [a.coordinates if raw_dimension else (0,) for a in addresses]
    axis_maps: list[dict[str, int]] = []
    for axis in range(dimension):
        atoms = sorted({_stable_atom(coords[axis]) for coords in effective_coordinates})
        axis_maps.append({atom: idx for idx, atom in enumerate(atoms)})

    side_needed = max(1, *(len(axis_map) for axis_map in axis_maps))
    bits = _bits_for_side(side_needed)
    curve = HilbertCurve(dimension=dimension, bits=bits)

    component = addresses[0].component
    offset_digest = hashlib.sha256(f"{seed}:{component}".encode("utf-8")).digest()
    offset = int.from_bytes(offset_digest[:8], "big") % curve.size

    result: dict[str, tuple[tuple[int, ...], int, int]] = {}
    for address, coords in zip(addresses, effective_coordinates):
        point = tuple(axis_maps[axis][_stable_atom(coords[axis])] for axis in range(dimension))
        distance = curve.distance_from_point(point)
        rotated = (distance - offset) % curve.size
        result[address.fingerprint] = (point, rotated, curve.size)
    return result


def rank_legal_applications(
    records: Iterable[RecordT],
    *,
    component_of: Callable[[RecordT], str],
    coordinates_of: Callable[[RecordT], Sequence[Scalar]],
    learned_score_of: Callable[[RecordT], float],
    identity_of: Callable[[RecordT], str],
    hilbert_mix: float = 0.25,
    seed: int = 2301,
) -> list[RankedApplication]:
    """Rank already-legal applications by learned guidance + Hilbert coverage.

    ``hilbert_mix=0`` is a learned-score control. ``hilbert_mix=1`` ignores the
    learned score and orders by Hilbert coverage.  Intermediate values blend
    rank percentiles, keeping the two scales comparable without assuming that
    model scores are calibrated probabilities.
    """
    if not 0.0 <= hilbert_mix <= 1.0:
        raise ValueError("hilbert_mix must lie in [0,1]")

    materialized = list(records)
    if not materialized:
        return []

    pairs: list[tuple[RecordT, LegalApplicationAddress]] = []
    for record in materialized:
        address = LegalApplicationAddress(
            component=str(component_of(record)),
            coordinates=tuple(coordinates_of(record)),
            identity=str(identity_of(record)),
            learned_score=float(learned_score_of(record)),
        )
        if not math.isfinite(address.learned_score):
            raise ValueError("learned scores must be finite")
        pairs.append((record, address))

    # Global learned ranks reproduce the ordinary legal-candidate ranking at mix=0.
    learned_order = sorted(
        range(len(pairs)),
        key=lambda i: (-pairs[i][1].learned_score, pairs[i][1].fingerprint),
    )
    learned_rank = {index: rank for rank, index in enumerate(learned_order)}

    by_component: dict[str, list[int]] = {}
    for index, (_, address) in enumerate(pairs):
        by_component.setdefault(address.component, []).append(index)

    geometry: dict[int, tuple[tuple[int, ...], int, int, int]] = {}
    for indices in by_component.values():
        addresses = [pairs[index][1] for index in indices]
        metadata = _component_hilbert_metadata(addresses, seed=seed)
        local_order = sorted(
            indices,
            key=lambda index: (
                metadata[pairs[index][1].fingerprint][1],
                pairs[index][1].fingerprint,
            ),
        )
        local_rank = {index: rank for rank, index in enumerate(local_order)}
        for index in indices:
            point, distance, size = metadata[pairs[index][1].fingerprint]
            geometry[index] = (point, distance, size, local_rank[index])

    count = len(pairs)
    ranked: list[RankedApplication] = []
    for index, (record, address) in enumerate(pairs):
        point, distance, size, local_h_rank = geometry[index]
        l_pct = _rank_percentile(learned_rank[index], count)
        h_count = len(by_component[address.component])
        h_pct = _rank_percentile(local_h_rank, h_count)
        priority = (1.0 - hilbert_mix) * l_pct + hilbert_mix * h_pct
        ranked.append(
            RankedApplication(
                record=record,
                address=address,
                grid_point=point,
                hilbert_distance=distance,
                hilbert_size=size,
                learned_rank=learned_rank[index],
                hilbert_rank=local_h_rank,
                blended_priority=priority,
            )
        )

    ranked.sort(
        key=lambda item: (
            item.blended_priority,
            item.learned_rank,
            item.hilbert_rank,
            item.address.fingerprint,
        )
    )
    return ranked


def fair_cap(
    ranked: Sequence[RankedApplication],
    cap: int | None,
    *,
    round_index: int = 0,
) -> list[RankedApplication]:
    """Apply a cap while rotating coproduct components to avoid starvation.

    Within each component the blended order is preserved.  Across calls, an
    increasing ``round_index`` rotates which assertion component gets the first
    slot.  If ``cap`` is None all applications are returned in blended order.
    """
    if cap is None:
        return list(ranked)
    if cap < 0:
        raise ValueError("cap must be nonnegative")
    if cap == 0 or not ranked:
        return []

    buckets: dict[str, list[RankedApplication]] = {}
    for item in ranked:
        buckets.setdefault(item.address.component, []).append(item)

    components = sorted(
        buckets,
        key=lambda component: (
            buckets[component][0].blended_priority,
            component,
        ),
    )
    if components:
        shift = round_index % len(components)
        components = components[shift:] + components[:shift]

    output: list[RankedApplication] = []
    positions = {component: 0 for component in components}
    while len(output) < min(cap, len(ranked)):
        progressed = False
        for component in components:
            pos = positions[component]
            bucket = buckets[component]
            if pos < len(bucket):
                output.append(bucket[pos])
                positions[component] = pos + 1
                progressed = True
                if len(output) >= min(cap, len(ranked)):
                    break
        if not progressed:
            break
    return output


def schedule_legal_applications(
    records: Iterable[RecordT],
    *,
    component_of: Callable[[RecordT], str],
    coordinates_of: Callable[[RecordT], Sequence[Scalar]],
    learned_score_of: Callable[[RecordT], float],
    identity_of: Callable[[RecordT], str],
    hilbert_mix: float = 0.25,
    seed: int = 2301,
    cap: int | None = None,
    round_index: int = 0,
) -> list[RankedApplication]:
    """Convenience composition of ranking plus starvation-resistant capping."""
    ranked = rank_legal_applications(
        records,
        component_of=component_of,
        coordinates_of=coordinates_of,
        learned_score_of=learned_score_of,
        identity_of=identity_of,
        hilbert_mix=hilbert_mix,
        seed=seed,
    )
    return fair_cap(ranked, cap, round_index=round_index)
