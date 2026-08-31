#!/usr/bin/env python3
"""DATA-MIND 2.7: 95%-educated TPTP held-out pilot with proof-density-inspired objective.

This experiment changes the controller objective, so it is architecture 2.7.
The objective uses measurable surrogates inspired by the proof-density paper:
  q_proxy        -> training-derived symbol-structure relevance,
  repair_proxy   -> exp(- predicted log-cost / h),
  density_proxy  -> empirical strategy success rate on the 95% education set.
The binary E/TPTP proof verdict remains the hard settlement gate.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import random
import re
import time

import numpy as np

import data_mind_2_6_tptp95_pilot as base

# Correct the escaped regular expressions in the 2.6 external adapter.
base.FOF_RE = re.compile(r"^[A-Z]{3}\d{3}\+\d+(?:\.\d+)?\.p$")
base.STATUS_RE = re.compile(r"(?mi)^%\s*Status\s*:\s*([A-Za-z]+)")
base.ABSTRACT_RE = re.compile(r"^([A-Z]{3}\d{3})")

ARCH = "2.7"
WEIGHTS = {"q_proxy": 0.20, "repair_proxy": 0.35, "density_proxy": 0.45}
H = 1.0


def rewrite_json(path: Path, mutate):
    obj = json.loads(path.read_text(encoding="utf-8"))
    mutate(obj)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")
    return obj


def choose_random_target(root: Path, domain: str, seed: int) -> str:
    domain_dir = root / "Problems" / domain
    paths = sorted(p for p in domain_dir.glob("*.p") if base.eligible_problem(p))
    if len(paths) < 20:
        raise SystemExit(f"eligible FOF Theorem universe unexpectedly small: {len(paths)}")
    rng = random.Random(seed ^ 0xD27A)
    return rng.choice(paths).name


def train(args) -> int:
    root = Path(args.tptp_root)
    target = choose_random_target(root, args.domain, args.seed)
    args.target = target
    print(f"random_heldout_target={target}", flush=True)

    rc = base.train(args)
    out = Path(args.out)

    records = json.loads((out / "education_records.json").read_text(encoding="utf-8"))
    counts = {}
    for strategy in base.STRATEGIES:
        runs = [r for rec in records for r in rec.get("runs", []) if r.get("strategy") == strategy]
        if runs:
            counts[strategy] = {
                "n": len(runs),
                "successes": sum(bool(r.get("success")) for r in runs),
                "success_rate": sum(bool(r.get("success")) for r in runs) / len(runs),
            }

    def patch_manifest(m):
        m["architecture_version"] = ARCH
        m["architecture_changed"] = True
        m["architecture_change"] = "proof-density-inspired settlement-progress objective"
        m["target_selection"] = "uniform random eligible FOF Theorem target, forced into held-out set"
        m["objective_surrogates"] = ["q_proxy", "repair_proxy", "density_proxy"]
        m["objective_weights"] = WEIGHTS

    manifest = rewrite_json(out / "split_manifest.json", patch_manifest)

    def patch_model(m):
        m["architecture_version"] = ARCH
        m["changes_solver_architecture"] = True
        m["architecture_change"] = "controller objective changed from predicted-cost ordering to settlement-progress objective"
        m["objective"] = {
            "formula": "J=0.20*q_proxy+0.35*repair_proxy+0.45*density_proxy",
            "paper_terms_are_surrogates_not_exact_q_H_rho": True,
            "h": H,
            "weights": WEIGHTS,
            "strategy_training_density": counts,
            "binary_verifier_remains_hard_gate": True,
        }

    model = rewrite_json(out / "tptp95_policy.json", patch_model)

    def patch_result(r):
        r["architecture_version"] = ARCH
        r["architecture_changed"] = True
        r["random_heldout_target"] = target
        r["objective_weights"] = WEIGHTS
        r["strategy_training_density"] = counts

    result = rewrite_json(out / "result.json", patch_result)
    print(json.dumps({
        "architecture_version": ARCH,
        "random_heldout_target": target,
        "training_count": manifest["training_count"],
        "holdout_count": manifest["holdout_count"],
        "actual_training_fraction": manifest["actual_training_fraction"],
        "strategy_training_density": counts,
        "objective": model["objective"],
    }, indent=2, sort_keys=True), flush=True)
    return rc


def logistic(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def q_proxy_for_target(text: str, model: dict) -> float:
    csy, background = base.problem_roles(text)
    vals = []
    for _, _, sy in background:
        if sy:
            vals.append(logistic(base.symbol_score(model, csy, sy)))
    return float(sum(vals) / len(vals)) if vals else 0.0


def objective_table(text: str, model: dict):
    feat = base.feature_vector(text)
    q = q_proxy_for_target(text, model)
    density_info = model["objective"]["strategy_training_density"]
    rows = []
    for strategy in model["supported_strategies"]:
        predicted_log_cost = base.score_model(model, feat, strategy)
        repair = math.exp(-max(0.0, predicted_log_cost) / H)
        density = float(density_info.get(strategy, {}).get("success_rate", 0.0))
        J = WEIGHTS["q_proxy"] * q + WEIGHTS["repair_proxy"] * repair + WEIGHTS["density_proxy"] * density
        rows.append({
            "strategy": strategy,
            "q_proxy": q,
            "repair_proxy": repair,
            "density_proxy": density,
            "predicted_log_cost": predicted_log_cost,
            "objective_J": J,
        })
    rows.sort(key=lambda r: (-r["objective_J"], r["predicted_log_cost"], r["strategy"]))
    return rows


def examine(args) -> int:
    root = Path(args.tptp_root)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    model = json.loads(Path(args.policy).read_text(encoding="utf-8"))
    target = model["target"]
    original = root / "Problems" / args.domain / target
    if not original.exists():
        raise SystemExit(f"target missing: {original}")
    text = original.read_text(encoding="utf-8", errors="replace")

    problem = out / f"{target}.objective-reordered.p"
    problem.write_text(base.reorder_target(text, model), encoding="utf-8")
    table = objective_table(text, model)
    (out / "objective_table.json").write_text(json.dumps(table, indent=2, sort_keys=True), encoding="utf-8")

    ranked = [r["strategy"] for r in table]
    # Preserve exploration but let the new objective control priority and budget.
    shares = [0.50, 0.30, 0.20]
    allocations = []
    remaining_budget = args.total_seconds
    for i, strategy in enumerate(ranked[:3]):
        if i == len(ranked[:3]) - 1:
            sec = remaining_budget
        else:
            sec = max(1, int(args.total_seconds * shares[i]))
            sec = min(sec, remaining_budget)
        allocations.append((strategy, sec))
        remaining_budget -= sec

    runs = []
    settled = None
    proof_path = None
    t0 = time.perf_counter()
    for strategy, planned in allocations:
        remaining = args.total_seconds - int(time.perf_counter() - t0)
        if remaining <= 0:
            break
        seconds = min(planned, remaining)
        result = base.run_e(problem, strategy, seconds, root)
        raw = result.pop("output")
        log_path = out / f"e_{strategy}.log"
        log_path.write_text(raw, encoding="utf-8")
        result["allocated_seconds"] = seconds
        result["objective"] = next(r for r in table if r["strategy"] == strategy)
        result["ternary_credit"] = 1 if result["success"] else 0
        runs.append(result)
        if result["success"]:
            settled = result
            proof_path = log_path.name
            break

    elapsed = time.perf_counter() - t0
    result = {
        "status": "SETTLED" if settled else "UNSETTLED_WITHIN_BUDGET",
        "architecture_version": ARCH,
        "architecture_changed": True,
        "architecture_change": "proof-density-inspired settlement-progress objective",
        "arm": "educated95_objective",
        "educated": True,
        "target": target,
        "target_selected_randomly_before_education": True,
        "target_seen_during_education": False,
        "same_abstract_problem_variants_seen_during_education": False,
        "objective_formula": "J=0.20*q_proxy+0.35*repair_proxy+0.45*density_proxy",
        "paper_terms_are_surrogates_not_exact_q_H_rho": True,
        "objective_table": table,
        "strategy_order": ranked,
        "planned_allocations": allocations,
        "total_budget_seconds": args.total_seconds,
        "elapsed_seconds": elapsed,
        "settled_strategy": settled["strategy"] if settled else None,
        "settled_szs_status": settled["status"] if settled else None,
        "proof_log": proof_path,
        "runs": runs,
    }
    (out / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True), flush=True)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="mode", required=True)

    tp = sub.add_parser("train")
    tp.add_argument("--tptp-root", required=True)
    tp.add_argument("--domain", default="GRP")
    tp.add_argument("--target", default="AUTO")
    tp.add_argument("--tptp-version", default="9.3.1")
    tp.add_argument("--fraction", type=float, default=0.95)
    tp.add_argument("--seed", type=int, default=314159)
    tp.add_argument("--train-seconds", type=int, default=1)
    tp.add_argument("--out", required=True)
    tp.set_defaults(func=train)

    ep = sub.add_parser("examine")
    ep.add_argument("--tptp-root", required=True)
    ep.add_argument("--domain", default="GRP")
    ep.add_argument("--policy", required=True)
    ep.add_argument("--total-seconds", type=int, default=21600)
    ep.add_argument("--out", required=True)
    ep.set_defaults(func=examine)

    args = ap.parse_args()
    if hasattr(args, "fraction") and not (0.0 < args.fraction < 1.0):
        raise SystemExit("fraction must be between 0 and 1")
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
