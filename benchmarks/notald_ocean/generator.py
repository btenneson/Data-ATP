"""Deterministic Ocean generator for the NOTALD benchmark.

Creating this module does NOT authorize benchmark generation. The scored geometry must be
frozen in protocol.json first. The generator requires an explicit OceanGeometry object and
an explicit seed; there is no hidden default difficulty geometry.
"""

from __future__ import annotations

from dataclasses import dataclass
import random


@dataclass(frozen=True)
class OceanGeometry:
    """Search-burden parameters that must be frozen before scored generation."""

    distractors_per_backbone_node: int
    distractor_min_length: int
    distractor_max_length: int
    parallel_detour_probability: float

    def validate(self) -> None:
        if self.distractors_per_backbone_node < 0:
            raise ValueError("distractors_per_backbone_node must be nonnegative")
        if self.distractor_min_length < 1:
            raise ValueError("distractor_min_length must be at least 1")
        if self.distractor_max_length < self.distractor_min_length:
            raise ValueError("distractor_max_length must be >= distractor_min_length")
        if not 0.0 <= self.parallel_detour_probability <= 1.0:
            raise ValueError("parallel_detour_probability must be between 0 and 1")


@dataclass(frozen=True)
class OceanInstance:
    L: int
    seed: int
    source: str
    target: str
    edges: tuple[tuple[str, str], ...]
    planted_backbone: tuple[str, ...]


def generate_ocean(L: int, seed: int, geometry: OceanGeometry) -> OceanInstance:
    """Generate an Ocean with a planted source-to-target backbone of exactly L edges.

    Distractor branches are dead ends or longer re-entry detours. Every optional re-entry
    replaces a backbone segment of `branch_length` edges with a detour of
    `branch_length + 1` edges, so that edge cannot shorten the planted route. An independent
    auditor MUST still verify d(s,t) == L before any instance is accepted.
    """
    if L < 1:
        raise ValueError("L must be at least 1")
    geometry.validate()
    rng = random.Random(seed)

    backbone = tuple(f"b{i}" for i in range(L + 1))
    edges: list[tuple[str, str]] = [(backbone[i], backbone[i + 1]) for i in range(L)]
    counter = 0

    for i in range(L):
        origin = backbone[i]
        for _ in range(geometry.distractors_per_backbone_node):
            branch_length = rng.randint(
                geometry.distractor_min_length,
                geometry.distractor_max_length,
            )
            previous = origin
            for _step in range(branch_length):
                node = f"d{counter}"
                counter += 1
                edges.append((previous, node))
                previous = node

            # The branch already used branch_length edges. One additional edge returning
            # to b_(i + branch_length) makes this route one edge LONGER than the equivalent
            # backbone segment. Therefore the re-entry edge cannot create a shortcut.
            if rng.random() < geometry.parallel_detour_probability:
                reentry = i + branch_length
                if reentry <= L:
                    edges.append((previous, backbone[reentry]))

    rng.shuffle(edges)
    return OceanInstance(
        L=L,
        seed=seed,
        source=backbone[0],
        target=backbone[-1],
        edges=tuple(edges),
        planted_backbone=backbone,
    )
