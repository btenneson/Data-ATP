#!/usr/bin/env python3
"""Leakage-controlled 95% set.mm pretraining for DATA-MIND 2.6.

This is an external education phase, not a new solver architecture. It uses
ML-SIC theorem-graph/premise-learning machinery and freezes a policy for the
rank-scoring interface already present in the pinned Predator kernel.

The target is visible only to the experiment administrator that constructs the
exclusion halo. Its statement, proof, downstream dependents, close syntactic
proxies, and every theorem downstream of those proxies are excluded before any
training pair is constructed.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import random
import time

import numpy as np


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("dm26_mlsic_pretrain", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import ML-SIC module from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def norm_statement(s: str) -> str:
    return " ".join(s.split())


def token_multiset_signature(s: str):
    return tuple(sorted(Counter(norm_statement(s).split()).items()))


def top_level_converse(s: str):
    """Swap the two sides of a top-level Metamath implication, if present."""
    toks = norm_statement(s).split()
    if toks and toks[0] == "|-":
        prefix, body = ["|-"], toks[1:]
    else:
        prefix, body = [], toks
    if len(body) >= 5 and body[0] == "(" and body[-1] == ")":
        inner = body[1:-1]
    else:
        inner = body
    depth = 0
    split = None
    for i, tok in enumerate(inner):
        if tok == "(":
            depth += 1
        elif tok == ")":
            depth -= 1
        elif tok == "->" and depth == 0:
            split = i
            break
    if split is None:
        return None
    a, b = inner[:split], inner[split + 1:]
    if not a or not b:
        return None
    return " ".join(prefix + ["("] + b + ["->"] + a + [")"])


def jaccard_tokens(a: str, b: str) -> float:
    aa, bb = set(a.split()), set(b.split())
    return len(aa & bb) / max(1, len(aa | bb))


def descendants(g, seeds: set[str]) -> set[str]:
    out = set(seeds)
    q = deque(seeds)
    while q:
        x = q.popleft()
        for y in g.out.get(x, ()):
            if y not in out:
                out.add(y)
                q.append(y)
    return out


def clone_node(MLSIC, nd, allowed: set[str]):
    x = MLSIC.Node(
        nd.name,
        nd.kind,
        nd.statement,
        [p for p in nd.premises if p in allowed],
        nd.rule,
        nd.order,
    )
    x.proof_steps = nd.proof_steps
    return x


def make_train_graph(MLSIC, full, allowed: set[str]):
    g = MLSIC.TheoremGraph()
    for nd in sorted(full.nodes.values(), key=lambda z: z.order):
        if nd.name in allowed:
            g.add(clone_node(MLSIC, nd, allowed))
    return g


def fit_pairs(MLSIC, g, train_theorems, negatives: int, seed: int, epochs: int):
    rng = random.Random(seed)
    ordered = sorted(g.nodes.values(), key=lambda nd: nd.order)
    positions = {nd.name: i for i, nd in enumerate(ordered)}
    usage = defaultdict(int)
    for nd in train_theorems:
        for p in nd.premises:
            if p in g.nodes:
                usage[p] += 1
    depth = g.closure_depth()

    X = []
    y = []
    positives = 0
    negatives_count = 0

    for tgt in train_theorems:
        i = positions[tgt.name]
        gold = {p for p in tgt.premises if p in g.nodes}
        if not gold:
            continue
        for p in sorted(gold):
            X.append(MLSIC.featurise(g, tgt, g.nodes[p], usage, depth))
            y.append(1)
            positives += 1

        if i <= 1:
            continue
        seen = set()
        tries = 0
        want = min(negatives, max(0, i - len(gold)))
        while len(seen) < want and tries < max(64, 12 * want):
            tries += 1
            cand = ordered[rng.randrange(i)]
            if cand.name in gold or cand.name in seen:
                continue
            seen.add(cand.name)
            X.append(MLSIC.featurise(g, tgt, cand, usage, depth))
            y.append(0)
            negatives_count += 1

    if not X or positives == 0:
        raise RuntimeError("no premise-selection training pairs were generated")

    Xn = np.asarray(X, dtype=float)
    yn = np.asarray(y, dtype=float)
    w, mu, sigma = MLSIC.logistic_fit(
        Xn, yn, epochs=epochs, lr=0.5, l2=1e-4, seed=seed
    )
    return w, mu, sigma, dict(usage), depth, {
        "pairs": int(len(yn)),
        "positive_pairs": int(positives),
        "negative_pairs": int(negatives_count),
        "positive_fraction": float(yn.mean()),
    }


def validate_model(MLSIC, full, train_names: set[str], validation,
                   w, mu, sigma, usage, depth, seed: int, cap: int = 500):
    """Score unseen clean theorems using only studied theorem candidates."""
    rng = random.Random(seed + 991)
    train_nodes = [full.nodes[n] for n in train_names if n in full.nodes]
    train_nodes.sort(key=lambda nd: nd.order)
    train_by_name = {nd.name: nd for nd in train_nodes}
    recalls = {1: [], 5: [], 10: []}
    rr = []
    scored = 0

    class View:
        pass

    view = View()
    view.nodes = train_by_name

    for tgt in validation:
        gold = {p for p in tgt.premises if p in train_by_name}
        if not gold:
            continue
        prior = [x for x in train_nodes if x.order < tgt.order and x.name not in gold]
        if len(prior) > cap:
            prior = rng.sample(prior, cap)
        cands = prior + [train_by_name[p] for p in sorted(gold)]
        F = np.asarray(
            [MLSIC.featurise(view, tgt, cand, usage, depth) for cand in cands],
            dtype=float,
        )
        scores = ((F - mu) / sigma) @ w
        ranked = [cands[i].name for i in np.argsort(-scores)]
        for k in recalls:
            recalls[k].append(len(gold & set(ranked[:k])) / len(gold))
        first = next((i + 1 for i, name in enumerate(ranked) if name in gold), None)
        rr.append(1.0 / first if first else 0.0)
        scored += 1

    return {
        "validation_theorems_scored": scored,
        "recall_at": {
            str(k): (float(np.mean(v)) if v else None) for k, v in recalls.items()
        },
        "mrr": float(np.mean(rr)) if rr else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--ml-sic", required=True)
    ap.add_argument("--target", default="sgrpcl")
    ap.add_argument("--fraction", type=float, default=0.95)
    ap.add_argument("--near-clone-jaccard", type=float, default=0.90)
    ap.add_argument("--near-clone-length-ratio", type=float, default=0.80)
    ap.add_argument("--negatives", type=int, default=12)
    ap.add_argument("--epochs", type=int, default=160)
    ap.add_argument("--seed", type=int, default=2301)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    if not (0.0 < args.fraction < 1.0):
        raise SystemExit("--fraction must be strictly between 0 and 1")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    MLSIC = load_module(Path(args.ml_sic))

    print(f"[1/6] parsing pinned set.mm from {args.db}", flush=True)
    p0 = time.perf_counter()
    full = MLSIC.parse_metamath(args.db, limit=None)
    parse_seconds = time.perf_counter() - p0
    if args.target not in full.nodes:
        raise SystemExit(f"target {args.target!r} not found in parsed set.mm")
    target = full.nodes[args.target]
    target_stmt = norm_statement(target.statement)
    target_multiset = token_multiset_signature(target_stmt)

    print("[2/6] constructing target-exclusion halo", flush=True)
    s0 = time.perf_counter()
    exact = set()
    multiset_alias = set()
    converse = set()
    near_clone = set()
    conv = top_level_converse(target_stmt)
    target_len = len(target_stmt.split())

    for name, nd in full.nodes.items():
        if nd.kind != "theorem":
            continue
        ns = norm_statement(nd.statement)
        if ns == target_stmt:
            exact.add(name)
            continue
        if token_multiset_signature(ns) == target_multiset:
            multiset_alias.add(name)
            continue
        if conv is not None and ns == conv:
            converse.add(name)
            continue
        nlen = len(ns.split())
        ratio = min(nlen, target_len) / max(1, max(nlen, target_len))
        if ratio >= args.near_clone_length_ratio:
            if jaccard_tokens(ns, target_stmt) >= args.near_clone_jaccard:
                near_clone.add(name)

    proxy_seeds = {args.target} | exact | multiset_alias | converse | near_clone
    excluded = descendants(full, proxy_seeds)
    sanitize_seconds = time.perf_counter() - s0

    theorem_nodes = [
        nd for nd in sorted(full.nodes.values(), key=lambda z: z.order)
        if nd.kind == "theorem"
    ]
    admissible = [nd for nd in theorem_nodes if nd.name not in excluded]
    if len(admissible) < 2:
        raise RuntimeError("sanitizer left too few admissible theorem nodes")

    # Temporal 95% split. Metamath proofs cite only earlier labels, so the
    # studied prefix cannot reveal the benign 5% holdout through its proofs.
    n_train = max(1, min(len(admissible) - 1,
                         int(math.floor(args.fraction * len(admissible)))))
    train_theorems = admissible[:n_train]
    validation = admissible[n_train:]
    train_names = {nd.name for nd in train_theorems}

    # Axioms are the formal calculus, not target examples.
    axiom_names = {n for n, nd in full.nodes.items() if nd.kind == "axiom"}
    allowed = axiom_names | train_names

    # Strong leakage/proof-closure audit.
    halo_refs = []
    missing_refs = []
    for nd in train_theorems:
        for p in nd.premises:
            if p in excluded:
                halo_refs.append((nd.name, p))
            elif p in full.nodes and p not in allowed:
                missing_refs.append((nd.name, p))
    if halo_refs:
        raise RuntimeError(f"leakage audit failed: halo references {halo_refs[:10]}")
    if missing_refs:
        raise RuntimeError(
            "temporal training set is not proof-closed; examples "
            + repr(missing_refs[:10])
        )
    if args.target in train_names:
        raise RuntimeError("target leaked into training set")

    # The learner only receives this restricted graph. The administrator may
    # inspect target metadata for sanitization; the learner never receives T.
    train_graph = make_train_graph(MLSIC, full, allowed)
    learner_target_exposed = args.target in train_graph.nodes
    if learner_target_exposed:
        raise RuntimeError("target is present in learner graph")

    print(
        f"    full theorems={len(theorem_nodes):,}; excluded halo={len(excluded):,}; "
        f"admissible={len(admissible):,}; studied={len(train_theorems):,}; "
        f"holdout={len(validation):,}",
        flush=True,
    )

    print("[3/6] building and fitting premise-selection education", flush=True)
    f0 = time.perf_counter()
    w, mu, sigma, usage, depth, pair_stats = fit_pairs(
        MLSIC,
        train_graph,
        [train_graph.nodes[x.name] for x in train_theorems],
        args.negatives,
        args.seed,
        args.epochs,
    )
    fit_seconds = time.perf_counter() - f0

    print("[4/6] validating transfer on the clean 5% holdout", flush=True)
    v0 = time.perf_counter()
    validation_stats = validate_model(
        MLSIC, full, train_names, validation, w, mu, sigma,
        usage, depth, args.seed
    )
    validation_seconds = time.perf_counter() - v0

    print("[5/6] freezing learned policy and telemetry", flush=True)
    label_order = {n: int(nd.order) for n, nd in full.nodes.items() if n in allowed}
    model = {
        "architecture_version": "2.6",
        "artifact_type": "external_pretraining_for_existing_rank_interface",
        "changes_solver_architecture": False,
        "target": args.target,
        "training_fraction_of_target_clean_corpus": args.fraction,
        "feature_schema": [
            "bias",
            "goal_candidate_jaccard",
            "candidate_token_coverage",
            "log1p_training_usage",
            "candidate_closure_depth_div_10",
            "goal_candidate_order_gap_div_1000",
            "candidate_is_axiom",
            "candidate_unique_token_count_div_20",
        ],
        "weights": [float(x) for x in w],
        "mu": [float(x) for x in mu],
        "sigma": [float(x) for x in sigma],
        "usage": {k: int(v) for k, v in usage.items()},
        "depth": {
            k: (None if v == float("inf") else float(v))
            for k, v in depth.items()
        },
        "order": label_order,
        "target_order": int(target.order),
        "seed": args.seed,
        "learner_target_statement_exposed": False,
        "learner_target_proof_exposed": False,
        "administrator_target_metadata_used_for_sanitization": True,
    }
    model_text = json.dumps(model, sort_keys=True, separators=(",", ":"))
    model_sha = hashlib.sha256(model_text.encode("utf-8")).hexdigest()
    (out / "ranker95.json").write_text(
        json.dumps(model, indent=2, sort_keys=True), encoding="utf-8"
    )

    # Never write the target statement/proof into learner artifacts.
    exclusion_manifest = {
        "target": args.target,
        "target_statement_sha256": hashlib.sha256(target_stmt.encode()).hexdigest(),
        "target_order": int(target.order),
        "near_clone_jaccard_threshold": args.near_clone_jaccard,
        "near_clone_length_ratio_threshold": args.near_clone_length_ratio,
        "seed_categories": {
            "target_plus_exact": len({args.target} | exact),
            "multiset_alias": len(multiset_alias),
            "top_level_converse": len(converse),
            "near_clone": len(near_clone),
            "all_proxy_seeds": len(proxy_seeds),
        },
        "forward_transitive_exclusion_count": len(excluded),
        "training_halo_reference_violations": len(halo_refs),
        "training_missing_reference_violations": len(missing_refs),
        "target_in_training": args.target in train_names,
        "target_in_learner_graph": learner_target_exposed,
        "learner_target_statement_exposed": False,
        "learner_target_proof_exposed": False,
    }
    (out / "exclusion_audit.json").write_text(
        json.dumps(exclusion_manifest, indent=2, sort_keys=True), encoding="utf-8"
    )

    elapsed = time.perf_counter() - t0
    result = {
        "status": "TRAINING_COMPLETE",
        "architecture_version": "2.6",
        "architecture_changed": False,
        "education_protocol": "95% target-clean set.mm",
        "target": args.target,
        "full_nodes": len(full.nodes),
        "full_theorems": len(theorem_nodes),
        "excluded_halo": len(excluded),
        "admissible_target_clean_theorems": len(admissible),
        "studied_theorems": len(train_theorems),
        "holdout_theorems": len(validation),
        "actual_studied_fraction": len(train_theorems) / len(admissible),
        "training_pairs": pair_stats,
        "validation": validation_stats,
        "model_sha256": model_sha,
        "parse_seconds": parse_seconds,
        "sanitize_seconds": sanitize_seconds,
        "fit_seconds": fit_seconds,
        "validation_seconds": validation_seconds,
        "elapsed_seconds": elapsed,
        "theorems_per_second_overall": len(train_theorems) / max(elapsed, 1e-9),
        "leakage_audit_passed": (
            not halo_refs and not missing_refs and
            args.target not in train_names and not learner_target_exposed
        ),
        "correctness_spine_outside_optimizer": True,
        "rank_interface_already_present_in_pinned_predator": True,
    }
    (out / "result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    (out / "TRAINING_COMPLETE").write_text(model_sha + "\n", encoding="utf-8")

    print("[6/6] complete", flush=True)
    print(json.dumps(result, indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
