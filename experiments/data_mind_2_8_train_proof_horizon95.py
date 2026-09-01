#!/usr/bin/env python3
"""Train the DATA-MIND 2.8 learned proof horizon on the exact 95% cohort.

This does NOT resample or redefine the education corpus.  The theorem labels
used for learning are recovered from the frozen DATA-MIND 2.6 ranker95.json
and independently reconstructed with the original leakage sanitizer.  The two
sets must agree exactly before fitting proceeds.

The learned object is a state-value heuristic, not a premise selector.  It
learns reusable proof-shape classes from verified Metamath theorem statements.
For a live goal, an alpha-equivalent theorem already present in the studied
library has remaining search cost 1 (one legal theorem application).  For an
unseen goal, the horizon backs off to progressively coarser proof-shape motifs
whose costs are learned from the compiled logical dependency counts of studied
proofs.

No target proof is read by the learner.  The administrator may use target
metadata only to reconstruct and audit the same exclusion halo used in the
original 95% education run.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import statistics
import sys
from typing import Any


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def htext(x: str) -> str:
    return hashlib.sha256(x.encode("utf-8")).hexdigest()


def median_table(rows: dict[str, list[float]]) -> tuple[dict[str, float], dict[str, int]]:
    return (
        {k: float(statistics.median(v)) for k, v in rows.items()},
        {k: len(v) for k, v in rows.items()},
    )


def pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 3:
        return 0.0
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    vx = sum(x*x for x in dx)
    vy = sum(y*y for y in dy)
    if vx <= 1e-18 or vy <= 1e-18:
        return 0.0
    return sum(a*b for a, b in zip(dx, dy)) / math.sqrt(vx*vy)


def canonical_tree_hash(tree, mode: str) -> str:
    """Alpha-invariant tree hash.

    exact: retain every syntax-rule label.
    skeleton: abstract only nullary constants by type, retaining operators.
    shape: retain only node type/arity plus variable identity pattern.
    """
    seen: dict[tuple[str, str], int] = {}
    next_by_type: defaultdict[str, int] = defaultdict(int)

    def rec(t) -> str:
        tc = str(t.typecode)
        if t.var is not None:
            key = (tc, str(t.var))
            if key not in seen:
                seen[key] = next_by_type[tc]
                next_by_type[tc] += 1
            return f"V:{tc}:{seen[key]}"
        kids = [rec(k) for k in t.kids]
        if mode == "exact":
            head = f"L:{t.label}:{tc}:{len(kids)}"
        elif mode == "skeleton":
            head = (f"C:{tc}:0" if not kids else f"L:{t.label}:{tc}:{len(kids)}")
        elif mode == "shape":
            head = f"N:{tc}:{len(kids)}"
        else:
            raise ValueError(mode)
        return head + "[" + "|".join(kids) + "]"

    return htext(rec(tree))


def logical_dependency_cost(full, nd) -> float:
    """Target for the compiled proof-horizon motif.

    Earlier proved theorems are callable as one-step derived rules in the exam
    environment.  We therefore count only referenced logical assertions and
    compress the count logarithmically so the heuristic remains on a search-
    action scale rather than exploding with proof-script length.
    """
    refs = {
        p for p in nd.premises
        if p in full.nodes and full.nodes[p].statement.split()[:1] == ["|-"]
    }
    return 1.0 + math.log2(1.0 + len(refs))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--ml-sic", required=True)
    ap.add_argument("--sanitizer", required=True)
    ap.add_argument("--atp-root", required=True)
    ap.add_argument("--old-ranker", required=True)
    ap.add_argument("--target", default="sgrpcl")
    ap.add_argument("--fraction", type=float, default=0.95)
    ap.add_argument("--seed", type=int, default=2301)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    db = Path(args.db).resolve()
    atp_root = Path(args.atp_root).resolve()
    old_ranker_path = Path(args.old_ranker).resolve()
    old_ranker_raw = old_ranker_path.read_bytes()
    old_ranker_sha = hashlib.sha256(old_ranker_raw).hexdigest()
    old_ranker = json.loads(old_ranker_raw)

    if old_ranker.get("architecture_version") != "2.6":
        raise SystemExit("old checkpoint is not the frozen DATA-MIND 2.6 education")
    if old_ranker.get("target") != args.target:
        raise SystemExit("old checkpoint target mismatch")
    if old_ranker.get("learner_target_statement_exposed") is not False:
        raise SystemExit("old checkpoint says target statement was exposed")
    if old_ranker.get("learner_target_proof_exposed") is not False:
        raise SystemExit("old checkpoint says target proof was exposed")

    MLSIC = load_module("dm28_mlsic", Path(args.ml_sic).resolve())
    SAN = load_module("dm28_sanitizer", Path(args.sanitizer).resolve())

    print("[1/6] parse pinned set.mm theorem graph", flush=True)
    full = MLSIC.parse_metamath(str(db), limit=None)
    if args.target not in full.nodes:
        raise SystemExit("target not found")

    # Reconstruct the original sanitizer split exactly, then require agreement
    # with theorem labels carried by the frozen ranker checkpoint.
    print("[2/6] reconstruct and verify exact 95% cohort", flush=True)
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
    n_train = max(1, min(len(admissible)-1, int(math.floor(args.fraction*len(admissible)))))
    train = admissible[:n_train]
    holdout = admissible[n_train:]
    train_names = {nd.name for nd in train}
    ranker_names = {
        n for n in old_ranker.get("order", {})
        if n in full.nodes and full.nodes[n].kind == "theorem"
    }
    if train_names != ranker_names:
        only_new = sorted(train_names-ranker_names)[:10]
        only_old = sorted(ranker_names-train_names)[:10]
        raise RuntimeError(f"95% cohort drift: reconstructed-only={only_new}, checkpoint-only={only_old}")
    if args.target in train_names:
        raise RuntimeError("target leaked into exact 95% cohort")
    cohort_sha = htext("\n".join(nd.name for nd in train))
    print(f"    studied={len(train):,}; holdout={len(holdout):,}; excluded={len(excluded):,}", flush=True)

    print("[3/6] build grammar and proof-shape signatures", flush=True)
    sys.path.insert(0, str(atp_root))
    import metamath
    import setmm_grammar as G
    import predator_fast_parse as PFP
    mm = metamath.load(str(db), say=lambda _s: None)
    by_tc = G.build_grammar(mm)
    PFP.install(G)

    exact_hashes: set[str] = set()
    skeleton_rows: dict[str, list[float]] = defaultdict(list)
    shape_rows: dict[str, list[float]] = defaultdict(list)
    parse_fail_train = 0
    train_costs: list[float] = []

    def parse_theorem(nd):
        toks = nd.statement.split()
        if not toks or toks[0] != "|-":
            return None
        return G.parse(toks[1:], "wff", by_tc)

    for i, nd in enumerate(train, 1):
        tree = parse_theorem(nd)
        if tree is None:
            parse_fail_train += 1
            continue
        cost = logical_dependency_cost(full, nd)
        train_costs.append(cost)
        eh = canonical_tree_hash(tree, "exact")
        sh = canonical_tree_hash(tree, "skeleton")
        gh = canonical_tree_hash(tree, "shape")
        exact_hashes.add(eh)
        skeleton_rows[sh].append(cost)
        shape_rows[gh].append(cost)
        if i % 5000 == 0:
            print(f"    signed {i:,}/{len(train):,}", flush=True)

    if len(train_costs) < 0.95*len(train):
        raise RuntimeError(f"proof-shape parse coverage too low: {len(train_costs)}/{len(train)}")
    skeleton_cost, skeleton_count = median_table(skeleton_rows)
    shape_cost, shape_count = median_table(shape_rows)
    global_cost = float(statistics.median(train_costs))

    print("[4/6] validate learned horizon on untouched clean 5% holdout", flush=True)
    y_true: list[float] = []
    y_pred: list[float] = []
    source_counts = defaultdict(int)
    parse_fail_holdout = 0
    for nd in holdout:
        tree = parse_theorem(nd)
        if tree is None:
            parse_fail_holdout += 1
            continue
        eh = canonical_tree_hash(tree, "exact")
        sh = canonical_tree_hash(tree, "skeleton")
        gh = canonical_tree_hash(tree, "shape")
        if eh in exact_hashes:
            pred, src = 1.0, "exact_studied_theorem"
        elif sh in skeleton_cost:
            pred, src = skeleton_cost[sh], "skeleton_motif"
        elif gh in shape_cost:
            pred, src = shape_cost[gh], "shape_motif"
        else:
            pred, src = global_cost, "global_median"
        y_true.append(logical_dependency_cost(full, nd))
        y_pred.append(float(pred))
        source_counts[src] += 1

    mae = sum(abs(a-b) for a,b in zip(y_true,y_pred))/max(1,len(y_true))
    rmse = math.sqrt(sum((a-b)**2 for a,b in zip(y_true,y_pred))/max(1,len(y_true)))
    corr = pearson(y_true,y_pred)

    print("[5/6] freeze learned proof horizon", flush=True)
    model: dict[str, Any] = {
        "architecture_version": "2.8",
        "artifact_type": "learned_proof_horizon_same_95pct_cohort",
        "changes_solver_architecture": True,
        "single_architecture_change": "replace hand-written open-goal settlement distance with corpus-learned additive proof horizon",
        "target": args.target,
        "training_fraction_of_target_clean_corpus": args.fraction,
        "seed": args.seed,
        "source_ranker_architecture": "2.6",
        "source_ranker_file_sha256": old_ranker_sha,
        "training_cohort_sha256": cohort_sha,
        "studied_theorems": len(train),
        "holdout_theorems": len(holdout),
        "excluded_halo": len(excluded),
        "learner_target_statement_exposed": False,
        "learner_target_proof_exposed": False,
        "administrator_target_metadata_used_only_to_reconstruct_original_sanitizer": True,
        "goal_cost_semantics": "estimated remaining legal search actions; exact studied theorem = 1; unseen goals back off to learned proof-shape motif cost",
        "state_horizon_semantics": "sum of learned per-goal costs",
        "motif_training_target": "1 + log2(1 + distinct referenced logical assertions in verified compiled proof)",
        "canonicalization": {
            "exact": "alpha-normalized syntax-rule tree",
            "skeleton": "exact operator tree with nullary constants abstracted by type",
            "shape": "type-and-arity tree with alpha-normalized variables",
        },
        "exact_studied_goal_hashes": sorted(exact_hashes),
        "skeleton_cost": skeleton_cost,
        "skeleton_count": skeleton_count,
        "shape_cost": shape_cost,
        "shape_count": shape_count,
        "global_median_cost": global_cost,
        "training_parse_failures": parse_fail_train,
        "validation": {
            "theorems_scored": len(y_true),
            "parse_failures": parse_fail_holdout,
            "mae": mae,
            "rmse": rmse,
            "pearson": corr,
            "prediction_sources": dict(source_counts),
        },
    }
    canonical = json.dumps(model, sort_keys=True, separators=(",", ":"))
    model_sha = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    (out/"proof_horizon95.json").write_text(json.dumps(model, indent=2, sort_keys=True)+"\n", encoding="utf-8")

    result = {
        "status": "TRAINING_COMPLETE",
        "architecture_version": "2.8",
        "architecture_changed": True,
        "single_change": model["single_architecture_change"],
        "target": args.target,
        "same_95pct_cohort_as_ranker26": True,
        "training_cohort_sha256": cohort_sha,
        "studied_theorems": len(train),
        "holdout_theorems": len(holdout),
        "excluded_halo": len(excluded),
        "learner_target_statement_exposed": False,
        "learner_target_proof_exposed": False,
        "proof_horizon_model_sha256": model_sha,
        "validation": model["validation"],
        "global_median_cost": global_cost,
    }
    (out/"result.json").write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    (out/"TRAINING_COMPLETE").write_text(model_sha+"\n", encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)
    print("[6/6] TRAINING_COMPLETE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
