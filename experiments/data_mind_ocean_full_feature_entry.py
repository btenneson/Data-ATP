#!/usr/bin/env python3
"""Memory-safe/deterministic entrypoint for data_mind_ocean_full_feature.py.

Registers dynamically loaded modules in sys.modules (needed by dataclasses in
Predator 8.038) and discards the reverse adjacency returned by the frozen R01
parser because this DATA-MIND search does not use it.  The positive input and
forward graph are otherwise unchanged.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
TARGET = HERE / "data_mind_ocean_full_feature.py"

spec = importlib.util.spec_from_file_location("data_mind_ocean_full_feature_impl", TARGET)
if spec is None or spec.loader is None:
    raise SystemExit(f"cannot load {TARGET}")
M = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = M
spec.loader.exec_module(M)


def fixed_load_module(name: str, path: Path):
    spec2 = importlib.util.spec_from_file_location(name, path)
    if spec2 is None or spec2.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec2)
    sys.modules[name] = mod
    spec2.loader.exec_module(mod)

    if name.startswith("ocean_reference"):
        original = mod.parse_problem

        def parse_forward_only(problem_path):
            source, target, edges, adj, radj = original(problem_path)
            # DATA-MIND uses only the forward graph in this experiment.
            # Drop reverse adjacency before returning to preserve RAM headroom.
            del radj
            return source, target, edges, adj, None

        mod.parse_problem = parse_forward_only
    return mod


M.load_module = fixed_load_module

if __name__ == "__main__":
    M.main()
