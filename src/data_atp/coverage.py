"""Budget-balanced Hilbert-derived coverage formulas."""

from __future__ import annotations

import math


def _validate(dimension: int, level: int, side_length: float) -> None:
    if dimension <= 1:
        raise ValueError("dimension must be greater than one")
    if level < 0:
        raise ValueError("level must be nonnegative")
    if side_length <= 0:
        raise ValueError("side_length must be positive")


def nominal_stage_length(dimension: int, level: int, side_length: float = 1.0) -> float:
    """Ideal center-to-center length for a face-adjacent dyadic traversal."""
    _validate(dimension, level, side_length)
    return side_length * (2 ** (level * (dimension - 1)) - 2 ** (-level))


def cumulative_nominal_length(dimension: int, level: int, side_length: float = 1.0) -> float:
    """Cumulative ideal length of complete levels 0 through ``level``."""
    _validate(dimension, level, side_length)
    numerator = 2 ** ((dimension - 1) * (level + 1)) - 1
    denominator = 2 ** (dimension - 1) - 1
    return side_length * (numerator / denominator - 2 + 2 ** (-level))


def coverage_defect_bound(dimension: int, level: int, side_length: float = 1.0) -> float:
    """Half-diagonal bound after every level-``level`` cell center is visited."""
    _validate(dimension, level, side_length)
    return math.sqrt(dimension) * side_length / (2 ** (level + 1))


def completed_level_for_budget(
    dimension: int,
    budget: float,
    side_length: float = 1.0,
    max_level: int = 10_000,
) -> int:
    """Largest complete nominal level affordable by ``budget``; -1 if none."""
    if budget < 0:
        raise ValueError("budget must be nonnegative")
    if dimension <= 1 or side_length <= 0:
        raise ValueError("invalid dimension or side_length")
    completed = -1
    for level in range(max_level + 1):
        if cumulative_nominal_length(dimension, level, side_length) <= budget:
            completed = level
        else:
            break
    return completed


def hierarchical_atp_defect(
    initial_diameter: float,
    completed_level: int,
    contraction: float = 0.5,
) -> float:
    """Declared feature-space defect after a complete hierarchical ATP level."""
    if initial_diameter < 0:
        raise ValueError("initial_diameter must be nonnegative")
    if completed_level < 0:
        return initial_diameter
    if not 0 < contraction < 1:
        raise ValueError("contraction must lie in (0, 1)")
    return initial_diameter * contraction ** completed_level
