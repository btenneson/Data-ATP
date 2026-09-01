#!/usr/bin/env python3
"""DATA-MIND 2.8: one-change learned proof-horizon experiment.

Relative to the frozen 95%-educated DATA-MIND 2.6 arm, this adapter changes one
search-architecture component only: the hand-written settlement-distance
surrogate is replaced by an additive proof horizon learned from the exact same
95% target-clean theorem cohort.

Unchanged: proof calculus, legal candidate set, frozen 2.6 premise ranker,
Creativity, Mathematician, QH, Revision/Child, module adaptation, R3/I4 search,
DV gates, BANK admission, independent verifier, seed, opener cap and budgets.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
from typing import Any

HERE = Path(__file__).resolve().parent
DM26_PATH = HERE / "data_mind_2_6_integrated_semigroup.py"
EDU26_PATH = HERE / "data_mind_2_6_educated_ranker_adapter.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


DM26 = load_module("dm28_integrated26", DM26_PATH)
EDU26 = load_module("dm28_education26", EDU26_PATH)
BASEMOD = DM26.DM24.V2.BASE
_ORIGINAL_MAKE_PROVER = BASEMOD.make_prover
_ORIGINAL_WRITE_SUMMARY = BASEMOD.write_summary


def arg_value(argv: list[str], flag: str, default: str | None = None) -> str | None:
    try:
        i = argv.index(flag)
    except ValueError:
        return default
    return argv[i + 1] if i + 1 < len(argv) else default


def canonical_tree_hash(tree, mode: str) -> str:
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

    return hashlib.sha256(rec(tree).encode("utf-8")).hexdigest()


class LearnedProofHorizon:
    def __init__(self, path: Path, *, target: str):
        self.path = path.resolve()
        self.raw = self.path.read_bytes()
        self.file_sha256 = hashlib.sha256(self.raw).hexdigest()
        self.data = json.loads(self.raw)
        if self.data.get("architecture_version") != "2.8":
            raise SystemExit("proof horizon is not marked for DATA-MIND 2.8")
        if self.data.get("changes_solver_architecture") is not True:
            raise SystemExit("proof horizon checkpoint does not declare architecture change")
        if self.data.get("target") != target:
            raise SystemExit("proof horizon target mismatch")
        if self.data.get("learner_target_statement_exposed") is not False:
            raise SystemExit("refusing horizon: learner saw target statement")
        if self.data.get("learner_target_proof_exposed") is not False:
            raise SystemExit("refusing horizon: learner saw target proof")
        self.target = target
        self.exact = set(self.data["exact_studied_goal_hashes"])
        self.skeleton = {str(k): float(v) for k,v in self.data["skeleton_cost"].items()}
        self.shape = {str(k): float(v) for k,v in self.data["shape_cost"].items()}
        self.global_cost = float(self.data["global_median_cost"])
        self.calls = 0
        self.goals_scored = 0
        self.source_counts = Counter()
        self.cost_sum = 0.0
        self.cost_min = math.inf
        self.cost_max = -math.inf
        self.multi_goal_calls = 0
        self.max_goal_count = 0

    def goal_cost(self, tree) -> tuple[float, str]:
        eh = canonical_tree_hash(tree, "exact")
        if eh in self.exact:
            return 1.0, "exact_studied_theorem"
        sh = canonical_tree_hash(tree, "skeleton")
        if sh in self.skeleton:
            return self.skeleton[sh], "skeleton_motif"
        gh = canonical_tree_hash(tree, "shape")
        if gh in self.shape:
            return self.shape[gh], "shape_motif"
        return self.global_cost, "global_median"

    def install(self, comp, p8) -> None:
        horizon = self

        def learned_settlement_distance(goals, sub):
            horizon.calls += 1
            n = len(goals)
            horizon.max_goal_count = max(horizon.max_goal_count, n)
            if n > 1:
                horizon.multi_goal_calls += 1
            if not goals:
                return 0.0
            total = 0.0
            for g, _slot, _hix in goals:
                gg = p8.apply_sub(g, sub)
                cost, source = horizon.goal_cost(gg)
                total += cost
                horizon.goals_scored += 1
                horizon.source_counts[source] += 1
                horizon.cost_sum += cost
                horizon.cost_min = min(horizon.cost_min, cost)
                horizon.cost_max = max(horizon.cost_max, cost)
            return float(total)

        comp.settlement_distance_hat = learned_settlement_distance

    def summary(self) -> dict[str, Any]:
        n = self.goals_scored
        return {
            "learned_proof_horizon_loaded": True,
            "proof_horizon_file_sha256": self.file_sha256,
            "proof_horizon_training_cohort_sha256": self.data.get("training_cohort_sha256"),
            "proof_horizon_training_fraction": self.data.get("training_fraction_of_target_clean_corpus"),
            "proof_horizon_studied_theorems": self.data.get("studied_theorems"),
            "proof_horizon_holdout_theorems": self.data.get("holdout_theorems"),
            "proof_horizon_target_statement_exposed_during_training": False,
            "proof_horizon_target_proof_exposed_during_training": False,
            "proof_horizon_state_semantics": self.data.get("state_horizon_semantics"),
            "proof_horizon_goal_semantics": self.data.get("goal_cost_semantics"),
            "proof_horizon_calls": self.calls,
            "proof_horizon_goals_scored": self.goals_scored,
            "proof_horizon_source_counts": dict(self.source_counts),
            "proof_horizon_cost_mean": self.cost_sum/n if n else None,
            "proof_horizon_cost_min": self.cost_min if n else None,
            "proof_horizon_cost_max": self.cost_max if n else None,
            "proof_horizon_multi_goal_calls": self.multi_goal_calls,
            "proof_horizon_max_goal_count": self.max_goal_count,
            "proof_horizon_validation": self.data.get("validation"),
        }


_HORIZON: LearnedProofHorizon | None = None
_RANKER = None


class Integrated28Controller(DM26.Integrated26Controller):
    architecture_version = "2.8"

    def _install_structural_observer(self) -> None:
        if _HORIZON is None:
            raise RuntimeError("DATA-MIND 2.8 horizon missing")
        # Install the ONE changed objective before the inherited QH observer
        # wraps it. QH therefore receives the learned horizon as its feedback.
        _HORIZON.install(self.base6.COMP, self.base6.P8)
        return super()._install_structural_observer()

    def summary(self) -> dict[str, Any]:
        data = super().summary()
        data.update({
            "architecture_version": "2.8",
            "solver": "DATA-MIND 2.8 learned proof horizon",
            "module_controller_subarchitecture": "2.6 unchanged",
            "single_architecture_change": "hand-written settlement-distance surrogate -> corpus-learned additive proof horizon",
        })
        if _HORIZON is not None:
            data.update(_HORIZON.summary())
        return data


def main() -> int:
    global _HORIZON, _RANKER
    custom = argparse.ArgumentParser(add_help=False)
    custom.add_argument("--educated-ranker", required=True)
    custom.add_argument("--education-blend", type=float, default=1.0)
    custom.add_argument("--proof-horizon", required=True)
    ours, remaining = custom.parse_known_args(sys.argv[1:])

    target = arg_value(remaining, "--target", "sgrpcl") or "sgrpcl"
    setmm_raw = arg_value(remaining, "--setmm")
    summary_raw = arg_value(remaining, "--summary")
    if not setmm_raw or not summary_raw:
        raise SystemExit("2.8 adapter requires --setmm and --summary")

    _HORIZON = LearnedProofHorizon(Path(ours.proof_horizon), target=target)
    _RANKER = EDU26.FrozenEducationRanker(
        Path(ours.educated_ranker),
        setmm=Path(setmm_raw).resolve(),
        target=target,
        blend=max(0.0, min(4.0, float(ours.education_blend))),
    )

    # Make DM26.main install the 2.8 subclass rather than the inherited class.
    DM26.Integrated26Controller = Integrated28Controller

    def combined_make_prover(base7, controller):
        comp = base7.BASE6.COMP
        original_scores = comp._legacy_scores

        def educated_scores(goal_tree, items, profile, rng, local_use, shared_use):
            legacy = original_scores(goal_tree, items, profile, rng, local_use, shared_use)
            return _RANKER.score_candidates(goal_tree, items, legacy)

        comp._legacy_scores = educated_scores
        return _ORIGINAL_MAKE_PROVER(base7, controller)

    def write_summary28(path, controller, *, target: str, rc: int | None):
        _ORIGINAL_WRITE_SUMMARY(path, controller, target=target, rc=rc)
        p = Path(path)
        if not p.exists():
            return
        data = json.loads(p.read_text(encoding="utf-8"))
        data.update(_RANKER.summary())
        data.update(_HORIZON.summary())
        data.update({
            "architecture_version": "2.8",
            "architecture_changed": True,
            "solver": "DATA-MIND 2.8 learned proof horizon + frozen 95% premise education",
            "single_architecture_change": "replace hand-written settlement-distance surrogate with corpus-learned additive proof horizon",
            "premise_ranker_unchanged_from_educated_2_6": True,
            "formal_calculus_unchanged": True,
            "verifier_and_bank_unchanged": True,
        })
        p.write_text(json.dumps(data, indent=2)+"\n", encoding="utf-8")

    BASEMOD.make_prover = combined_make_prover
    BASEMOD.write_summary = write_summary28

    print(
        "LEARNED_PROOF_HORIZON_LOADED "
        f"target={target} sha256={_HORIZON.file_sha256} architecture=2.8 single-change=true",
        flush=True,
    )
    print(
        "EDUCATION_CHECKPOINT_LOADED "
        f"target={target} sha256={_RANKER.file_sha256} premise-ranker-unchanged=true",
        flush=True,
    )

    old = sys.argv[:]
    sys.argv = [old[0], *remaining]
    try:
        rc = int(DM26.main() or 0)
    finally:
        sys.argv = old

    p = Path(summary_raw).resolve()
    if p.exists():
        data = json.loads(p.read_text(encoding="utf-8"))
        data.update(_RANKER.summary())
        data.update(_HORIZON.summary())
        data.update({
            "architecture_version": "2.8",
            "architecture_changed": True,
            "solver": "DATA-MIND 2.8 learned proof horizon + frozen 95% premise education",
            "single_architecture_change": "replace hand-written settlement-distance surrogate with corpus-learned additive proof horizon",
            "premise_ranker_unchanged_from_educated_2_6": True,
            "formal_calculus_unchanged": True,
            "verifier_and_bank_unchanged": True,
        })
        p.write_text(json.dumps(data, indent=2)+"\n", encoding="utf-8")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
