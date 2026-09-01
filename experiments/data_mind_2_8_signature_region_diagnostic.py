#!/usr/bin/env python3
"""Targeted diagnostic for the DATA-MIND 2.8 proof-shape signature stall.

Reconstructs the exact frozen 95% cohort, then evaluates a requested 1-based
cohort slice theorem-by-theorem.  A hard SIGALRM deadline covers the *entire*
per-theorem signature computation: parse, dependency cost, and all three
canonical hashes.  Each theorem is logged before and after computation so a
single pathological input cannot hide behind 5,000-item progress reports.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import resource
import signal
import sys
import time


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


class TheoremDeadline(Exception):
    pass


def _deadline_handler(_signum, _frame):
    raise TheoremDeadline()


def rss_kb() -> int:
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--ml-sic", required=True)
    ap.add_argument("--sanitizer", required=True)
    ap.add_argument("--atp-root", required=True)
    ap.add_argument("--old-ranker", required=True)
    ap.add_argument("--target", default="sgrpcl")
    ap.add_argument("--fraction", type=float, default=0.95)
    ap.add_argument("--start", type=int, default=30001, help="1-based inclusive cohort position")
    ap.add_argument("--end", type=int, default=35000, help="1-based inclusive cohort position")
    ap.add_argument("--timeout-s", type=float, default=30.0)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    if args.start < 1 or args.end < args.start:
        raise SystemExit("invalid start/end range")
    if args.timeout_s <= 0:
        raise SystemExit("--timeout-s must be positive")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    db = Path(args.db).resolve()
    atp_root = Path(args.atp_root).resolve()
    old_ranker = json.loads(Path(args.old_ranker).read_text())

    BASE = load_module("dm28_base_diag", Path(__file__).with_name("data_mind_2_8_train_proof_horizon95.py"))
    MLSIC = load_module("dm28_mlsic_diag", Path(args.ml_sic).resolve())
    SAN = load_module("dm28_sanitizer_diag", Path(args.sanitizer).resolve())

    print("[1/4] parse pinned set.mm theorem graph", flush=True)
    full = MLSIC.parse_metamath(str(db), limit=None)
    if args.target not in full.nodes:
        raise SystemExit("target not found")

    print("[2/4] reconstruct and verify exact frozen 95% cohort", flush=True)
    target = full.nodes[args.target]
    target_stmt = SAN.norm_statement(target.statement)
    target_multiset = SAN.token_multiset_signature(target_stmt)
    conv = SAN.top_level_converse(target_stmt)
    target_len = len(target_stmt.split())
    exact, multiset_alias, converse, near_clone = set(), set(), set(), set()
    for name, nd in full.nodes.items():
        if nd.kind != "theorem":
            continue
        ns = SAN.norm_statement(nd.statement)
        if ns == target_stmt:
            exact.add(name); continue
        if SAN.token_multiset_signature(ns) == target_multiset:
            multiset_alias.add(name); continue
        if conv is not None and ns == conv:
            converse.add(name); continue
        nlen = len(ns.split())
        ratio = min(nlen, target_len) / max(1, max(nlen, target_len))
        if ratio >= 0.80 and SAN.jaccard_tokens(ns, target_stmt) >= 0.90:
            near_clone.add(name)
    proxy = {args.target} | exact | multiset_alias | converse | near_clone
    excluded = SAN.descendants(full, proxy)
    theorem_nodes = [
        nd for nd in sorted(full.nodes.values(), key=lambda z: z.order)
        if nd.kind == "theorem"
    ]
    admissible = [nd for nd in theorem_nodes if nd.name not in excluded]
    n_train = max(1, min(len(admissible)-1, int(math.floor(args.fraction * len(admissible)))))
    train = admissible[:n_train]
    train_names = {nd.name for nd in train}
    ranker_names = {
        n for n in old_ranker.get("order", {})
        if n in full.nodes and full.nodes[n].kind == "theorem"
    }
    if train_names != ranker_names:
        raise RuntimeError("95% cohort drift relative to frozen ranker")
    if args.end > len(train):
        raise SystemExit(f"range ends at {args.end}, but cohort has only {len(train)} theorems")
    print(f"    verified studied={len(train):,}; testing positions {args.start:,}-{args.end:,}", flush=True)

    print("[3/4] build grammar", flush=True)
    sys.path.insert(0, str(atp_root))
    import metamath
    import setmm_grammar as G
    import predator_fast_parse as PFP
    mm = metamath.load(str(db), say=lambda _s: None)
    by_tc = G.build_grammar(mm)
    PFP.install(G)

    csv_path = out / "per_theorem.csv"
    jsonl_path = out / "per_theorem.jsonl"
    summary_path = out / "summary.json"
    fieldnames = [
        "position", "name", "status", "stage", "elapsed_s", "tokens",
        "logical_cost", "rss_before_kb", "rss_after_kb", "error"
    ]
    counts = {"ok": 0, "timeout": 0, "parse_none": 0, "error": 0}
    slowest: list[dict] = []
    timeouts: list[dict] = []

    prior_handler = signal.getsignal(signal.SIGALRM)
    signal.signal(signal.SIGALRM, _deadline_handler)
    try:
        with csv_path.open("w", newline="", encoding="utf-8") as cf, jsonl_path.open("w", encoding="utf-8") as jf:
            cw = csv.DictWriter(cf, fieldnames=fieldnames)
            cw.writeheader()
            for pos in range(args.start, args.end + 1):
                nd = train[pos - 1]
                toks = nd.statement.split()
                stage = "start"
                started = time.monotonic()
                before = rss_kb()
                print(f"[THEOREM-START] position={pos} name={nd.name} tokens={len(toks)} rss_kb={before}", flush=True)
                signal.setitimer(signal.ITIMER_REAL, args.timeout_s)
                status = "ok"
                err = ""
                logical_cost = ""
                try:
                    stage = "parse"
                    if not toks or toks[0] != "|-":
                        tree = None
                    else:
                        tree = G.parse(toks[1:], "wff", by_tc)
                    if tree is None:
                        status = "parse_none"
                    else:
                        stage = "dependency_cost"
                        logical_cost = BASE.logical_dependency_cost(full, nd)
                        stage = "exact_hash"
                        BASE.canonical_tree_hash(tree, "exact")
                        stage = "skeleton_hash"
                        BASE.canonical_tree_hash(tree, "skeleton")
                        stage = "shape_hash"
                        BASE.canonical_tree_hash(tree, "shape")
                        stage = "done"
                except TheoremDeadline:
                    status = "timeout"
                    err = f"hard timeout after {args.timeout_s:.3f}s"
                except Exception as exc:
                    status = "error"
                    err = f"{type(exc).__name__}: {exc}"
                finally:
                    signal.setitimer(signal.ITIMER_REAL, 0.0)

                elapsed = time.monotonic() - started
                after = rss_kb()
                row = {
                    "position": pos,
                    "name": nd.name,
                    "status": status,
                    "stage": stage,
                    "elapsed_s": f"{elapsed:.6f}",
                    "tokens": len(toks),
                    "logical_cost": logical_cost,
                    "rss_before_kb": before,
                    "rss_after_kb": after,
                    "error": err,
                }
                cw.writerow(row); cf.flush()
                jf.write(json.dumps(row, sort_keys=True) + "\n"); jf.flush()
                counts[status] += 1
                rec = {"position": pos, "name": nd.name, "elapsed_s": elapsed, "stage": stage, "status": status}
                slowest.append(rec)
                slowest = sorted(slowest, key=lambda r: r["elapsed_s"], reverse=True)[:25]
                if status == "timeout":
                    timeouts.append(rec)
                print(
                    f"[THEOREM-END] position={pos} name={nd.name} status={status} "
                    f"stage={stage} elapsed_s={elapsed:.6f} rss_kb={after}",
                    flush=True,
                )
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0.0)
        signal.signal(signal.SIGALRM, prior_handler)

    summary = {
        "status": "DIAGNOSTIC_COMPLETE",
        "architecture_version": "2.8",
        "changes_solver_architecture": False,
        "diagnostic_only": True,
        "frozen_95pct_cohort_verified": True,
        "range_1_based_inclusive": [args.start, args.end],
        "per_theorem_timeout_s": args.timeout_s,
        "counts": counts,
        "timeouts": timeouts,
        "slowest_25": slowest,
        "interpretation": (
            "Any timeout identifies a theorem whose full signature computation exceeds the hard per-theorem deadline. "
            "If no theorem times out but elapsed time or RSS rises systematically, investigate cumulative state/resource growth."
        ),
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("[4/4] DIAGNOSTIC_COMPLETE", flush=True)
    print(json.dumps(summary, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
