#!/usr/bin/env python3
"""Frozen Ocean reference adapters for Data-ATP and DATA 2.0.1.

These are benchmark-specific reference implementations, not claims that the
full research architectures are production-complete general ATPs.

Input contract:
- one opaque TPTP problem containing only start, unary implication axioms,
  and a conjecture;
- no manifest, planted route, generator seed, or L* is read by this program.

All returned paths are checked by an independent graph-path verifier before
PROVED is emitted.
"""
from __future__ import annotations

import argparse
import heapq
import json
import re
import time
from collections import defaultdict, deque
from pathlib import Path

START_RE = re.compile(r"fof\(\s*start\s*,\s*axiom\s*,\s*p\(n(\d+)\)\s*\)\s*\.")
GOAL_RE = re.compile(r"fof\(\s*goal\s*,\s*conjecture\s*,\s*p\(n(\d+)\)\s*\)\s*\.")
EDGE_RE = re.compile(
    r"fof\(\s*[^,]+\s*,\s*axiom\s*,\s*\(\s*p\(n(\d+)\)\s*=>\s*p\(n(\d+)\)\s*\)\s*\)\s*\."
)

LOOKAHEAD_DEPTH = 6
MAX_EXPANSIONS = 5_000_000


def parse_problem(path: Path):
    source = target = None
    edges = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("%"):
            continue
        m = START_RE.fullmatch(line)
        if m:
            source = int(m.group(1))
            continue
        m = GOAL_RE.fullmatch(line)
        if m:
            target = int(m.group(1))
            continue
        m = EDGE_RE.fullmatch(line)
        if m:
            edges.append((int(m.group(1)), int(m.group(2))))
    if source is None or target is None or not edges:
        raise ValueError("unsupported or malformed Ocean TPTP problem")
    adj = defaultdict(list)
    radj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        radj[v].append(u)
    for u in list(adj):
        adj[u].sort()
    for u in list(radj):
        radj[u].sort()
    return source, target, edges, dict(adj), dict(radj)


def verify_path(source, target, edges, path):
    if not path or path[0] != source or path[-1] != target:
        return False
    edge_set = set(edges)
    return all((u, v) in edge_set for u, v in zip(path, path[1:]))


def reconstruct(parent, source, target):
    if target not in parent:
        return None
    path = [target]
    while path[-1] != source:
        prev = parent.get(path[-1])
        if prev is None:
            return None
        path.append(prev)
    path.reverse()
    return path


def bounded_recon(node, adj, limit=LOOKAHEAD_DEPTH):
    """Local reconnaissance only; it never reads the target or hidden metadata."""
    frontier = {node}
    seen = {node}
    probes = 0
    reached = 0
    for depth in range(1, limit + 1):
        nxt = set()
        for u in frontier:
            for v in adj.get(u, ()):
                probes += 1
                if v not in seen:
                    seen.add(v)
                    nxt.add(v)
        if not nxt:
            return depth - 1, len(seen), probes
        frontier = nxt
        reached = depth
    return reached, len(seen), probes


def data_atp_reference(source, target, edges, adj):
    """Data-ATP Ocean Reference 1.0.

    Frozen deterministic portfolio:
      8 reconnaissance selections : 1 breadth resurvey : 1 branching resurvey.
    Reconnaissance is bounded to six implication layers. Because this Ocean
    family is unary, Hilbert locality degenerates to one-dimensional canonical
    ordering; integer node order is therefore used only as a deterministic
    tie-break, not as a hidden-distance heuristic.
    """
    if source == target:
        return {"status": "PROVED", "path": [source], "expansions": 0,
                "scoring_edge_probes": 0, "discovered_states": 1}

    cache = {}
    scoring_probes = 0

    def recon_score(v):
        nonlocal scoring_probes
        if v not in cache:
            s, volume, probes = bounded_recon(v, adj)
            cache[v] = (s, volume)
            scoring_probes += probes
        return cache[v]

    parent = {source: None}
    depth = {source: 0}
    expanded = set()
    recon_q = []
    breadth_q = []
    resurvey_q = []
    serial = 0

    s, volume = recon_score(source)
    heapq.heappush(recon_q, (-s, -depth[source], -volume, source, serial))
    heapq.heappush(breadth_q, (depth[source], source, serial))
    heapq.heappush(resurvey_q, (-len(adj.get(source, ())), -depth[source], source, serial))

    cycle = ("recon",) * 8 + ("breadth", "resurvey")
    cycle_i = 0
    expansions = 0

    queues = {"recon": recon_q, "breadth": breadth_q, "resurvey": resurvey_q}

    def pop_live(name):
        q = queues[name]
        while q:
            item = heapq.heappop(q)
            u = item[-2]
            if u not in expanded:
                return u
        return None

    while expansions < MAX_EXPANSIONS:
        u = None
        for _ in range(len(cycle)):
            name = cycle[cycle_i % len(cycle)]
            cycle_i += 1
            u = pop_live(name)
            if u is not None:
                break
        if u is None:
            for name in ("recon", "breadth", "resurvey"):
                u = pop_live(name)
                if u is not None:
                    break
        if u is None:
            break

        expanded.add(u)
        for v in adj.get(u, ()):
            expansions += 1
            if v not in parent:
                parent[v] = u
                depth[v] = depth[u] + 1
                serial += 1
                if v == target:
                    path = reconstruct(parent, source, target)
                    return {
                        "status": "PROVED",
                        "path": path,
                        "expansions": expansions,
                        "scoring_edge_probes": scoring_probes,
                        "discovered_states": len(parent),
                    }

                sv, vol = recon_score(v)
                heapq.heappush(recon_q, (-sv, -depth[v], -vol, v, serial))
                heapq.heappush(breadth_q, (depth[v], v, serial))
                heapq.heappush(
                    resurvey_q,
                    (-len(adj.get(v, ())), -depth[v], v, serial),
                )
            if expansions >= MAX_EXPANSIONS:
                break

    return {
        "status": "BOUNDED_UNKNOWN",
        "path": None,
        "expansions": expansions,
        "scoring_edge_probes": scoring_probes,
        "discovered_states": len(parent),
    }


def data2_fast_reference(source, target, edges, adj, radj):
    """DATA 2.0.1 Ocean Reference 1.0 fast wing: transparent bidirectional BFS."""
    if source == target:
        return {"status": "PROVED", "path": [source], "expansions": 0}

    f_parent = {source: None}
    b_next = {target: None}
    f_front = {source}
    b_front = {target}
    expansions = 0
    forward_turn = True

    def build_path(meet):
        left = [meet]
        x = meet
        while f_parent[x] is not None:
            x = f_parent[x]
            left.append(x)
        left.reverse()

        right = []
        x = b_next[meet]
        while x is not None:
            right.append(x)
            x = b_next[x]
        return left + right

    while f_front and b_front and expansions < MAX_EXPANSIONS:
        if forward_turn:
            nxt = set()
            for u in sorted(f_front):
                for v in adj.get(u, ()):
                    expansions += 1
                    if v not in f_parent:
                        f_parent[v] = u
                        nxt.add(v)
                        if v in b_next:
                            return {"status": "PROVED", "path": build_path(v),
                                    "expansions": expansions}
                    if expansions >= MAX_EXPANSIONS:
                        break
                if expansions >= MAX_EXPANSIONS:
                    break
            f_front = nxt
        else:
            nxt = set()
            for u in sorted(b_front):
                for pred in radj.get(u, ()):
                    expansions += 1
                    if pred not in b_next:
                        b_next[pred] = u
                        nxt.add(pred)
                        if pred in f_parent:
                            return {"status": "PROVED", "path": build_path(pred),
                                    "expansions": expansions}
                    if expansions >= MAX_EXPANSIONS:
                        break
                if expansions >= MAX_EXPANSIONS:
                    break
            b_front = nxt
        forward_turn = not forward_turn

    return {"status": "BOUNDED_UNKNOWN", "path": None, "expansions": expansions}


def horizon_bfs(source, target, edges, adj):
    """Exact fewest-edge certifier for this finite unit-cost Ocean graph."""
    q = deque([source])
    parent = {source: None}
    expansions = 0
    if source == target:
        return {"status": "CERTIFIED_MINIMUM", "path": [source], "expansions": 0}
    while q and expansions < MAX_EXPANSIONS:
        u = q.popleft()
        for v in adj.get(u, ()):
            expansions += 1
            if v not in parent:
                parent[v] = u
                if v == target:
                    return {
                        "status": "CERTIFIED_MINIMUM",
                        "path": reconstruct(parent, source, target),
                        "expansions": expansions,
                    }
                q.append(v)
            if expansions >= MAX_EXPANSIONS:
                break
    return {"status": "BOUNDED_UNKNOWN", "path": None, "expansions": expansions}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solver", required=True,
                    choices=["data-atp", "data2-fast", "data2-certify"])
    ap.add_argument("--problem", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    problem = Path(args.problem)
    source, target, edges, adj, radj = parse_problem(problem)

    t0 = time.perf_counter()
    if args.solver == "data-atp":
        result = data_atp_reference(source, target, edges, adj)
        solver_name = "Data-ATP_Ocean_Reference_1.0"
    elif args.solver == "data2-fast":
        result = data2_fast_reference(source, target, edges, adj, radj)
        solver_name = "DATA_2.0.1_Ocean_Reference_1.0_fast"
    else:
        result = horizon_bfs(source, target, edges, adj)
        solver_name = "DATA_2.0.1_Ocean_Reference_1.0_Horizon"
    elapsed = time.perf_counter() - t0

    path = result.get("path")
    verified = bool(path is not None and verify_path(source, target, edges, path))
    if result["status"] in {"PROVED", "CERTIFIED_MINIMUM"} and not verified:
        result["status"] = "FAULT"

    result.update({
        "solver": solver_name,
        "problem": problem.name,
        "wall_s_internal": elapsed,
        "proof_length": (len(path) - 1) if verified else None,
        "certificate_verified": verified,
        "input_contract": "opaque_tptp_only",
        "hidden_Lstar_read": False,
    })

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
