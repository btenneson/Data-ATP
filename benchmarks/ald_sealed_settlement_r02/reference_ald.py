from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional

from common import Literal, Problem, bfs_certificate, parse_problem, write_json


def lit_index(l: Literal) -> int:
    return 2 * l.var + (0 if l.positive else 1)


def neg_index(i: int) -> int:
    return i ^ 1


def solve_2sat(problem: Problem, extra_unit: Optional[Literal] = None) -> Optional[Dict[int, bool]]:
    max_var = max(problem.variables)
    n = 2 * (max_var + 1)
    g: List[List[int]] = [[] for _ in range(n)]
    rg: List[List[int]] = [[] for _ in range(n)]

    def add_imp(a: int, b: int) -> None:
        g[a].append(b)
        rg[b].append(a)

    def add_clause(a: Literal, b: Literal) -> None:
        ai, bi = lit_index(a), lit_index(b)
        add_imp(neg_index(ai), bi)
        add_imp(neg_index(bi), ai)

    def add_unit(a: Literal) -> None:
        ai = lit_index(a)
        add_imp(neg_index(ai), ai)

    for _, u in problem.units:
        add_unit(u)
    for _, a, b in problem.edges:
        add_clause(a.complement(), b)
    if extra_unit is not None:
        add_unit(extra_unit)

    seen = [False] * n
    order: List[int] = []
    for s in range(n):
        if seen[s]:
            continue
        stack = [(s, 0)]
        seen[s] = True
        while stack:
            v, k = stack[-1]
            if k < len(g[v]):
                w = g[v][k]
                stack[-1] = (v, k + 1)
                if not seen[w]:
                    seen[w] = True
                    stack.append((w, 0))
            else:
                order.append(v)
                stack.pop()

    comp = [-1] * n
    cid = 0
    for s in reversed(order):
        if comp[s] != -1:
            continue
        comp[s] = cid
        stack = [s]
        while stack:
            v = stack.pop()
            for w in rg[v]:
                if comp[w] == -1:
                    comp[w] = cid
                    stack.append(w)
        cid += 1

    for v in problem.variables:
        if comp[lit_index(Literal(v, True))] == comp[lit_index(Literal(v, False))]:
            return None

    assignment: Dict[int, bool] = {}
    for v in problem.variables:
        p = lit_index(Literal(v, True))
        q = lit_index(Literal(v, False))
        assignment[v] = comp[p] > comp[q]
    return assignment


def settle(problem: Problem) -> dict:
    cert_p = bfs_certificate(problem, problem.goal)
    if cert_p is not None:
        return {"claim": "PROVED", "certificate": cert_p, "agent": "P"}

    cert_r = bfs_certificate(problem, problem.goal.complement())
    if cert_r is not None:
        return {"claim": "REFUTED", "certificate": cert_r, "agent": "R"}

    m_c = solve_2sat(problem, problem.goal)
    m_n = solve_2sat(problem, problem.goal.complement())
    if m_c is not None and m_n is not None:
        return {
            "claim": "INDEPENDENT",
            "agent": "I",
            "model_C": {f"n{k}": v for k, v in sorted(m_c.items())},
            "model_not_C": {f"n{k}": v for k, v in sorted(m_n.items())},
        }

    return {"claim": "UNKNOWN", "reason": "no certificate produced by reference ALD", "agent": "scheduler"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--problem", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    problem = parse_problem(Path(args.problem))
    result = settle(problem)
    write_json(Path(args.out), result)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
