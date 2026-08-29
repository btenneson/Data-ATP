#!/usr/bin/env python3
"""Runtime calibration for the generic DATA-MIND Ocean search core.

Uses the frozen Data-ATP Ocean reference search policy as the common generic
search core, with a larger expansion budget only so timing rather than the old
5M reference cap determines the calibration point.  This script does NOT use
Depths-F, the planted route, L*, or generator metadata while searching.
"""
from __future__ import annotations
import argparse, importlib.util, json, time
from pathlib import Path


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("ocean_ref", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Ocean reference solver")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--problem", required=True)
    ap.add_argument("--reference", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-expansions", type=int, default=100_000_000)
    a = ap.parse_args()

    mod = load_module(Path(a.reference))
    mod.MAX_EXPANSIONS = int(a.max_expansions)
    source, target, edges, adj, _ = mod.parse_problem(Path(a.problem))

    t0 = time.perf_counter()
    result = mod.data_atp_reference(source, target, edges, adj)
    search_wall = time.perf_counter() - t0
    path = result.get("path")

    t1 = time.perf_counter()
    verified = bool(path is not None and mod.verify_path(source, target, edges, path))
    verify_wall = time.perf_counter() - t1

    out = {
        "status": result.get("status"),
        "certificate_verified": verified,
        "proof_length": len(path)-1 if verified else None,
        "expansions": result.get("expansions"),
        "scoring_edge_probes": result.get("scoring_edge_probes"),
        "discovered_states": result.get("discovered_states"),
        "search_wall_s": search_wall,
        "verify_wall_s": verify_wall,
        "max_expansions": int(a.max_expansions),
        "search_core": "frozen Data-ATP Ocean Reference 1.0 policy; enlarged resource cap",
        "hidden_metadata_read": False,
    }
    Path(a.out).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2), flush=True)
    if result.get("status") == "PROVED" and not verified:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
