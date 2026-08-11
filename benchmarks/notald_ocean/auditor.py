"""Independent graph auditor for the NOTALD Tied-Ocean benchmark.

This module intentionally knows nothing about how an Ocean instance was generated.
It verifies the shortest directed source-to-target distance from a plain edge list.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Hashable, Iterable, Mapping

Node = Hashable
Edge = tuple[Node, Node]


@dataclass(frozen=True)
class AuditResult:
    reachable: bool
    shortest_distance: int | None
    expected_distance: int
    distance_matches: bool
    path: tuple[Node, ...]


def _adjacency(edges: Iterable[Edge]) -> dict[Node, list[Node]]:
    graph: dict[Node, list[Node]] = {}
    for u, v in edges:
        graph.setdefault(u, []).append(v)
        graph.setdefault(v, [])
    return graph


def shortest_path(edges: Iterable[Edge], source: Node, target: Node) -> tuple[int | None, tuple[Node, ...]]:
    """Return exact unweighted directed shortest-path distance and one shortest path."""
    graph = _adjacency(edges)
    if source == target:
        return 0, (source,)

    queue = deque([source])
    distance: dict[Node, int] = {source: 0}
    predecessor: dict[Node, Node] = {}

    while queue:
        u = queue.popleft()
        for v in graph.get(u, ()):  # tolerate isolated source
            if v in distance:
                continue
            distance[v] = distance[u] + 1
            predecessor[v] = u
            if v == target:
                rev = [target]
                cur = target
                while cur != source:
                    cur = predecessor[cur]
                    rev.append(cur)
                rev.reverse()
                return distance[target], tuple(rev)
            queue.append(v)

    return None, ()


def audit_ocean(edges: Iterable[Edge], source: Node, target: Node, expected_L: int) -> AuditResult:
    """Independently verify d(source, target) == expected_L."""
    if expected_L < 0:
        raise ValueError("expected_L must be nonnegative")

    distance, path = shortest_path(edges, source, target)
    return AuditResult(
        reachable=distance is not None,
        shortest_distance=distance,
        expected_distance=expected_L,
        distance_matches=(distance == expected_L),
        path=path,
    )


def require_exact_horizon(edges: Iterable[Edge], source: Node, target: Node, expected_L: int) -> AuditResult:
    """Raise if the independently measured Ocean proof horizon is not exactly L."""
    result = audit_ocean(edges, source, target, expected_L)
    if not result.reachable:
        raise RuntimeError("Ocean audit failed: target is unreachable")
    if not result.distance_matches:
        raise RuntimeError(
            f"Ocean audit failed: expected shortest distance {expected_L}, "
            f"measured {result.shortest_distance}"
        )
    return result
