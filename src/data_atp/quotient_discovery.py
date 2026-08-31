"""DATA-MIND 2.7 generalized Quotient Hunter discovery engine.

2.6 demonstrated that a useful quotient geometry can collapse proof search.
2.7 removes the built-in exact reverse-distance quotient from Quotient Hunter's
candidate list.  Instead, QH enumerates a small language of metalogical
operators and asks which one induces a verifier-safe settlement geometry.

The first candidate language is deliberately simple and auditable:

* fixed-point shell operators generated from {source,target} x
  {predecessor,successor};
* modular node observables n mod k, k=2..7;
* degree-signature observables.

A fixed-point shell operator is evaluated by a generic work-list engine.  For
example, if QH happens to select ``target_predecessor_fixed_point``, the
resulting entry-time shells coincide with distance-to-target, but that metric
is an OUTPUT of the discovered operator, not an input handed to QH.

This module certifies search geometry only.  It never certifies theoremhood or
writes theorem certificates to BANK.
"""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping, Sequence
import math


INF = "INF"


@dataclass(frozen=True, slots=True)
class OperatorReport:
    name: str
    family: str
    generated_index: int
    quotient_size: int
    compression_ratio: float
    source_label: Any
    target_label: Any
    source_represented: bool
    target_is_zero: bool
    strict_descent_to_target: bool
    policy_path_verified: bool
    unique_policy_fixed_point: bool
    target_reachability_equivalence_certified: bool
    source_horizon: int | None
    lambda_h_bound: float | None
    fixed_point_rounds: int | None
    score: float
    notes: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class DiscoveryResult:
    selected_operator: str | None
    selected_family: str | None
    reports: tuple[OperatorReport, ...]
    generated_candidate_count: int
    source_horizon: int | None
    policy_path: tuple[int, ...]
    policy_path_verified: bool
    trade_activatable: bool
    exact_reverse_distance_handed_to_qh: bool
    hidden_metadata_read: bool
    discovery_statement: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "selected_operator": self.selected_operator,
            "selected_family": self.selected_family,
            "reports": [r.as_dict() for r in self.reports],
            "generated_candidate_count": self.generated_candidate_count,
            "source_horizon": self.source_horizon,
            "policy_path": list(self.policy_path),
            "policy_path_verified": self.policy_path_verified,
            "trade_activatable": self.trade_activatable,
            "exact_reverse_distance_handed_to_qh": self.exact_reverse_distance_handed_to_qh,
            "hidden_metadata_read": self.hidden_metadata_read,
            "discovery_statement": self.discovery_statement,
        }


class QuotientDiscoveryEngine:
    """Enumerate and test metalogical quotient/operator candidates."""

    def __init__(
        self,
        *,
        source: int,
        target: int,
        edges: Sequence[tuple[int, int]],
        preferred_operators: Sequence[str] = (),
    ) -> None:
        self.source = int(source)
        self.target = int(target)
        self.edges = tuple((int(u), int(v)) for u, v in edges)
        self.nodes: set[int] = {self.source, self.target}
        self.adj: dict[int, list[int]] = defaultdict(list)
        self.radj: dict[int, list[int]] = defaultdict(list)
        for u, v in self.edges:
            self.nodes.add(u); self.nodes.add(v)
            self.adj[u].append(v)
            self.radj[v].append(u)
        for d in (self.adj, self.radj):
            for k in d:
                d[k].sort()
        self.edge_set = set(self.edges)
        self.preferred_operators = tuple(dict.fromkeys(str(x) for x in preferred_operators))
        self._labels_by_operator: dict[str, dict[int, int]] = {}
        self._path_by_operator: dict[str, tuple[int, ...]] = {}

    def _fixed_point_shells(
        self,
        *,
        seed: int,
        expansion_relation: Mapping[int, Sequence[int]],
    ) -> tuple[dict[int, int], int]:
        """Generic least-fixed-point shell evaluator.

        ``expansion_relation[x]`` contains states admitted one shell after x.
        Work-list evaluation returns first-entry shell numbers.  The evaluator
        knows nothing about proof distance, source/target semantics, or which
        relation orientation is useful.
        """
        labels = {int(seed): 0}
        q = deque([int(seed)])
        max_round = 0
        while q:
            u = q.popleft()
            nxt_round = labels[u] + 1
            max_round = max(max_round, nxt_round)
            for v in expansion_relation.get(u, ()):
                if v not in labels:
                    labels[v] = nxt_round
                    q.append(v)
        return labels, max(0, max_round)

    def _extract_descent_path(self, labels: Mapping[int, int]) -> tuple[int, ...]:
        if self.source not in labels or labels.get(self.target) != 0:
            return ()
        path = [self.source]
        seen = {self.source}
        u = self.source
        while u != self.target:
            h = labels.get(u)
            if h is None or h <= 0:
                return ()
            candidates = [v for v in self.adj.get(u, ()) if labels.get(v) == h - 1]
            if not candidates:
                return ()
            v = min(candidates, key=lambda z: (len(self.adj.get(z, ())), z))
            if v in seen:
                return ()
            path.append(v)
            seen.add(v)
            u = v
        return tuple(path)

    def _verify_path(self, path: Sequence[int]) -> bool:
        if not path or path[0] != self.source or path[-1] != self.target:
            return False
        return all((int(u), int(v)) in self.edge_set for u, v in zip(path, path[1:]))

    def _strict_descent_certificate(self, labels: Mapping[int, int]) -> bool:
        if self.source not in labels or labels.get(self.target) != 0:
            return False
        # It is enough for every finite nonterminal state to have a legal edge
        # into the previous shell.  This proves termination of the selected
        # policy and preserves source->target reachability for the target task.
        for u, h in labels.items():
            if u == self.target:
                continue
            if h <= 0:
                return False
            if not any(labels.get(v) == h - 1 for v in self.adj.get(u, ())):
                return False
        return True

    def _fixed_point_report(
        self,
        *,
        name: str,
        seed: int,
        relation: Mapping[int, Sequence[int]],
        index: int,
        notes: str,
    ) -> OperatorReport:
        labels, rounds = self._fixed_point_shells(seed=seed, expansion_relation=relation)
        self._labels_by_operator[name] = labels
        path = self._extract_descent_path(labels)
        self._path_by_operator[name] = path
        path_ok = self._verify_path(path)
        strict = self._strict_descent_certificate(labels)
        h0 = labels.get(self.source)
        target_zero = labels.get(self.target) == 0
        fixed_unique = bool(
            strict
            and target_zero
            and all(
                (u == self.target)
                or any(labels.get(v) == labels[u] - 1 for v in self.adj.get(u, ()))
                for u in labels
            )
        )
        certified = bool(strict and path_ok and target_zero)
        if h0 is None:
            lam = None
        elif h0 <= 1:
            lam = 0.0
        else:
            lam = (h0 - 1.0) / h0
        qsize = len(set(labels.values())) + (1 if len(labels) < len(self.nodes) else 0)
        compression = len(self.nodes) / max(1, qsize)
        # Certification dominates.  Then prefer smaller contraction constant;
        # compression is a secondary tie-breaker.
        score = (
            (1_000_000.0 if certified else 0.0)
            + (100_000.0 if fixed_unique else 0.0)
            + (10_000.0 if self.source in labels else 0.0)
            + (1_000.0 * (1.0 - lam) if lam is not None else 0.0)
            + min(999.0, compression)
        )
        return OperatorReport(
            name=name,
            family="fixed_point_shell",
            generated_index=index,
            quotient_size=qsize,
            compression_ratio=compression,
            source_label=h0 if h0 is not None else INF,
            target_label=labels.get(self.target, INF),
            source_represented=self.source in labels,
            target_is_zero=target_zero,
            strict_descent_to_target=strict,
            policy_path_verified=path_ok,
            unique_policy_fixed_point=fixed_unique,
            target_reachability_equivalence_certified=certified,
            source_horizon=h0,
            lambda_h_bound=lam,
            fixed_point_rounds=rounds,
            score=score,
            notes=notes,
        )

    def _observable_report(
        self,
        *,
        name: str,
        labels: Mapping[int, Any],
        family: str,
        index: int,
        notes: str,
    ) -> OperatorReport:
        classes = set(labels.values())
        qsize = len(classes)
        compression = len(self.nodes) / max(1, qsize)
        target_label = labels.get(self.target, INF)
        source_label = labels.get(self.source, INF)
        target_unique = sum(1 for x in labels.values() if x == target_label) == 1
        # Generic observables are retained as hypotheses but are not permitted
        # to activate a proof-search trade without a descent certificate.
        score = (100.0 if target_unique else 0.0) + min(99.0, compression)
        return OperatorReport(
            name=name,
            family=family,
            generated_index=index,
            quotient_size=qsize,
            compression_ratio=compression,
            source_label=source_label,
            target_label=target_label,
            source_represented=self.source in labels,
            target_is_zero=target_label == 0,
            strict_descent_to_target=False,
            policy_path_verified=False,
            unique_policy_fixed_point=False,
            target_reachability_equivalence_certified=False,
            source_horizon=None,
            lambda_h_bound=None,
            fixed_point_rounds=None,
            score=score,
            notes=notes,
        )

    def _candidate_reports(self) -> list[OperatorReport]:
        reports: list[OperatorReport] = []
        idx = 0

        fixed_specs = (
            (
                "source_successor_fixed_point", self.source, self.adj,
                "Least fixed point generated forward from the source."
            ),
            (
                "source_predecessor_fixed_point", self.source, self.radj,
                "Least fixed point generated backward from the source."
            ),
            (
                "target_successor_fixed_point", self.target, self.adj,
                "Least fixed point generated forward from the target."
            ),
            (
                "target_predecessor_fixed_point", self.target, self.radj,
                "Least fixed point generated from the target through rule predecessors."
            ),
        )
        for name, seed, relation, note in fixed_specs:
            reports.append(self._fixed_point_report(
                name=name, seed=seed, relation=relation, index=idx, notes=note
            ))
            idx += 1

        indeg = {u: len(self.radj.get(u, ())) for u in self.nodes}
        outdeg = {u: len(self.adj.get(u, ())) for u in self.nodes}
        degree_labels = {
            u: (min(3, indeg[u]), min(3, outdeg[u]))
            for u in self.nodes
        }
        reports.append(self._observable_report(
            name="bounded_degree_signature",
            labels=degree_labels,
            family="structural_observable",
            index=idx,
            notes="Bounded in/out-degree quotient candidate.",
        ))
        idx += 1

        for k in range(2, 8):
            reports.append(self._observable_report(
                name=f"node_id_mod_{k}",
                labels={u: u % k for u in self.nodes},
                family="modular_observable",
                index=idx,
                notes=f"MIU-style modular observable candidate modulo {k}.",
            ))
            idx += 1
        return reports

    def discover(self) -> DiscoveryResult:
        reports = self._candidate_reports()
        pref = {name: i for i, name in enumerate(self.preferred_operators)}
        reports.sort(key=lambda r: (
            r.score,
            -pref.get(r.name, 10_000),
            -r.generated_index,
        ), reverse=True)
        selected = next(
            (r for r in reports if r.target_reachability_equivalence_certified),
            None,
        )
        if selected is None:
            path: tuple[int, ...] = ()
            statement = "No candidate operator produced a certified settlement geometry."
        else:
            path = self._path_by_operator.get(selected.name, ())
            statement = (
                f"QH selected {selected.name}; its least-fixed-point entry shells "
                f"induce H(source)={selected.source_horizon} and a strict legal "
                "descent to the target."
            )
        return DiscoveryResult(
            selected_operator=selected.name if selected else None,
            selected_family=selected.family if selected else None,
            reports=tuple(reports),
            generated_candidate_count=len(reports),
            source_horizon=selected.source_horizon if selected else None,
            policy_path=path,
            policy_path_verified=self._verify_path(path),
            trade_activatable=bool(selected and selected.target_reachability_equivalence_certified),
            exact_reverse_distance_handed_to_qh=False,
            hidden_metadata_read=False,
            discovery_statement=statement,
        )

    def labels_for(self, operator_name: str) -> dict[int, int]:
        return dict(self._labels_by_operator.get(str(operator_name), {}))

    def best_live_vertex(self, operator_name: str, vertices: Iterable[int]) -> int | None:
        labels = self._labels_by_operator.get(str(operator_name), {})
        finite = [int(v) for v in vertices if int(v) in labels]
        if not finite:
            return None
        return min(finite, key=lambda v: (labels[v], len(self.adj.get(v, ())), v))

    def horizon(self, operator_name: str, vertex: int) -> int | None:
        return self._labels_by_operator.get(str(operator_name), {}).get(int(vertex))


def independently_verify_discovered_rank(
    *,
    source: int,
    target: int,
    edges: Iterable[tuple[int, int]],
    labels: Mapping[int, int],
) -> bool:
    """Independent certificate check; does not reuse discovery internals."""
    adj: dict[int, list[int]] = defaultdict(list)
    for u, v in edges:
        adj[int(u)].append(int(v))
    source = int(source); target = int(target)
    if labels.get(target) != 0 or source not in labels:
        return False
    for u, h in labels.items():
        if u == target:
            continue
        if h <= 0 or not any(labels.get(v) == h - 1 for v in adj.get(u, ())):
            return False
    u = source
    seen = {u}
    while u != target:
        h = labels.get(u)
        if h is None or h <= 0:
            return False
        nxt = [v for v in adj.get(u, ()) if labels.get(v) == h - 1]
        if not nxt:
            return False
        u = min(nxt)
        if u in seen:
            return False
        seen.add(u)
    return True
