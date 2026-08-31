#!/usr/bin/env python3
"""Load a frozen 95%-educated set.mm premise ranker into DATA-MIND 2.6.

This is an education/checkpoint adapter, not a solver-architecture revision.
DATA-MIND 2.6's proof calculus, controller, QH, Mathematician, Child revision,
BANK/verifier boundary, resource controls, and search state are unchanged.
The adapter supplies learned premise scores at the existing candidate-ranking
stage and records exactly how often the frozen education was consulted.

The learner was trained before examination.  At test time the target statement
is of course visible to the prover as the problem to solve, but the checkpoint
must certify that neither the target statement nor its proof was exposed to the
learner during training.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import sys
from typing import Any

HERE = Path(__file__).resolve().parent
DM26_PATH = HERE / "data_mind_2_6_integrated_semigroup.py"
spec = importlib.util.spec_from_file_location("dm26_integrated_for_educated", DM26_PATH)
if spec is None or spec.loader is None:
    raise SystemExit(f"cannot load {DM26_PATH}")
DM26 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = DM26
spec.loader.exec_module(DM26)

BASEMOD = DM26.DM24.V2.BASE
_ORIGINAL_MAKE_PROVER = BASEMOD.make_prover


def arg_value(argv: list[str], flag: str, default: str | None = None) -> str | None:
    try:
        i = argv.index(flag)
    except ValueError:
        return default
    return argv[i + 1] if i + 1 < len(argv) else default


class FrozenEducationRanker:
    def __init__(self, path: Path, *, setmm: Path, target: str, blend: float = 1.0):
        self.path = path.resolve()
        self.raw = self.path.read_bytes()
        self.file_sha256 = hashlib.sha256(self.raw).hexdigest()
        self.data = json.loads(self.raw)
        self.target = str(target)
        self.blend = float(blend)

        if self.data.get("architecture_version") != "2.6":
            raise SystemExit("education checkpoint is not marked for DATA-MIND 2.6")
        if self.data.get("changes_solver_architecture") is not False:
            raise SystemExit("education checkpoint claims an architecture change")
        if self.data.get("learner_target_statement_exposed") is not False:
            raise SystemExit("refusing checkpoint: learner saw target statement")
        if self.data.get("learner_target_proof_exposed") is not False:
            raise SystemExit("refusing checkpoint: learner saw target proof")
        if str(self.data.get("target")) != self.target:
            raise SystemExit(
                f"education checkpoint target mismatch: {self.data.get('target')!r} != {self.target!r}"
            )

        self.weights = [float(x) for x in self.data["weights"]]
        self.mu = [float(x) for x in self.data["mu"]]
        self.sigma = [float(x) for x in self.data["sigma"]]
        if not (len(self.weights) == len(self.mu) == len(self.sigma) == 8):
            raise SystemExit("unexpected frozen ranker feature dimension")

        self.usage = {str(k): float(v) for k, v in self.data.get("usage", {}).items()}
        self.depth = {str(k): float(v) for k, v in self.data.get("depth", {}).items()}
        self.order = {str(k): int(v) for k, v in self.data.get("order", {}).items()}
        self.target_order = int(self.data["target_order"])

        # Axiom/theorem type is not a learned parameter.  Recover it from the
        # pinned exam environment so feature 7 is evaluated exactly at test time.
        text = setmm.read_text(encoding="utf-8", errors="replace")
        text = re.sub(r"\$\(.*?\$\)", " ", text, flags=re.S)
        toks = text.split()
        self.axioms: set[str] = set()
        for i in range(len(toks) - 1):
            if toks[i + 1] == "$a":
                self.axioms.add(toks[i])

        self.score_calls = 0
        self.candidates_seen = 0
        self.candidates_educated = 0
        self.candidates_fallback = 0
        self.learned_score_sum = 0.0
        self.learned_score_min = math.inf
        self.learned_score_max = -math.inf

    @staticmethod
    def _tokens(tree) -> list[str]:
        return [str(t) for t in tree.tokens()]

    def learned_score(self, goal_tree, item) -> float | None:
        lab, candidate_tree, _data = item
        lab = str(lab)
        # Labels missing from frozen corpus metadata get the pre-existing score.
        if lab not in self.order or lab not in self.depth:
            return None

        gt = set(self._tokens(goal_tree))
        ct = set(self._tokens(candidate_tree))
        inter = len(gt & ct)
        union = len(gt | ct) or 1
        features = [
            1.0,
            inter / union,
            inter / (len(ct) or 1),
            math.log1p(self.usage.get(lab, 0.0)),
            self.depth[lab] / 10.0,
            (self.target_order - self.order[lab]) / 1000.0,
            1.0 if lab in self.axioms else 0.0,
            len(ct) / 20.0,
        ]
        z = [
            (features[i] - self.mu[i]) / self.sigma[i]
            for i in range(8)
        ]
        return sum(self.weights[i] * z[i] for i in range(8))

    def score_candidates(self, goal_tree, items, legacy: dict[str, float]) -> dict[str, float]:
        self.score_calls += 1
        out: dict[str, float] = {}
        for item in items:
            lab = str(item[0])
            self.candidates_seen += 1
            learned = self.learned_score(goal_tree, item)
            old = float(legacy.get(lab, 0.0))
            if learned is None:
                self.candidates_fallback += 1
                out[lab] = old
                continue
            self.candidates_educated += 1
            self.learned_score_sum += learned
            self.learned_score_min = min(self.learned_score_min, learned)
            self.learned_score_max = max(self.learned_score_max, learned)
            # Frozen education is an additive prior over the same legal
            # candidates.  No candidate is invented and no inference is relaxed.
            out[lab] = old + self.blend * learned
        return out

    def summary(self) -> dict[str, Any]:
        n = self.candidates_educated
        return {
            "education_checkpoint_loaded": True,
            "education_protocol": "95% target-clean set.mm",
            "education_architecture_change": False,
            "education_artifact_type": self.data.get("artifact_type"),
            "education_training_fraction": self.data.get("training_fraction_of_target_clean_corpus"),
            "education_seed": self.data.get("seed"),
            "education_checkpoint_file_sha256": self.file_sha256,
            "education_target": self.target,
            "education_target_statement_exposed_during_training": False,
            "education_target_proof_exposed_during_training": False,
            "education_feature_schema": self.data.get("feature_schema"),
            "education_score_blend": self.blend,
            "education_score_rule": "existing_legacy_score + blend * frozen_learned_premise_score",
            "education_rank_calls": self.score_calls,
            "education_candidates_seen": self.candidates_seen,
            "education_candidates_scored": self.candidates_educated,
            "education_candidates_fallback_to_legacy": self.candidates_fallback,
            "education_candidate_coverage": (n / self.candidates_seen if self.candidates_seen else 0.0),
            "education_learned_score_mean": (self.learned_score_sum / n if n else None),
            "education_learned_score_min": (self.learned_score_min if n else None),
            "education_learned_score_max": (self.learned_score_max if n else None),
            "education_only_reorders_legal_candidates": True,
            "verifier_authority_from_education": False,
            "bank_authority_from_education": False,
        }


def main() -> int:
    import argparse

    custom = argparse.ArgumentParser(add_help=False)
    custom.add_argument("--educated-ranker", required=True)
    custom.add_argument("--education-blend", type=float, default=1.0)
    ours, remaining = custom.parse_known_args(sys.argv[1:])

    target = arg_value(remaining, "--target", "sgrpcl") or "sgrpcl"
    setmm_raw = arg_value(remaining, "--setmm")
    summary_raw = arg_value(remaining, "--summary")
    if not setmm_raw or not summary_raw:
        raise SystemExit("educated adapter requires --setmm and --summary")

    ranker = FrozenEducationRanker(
        Path(ours.educated_ranker),
        setmm=Path(setmm_raw).resolve(),
        target=target,
        blend=max(0.0, min(4.0, float(ours.education_blend))),
    )

    def educated_make_prover(base7, controller):
        comp = base7.BASE6.COMP
        original_scores = comp._legacy_scores

        def educated_scores(goal_tree, items, profile, rng, local_use, shared_use):
            legacy = original_scores(goal_tree, items, profile, rng, local_use, shared_use)
            return ranker.score_candidates(goal_tree, items, legacy)

        comp._legacy_scores = educated_scores
        return _ORIGINAL_MAKE_PROVER(base7, controller)

    BASEMOD.make_prover = educated_make_prover

    old = sys.argv[:]
    sys.argv = [old[0], *remaining]
    try:
        rc = int(DM26.main() or 0)
    finally:
        sys.argv = old

    summary_path = Path(summary_raw).resolve()
    if summary_path.exists():
        data = json.loads(summary_path.read_text(encoding="utf-8"))
        data.update(ranker.summary())
        data.update({
            "architecture_version": "2.6",
            "solver": "DATA-MIND 2.6 + frozen 95% education",
            "architecture_changed": False,
        })
        summary_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
