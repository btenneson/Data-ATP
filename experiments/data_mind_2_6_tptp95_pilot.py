#!/usr/bin/env python3
"""DATA-MIND 2.6 TPTP 95%-education held-out pilot.

This is an external TPTP education/backend adapter for the existing DATA-MIND
2.6 architecture.  It does not share checkpoints, BANK contents, or learned
state with the Metamath/sgrpcl experiment.

Protocol:
* Work in one declared TPTP universe (FOF Theorem problems in one domain).
* Force the selected target into the held-out 5%.
* Remove every same-abstract-problem variant from education as a leakage halo.
* Randomly choose the remainder of the held-out 5% with a frozen seed.
* Learn only from the 95% education problems.
* Freeze a strategy-selection and symbol-association policy.
* Examine the target with the frozen policy and compare to an uneducated arm.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import random
import re
import subprocess
import time
from typing import Iterable

import numpy as np

FOF_RE = re.compile(r"^[A-Z]{3}\d{3}\+\d+(?:\.\d+)?\.p$")
STATUS_RE = re.compile(r"(?mi)^%\s*Status\s*:\s*([A-Za-z]+)")
ABSTRACT_RE = re.compile(r"^([A-Z]{3}\d{3})")
RESERVED = {
    "fof", "cnf", "tff", "thf", "include", "axiom", "hypothesis",
    "definition", "assumption", "lemma", "theorem", "corollary",
    "conjecture", "negated_conjecture", "plain", "type", "unknown",
    "$true", "$false",
}
STRATEGIES = {
    "auto_schedule": ["--auto-schedule"],
    "auto": ["--auto"],
    "satauto": ["--satauto"],
}
BASELINE_ORDER = ["auto_schedule", "auto", "satauto"]


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def strip_comments(text: str) -> str:
    return "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("%"))


def split_units(text: str) -> list[str]:
    text = strip_comments(text)
    out: list[str] = []
    buf: list[str] = []
    depth = 0
    quote = None
    escaped = False
    for ch in text:
        buf.append(ch)
        if quote is not None:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                quote = None
            continue
        if ch in ("'", '"'):
            quote = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        elif ch == "." and depth == 0:
            unit = "".join(buf).strip()
            if unit:
                out.append(unit)
            buf = []
    tail = "".join(buf).strip()
    if tail:
        out.append(tail)
    return out


def split_top_level_commas(s: str, max_parts: int = 3) -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    depth = 0
    quote = None
    escaped = False
    for ch in s:
        if quote is not None:
            buf.append(ch)
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                quote = None
            continue
        if ch in ("'", '"'):
            quote = ch
            buf.append(ch)
        elif ch == "(":
            depth += 1
            buf.append(ch)
        elif ch == ")":
            depth -= 1
            buf.append(ch)
        elif ch == "," and depth == 0 and len(parts) < max_parts - 1:
            parts.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    parts.append("".join(buf).strip())
    return parts


def parse_fof_unit(unit: str):
    u = unit.strip()
    if not u.lower().startswith("fof(") or not u.endswith("."):
        return None
    core = u[4:-1].strip()
    if not core.endswith(")"):
        return None
    core = core[:-1]
    parts = split_top_level_commas(core, 3)
    if len(parts) != 3:
        return None
    return parts[0], parts[1].strip().lower(), parts[2]


def symbols(formula: str) -> set[str]:
    toks = set(re.findall(r"(?<![A-Za-z0-9_$])(\$?[a-z][A-Za-z0-9_]*)", formula))
    return {t for t in toks if t not in RESERVED}


def problem_roles(text: str):
    conjecture: set[str] = set()
    background: list[tuple[str, str, set[str]]] = []
    for unit in split_units(text):
        parsed = parse_fof_unit(unit)
        if parsed is None:
            continue
        name, role, formula = parsed
        sy = symbols(formula)
        if role == "conjecture":
            conjecture |= sy
        else:
            background.append((name, role, sy))
    return conjecture, background


def feature_vector(text: str) -> np.ndarray:
    clean = strip_comments(text)
    conjs, background = problem_roles(text)
    all_sy = set(conjs)
    for _, _, sy in background:
        all_sy |= sy
    counts = [
        len(clean), len(clean.split()), clean.lower().count("fof("), len(conjs),
        len(all_sy), clean.count("="), clean.count("!"), clean.count("?"),
        clean.count("&"), clean.count("|"), clean.count("=>"), clean.count("<=>"),
        clean.count("~"), clean.lower().count("include("), len(background),
    ]
    return np.asarray([1.0] + [math.log1p(float(x)) for x in counts], dtype=float)


def expected_status(text: str) -> str | None:
    match = STATUS_RE.search(text)
    return match.group(1) if match else None


def eligible_problem(path: Path) -> bool:
    if not FOF_RE.match(path.name):
        return False
    try:
        return expected_status(path.read_text(encoding="utf-8", errors="replace")) == "Theorem"
    except OSError:
        return False


def run_e(problem: Path, strategy: str, seconds: int, tptp_root: Path):
    cmd = [
        "eprover", *STRATEGIES[strategy], "--tptp3-format", "--proof-object",
        f"--cpu-limit={max(1, int(seconds))}", str(problem),
    ]
    env = os.environ.copy()
    env["TPTP"] = str(tptp_root.resolve())
    t0 = time.perf_counter()
    try:
        cp = subprocess.run(
            cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            env=env, timeout=max(3.0, float(seconds) + 5.0), check=False,
        )
        output = cp.stdout
        rc = cp.returncode
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        rc = 124
        timed_out = True
    elapsed = time.perf_counter() - t0
    match = re.search(r"(?mi)^#?\s*%?\s*SZS status\s+([A-Za-z]+)", output)
    if not match:
        match = re.search(r"(?mi)SZS status\s+([A-Za-z]+)", output)
    status = match.group(1) if match else None
    success = status in {"Theorem", "Unsatisfiable"}
    unsupported = bool(re.search(r"(?i)(usage error|unknown option|unrecognized option)", output))
    return {
        "strategy": strategy, "success": success, "status": status,
        "elapsed_seconds": elapsed, "returncode": rc, "timed_out": timed_out,
        "unsupported": unsupported, "output": output,
    }


def fit_ridge(X: np.ndarray, y: np.ndarray, l2: float = 1e-2):
    mu = X[:, 1:].mean(axis=0)
    sigma = X[:, 1:].std(axis=0)
    sigma[sigma < 1e-9] = 1.0
    Z = X.copy()
    Z[:, 1:] = (Z[:, 1:] - mu) / sigma
    reg = np.eye(Z.shape[1]) * l2
    reg[0, 0] = 0.0
    w = np.linalg.solve(Z.T @ Z + reg, Z.T @ y)
    return w, mu, sigma


def score_model(model: dict, feat: np.ndarray, strategy: str) -> float:
    sub = model["strategy_models"][strategy]
    z = feat.copy()
    mu = np.asarray(sub["mu"], dtype=float)
    sigma = np.asarray(sub["sigma"], dtype=float)
    z[1:] = (z[1:] - mu) / sigma
    return float(z @ np.asarray(sub["weights"], dtype=float))


def build_symbol_policy(training_paths: Iterable[Path]):
    n = 0
    c_count = Counter()
    a_count = Counter()
    pair = Counter()
    for path in training_paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        csy, background = problem_roles(text)
        asy = set()
        for _, _, sy in background:
            asy |= sy
        if not csy or not asy:
            continue
        n += 1
        for c in csy:
            c_count[c] += 1
        for a in asy:
            a_count[a] += 1
        for c in csy:
            for a in asy:
                pair[(c, a)] += 1
    assoc: dict[str, list[list[object]]] = {}
    alpha = 0.5
    for c in c_count:
        vals = []
        for a in a_count:
            k = pair.get((c, a), 0)
            score = math.log(((k + alpha) * max(1, n)) /
                             ((c_count[c] + alpha) * (a_count[a] + alpha)))
            if k:
                vals.append((a, score, k))
        vals.sort(key=lambda x: (-x[1], -x[2], x[0]))
        assoc[c] = [[a, float(score), int(k)] for a, score, k in vals[:64]]
    return {
        "training_problems_with_symbol_pairs": n,
        "conjecture_symbol_counts": dict(c_count),
        "background_symbol_counts": dict(a_count),
        "associations": assoc,
    }


def symbol_score(model: dict, conjecture_symbols: set[str], axiom_symbols: set[str]) -> float:
    assoc = model["symbol_policy"]["associations"]
    table = {c: {row[0]: float(row[1]) for row in assoc.get(c, [])}
             for c in conjecture_symbols}
    vals = [table[c][a] for c in conjecture_symbols for a in axiom_symbols
            if a in table.get(c, {})]
    return float(sum(vals) / len(vals)) if vals else 0.0


def reorder_target(text: str, model: dict) -> str:
    units = split_units(text)
    csy, _ = problem_roles(text)
    movable = []
    fixed = []
    for idx, unit in enumerate(units):
        parsed = parse_fof_unit(unit)
        if parsed is None:
            fixed.append((idx, unit))
            continue
        _, role, formula = parsed
        if role == "conjecture":
            fixed.append((idx, unit))
        else:
            movable.append((symbol_score(model, csy, symbols(formula)), idx, unit))
    movable.sort(key=lambda x: (-x[0], x[1]))
    prefix = [u for _, u in fixed if not (parse_fof_unit(u) and parse_fof_unit(u)[1] == "conjecture")]
    conjectures = [u for _, u in fixed if parse_fof_unit(u) and parse_fof_unit(u)[1] == "conjecture"]
    return "\n\n".join(prefix + [u for _, _, u in movable] + conjectures) + "\n"


def train(args) -> int:
    root = Path(args.tptp_root)
    domain_dir = root / "Problems" / args.domain
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    paths = sorted(path for path in domain_dir.glob("*.p") if eligible_problem(path))
    target = domain_dir / args.target
    if target not in paths:
        raise SystemExit(f"target {args.target} is not an eligible FOF Theorem problem in {domain_dir}")

    abstract_match = ABSTRACT_RE.match(args.target)
    if not abstract_match:
        raise SystemExit("cannot derive abstract-problem id from target")
    abstract_id = abstract_match.group(1)
    proxies = [path for path in paths if ABSTRACT_RE.match(path.name) and ABSTRACT_RE.match(path.name).group(1) == abstract_id]
    clean = [path for path in paths if path.name == args.target or path not in proxies]
    if len(clean) < 20:
        raise SystemExit("clean corpus is unexpectedly small")

    rng = random.Random(args.seed)
    others = [path for path in clean if path.name != args.target]
    rng.shuffle(others)
    n_holdout = max(1, int(round((1.0 - args.fraction) * len(clean))))
    n_holdout = max(1, min(len(clean) - 1, n_holdout))
    extra_holdout = others[:max(0, n_holdout - 1)]
    holdout = [target] + extra_holdout
    train_paths = others[max(0, n_holdout - 1):]
    rng.shuffle(train_paths)

    if target in train_paths:
        raise RuntimeError("target leaked into training set")
    if any(path in train_paths for path in proxies if path.name != args.target):
        raise RuntimeError("same-abstract-problem proxy leaked into training set")

    manifest = {
        "architecture_version": "2.6", "architecture_changed": False,
        "adapter": "TPTP_FOF_external_education_backend",
        "tptp_declared_version": args.tptp_version, "domain": args.domain,
        "universe": "FOF problems in domain with % Status : Theorem",
        "target": args.target, "target_abstract_problem": abstract_id,
        "seed": args.seed, "requested_training_fraction": args.fraction,
        "eligible_theorem_count_before_proxy_sanitization": len(paths),
        "proxy_halo": sorted(path.name for path in proxies if path.name != args.target),
        "clean_universe_count": len(clean), "training_count": len(train_paths),
        "holdout_count": len(holdout),
        "actual_training_fraction": len(train_paths) / len(clean),
        "training_files": sorted(path.name for path in train_paths),
        "holdout_files": sorted(path.name for path in holdout),
        "target_in_training": False, "same_abstract_problem_variants_in_training": False,
    }
    (out / "split_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    records = []
    features = {}
    valid_strategies = set(STRATEGIES)
    for i, path in enumerate(train_paths, 1):
        text = path.read_text(encoding="utf-8", errors="replace")
        features[path.name] = feature_vector(text)
        per = []
        for strategy in STRATEGIES:
            if strategy not in valid_strategies:
                continue
            result = run_e(path, strategy, args.train_seconds, root)
            if result["unsupported"]:
                valid_strategies.discard(strategy)
            per.append({key: value for key, value in result.items() if key != "output"})
        records.append({"problem": path.name, "runs": per})
        if i % 25 == 0 or i == len(train_paths):
            print(f"education {i}/{len(train_paths)}", flush=True)

    if not valid_strategies:
        raise RuntimeError("no supported E strategy remained after training probes")

    strategy_models = {}
    X = np.asarray([features[path.name] for path in train_paths], dtype=float)
    for strategy in sorted(valid_strategies):
        costs = []
        for record in records:
            run = next((x for x in record["runs"] if x["strategy"] == strategy), None)
            if run is None:
                costs.append(args.train_seconds * 3.0)
            elif run["success"]:
                costs.append(max(0.001, float(run["elapsed_seconds"])))
            else:
                costs.append(args.train_seconds * 3.0)
        y = np.log1p(np.asarray(costs, dtype=float))
        w, mu, sigma = fit_ridge(X, y)
        strategy_models[strategy] = {
            "weights": [float(x) for x in w], "mu": [float(x) for x in mu],
            "sigma": [float(x) for x in sigma],
            "training_mean_log_cost": float(y.mean()),
        }

    symbol_policy = build_symbol_policy(train_paths)
    model = {
        "architecture_version": "2.6", "changes_solver_architecture": False,
        "artifact_type": "frozen_TPTP_education_policy", "target": args.target,
        "learner_target_exposed_during_education": False,
        "same_abstract_problem_proxy_exposed_during_education": False,
        "seed": args.seed, "training_fraction": args.fraction,
        "feature_schema": [
            "bias", "log_chars", "log_tokens", "log_fof_units",
            "log_conjecture_symbol_count", "log_unique_symbol_count", "log_equals",
            "log_forall", "log_exists", "log_and", "log_or", "log_implies",
            "log_iff", "log_negation", "log_includes", "log_background_formula_count",
        ],
        "supported_strategies": sorted(valid_strategies),
        "strategy_models": strategy_models, "symbol_policy": symbol_policy,
    }
    model_text = json.dumps(model, sort_keys=True, separators=(",", ":"))
    model_sha = sha256_text(model_text)
    (out / "tptp95_policy.json").write_text(json.dumps(model, indent=2, sort_keys=True), encoding="utf-8")
    (out / "education_records.json").write_text(json.dumps(records, indent=2, sort_keys=True), encoding="utf-8")
    result = {
        "status": "TRAINING_COMPLETE", "architecture_version": "2.6",
        "architecture_changed": False, "target": args.target, "domain": args.domain,
        "model_sha256": model_sha, "training_count": len(train_paths),
        "holdout_count": len(holdout),
        "actual_training_fraction": len(train_paths) / len(clean),
        "leakage_audit_passed": True, "supported_strategies": sorted(valid_strategies),
    }
    (out / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    (out / "TRAINING_COMPLETE").write_text(model_sha + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True), flush=True)
    return 0


def examine(args) -> int:
    root = Path(args.tptp_root)
    original = root / "Problems" / args.domain / args.target
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    if not original.exists():
        raise SystemExit(f"target missing: {original}")
    text = original.read_text(encoding="utf-8", errors="replace")
    expected = expected_status(text)

    if args.educated:
        model = json.loads(Path(args.policy).read_text(encoding="utf-8"))
        if model["target"] != args.target:
            raise RuntimeError("frozen policy target mismatch")
        if model.get("learner_target_exposed_during_education") is not False:
            raise RuntimeError("education leakage flag is not clean")
        problem = out / f"{args.target}.educated-reordered.p"
        problem.write_text(reorder_target(text, model), encoding="utf-8")
        feat = feature_vector(text)
        ranked = sorted(model["supported_strategies"],
                        key=lambda strategy: (score_model(model, feat, strategy), strategy))
        arm = "educated95"
    else:
        problem = original
        ranked = [strategy for strategy in BASELINE_ORDER if strategy in STRATEGIES]
        arm = "uneducated"

    ranked = ranked[:3]
    slice_seconds = max(1, args.total_seconds // max(1, len(ranked)))
    runs = []
    settled = None
    proof_path = None
    t0 = time.perf_counter()
    for strategy in ranked:
        remaining = args.total_seconds - int(time.perf_counter() - t0)
        if remaining <= 0:
            break
        seconds = min(slice_seconds, remaining)
        result = run_e(problem, strategy, seconds, root)
        raw = result.pop("output")
        run_file = out / f"e_{strategy}.log"
        run_file.write_text(raw, encoding="utf-8")
        result["allocated_seconds"] = seconds
        runs.append(result)
        if result["success"]:
            settled = result
            proof_path = run_file.name
            break

    elapsed = time.perf_counter() - t0
    result = {
        "status": "SETTLED" if settled else "UNSETTLED_WITHIN_BUDGET",
        "architecture_version": "2.6", "architecture_changed": False,
        "arm": arm, "educated": bool(args.educated), "target": args.target,
        "expected_tptp_status_for_evaluation_only": expected,
        "strategy_order": ranked, "total_budget_seconds": args.total_seconds,
        "elapsed_seconds": elapsed,
        "settled_strategy": settled["strategy"] if settled else None,
        "settled_szs_status": settled["status"] if settled else None,
        "proof_log": proof_path, "runs": runs,
        "target_seen_during_education": False if args.educated else None,
    }
    (out / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True), flush=True)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="mode", required=True)
    train_parser = sub.add_parser("train")
    train_parser.add_argument("--tptp-root", required=True)
    train_parser.add_argument("--domain", default="GRP")
    train_parser.add_argument("--target", default="GRP012+5.p")
    train_parser.add_argument("--tptp-version", default="9.3.1")
    train_parser.add_argument("--fraction", type=float, default=0.95)
    train_parser.add_argument("--seed", type=int, default=314159)
    train_parser.add_argument("--train-seconds", type=int, default=1)
    train_parser.add_argument("--out", required=True)
    train_parser.set_defaults(func=train)

    exam_parser = sub.add_parser("examine")
    exam_parser.add_argument("--tptp-root", required=True)
    exam_parser.add_argument("--domain", default="GRP")
    exam_parser.add_argument("--target", default="GRP012+5.p")
    exam_parser.add_argument("--policy")
    exam_parser.add_argument("--educated", action="store_true")
    exam_parser.add_argument("--total-seconds", type=int, default=1800)
    exam_parser.add_argument("--out", required=True)
    exam_parser.set_defaults(func=examine)

    args = ap.parse_args()
    if not (0.0 < getattr(args, "fraction", 0.95) < 1.0):
        raise SystemExit("fraction must be between 0 and 1")
    if getattr(args, "educated", False) and not args.policy:
        raise SystemExit("--policy is required for educated examination")
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
