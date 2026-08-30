#!/usr/bin/env python3
"""Full-feature experimental DATA-MIND adapter for Metamath target ``sgrpcl``.

This adapter intentionally separates architecture from proof authority.
Both DATA-MIND 1.0 and 1.1 use the same pinned Predator 8.040 R3/I4
mathematical search engine.  DATA-MIND 1.0 preserves the engine's supervisory
strategy controller while adding an auditable self-report layer.  DATA-MIND
1.1 adds the eight-agent revision fallback, shared pre-BANK deliberation,
Counselor/Professor diagnostics, and online strategy-utility learning.  The 1.1
controller may change only the high-level legal search strategy selected by R3;
it cannot change Metamath rules or verification.

A candidate is only a BANK proposal here.  The workflow performs an independent
context-substitution verification and appends the verifier/BANK decision to the
same hash-chained TransactionLog afterward.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys
from typing import Any

from data_atp.events import EventType, TransactionLog

AGENTS = ("P1", "P2", "R1", "R2", "I1", "I2", "C1", "C2")
STRATEGIES = ("COMPASS", "CERTIFY", "DIVERSIFY", "LEAN", "ROTATED")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def emit(log: TransactionLog, event_type: EventType, kind: str, **payload: Any) -> None:
    log.append(event_type, {"kind": kind, **payload})


class DataMindController:
    """Target-agnostic architecture controller wrapped around R3 strategy choice."""

    def __init__(self, version: str, supervisory, p8038, log: TransactionLog, rotate_stale: int):
        self.version = version
        self.supervisory = supervisory
        self.p8038 = p8038
        self.log = log
        self.rotate_stale = max(1, int(rotate_stale))
        self.last_bucket: tuple[int, int] | None = None
        self.last_stale: int | None = None
        self.last_choice: str | None = None
        self.last_base: str | None = None
        self.latest_dissatisfaction = 0.0
        self.trajectory: list[dict[str, Any]] = []
        self.utility = {s: 1.0 for s in STRATEGIES}
        self.agent_vectors: dict[str, dict[str, float]] | None = None
        self.eight = None
        self.agent_message_count = 0
        self.counselor_events = 0
        self.professor_events = 0
        self.learning_events = 0
        self.override_count = 0

        if version == "1.1":
            self._install_eight_agent_controller()

    def _install_eight_agent_controller(self) -> None:
        p8 = self.p8038
        groups = {s: p8.GroupCoordinate.logit(s) for s in STRATEGIES}
        # Role priors are architectural, not theorem-specific.  They express
        # proof-seeking, challenge/diversity, independence/exploration, and
        # contradiction/balance emphases over the existing legal R3 strategies.
        preferences = {
            "P1": {"COMPASS": .85, "CERTIFY": .66, "DIVERSIFY": .22, "LEAN": .28, "ROTATED": .18},
            "P2": {"COMPASS": .66, "CERTIFY": .85, "DIVERSIFY": .25, "LEAN": .32, "ROTATED": .18},
            "R1": {"COMPASS": .22, "CERTIFY": .25, "DIVERSIFY": .78, "LEAN": .46, "ROTATED": .82},
            "R2": {"COMPASS": .26, "CERTIFY": .30, "DIVERSIFY": .68, "LEAN": .52, "ROTATED": .76},
            "I1": {"COMPASS": .34, "CERTIFY": .48, "DIVERSIFY": .42, "LEAN": .82, "ROTATED": .68},
            "I2": {"COMPASS": .40, "CERTIFY": .55, "DIVERSIFY": .36, "LEAN": .76, "ROTATED": .72},
            "C1": {"COMPASS": .50, "CERTIFY": .50, "DIVERSIFY": .50, "LEAN": .50, "ROTATED": .50},
            "C2": {"COMPASS": .46, "CERTIFY": .54, "DIVERSIFY": .50, "LEAN": .56, "ROTATED": .44},
        }
        policies = {}
        for agent in AGENTS:
            pref = preferences[agent]

            def diagnostic(_trajectory, self=self):
                return float(self.latest_dissatisfaction)

            def optimizer(_trajectory, vector, pref=pref, self=self):
                umax = max(self.utility.values()) or 1.0
                return {
                    s: min(.999, max(.001,
                        .72 * float(vector[s]) + .20 * float(pref[s])
                        + .08 * (self.utility[s] / umax)))
                    for s in STRATEGIES
                }

            policies[agent] = p8.AgentRevisionPolicy(
                agent=agent,
                threshold=0.55,
                diagnostic=diagnostic,
                optimizer=optimizer,
                groups=groups,
                verifier=lambda z: int(z.get("V", 1)) if isinstance(z, dict) else 1,
                min_post_revision_steps=2,
            )
        self.eight = p8.EightAgentRevisionFallback(policies)
        self.agent_vectors = {a: dict(preferences[a]) for a in AGENTS}

    def _metrics(self, stale: int, terminal_rejects: int) -> dict[str, float]:
        stale_component = min(1.0, max(0.0, stale / float(self.rotate_stale)))
        reject_component = min(1.0, max(0.0, terminal_rejects / 500.0))
        dissatisfaction = min(1.0, 0.78 * stale_component + 0.22 * reject_component)
        return {
            "stale": float(stale),
            "terminal_rejects": float(terminal_rejects),
            "dissatisfaction": dissatisfaction,
        }

    def _maybe_learn(self, stale: int) -> None:
        if self.last_stale is None or self.last_choice is None:
            return
        if stale < self.last_stale:
            self.utility[self.last_choice] = min(3.0, self.utility[self.last_choice] + 0.18)
            outcome = "progress"
        elif stale > self.last_stale:
            self.utility[self.last_choice] = max(0.25, self.utility[self.last_choice] * 0.985)
            outcome = "stagnation"
        else:
            outcome = "flat"
        if self.version == "1.1":
            emit(self.log, EventType.SELF_REPORT_FILED, "learning_update",
                 previous_strategy=self.last_choice, observed=outcome,
                 utility=dict(self.utility), verifier_authority=False)
            self.learning_events += 1

    def _one_one_deliberate(self, base: str, stale: int, terminal_rejects: int, metrics: dict[str, float]) -> str:
        assert self.eight is not None and self.agent_vectors is not None
        self.latest_dissatisfaction = metrics["dissatisfaction"]
        state = {
            "V": 1,
            "stale": stale,
            "terminal_rejects": terminal_rejects,
            "dissatisfaction": self.latest_dissatisfaction,
            "base_strategy": base,
        }
        self.trajectory = (self.trajectory + [state])[-8:]
        trajectories = {a: tuple(self.trajectory) for a in AGENTS}
        vectors = {a: dict(self.agent_vectors[a]) for a in AGENTS}
        next_vectors, decisions = self.eight.step_all(trajectories, vectors)
        self.agent_vectors = next_vectors

        for agent in AGENTS:
            vec = next_vectors[agent]
            top = max(STRATEGIES, key=lambda s: (vec[s], s))
            d = decisions[agent]
            emit(self.log, EventType.SELF_REPORT_FILED, "agent_message",
                 agent=agent, channel="shared_pre_bank_deliberation",
                 proposed_strategy=top, revision_mode=d["mode"],
                 diagnostic=d["D(T)"], threshold=d["threshold"],
                 certified_math=False)
            self.agent_message_count += 1

        if terminal_rejects > 250:
            advice = "terminal rejection pressure high; preserve diversity and challenge current basin"
        elif stale >= self.rotate_stale:
            advice = "ordinary strategy family is stale; favor a genuine escape regime"
        elif self.latest_dissatisfaction > 0.45:
            advice = "progress is weakening; compare alternate legal search regimes"
        else:
            advice = "continue local refinement while progress evidence remains adequate"
        emit(self.log, EventType.SELF_REPORT_FILED, "counselor_advice",
             advice=advice, authority="advisory_only", may_verify=False)
        self.counselor_events += 1

        if self.last_choice is not None:
            grade = "productive" if stale < (self.last_stale if self.last_stale is not None else stale) else "needs_revision"
            emit(self.log, EventType.SELF_REPORT_FILED, "professor_review",
                 previous_strategy=self.last_choice, evaluation=grade,
                 authority="teaching_evaluation_only", may_verify=False)
            self.professor_events += 1

        mean = {
            s: sum(next_vectors[a][s] for a in AGENTS) / len(AGENTS)
            for s in STRATEGIES
        }
        umax = max(self.utility.values()) or 1.0
        # Trust the frozen R3 controller strongly when it is satisfied; allow
        # the eight-agent consensus to take control only as dissatisfaction grows.
        base_prior = 0.24 * (1.0 - self.latest_dissatisfaction)
        scores = {
            s: 0.72 * mean[s] + 0.28 * (self.utility[s] / umax)
               + (base_prior if s == base else 0.0)
            for s in STRATEGIES
        }
        choice = max(STRATEGIES, key=lambda s: (scores[s], s))
        emit(self.log, EventType.STRATEGY_OVERRIDE_PROPOSED, "eight_agent_consensus",
             base_strategy=base, proposed_strategy=choice, scores=scores,
             dissatisfaction=self.latest_dissatisfaction,
             verifier_authority=False)
        if choice != base:
            emit(self.log, EventType.STRATEGY_OVERRIDE_EXECUTED, "strategy_override",
                 from_strategy=base, to_strategy=choice,
                 reason="eight-agent consensus under current dissatisfaction",
                 verifier_authority=False)
            self.override_count += 1
        return choice

    def choose(self, stale: int, terminal_rejects: int) -> str:
        stale = int(stale)
        terminal_rejects = int(terminal_rejects)
        base = self.supervisory(stale, terminal_rejects)
        # Control work is intentionally coarse.  Search can call _strategy_for
        # very often; architecture deliberation occurs only when the live state
        # crosses a new 500-stale or 50-rejection bucket.
        bucket = (stale // 500, terminal_rejects // 50)
        if self.last_bucket == bucket and self.last_choice is not None:
            return self.last_choice

        self._maybe_learn(stale)
        metrics = self._metrics(stale, terminal_rejects)
        emit(self.log, EventType.SELF_REPORT_FILED, "self_awareness",
             architecture=f"DATA-MIND {self.version}", stale=stale,
             terminal_rejects=terminal_rejects, base_strategy=base,
             metrics=metrics, verifier_sovereign=True)

        if self.version == "1.1":
            choice = self._one_one_deliberate(base, stale, terminal_rejects, metrics)
        else:
            choice = base

        self.last_bucket = bucket
        self.last_stale = stale
        self.last_base = base
        self.last_choice = choice
        return choice


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", choices=["1.0", "1.1"], required=True)
    ap.add_argument("--atp-root", required=True)
    ap.add_argument("--setmm", required=True)
    ap.add_argument("--target", default="sgrpcl")
    ap.add_argument("--budget", type=int, default=300000)
    ap.add_argument("--max-depth", type=int, default=12)
    ap.add_argument("--agents", type=int, default=4)
    ap.add_argument("--creativity", type=float, default=.55)
    ap.add_argument("--seed", type=int, default=2301)
    ap.add_argument("--opener-cap", type=int, default=48)
    ap.add_argument("--max-open", type=int, default=8)
    ap.add_argument("--progress", type=int, default=250)
    ap.add_argument("--rotate-stale", type=int, default=5200)
    ap.add_argument("--out", required=True)
    ap.add_argument("--transactions", required=True)
    ap.add_argument("--summary", required=True)
    a = ap.parse_args()

    atp_root = Path(a.atp_root).resolve()
    pred_dir = atp_root / "predator 8"
    script = pred_dir / "predator 8.040-R3I4-supervisory-rotation.py"
    p8038_path = pred_dir / "recovered8_002" / "predator8_038_eight_agent_revision_fallback.py"
    if not script.exists() or not p8038_path.exists():
        raise SystemExit("pinned Predator sources are missing")

    sys.path.insert(0, str(atp_root))
    sys.path.insert(0, str(pred_dir))
    os.environ["PREDATOR_840_ROTATE_STALE"] = str(a.rotate_stale)

    log = TransactionLog(a.transactions)
    emit(log, EventType.SELF_REPORT_FILED, "self_description",
         architecture=f"DATA-MIND {a.version}", target=a.target,
         shared_search_engine="pinned Predator 8.040 R3/I4",
         verifier_external_to_architecture=True,
         eight_agents_enabled=(a.version == "1.1"),
         sgrpcl_specific_tuning=False)

    p840 = load_module("data_mind_p840", script)
    p8038 = load_module("data_mind_p8038", p8038_path)
    supervisory = p840.BASE6._strategy_for
    controller = DataMindController(a.version, supervisory, p8038, log, a.rotate_stale)
    p840.BASE6._strategy_for = controller.choose

    emit(log, EventType.ACTION_PROPOSED, "search_start",
         budget=a.budget, max_depth=a.max_depth, agents=a.agents,
         creativity=a.creativity, seed=a.seed, opener_cap=a.opener_cap,
         max_open=a.max_open, rotate_stale=a.rotate_stale,
         certificate_authority=False)

    old_argv = sys.argv[:]
    sys.argv = [
        str(script), "prove", str(Path(a.setmm).resolve()),
        "--label", a.target,
        "--budget", str(a.budget),
        "--max-depth", str(a.max_depth),
        "--agents", str(a.agents),
        "--creativity", str(a.creativity),
        "--seed", str(a.seed),
        "--opener-cap", str(a.opener_cap),
        "--max-open", str(a.max_open),
        "--progress", str(a.progress),
        "--out", str(Path(a.out).resolve()),
    ]
    try:
        rc = int(p840.main() or 0)
    finally:
        sys.argv = old_argv

    candidate = Path(a.out)
    if candidate.exists() and candidate.stat().st_size:
        emit(log, EventType.CERTIFICATE_SUBMITTED, "bank_proposal",
             target=a.target, candidate_path=str(candidate),
             certified_at_proposal_time=False,
             independent_verification_pending=True)

    summary = {
        "solver": f"DATA-MIND {a.version} sgrpcl full-feature experimental adapter",
        "version": a.version,
        "target": a.target,
        "shared_search_engine": "pinned Predator 8.040 R3/I4",
        "run_returncode": rc,
        "candidate_emitted": bool(candidate.exists() and candidate.stat().st_size),
        "budget": a.budget,
        "seed": a.seed,
        "max_depth": a.max_depth,
        "agents_low_level": a.agents,
        "creativity": a.creativity,
        "rotate_stale": a.rotate_stale,
        "transaction_log_verified_pre_external_cv": log.verify(),
        "eight_agent_deliberation_enabled": a.version == "1.1",
        "agent_message_count": controller.agent_message_count,
        "counselor_events": controller.counselor_events,
        "professor_events": controller.professor_events,
        "learning_events": controller.learning_events,
        "strategy_override_count": controller.override_count,
        "search_policy_difference_allowed": a.version == "1.1",
        "sgrpcl_specific_tuning": False,
        "bank_commit_written": False,
        "independent_verification_pending": True,
    }
    Path(a.summary).write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
