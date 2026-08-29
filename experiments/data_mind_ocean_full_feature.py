#!/usr/bin/env python3
"""Experimental full-feature DATA-MIND Ocean adapter.

Purpose
-------
Run the strongest *executable* Ocean-native form we can presently justify for
DATA-MIND 1.0 and 1.1 without freezing their search policy.  This is not a
claim that the general DATA-MIND architecture is production-complete.

Shared invariants
-----------------
* Solver sees only the opaque positive Ocean TPTP problem.
* No planted route, generator seed, manifest, evaluator key, or L* is read.
* Search control may reorder legal expansions but cannot certify theoremhood.
* A candidate enters BANK only after the independent path verifier accepts it.
* One shared frontier/state store is used; extra 1.1 agents do not duplicate
  the graph in memory.

DATA-MIND 1.0
-------------
Uses adaptive self-awareness/control, structured creativity (alternative
search schedules), dissatisfaction-triggered revision, and verifier-gated BANK.
The controller may change the mixture of reconnaissance, breadth, and
branching-resurvey search during the run.

DATA-MIND 1.1
-------------
Includes all 1.0 behavior plus machine-readable self-description, the existing
Predator 8.038 eight-agent revision fallback (P1,P2,R1,R2,I1,I2,C1,C2), shared
pre-BANK deliberation, Counselor diagnostics, Professor method evaluation,
online Learning of strategy utility, and the repository's real append-only
SHA-256 TransactionLog. These additions are allowed to alter the legal search
schedule.  They still cannot verify or commit a certificate.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import heapq
import importlib.util
import json
import math
from pathlib import Path
import random
import time
from typing import Any

from data_atp.events import EventType, TransactionLog

STRATEGIES = ("recon", "breadth", "resurvey")
AGENTS = ("P1", "P2", "R1", "R2", "I1", "I2", "C1", "C2")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def normalize_weights(raw: dict[str, float]) -> dict[str, float]:
    vals = {k: max(1e-6, float(raw.get(k, 0.0))) for k in STRATEGIES}
    z = sum(vals.values())
    return {k: vals[k] / z for k in STRATEGIES}


def integer_cycle(weights: dict[str, float], slots: int = 20) -> tuple[str, ...]:
    w = normalize_weights(weights)
    counts = {k: max(1, int(round(w[k] * slots))) for k in STRATEGIES}
    # Adjust deterministically to exactly slots while keeping each strategy alive.
    while sum(counts.values()) > slots:
        k = max(STRATEGIES, key=lambda x: (counts[x], w[x], x))
        if counts[k] > 1:
            counts[k] -= 1
        else:
            break
    while sum(counts.values()) < slots:
        k = max(STRATEGIES, key=lambda x: (w[x] - counts[x] / slots, w[x], x))
        counts[k] += 1
    # Interleave instead of running large homogeneous blocks.
    remaining = dict(counts)
    cycle: list[str] = []
    for i in range(slots):
        best = max(
            STRATEGIES,
            key=lambda k: (
                (counts[k] * (i + 1) / slots) - (counts[k] - remaining[k]),
                w[k], k,
            ),
        )
        if remaining[best] <= 0:
            best = max((k for k in STRATEGIES if remaining[k] > 0), key=lambda k: (w[k], k))
        cycle.append(best)
        remaining[best] -= 1
    return tuple(cycle)


class Audit:
    def __init__(self, path: Path):
        self.log = TransactionLog(path)
        self.counts: dict[str, int] = defaultdict(int)

    def emit(self, event_type: EventType, kind: str, **payload: Any) -> None:
        body = {"kind": kind, **payload}
        self.log.append(event_type, body)
        self.counts[kind] += 1


class FullFeatureOcean:
    def __init__(
        self,
        version: str,
        ref,
        source: int,
        target: int,
        edges: list[tuple[int, int]],
        adj: dict[int, list[int]],
        audit: Audit,
        time_limit_s: float,
        max_expansions: int,
        seed: int,
        p8038_path: Path | None,
        control_epoch: int,
    ) -> None:
        self.version = version
        self.ref = ref
        self.source = source
        self.target = target
        self.edges = edges
        self.adj = adj
        self.audit = audit
        self.time_limit_s = float(time_limit_s)
        self.max_expansions = int(max_expansions)
        self.rng = random.Random(seed)
        self.control_epoch = max(10_000, int(control_epoch))

        self.parent: dict[int, int | None] = {source: None}
        self.depth: dict[int, int] = {source: 0}
        self.expanded: set[int] = set()
        self.cache: dict[int, tuple[int, int]] = {}
        self.scoring_probes = 0
        self.serial = 0
        self.queues: dict[str, list[tuple]] = {
            "recon": [], "breadth": [], "resurvey": []
        }
        self.expansions = 0
        self.discoveries = 1
        self.duplicates = 0
        self.strategy_expansions: dict[str, int] = defaultdict(int)
        self.strategy_discoveries: dict[str, int] = defaultdict(int)
        self.epoch_strategy_expansions: dict[str, int] = defaultdict(int)
        self.epoch_strategy_discoveries: dict[str, int] = defaultdict(int)
        self.controller_switches: list[dict[str, Any]] = []
        self.revision_count = 0
        self.creativity_count = 0
        self.agent_messages = 0
        self.professor_events = 0
        self.counselor_events = 0
        self.learning_events = 0
        self.latest_metrics: dict[str, float] = {"dissatisfaction": 0.0}
        self.trajectory: list[dict[str, Any]] = []

        self.weights = normalize_weights({"recon": 0.80, "breadth": 0.10, "resurvey": 0.10})
        self.mode = "native"
        self.cycle = integer_cycle(self.weights)
        self.cycle_i = 0
        self.prev_epoch_yield = 1.0
        self.stale_epochs = 0
        self.learning_utility = {k: 1.0 for k in STRATEGIES}

        self.eight = None
        self.agent_vectors: dict[str, dict[str, float]] | None = None
        if version == "1.1":
            if p8038_path is None:
                raise RuntimeError("DATA-MIND 1.1 requires Predator 8.038 module")
            self._install_eight_agent_controller(p8038_path)

        self._push(source)

    def recon_score(self, v: int) -> tuple[int, int]:
        if v not in self.cache:
            s, volume, probes = self.ref.bounded_recon(v, self.adj)
            self.cache[v] = (s, volume)
            self.scoring_probes += probes
        return self.cache[v]

    def _push(self, v: int) -> None:
        s, volume = self.recon_score(v)
        self.serial += 1
        heapq.heappush(
            self.queues["recon"],
            (-s, -self.depth[v], -volume, v, self.serial),
        )
        heapq.heappush(
            self.queues["breadth"],
            (self.depth[v], v, self.serial),
        )
        heapq.heappush(
            self.queues["resurvey"],
            (-len(self.adj.get(v, ())), -self.depth[v], v, self.serial),
        )

    def pop_live(self, name: str) -> int | None:
        q = self.queues[name]
        while q:
            item = heapq.heappop(q)
            u = item[-2]
            if u not in self.expanded:
                return u
        return None

    def choose_strategy(self) -> tuple[str, int | None]:
        for _ in range(len(self.cycle)):
            name = self.cycle[self.cycle_i % len(self.cycle)]
            self.cycle_i += 1
            u = self.pop_live(name)
            if u is not None:
                return name, u
        for name in STRATEGIES:
            u = self.pop_live(name)
            if u is not None:
                return name, u
        return "recon", None

    def _set_weights(self, new: dict[str, float], reason: str, mode: str) -> None:
        old = dict(self.weights)
        self.weights = normalize_weights(new)
        self.cycle = integer_cycle(self.weights)
        self.cycle_i = 0
        changed = any(abs(self.weights[k] - old[k]) > 1e-6 for k in STRATEGIES)
        if changed:
            row = {
                "expansions": self.expansions,
                "from": old,
                "to": dict(self.weights),
                "mode": mode,
                "reason": reason,
            }
            self.controller_switches.append(row)
            self.audit.emit(
                EventType.STRATEGY_OVERRIDE_EXECUTED,
                "strategy_switch",
                **row,
            )
        self.mode = mode

    def _one_zero_controller(self, metrics: dict[str, float]) -> None:
        """1.0: self-aware adaptive control + creativity + revision."""
        y = metrics["yield_rate"]
        dup = metrics["duplicate_rate"]
        improvement = y - self.prev_epoch_yield

        # Self-awareness: explicitly report what the search is doing and how it is going.
        self.audit.emit(
            EventType.SELF_REPORT_FILED,
            "self_awareness",
            version=self.version,
            expansions=self.expansions,
            mode=self.mode,
            weights=self.weights,
            metrics=metrics,
        )

        # Control: productive basins are exploited; deteriorating ones trigger
        # structured alternatives rather than an unconditional fixed schedule.
        if y > 0.72 and dup < 0.20:
            self.stale_epochs = 0
            candidate = {"recon": 0.82, "breadth": 0.10, "resurvey": 0.08}
            self._set_weights(candidate, "high discovery yield; exploit productive basin", "exploit")
        else:
            self.stale_epochs += 1
            # Creativity: generate a legal alternative schedule.
            self.creativity_count += 1
            if dup > 0.32:
                candidate = {"recon": 0.40, "breadth": 0.45, "resurvey": 0.15}
                reason = "duplicate pressure high; creative breadth alternative"
                mode = "creative-breadth"
            elif improvement < -0.08:
                candidate = {"recon": 0.42, "breadth": 0.18, "resurvey": 0.40}
                reason = "yield deteriorated; creative branching-resurvey alternative"
                mode = "creative-resurvey"
            else:
                candidate = {"recon": 0.52, "breadth": 0.24, "resurvey": 0.24}
                reason = "uncertain progress; balanced creative alternative"
                mode = "creative-balanced"
            self._set_weights(candidate, reason, mode)

        # Revision fallback: after sustained dissatisfaction, invert the present
        # ranking emphasis (a practical Ocean analogue of the group half-turn).
        if self.stale_epochs >= 3 and metrics["dissatisfaction"] > 0.45:
            inv = {k: 1.0 / max(self.weights[k], 1e-4) for k in STRATEGIES}
            self.revision_count += 1
            self._set_weights(inv, "sustained dissatisfaction; inverse-emphasis revision", "revision")
            self.stale_epochs = 0

        self.prev_epoch_yield = y

    def _install_eight_agent_controller(self, path: Path) -> None:
        p8 = load_module("predator8_038_ocean_adapter", path)
        groups = {k: p8.GroupCoordinate.logit(k) for k in STRATEGIES}
        preferences = {
            "P1": {"recon": .82, "breadth": .10, "resurvey": .08},
            "P2": {"recon": .68, "breadth": .20, "resurvey": .12},
            "R1": {"recon": .16, "breadth": .14, "resurvey": .70},
            "R2": {"recon": .22, "breadth": .18, "resurvey": .60},
            "I1": {"recon": .16, "breadth": .70, "resurvey": .14},
            "I2": {"recon": .22, "breadth": .60, "resurvey": .18},
            "C1": {"recon": .34, "breadth": .33, "resurvey": .33},
            "C2": {"recon": .33, "breadth": .34, "resurvey": .33},
        }
        policies = {}
        for agent in AGENTS:
            pref = preferences[agent]

            def diagnostic(_trajectory, self=self):
                return float(self.latest_metrics.get("dissatisfaction", 0.0))

            def optimizer(_trajectory, vector, pref=pref):
                # Continuous local refinement toward the role's preferred search regime.
                return {
                    k: min(.999, max(.001, .78 * float(vector[k]) + .22 * float(pref[k])))
                    for k in STRATEGIES
                }

            policies[agent] = p8.AgentRevisionPolicy(
                agent=agent,
                threshold=0.25,
                diagnostic=diagnostic,
                optimizer=optimizer,
                groups=groups,
                verifier=lambda z: int(z.get("V", 1)) if isinstance(z, dict) else 1,
                min_post_revision_steps=2,
            )
        self.eight = p8.EightAgentRevisionFallback(policies)
        self.agent_vectors = {
            a: {k: min(.999, max(.001, preferences[a][k])) for k in STRATEGIES}
            for a in AGENTS
        }

    def _one_one_controller(self, metrics: dict[str, float]) -> None:
        """1.1: 1.0 faculties plus eight-agent deliberation/Counselor/Professor/Learning."""
        # First give 1.1 the full 1.0 controller; it is not deprived of its predecessor.
        self._one_zero_controller(metrics)
        assert self.eight is not None and self.agent_vectors is not None

        self.latest_metrics = dict(metrics)
        state = {
            "V": 1,
            "expansions": self.expansions,
            "yield_rate": metrics["yield_rate"],
            "duplicate_rate": metrics["duplicate_rate"],
            "dissatisfaction": metrics["dissatisfaction"],
        }
        self.trajectory = (self.trajectory + [state])[-8:]
        trajectories = {a: tuple(self.trajectory) for a in AGENTS}
        vectors = {a: dict(self.agent_vectors[a]) for a in AGENTS}
        next_vectors, decisions = self.eight.step_all(trajectories, vectors)
        self.agent_vectors = next_vectors

        # All eight agents speak on one shared pre-BANK bus. Their messages are
        # proposals about search control only, never certified mathematics.
        for agent in AGENTS:
            d = decisions[agent]
            self.agent_messages += 1
            if d.get("mode") == "revision":
                self.revision_count += 1
            self.audit.emit(
                EventType.SELF_REPORT_FILED,
                "agent_message",
                agent=agent,
                channel="shared_pre_bank_deliberation",
                proposal=self.agent_vectors[agent],
                decision=d,
                certified_math=False,
            )

        # Professor: score methods by held-back within-run evidence from the
        # preceding epoch (new-state yield per expansion), then update a modest
        # utility prior. This changes future ranking proportions but never proof rules.
        rewards = {}
        for k in STRATEGIES:
            n = self.epoch_strategy_expansions.get(k, 0)
            reward = self.epoch_strategy_discoveries.get(k, 0) / max(1, n)
            rewards[k] = reward
            self.learning_utility[k] = 0.82 * self.learning_utility[k] + 0.18 * max(.05, reward)
        self.professor_events += 1
        self.audit.emit(
            EventType.LOCAL_EVIDENCE_DETECTED,
            "professor_review",
            rewards=rewards,
            learned_utility=self.learning_utility,
            authority="method_evaluation_only",
            may_verify=False,
        )

        # Counselor: diagnose the immediate failure mode and provide a bounded
        # advisory multiplier. It cannot bypass control or verification.
        counselor = {k: 1.0 for k in STRATEGIES}
        diagnosis = "continue"
        if metrics["duplicate_rate"] > .30:
            counselor["breadth"] = 1.30
            counselor["recon"] = .90
            diagnosis = "duplicate pressure; widen breadth coverage"
        elif metrics["yield_rate"] < .55:
            counselor["resurvey"] = 1.25
            counselor["recon"] = .92
            diagnosis = "low discovery yield; inspect alternate branching basins"
        elif metrics["yield_rate"] > .78:
            counselor["recon"] = 1.15
            diagnosis = "productive basin; maintain focused reconnaissance"
        self.counselor_events += 1
        self.audit.emit(
            EventType.DIRECTIVE_RECEIVED,
            "counselor_advice",
            diagnosis=diagnosis,
            multiplier=counselor,
            authority="advisory_only",
        )

        # Learning + deliberation aggregation. Each agent has an equal voice;
        # Professor and Counselor only modulate the aggregate, not certify it.
        aggregate = {k: 0.0 for k in STRATEGIES}
        for a in AGENTS:
            for k in STRATEGIES:
                aggregate[k] += float(self.agent_vectors[a][k]) / len(AGENTS)
        learned = {
            k: aggregate[k] * self.learning_utility[k] * counselor[k]
            for k in STRATEGIES
        }
        self.learning_events += 1
        self.audit.emit(
            EventType.STRATEGY_OVERRIDE_PROPOSED,
            "learning_update",
            aggregate_agent_proposal=aggregate,
            professor_utility=self.learning_utility,
            counselor_multiplier=counselor,
            resulting_schedule=normalize_weights(learned),
            verifier_authority=False,
        )
        self._set_weights(
            learned,
            "eight-agent deliberation + Professor + Counselor + Learning",
            "1.1-deliberative-adaptive",
        )

        self.epoch_strategy_expansions.clear()
        self.epoch_strategy_discoveries.clear()

    def control(self, epoch_start_exp: int, epoch_start_discoveries: int,
                epoch_start_duplicates: int) -> None:
        n_exp = max(1, self.expansions - epoch_start_exp)
        n_new = max(0, self.discoveries - epoch_start_discoveries)
        n_dup = max(0, self.duplicates - epoch_start_duplicates)
        y = n_new / n_exp
        dup = n_dup / n_exp
        frontier_live_est = max(0, len(self.parent) - len(self.expanded))
        dissatisfaction = min(1.0, max(0.0, (1.0 - y) * .70 + dup * .30))
        metrics = {
            "yield_rate": y,
            "duplicate_rate": dup,
            "frontier_live_estimate": float(frontier_live_est),
            "dissatisfaction": dissatisfaction,
        }
        self.latest_metrics = dict(metrics)
        if self.version == "1.0":
            self._one_zero_controller(metrics)
            self.epoch_strategy_expansions.clear()
            self.epoch_strategy_discoveries.clear()
        else:
            self._one_one_controller(metrics)

    def search(self) -> dict[str, Any]:
        t0 = time.perf_counter()
        epoch_start_exp = 0
        epoch_start_discoveries = self.discoveries
        epoch_start_duplicates = 0

        self.audit.emit(
            EventType.SELF_REPORT_FILED,
            "self_description" if self.version == "1.1" else "run_description",
            architecture=f"DATA-MIND {self.version} Ocean full-feature experimental adapter",
            strategies=list(STRATEGIES),
            agents=list(AGENTS) if self.version == "1.1" else None,
            shared_frontier=True,
            hidden_metadata_read=False,
            verifier_sovereign=True,
        )

        if self.source == self.target:
            return {"status": "PROVED", "path": [self.source], "expansions": 0}

        while self.expansions < self.max_expansions:
            if time.perf_counter() - t0 >= self.time_limit_s:
                return {"status": "TIMEOUT", "path": None, "expansions": self.expansions}

            strategy, u = self.choose_strategy()
            if u is None:
                break
            self.expanded.add(u)
            children = self.adj.get(u, ())
            for v in children:
                self.expansions += 1
                self.strategy_expansions[strategy] += 1
                self.epoch_strategy_expansions[strategy] += 1
                if v not in self.parent:
                    self.parent[v] = u
                    self.depth[v] = self.depth[u] + 1
                    self.discoveries += 1
                    self.strategy_discoveries[strategy] += 1
                    self.epoch_strategy_discoveries[strategy] += 1
                    if v == self.target:
                        path = self.ref.reconstruct(self.parent, self.source, self.target)
                        return {"status": "PROVED", "path": path, "expansions": self.expansions}
                    self._push(v)
                else:
                    self.duplicates += 1

                if self.expansions >= self.max_expansions:
                    break
                if time.perf_counter() - t0 >= self.time_limit_s:
                    return {"status": "TIMEOUT", "path": None, "expansions": self.expansions}

            if self.expansions - epoch_start_exp >= self.control_epoch:
                self.control(epoch_start_exp, epoch_start_discoveries, epoch_start_duplicates)
                epoch_start_exp = self.expansions
                epoch_start_discoveries = self.discoveries
                epoch_start_duplicates = self.duplicates

        return {"status": "BOUNDED_UNKNOWN", "path": None, "expansions": self.expansions}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", choices=["1.0", "1.1"], required=True)
    ap.add_argument("--problem", required=True)
    ap.add_argument("--reference", required=True)
    ap.add_argument("--p8038")
    ap.add_argument("--out", required=True)
    ap.add_argument("--transactions", required=True)
    ap.add_argument("--time-limit", type=float, default=3600.0)
    ap.add_argument("--max-expansions", type=int, default=100_000_000)
    ap.add_argument("--control-epoch", type=int, default=50_000)
    ap.add_argument("--seed", type=int, default=2301)
    a = ap.parse_args()

    problem = Path(a.problem)
    ref = load_module("ocean_reference_full_feature", Path(a.reference))
    parse0 = time.perf_counter()
    source, target, edges, adj, _ = ref.parse_problem(problem)
    parse_wall = time.perf_counter() - parse0

    audit = Audit(Path(a.transactions))
    engine = FullFeatureOcean(
        version=a.version,
        ref=ref,
        source=source,
        target=target,
        edges=edges,
        adj=adj,
        audit=audit,
        time_limit_s=a.time_limit,
        max_expansions=a.max_expansions,
        seed=a.seed,
        p8038_path=Path(a.p8038) if a.p8038 else None,
        control_epoch=a.control_epoch,
    )

    search0 = time.perf_counter()
    result = engine.search()
    search_wall = time.perf_counter() - search0
    path = result.get("path")

    audit.emit(
        EventType.CERTIFICATE_SUBMITTED,
        "bank_proposal",
        status=result.get("status"),
        expansions=result.get("expansions"),
        certified_at_proposal_time=False,
    )
    verify0 = time.perf_counter()
    verified = bool(path is not None and ref.verify_path(source, target, edges, path))
    verify_wall = time.perf_counter() - verify0
    if verified:
        audit.emit(
            EventType.VERIFIER_ACCEPTED,
            "verifier_result",
            accepted=True,
            proof_length=len(path) - 1,
        )
        audit.emit(
            EventType.ACTION_EXECUTED,
            "bank_commit",
            gate="verifier_accepted",
        )
    else:
        audit.emit(
            EventType.VERIFIER_REJECTED,
            "verifier_result",
            accepted=False,
            status=result.get("status"),
        )

    # Never call a failed/timeout search a proof.
    status = "PROVED" if verified else result.get("status", "FAULT")
    tx_ok = audit.log.verify()
    summary = {
        "solver": f"DATA-MIND {a.version} Ocean full-feature experimental adapter",
        "version": a.version,
        "status": status,
        "certificate_verified": verified,
        "proof_length": (len(path) - 1) if verified else None,
        "expansions": result.get("expansions"),
        "discovered_states": len(engine.parent),
        "scoring_edge_probes": engine.scoring_probes,
        "parse_wall_s": parse_wall,
        "search_wall_s": search_wall,
        "verify_wall_s": verify_wall,
        "problem_sha256": sha256_file(problem),
        "time_limit_s": a.time_limit,
        "max_expansions": a.max_expansions,
        "adaptive_search_enabled": True,
        "creativity_enabled": True,
        "revision_enabled": True,
        "controller_switch_count": len(engine.controller_switches),
        "revision_count": engine.revision_count,
        "creativity_count": engine.creativity_count,
        "final_weights": engine.weights,
        "strategy_expansions": dict(engine.strategy_expansions),
        "strategy_discoveries": dict(engine.strategy_discoveries),
        "transaction_log_verified": tx_ok,
        "bank_commit_verifier_gated": bool(verified and audit.counts.get("bank_commit", 0) == 1) if verified else audit.counts.get("bank_commit", 0) == 0,
        "all_eight_agents_enabled": a.version == "1.1",
        "agent_message_count": engine.agent_messages,
        "professor_events": engine.professor_events,
        "counselor_events": engine.counselor_events,
        "learning_events": engine.learning_events,
        "policy_adaptation_from_1_1_modules_enabled": a.version == "1.1",
        "hidden_metadata_read": False,
        "scope_note": (
            "Experimental Ocean-native integration of executable DATA-MIND faculties; "
            "not a claim that the general DATA-MIND architecture is production-complete."
        ),
    }
    Path(a.out).write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)
    if not tx_ok:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
