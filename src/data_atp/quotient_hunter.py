"""DATA-MIND 2.6 Quotient Hunter.

Quotient Hunter (QH) is a metalogical search agent.  It does not certify
theoremhood.  It searches visible transition structure for smaller quotients,
ranking functions, invariants, and fixed-point geometries that can safely
reorder proof search.

The first executable adapter targets the transparent Depths/Ocean implication
graph.  QH tests several candidate quotients, including modular rank quotients
(MIU-like candidates) and the exact reverse-distance rank quotient.  A
target-specific search-policy trade is activatable only after an independent
graph check proves that restricting search to rank-decreasing edges preserves
source->target reachability.

Important distinction:
    H(Tx) < H(x)
is a contraction of distance-to-settlement along the selected dynamics.  This
module does NOT claim a Banach pairwise metric contraction unless such a metric
is separately certified.
"""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from typing import Any, Iterable, Mapping, Sequence
import math


INF_LABEL = "INF"


@dataclass(frozen=True, slots=True)
class CandidateReport:
    name: str
    quotient_size: int
    compression_ratio: float
    source_class: Any
    target_class: Any
    target_separated: bool
    strict_progress_policy: bool
    target_reachability_equivalence_certified: bool
    lambda_h_bound: float | None
    unique_policy_fixed_point: bool
    notes: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class QuotientDiscovery:
    selected: str | None
    reports: tuple[CandidateReport, ...]
    source_horizon: int | None
    policy_path: tuple[int, ...]
    policy_path_verified: bool
    trade_activatable: bool
    trade_scope: str
    hidden_metadata_read: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "selected": self.selected,
            "reports": [r.as_dict() for r in self.reports],
            "source_horizon": self.source_horizon,
            "policy_path": list(self.policy_path),
            "policy_path_verified": self.policy_path_verified,
            "trade_activatable": self.trade_activatable,
            "trade_scope": self.trade_scope,
            "hidden_metadata_read": self.hidden_metadata_read,
        }


class QuotientHunter:
    """Search visible directed-graph structure for a useful quotient.

    Parameters are only source, target, and visible edges.  No planted route,
    answer key, generator seed, or declared shortest proof length is consumed.
    """

    def __init__(
        self,
        *,
        source: int,
        target: int,
        edges: Sequence[tuple[int, int]],
        preferred_candidates: Sequence[str] = (),
    ) -> None:
        self.source = int(source)
        self.target = int(target)
        self.edges = tuple((int(u), int(v)) for u, v in edges)
        self.adj: dict[int, list[int]] = defaultdict(list)
        self.radj: dict[int, list[int]] = defaultdict(list)
        self.nodes: set[int] = {self.source, self.target}
        for u, v in self.edges:
            self.adj[u].append(v)
            self.radj[v].append(u)
            self.nodes.add(u)
            self.nodes.add(v)
        for u in self.adj:
            self.adj[u].sort()
        for v in self.radj:
            self.radj[v].sort()
        self.preferred_candidates = tuple(dict.fromkeys(str(x) for x in preferred_candidates))
        self.reverse_rank = self._bfs(self.target, self.radj)
        self.forward_rank = self._bfs(self.source, self.adj)

    @staticmethod
    def _bfs(start: int, adj: Mapping[int, Sequence[int]]) -> dict[int, int]:
        out = {int(start): 0}
        q = deque([int(start)])
        while q:
            u = q.popleft()
            d = out[u] + 1
            for v in adj.get(u, ()):
                if v not in out:
                    out[v] = d
                    q.append(v)
        return out

    def _policy_successor(self, u: int) -> int | None:
        if u == self.target:
            return self.target
        h = self.reverse_rank.get(u)
        if h is None or h <= 0:
            return None
        good = [v for v in self.adj.get(u, ()) if self.reverse_rank.get(v) == h - 1]
        if not good:
            return None
        return min(good, key=lambda v: (len(self.adj.get(v, ())), v))

    def policy_path(self) -> tuple[int, ...]:
        if self.source not in self.reverse_rank:
            return ()
        path = [self.source]
        seen = {self.source}
        u = self.source
        while u != self.target:
            v = self._policy_successor(u)
            if v is None or v in seen:
                return ()
            path.append(v)
            seen.add(v)
            u = v
        return tuple(path)

    def verify_policy_path(self, path: Sequence[int]) -> bool:
        if not path or path[0] != self.source or path[-1] != self.target:
            return False
        edge_set = set(self.edges)
        return all((int(u), int(v)) in edge_set for u, v in zip(path, path[1:]))

    def _rank_certificate(self) -> bool:
        """Bellman-check exact finite distance labels on the visible graph."""
        if self.reverse_rank.get(self.target) != 0:
            return False
        for u, h in self.reverse_rank.items():
            if u == self.target:
                continue
            child_h = [self.reverse_rank[v] for v in self.adj.get(u, ()) if v in self.reverse_rank]
            if not child_h or h != 1 + min(child_h):
                return False
        return self.source in self.reverse_rank

    def _rank_report(self) -> CandidateReport:
        finite = set(self.reverse_rank.values())
        quotient_size = len(finite) + (1 if len(self.reverse_rank) < len(self.nodes) else 0)
        cert = self._rank_certificate()
        path = self.policy_path()
        path_ok = self.verify_policy_path(path)
        h0 = self.reverse_rank.get(self.source)
        if h0 is None:
            lam = None
        elif h0 <= 1:
            lam = 0.0
        else:
            lam = (h0 - 1.0) / h0
        fixed_ok = cert and all(
            (u == self.target and self._policy_successor(u) == u)
            or (u != self.target and self._policy_successor(u) is not None
                and self.reverse_rank[self._policy_successor(u)] < self.reverse_rank[u])
            for u in self.reverse_rank
        )
        return CandidateReport(
            name="reverse_distance_rank",
            quotient_size=quotient_size,
            compression_ratio=(len(self.nodes) / max(1, quotient_size)),
            source_class=self.reverse_rank.get(self.source, INF_LABEL),
            target_class=0,
            target_separated=True,
            strict_progress_policy=bool(cert and path_ok),
            target_reachability_equivalence_certified=bool(cert and path_ok),
            lambda_h_bound=lam,
            unique_policy_fixed_point=bool(fixed_ok),
            notes=(
                "Exact visible-graph distance-to-target quotient.  The certified "
                "policy decreases H by one at every nonterminal step; target is "
                "the only fixed point of that selected policy."
            ),
        )

    def _mod_report(self, k: int) -> CandidateReport:
        labels = {
            u: (self.reverse_rank[u] % k if u in self.reverse_rank else INF_LABEL)
            for u in self.nodes
        }
        classes = set(labels.values())
        target_class = labels[self.target]
        target_members = [u for u, c in labels.items() if c == target_class]
        target_separated = target_members == [self.target] or set(target_members) == {self.target}
        strict = True
        for u, h in self.reverse_rank.items():
            if u == self.target:
                continue
            v = self._policy_successor(u)
            if v is None:
                strict = False
                break
            if labels[v] >= labels[u]:
                strict = False
                break
        return CandidateReport(
            name=f"reverse_rank_mod_{k}",
            quotient_size=len(classes),
            compression_ratio=(len(self.nodes) / max(1, len(classes))),
            source_class=labels[self.source] if self.source in labels else INF_LABEL,
            target_class=target_class,
            target_separated=target_separated,
            strict_progress_policy=strict,
            target_reachability_equivalence_certified=False,
            lambda_h_bound=None,
            unique_policy_fixed_point=False,
            notes=(
                f"MIU-style modular quotient candidate (mod {k}).  Retained as "
                "metalogical evidence even when wraparound prevents a certified "
                "distance-to-settlement contraction."
            ),
        )

    def _forward_report(self) -> CandidateReport:
        labels = {
            u: self.forward_rank.get(u, INF_LABEL)
            for u in self.nodes
        }
        classes = set(labels.values())
        target_class = labels.get(self.target, INF_LABEL)
        target_separated = sum(1 for c in labels.values() if c == target_class) == 1
        return CandidateReport(
            name="forward_depth_rank",
            quotient_size=len(classes),
            compression_ratio=(len(self.nodes) / max(1, len(classes))),
            source_class=0,
            target_class=target_class,
            target_separated=target_separated,
            strict_progress_policy=False,
            target_reachability_equivalence_certified=False,
            lambda_h_bound=None,
            unique_policy_fixed_point=False,
            notes=(
                "Distance from the source is a useful structural coordinate but "
                "does not by itself certify progress toward the target."
            ),
        )

    def discover(self) -> QuotientDiscovery:
        reports_by_name: dict[str, CandidateReport] = {}
        candidates: list[CandidateReport] = [self._forward_report()]
        candidates.extend(self._mod_report(k) for k in range(2, 8))
        candidates.append(self._rank_report())
        for r in candidates:
            reports_by_name[r.name] = r

        ordered: list[CandidateReport] = []
        for name in self.preferred_candidates:
            if name in reports_by_name and reports_by_name[name] not in ordered:
                ordered.append(reports_by_name[name])
        ordered.extend(r for r in candidates if r not in ordered)

        admissible = [
            r for r in ordered
            if r.target_reachability_equivalence_certified and r.strict_progress_policy
        ]
        if admissible:
            selected_report = max(
                admissible,
                key=lambda r: (
                    r.compression_ratio,
                    -(r.lambda_h_bound if r.lambda_h_bound is not None else math.inf),
                    -r.quotient_size,
                ),
            )
            selected = selected_report.name
        else:
            selected_report = None
            selected = None

        path = self.policy_path() if selected == "reverse_distance_rank" else ()
        path_ok = self.verify_policy_path(path)
        return QuotientDiscovery(
            selected=selected,
            reports=tuple(ordered),
            source_horizon=self.reverse_rank.get(self.source),
            policy_path=path,
            policy_path_verified=path_ok,
            trade_activatable=bool(
                selected_report is not None
                and selected_report.target_reachability_equivalence_certified
                and path_ok
            ),
            trade_scope=(
                "target-specific search-policy trade only; does not alter axioms, "
                "inference legality, theorem semantics, or the independent verifier"
            ),
        )

    def best_live_vertex(self, vertices: Iterable[int]) -> int | None:
        finite = [int(v) for v in vertices if int(v) in self.reverse_rank]
        if not finite:
            return None
        return min(
            finite,
            key=lambda v: (self.reverse_rank[v], len(self.adj.get(v, ())), v),
        )

    def horizon(self, vertex: int) -> int | None:
        return self.reverse_rank.get(int(vertex))
