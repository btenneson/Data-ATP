from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

LIT_RE = re.compile(r"^(~)?p\(n(\d+)\)$")
START_RE = re.compile(r"^fof\(([^,]+),\s*axiom,\s*(~?p\(n\d+\))\s*\)\.$")
EDGE_RE = re.compile(r"^fof\(([^,]+),\s*axiom,\s*\(\s*(~?p\(n\d+\))\s*=>\s*(~?p\(n\d+\))\s*\)\s*\)\.$")
GOAL_RE = re.compile(r"^fof\(goal,\s*conjecture,\s*(~?p\(n\d+\))\s*\)\.$")


@dataclass(frozen=True)
class Literal:
    var: int
    positive: bool = True

    def complement(self) -> "Literal":
        return Literal(self.var, not self.positive)

    def tptp(self) -> str:
        atom = f"p(n{self.var})"
        return atom if self.positive else f"~{atom}"

    @staticmethod
    def parse(text: str) -> "Literal":
        m = LIT_RE.fullmatch(text.strip())
        if not m:
            raise ValueError(f"bad literal: {text}")
        return Literal(int(m.group(2)), m.group(1) is None)


@dataclass
class Problem:
    units: List[Tuple[str, Literal]]
    edges: List[Tuple[str, Literal, Literal]]
    goal: Literal

    @property
    def variables(self) -> List[int]:
        out = {lit.var for _, lit in self.units}
        for _, a, b in self.edges:
            out.add(a.var)
            out.add(b.var)
        out.add(self.goal.var)
        return sorted(out)


def parse_problem(path: Path) -> Problem:
    units: List[Tuple[str, Literal]] = []
    edges: List[Tuple[str, Literal, Literal]] = []
    goal: Optional[Literal] = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("%"):
            continue
        mg = GOAL_RE.fullmatch(line)
        if mg:
            goal = Literal.parse(mg.group(1))
            continue
        me = EDGE_RE.fullmatch(line)
        if me:
            edges.append((me.group(1), Literal.parse(me.group(2)), Literal.parse(me.group(3))))
            continue
        mu = START_RE.fullmatch(line)
        if mu:
            units.append((mu.group(1), Literal.parse(mu.group(2))))
            continue
        raise ValueError(f"unsupported line: {line}")
    if goal is None or not units:
        raise ValueError("problem requires at least one unit axiom and one conjecture")
    return Problem(units=units, edges=edges, goal=goal)


def eval_literal(lit: Literal, valuation: Dict[int, bool]) -> bool:
    if lit.var not in valuation:
        raise ValueError(f"valuation missing variable n{lit.var}")
    v = bool(valuation[lit.var])
    return v if lit.positive else not v


def model_satisfies(problem: Problem, valuation: Dict[int, bool]) -> bool:
    if any(v not in valuation for v in problem.variables):
        return False
    for _, lit in problem.units:
        if not eval_literal(lit, valuation):
            return False
    for _, a, b in problem.edges:
        if eval_literal(a, valuation) and not eval_literal(b, valuation):
            return False
    return True


def adjacency(problem: Problem) -> Dict[Literal, List[Tuple[str, Literal]]]:
    out: Dict[Literal, List[Tuple[str, Literal]]] = {}
    for name, a, b in problem.edges:
        out.setdefault(a, []).append((name, b))
    for a in out:
        out[a].sort(key=lambda x: (x[1].var, x[1].positive, x[0]))
    return out


def bfs_certificate(problem: Problem, target: Literal) -> Optional[dict]:
    from collections import deque

    adj = adjacency(problem)
    parent: Dict[Literal, Optional[Literal]] = {}
    via: Dict[Literal, Optional[str]] = {}
    q = deque()
    for name, lit in problem.units:
        if lit not in parent:
            parent[lit] = None
            via[lit] = name
            q.append(lit)
    if target in parent:
        return {"literals": [target.tptp()], "axioms": [via[target]]}
    while q:
        u = q.popleft()
        for edge_name, v in adj.get(u, []):
            if v in parent:
                continue
            parent[v] = u
            via[v] = edge_name
            if v == target:
                lits: List[Literal] = [v]
                ax: List[str] = [edge_name]
                x = u
                while parent[x] is not None:
                    lits.append(x)
                    ax.append(via[x])
                    x = parent[x]  # type: ignore[index]
                lits.append(x)
                ax.append(via[x])
                lits.reverse()
                ax.reverse()
                return {"literals": [z.tptp() for z in lits], "axioms": ax}
            q.append(v)
    return None


def shortest_ocean_distance(problem: Problem, target: Literal) -> Optional[int]:
    cert = bfs_certificate(problem, target)
    if cert is None:
        return None
    return max(0, len(cert["literals"]) - 1)


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
