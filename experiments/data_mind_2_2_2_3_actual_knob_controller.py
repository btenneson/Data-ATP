#!/usr/bin/env python3
"""DATA-MIND 2.2 / 2.3 actual-knob adaptive controller for blind Metamath search.

2.2 and 2.3 share the same proof calculus, verifier boundary, search kernel,
eleven physical R3/I4 search controls, adult optimizer, telemetry, seed and
resource budget.

DATA-MIND 2.2
    Adult-only.  Small bounded updates continuously tune the actual eleven-
    dimensional search-control vector.

DATA-MIND 2.3
    The identical adult controller plus a rare reversible "child" experiment.
    After adult optimization demonstrably fails, the complete live search state
    is checkpointed and the actual knob vector is moved to its coordinatewise
    group inverse.  Adult optimization then gets a long evaluation window in
    the opposite basin.  A failed excursion restores the exact checkpoint.
    Child interventions cannot occur back-to-back: the trial itself is long,
    and every accept/rollback starts an additional cooldown and requires a fresh
    adult-failure diagnosis.

Neither version changes a Metamath rule.  Imagined states remain proposals only.
The workflow independently verifies any emitted certificate before BANK commit.
"""
from __future__ import annotations

import argparse
from collections import defaultdict, deque
from copy import deepcopy
import heapq
import importlib.util
import json
import math
import os
from pathlib import Path
import random
import signal
import sys
import time
from typing import Any

from data_atp.events import EventType, TransactionLog

AGENTS = ("P1", "P2", "R1", "R2", "I1", "I2", "C1", "C2")
KNOBS = (
    "imagine_top",
    "beam",
    "branch_cap",
    "progress_weight",
    "solve_bonus",
    "explore_extra",
    "cap_factor",
    "goal_meta_weight",
    "dv_meta_weight",
    "rhat_weight",
    "diversity_bonus",
)
INTEGER_KNOBS = {"imagine_top", "beam", "branch_cap"}
DYNAMIC_STRATEGY = "DATA_MIND_ACTUAL_11D"

_RUNTIME: dict[str, Any] = {}


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


class ActualKnobController:
    """Two-timescale control on the actual eleven R3/I4 knobs."""

    def __init__(
        self,
        *,
        version: str,
        base6,
        log: TransactionLog,
        control_interval: int = 250,
        adult_step: float = 0.025,
        adult_failure_stale: int = 6000,
        child_trial_expansions: int = 12000,
        child_cooldown_expansions: int = 12000,
        advisory_interval: int = 1000,
    ):
        if version not in {"2.2", "2.3"}:
            raise ValueError("version must be 2.2 or 2.3")
        self.version = version
        self.base6 = base6
        self.log = log
        self.control_interval = max(50, int(control_interval))
        self.adult_step = max(0.001, min(0.10, float(adult_step)))
        self.adult_failure_stale = max(1000, int(adult_failure_stale))
        self.child_trial_expansions = max(4 * self.control_interval, int(child_trial_expansions))
        self.child_cooldown_expansions = max(
            self.child_trial_expansions, int(child_cooldown_expansions)
        )
        self.advisory_interval = max(self.control_interval, int(advisory_interval))

        family = {k: dict(v) for k, v in base6.STRATEGY.items()
                  if k in {"COMPASS", "CERTIFY", "DIVERSIFY", "LEAN"}}
        if len(family) != 4:
            raise RuntimeError("expected frozen COMPASS/CERTIFY/DIVERSIFY/LEAN family")
        self.family = family
        self.bounds = {
            key: (
                min(float(family[name][key]) for name in family),
                max(float(family[name][key]) for name in family),
            )
            for key in KNOBS
        }
        # Both arms begin from the same ordinary COMPASS point.
        self.base_u = self._normalize_vector(family["COMPASS"])
        self.u = dict(self.base_u)
        self._install_vector(self.u)
        self.agent_summaries: list[dict[str, Any]] = []
        self.current_agent: str | None = None
        self._agent_counter_start: dict[str, int] = {}

        self.mode = "ADULT"
        self.last_control_exp = 0
        self.last_advisory_exp = 0
        self.last_terminal_rejects = 0
        self.quality_history: deque[float] = deque(maxlen=12)
        self.best_rhat = math.inf
        self.last_improvement_exp = 0
        self.cooldown_until_exp = 0
        self.fresh_failure_required = True

        self.child_checkpoint_u: dict[str, float] | None = None
        self.child_checkpoint_quality: float | None = None
        self.child_checkpoint_best_rhat: float | None = None
        self.child_checkpoint_quality_history: tuple[float, ...] | None = None
        self.child_checkpoint_last_terminal_rejects: int | None = None
        self.child_checkpoint_last_quality: float | None = None
        self.child_checkpoint_last_dissatisfaction: float | None = None
        self.child_start_exp: int | None = None
        self.child_best_rhat = math.inf
        self.failed_inverse_signatures: set[tuple[float, ...]] = set()

        self.adult_updates = 0
        self.child_trials = 0
        self.child_accepts = 0
        self.child_rollbacks = 0
        self.rekeys = 0
        self.control_samples = 0
        self.last_dissatisfaction = 0.0
        self.last_quality = math.inf
        self.last_action = "initial"

    def begin_agent(self, agent_name: str) -> None:
        """Start each population agent from the same controlled initial point."""
        self.current_agent = str(agent_name)
        self._install_vector(dict(self.base_u))
        self.mode = "ADULT"
        self.last_control_exp = 0
        self.last_advisory_exp = 0
        self.last_terminal_rejects = 0
        self.quality_history.clear()
        self.best_rhat = math.inf
        self.last_improvement_exp = 0
        self.cooldown_until_exp = 0
        self.fresh_failure_required = True
        self.child_checkpoint_u = None
        self.child_checkpoint_quality = None
        self.child_checkpoint_best_rhat = None
        self.child_checkpoint_quality_history = None
        self.child_checkpoint_last_terminal_rejects = None
        self.child_checkpoint_last_quality = None
        self.child_checkpoint_last_dissatisfaction = None
        self.child_start_exp = None
        self.child_best_rhat = math.inf
        self.failed_inverse_signatures.clear()
        self.last_quality = math.inf
        self.last_dissatisfaction = 0.0
        self.last_action = "agent_start"
        self._agent_counter_start = {
            "adult_updates": self.adult_updates,
            "child_trials": self.child_trials,
            "child_accepts": self.child_accepts,
            "child_rollbacks": self.child_rollbacks,
            "rekeys": self.rekeys,
        }
        emit(
            self.log, EventType.SELF_REPORT_FILED, "agent_control_start",
            agent=self.current_agent,
            initial_actual_knob_vector=self.decode_vector(),
            child_inverse_enabled=self.version == "2.3",
            verifier_authority=False,
        )

    def end_agent(self, *, expansions: int, imagined: int, terminal_rejects: int) -> None:
        start = self._agent_counter_start or {}
        data = {
            "agent": self.current_agent,
            "expansions": int(expansions),
            "imagined_states": int(imagined),
            "terminal_rejects": int(terminal_rejects),
            "adult_updates": self.adult_updates - start.get("adult_updates", self.adult_updates),
            "child_trials": self.child_trials - start.get("child_trials", self.child_trials),
            "child_accepts": self.child_accepts - start.get("child_accepts", self.child_accepts),
            "child_rollbacks": self.child_rollbacks - start.get("child_rollbacks", self.child_rollbacks),
            "rekeys": self.rekeys - start.get("rekeys", self.rekeys),
            "ending_knob_vector": self.decode_vector(),
        }
        self.agent_summaries.append(data)
        emit(self.log, EventType.SELF_REPORT_FILED, "agent_control_end", **data)

    def _normalize_value(self, key: str, value: float) -> float:
        lo, hi = self.bounds[key]
        if math.isclose(lo, hi):
            return 0.5
        return min(1.0, max(0.0, (float(value) - lo) / (hi - lo)))

    def _decode_value(self, key: str, u: float):
        lo, hi = self.bounds[key]
        if math.isclose(lo, hi):
            x = lo
        else:
            x = lo + min(1.0, max(0.0, float(u))) * (hi - lo)
        if key in INTEGER_KNOBS:
            return max(1, int(round(x)))
        return float(x)

    def _normalize_vector(self, vec: dict[str, Any]) -> dict[str, float]:
        return {key: self._normalize_value(key, vec[key]) for key in KNOBS}

    def decode_vector(self, uvec: dict[str, float] | None = None) -> dict[str, Any]:
        src = self.u if uvec is None else uvec
        return {key: self._decode_value(key, src[key]) for key in KNOBS}

    def inverse_vector(self, uvec: dict[str, float] | None = None) -> dict[str, float]:
        src = self.u if uvec is None else uvec
        return {key: 1.0 - float(src[key]) for key in KNOBS}

    def _signature(self, uvec: dict[str, float]) -> tuple[float, ...]:
        return tuple(round(float(uvec[k]), 6) for k in KNOBS)

    def _install_vector(self, uvec: dict[str, float]) -> None:
        self.u = {k: min(1.0, max(0.0, float(v))) for k, v in uvec.items()}
        self.base6.STRATEGY[DYNAMIC_STRATEGY] = self.decode_vector(self.u)

    def _bounded_move(self, key: str, delta: float) -> None:
        d = max(-self.adult_step, min(self.adult_step, float(delta)))
        self.u[key] = min(1.0, max(0.0, self.u[key] + d))

    def _quality(
        self,
        *,
        live_rhat: float,
        dup_rate: float,
        terminal_delta: int,
        frontier_size: int,
        imagined_delta: int,
    ) -> float:
        # Lower is better.  Unlike the old dissatisfaction score, this is not
        # clipped at 1: worsening duplication / illegal endings / cost remains
        # visible after a long stall.
        reject_pressure = math.log1p(max(0, terminal_delta))
        frontier_pressure = math.log1p(max(0, frontier_size)) / 20.0
        imagination_pressure = math.log1p(max(0, imagined_delta)) / 30.0
        return (
            float(live_rhat)
            + 0.70 * max(0.0, float(dup_rate))
            + 0.12 * reject_pressure
            + 0.04 * frontier_pressure
            + 0.03 * imagination_pressure
        )

    def _dissatisfaction(self, *, stale: int, quality: float) -> float:
        # Intentionally unsaturated: this continues to distinguish 6k, 20k,
        # and 60k stale trajectories.
        trend = 0.0
        if len(self.quality_history) >= 6:
            early = sum(list(self.quality_history)[:3]) / 3.0
            late = sum(list(self.quality_history)[-3:]) / 3.0
            trend = max(0.0, late - early)
        return math.log1p(max(0, int(stale)) / 1000.0) + 2.0 * trend + max(0.0, quality - 1.0)

    def _adult_failure(self, stale: int) -> bool:
        if stale < self.adult_failure_stale or len(self.quality_history) < 8:
            return False
        h = list(self.quality_history)
        old = sum(h[-8:-4]) / 4.0
        new = sum(h[-4:]) / 4.0
        # "Demonstrably failed" means a long no-rhat-improvement interval plus
        # no material rolling-quality improvement.
        return new >= old - 0.005

    def _adult_update(
        self,
        *,
        stale: int,
        dup_rate: float,
        terminal_delta: int,
        rhat_improved: bool,
    ) -> None:
        # Target-generic small local adjustments in normalized coordinates.
        dup = max(0.0, min(1.0, float(dup_rate)))
        cert = 1.0 - math.exp(-max(0, terminal_delta) / 4.0)
        stall = math.tanh(max(0, int(stale)) / 6000.0)
        progress = 1.0 if rhat_improved else 0.0

        # Repeated / saturated search -> slightly more real diversity.
        self._bounded_move("explore_extra", self.adult_step * (0.60 * stall + 0.90 * dup - 0.35 * progress))
        self._bounded_move("diversity_bonus", self.adult_step * (0.55 * stall + 0.75 * dup - 0.25 * progress))
        self._bounded_move("cap_factor", self.adult_step * (0.40 * stall + 0.45 * dup - 0.20 * cert))

        # Illegal terminal closures -> gently favor certifiability and reduce
        # expensive seductive imagination.
        self._bounded_move("dv_meta_weight", self.adult_step * (0.95 * cert - 0.10 * progress))
        self._bounded_move("goal_meta_weight", self.adult_step * (0.55 * cert - 0.10 * progress))
        self._bounded_move("solve_bonus", self.adult_step * (-0.60 * cert + 0.25 * progress))
        self._bounded_move("progress_weight", self.adult_step * (-0.30 * cert + 0.25 * progress))

        imagination_brake = 0.50 * dup + 0.50 * cert + 0.25 * stall
        self._bounded_move("imagine_top", -self.adult_step * imagination_brake + self.adult_step * 0.20 * progress)
        self._bounded_move("beam", -self.adult_step * imagination_brake + self.adult_step * 0.15 * progress)
        self._bounded_move("branch_cap", -self.adult_step * imagination_brake + self.adult_step * 0.15 * progress)

        # Keep settlement distance important while progress is real; relax it
        # slightly when a long stalled basin is being diversified.
        self._bounded_move("rhat_weight", self.adult_step * (0.35 * progress - 0.30 * stall - 0.20 * dup))

        self._install_vector(self.u)
        self.adult_updates += 1

    def _advisory_messages(self, exp: int, stale: int, dup_rate: float, terminal_rejects: int) -> None:
        if exp - self.last_advisory_exp < self.advisory_interval:
            return
        self.last_advisory_exp = exp
        decoded = self.decode_vector()
        for agent in AGENTS:
            emit(
                self.log,
                EventType.SELF_REPORT_FILED,
                "agent_message",
                agent=agent,
                channel="shared_pre_bank_advisory",
                mode=self.mode,
                stale=int(stale),
                duplicate_rate=float(dup_rate),
                terminal_rejects=int(terminal_rejects),
                knob_vector=decoded,
                may_change_knobs=False,
                may_verify=False,
            )
        emit(
            self.log,
            EventType.SELF_REPORT_FILED,
            "counselor_advice",
            advice=("continue subtle adult tuning" if self.mode == "ADULT"
                    else "protect the child trial from a second child intervention"),
            authority="advisory_only",
            may_change_knobs=False,
            may_verify=False,
        )
        emit(
            self.log,
            EventType.SELF_REPORT_FILED,
            "professor_review",
            evaluation=("adult_local_control" if self.mode == "ADULT"
                        else "inverse_excursion_under_long_evaluation"),
            authority="teaching_evaluation_only",
            may_change_knobs=False,
            may_verify=False,
        )

    def sample(
        self,
        *,
        exp: int,
        live_rhat: float,
        stale: int,
        dup_rate: float,
        terminal_rejects: int,
        frontier_size: int,
        imagined_total: int,
        imagined_previous: int,
        remaining_budget: int,
    ) -> str:
        """Update adult control and return NONE / START_CHILD / ACCEPT_CHILD / ROLLBACK_CHILD."""
        rhat_improved = live_rhat < self.best_rhat - 1e-12
        if rhat_improved:
            self.best_rhat = float(live_rhat)
            self.last_improvement_exp = int(exp)
            self.fresh_failure_required = True

        self._advisory_messages(exp, stale, dup_rate, terminal_rejects)
        if exp - self.last_control_exp < self.control_interval:
            return "NONE"

        terminal_delta = max(0, int(terminal_rejects) - int(self.last_terminal_rejects))
        imagined_delta = max(0, int(imagined_total) - int(imagined_previous))
        quality = self._quality(
            live_rhat=live_rhat,
            dup_rate=dup_rate,
            terminal_delta=terminal_delta,
            frontier_size=frontier_size,
            imagined_delta=imagined_delta,
        )
        self.quality_history.append(quality)
        self.last_quality = quality
        self.last_dissatisfaction = self._dissatisfaction(stale=stale, quality=quality)
        self.last_control_exp = int(exp)
        self.last_terminal_rejects = int(terminal_rejects)
        self.control_samples += 1

        before = self.decode_vector()
        self._adult_update(
            stale=stale,
            dup_rate=dup_rate,
            terminal_delta=terminal_delta,
            rhat_improved=rhat_improved,
        )
        after = self.decode_vector()
        emit(
            self.log,
            EventType.SELF_REPORT_FILED,
            "adult_knob_update",
            version=self.version,
            expansion=int(exp),
            mode=self.mode,
            quality=quality,
            dissatisfaction=self.last_dissatisfaction,
            stale=int(stale),
            duplicate_rate=float(dup_rate),
            terminal_reject_delta=terminal_delta,
            before=before,
            after=after,
            max_normalized_step=self.adult_step,
            actual_physical_knobs=True,
        )

        if self.version == "2.2":
            self.last_action = "adult_only"
            return "NONE"

        if self.mode == "CHILD_TRIAL":
            self.child_best_rhat = min(self.child_best_rhat, float(live_rhat))
            assert self.child_start_exp is not None
            if exp - self.child_start_exp >= self.child_trial_expansions:
                baseline_rhat = (
                    self.child_checkpoint_best_rhat
                    if self.child_checkpoint_best_rhat is not None
                    else math.inf
                )
                baseline_quality = (
                    self.child_checkpoint_quality
                    if self.child_checkpoint_quality is not None
                    else math.inf
                )
                improved = (
                    self.child_best_rhat < baseline_rhat - 1e-12
                    or quality < baseline_quality - 0.02
                )
                if improved:
                    self.mode = "ADULT"
                    self.cooldown_until_exp = exp + self.child_cooldown_expansions
                    self.fresh_failure_required = False
                    self.child_accepts += 1
                    self.last_action = "accept_child"
                    emit(
                        self.log,
                        EventType.ACTION_EXECUTED,
                        "child_excursion_accepted",
                        expansion=int(exp),
                        trial_expansions=int(exp - self.child_start_exp),
                        baseline_rhat=baseline_rhat,
                        child_best_rhat=self.child_best_rhat,
                        baseline_quality=baseline_quality,
                        ending_quality=quality,
                        cooldown_until_expansion=self.cooldown_until_exp,
                        verifier_authority=False,
                    )
                    return "ACCEPT_CHILD"
                self.last_action = "rollback_child"
                return "ROLLBACK_CHILD"
            self.last_action = "child_trial_adult_refinement"
            return "NONE"

        failure = self._adult_failure(stale)
        if exp >= self.cooldown_until_exp and not self.fresh_failure_required:
            # A long adult-only interval has elapsed since the last child
            # decision.  Re-arm only now; this is the fresh-trial barrier.
            self.fresh_failure_required = True

        if (
            failure
            and exp >= self.cooldown_until_exp
            and self.fresh_failure_required
            and int(remaining_budget) >= self.child_trial_expansions
        ):
            inverse = self.inverse_vector(self.u)
            sig = self._signature(inverse)
            if sig not in self.failed_inverse_signatures:
                self.child_checkpoint_u = dict(self.u)
                self.child_checkpoint_quality = float(quality)
                self.child_checkpoint_best_rhat = float(self.best_rhat)
                self.child_checkpoint_quality_history = tuple(self.quality_history)
                self.child_checkpoint_last_terminal_rejects = int(self.last_terminal_rejects)
                self.child_checkpoint_last_quality = float(self.last_quality)
                self.child_checkpoint_last_dissatisfaction = float(self.last_dissatisfaction)
                self.child_start_exp = int(exp)
                self.child_best_rhat = math.inf
                self.mode = "CHILD_TRIAL"
                self.child_trials += 1
                self.fresh_failure_required = False
                self._install_vector(inverse)
                self.last_action = "start_child"
                emit(
                    self.log,
                    EventType.ACTION_EXECUTED,
                    "child_inverse_excursion_started",
                    expansion=int(exp),
                    checkpoint_vector=self.decode_vector(self.child_checkpoint_u),
                    inverse_vector=self.decode_vector(inverse),
                    trial_expansions=self.child_trial_expansions,
                    child_reentry_forbidden_until_trial_complete=True,
                    verifier_authority=False,
                )
                return "START_CHILD"

        self.last_action = "adult_refinement"
        return "NONE"

    def rollback_child(self, *, exp: int) -> None:
        if self.child_checkpoint_u is None:
            raise RuntimeError("rollback requested without child checkpoint")
        failed_sig = self._signature(self.inverse_vector(self.child_checkpoint_u))
        self.failed_inverse_signatures.add(failed_sig)
        self._install_vector(self.child_checkpoint_u)
        if self.child_checkpoint_best_rhat is not None:
            self.best_rhat = float(self.child_checkpoint_best_rhat)
        if self.child_checkpoint_quality_history is not None:
            self.quality_history = deque(self.child_checkpoint_quality_history, maxlen=12)
        if self.child_checkpoint_last_terminal_rejects is not None:
            self.last_terminal_rejects = int(self.child_checkpoint_last_terminal_rejects)
        if self.child_checkpoint_last_quality is not None:
            self.last_quality = float(self.child_checkpoint_last_quality)
        if self.child_checkpoint_last_dissatisfaction is not None:
            self.last_dissatisfaction = float(self.child_checkpoint_last_dissatisfaction)
        self.mode = "ADULT"
        self.cooldown_until_exp = int(exp) + self.child_cooldown_expansions
        self.fresh_failure_required = False
        self.child_rollbacks += 1
        emit(
            self.log,
            EventType.ACTION_EXECUTED,
            "child_excursion_rolled_back",
            expansion=int(exp),
            restored_vector=self.decode_vector(self.child_checkpoint_u),
            failed_inverse_signature=failed_sig,
            cooldown_until_expansion=self.cooldown_until_exp,
            same_inverse_blocked=True,
            verifier_authority=False,
        )

    def note_rekey(self) -> None:
        self.rekeys += 1

    def summary(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "actual_11d_knob_control": True,
            "adult_continuous_local_optimization": True,
            "adult_max_normalized_step": self.adult_step,
            "adult_failure_stale": self.adult_failure_stale,
            "dissatisfaction_unsaturated": True,
            "control_interval_expansions": self.control_interval,
            "adult_updates": self.adult_updates,
            "control_samples": self.control_samples,
            "rekeys": self.rekeys,
            "last_quality": self.last_quality if math.isfinite(self.last_quality) else None,
            "last_dissatisfaction": self.last_dissatisfaction,
            "mode_at_end": self.mode,
            "current_knob_vector": self.decode_vector(),
            "child_inverse_enabled": self.version == "2.3",
            "child_trial_expansions": self.child_trial_expansions if self.version == "2.3" else None,
            "child_cooldown_expansions": self.child_cooldown_expansions if self.version == "2.3" else None,
            "child_trials": self.child_trials,
            "child_accepts": self.child_accepts,
            "child_rollbacks": self.child_rollbacks,
            "failed_inverse_regions": len(self.failed_inverse_signatures),
            "full_search_state_checkpoint_and_rollback": self.version == "2.3",
            "no_consecutive_child_interventions": self.version == "2.3",
            "five_strategy_labels_are_not_adaptive_object": True,
            "eight_agents_advisory_only": True,
            "counselor_professor_advisory_only": True,
            "verifier_sovereign": True,
            "agent_summaries": list(self.agent_summaries),
        }


def make_prover(base7, controller: ActualKnobController):
    BASE6 = base7.BASE6
    BASE5 = BASE6.BASE5
    R3I4 = BASE6.R3I4
    P8 = BASE6.P8
    COMP = BASE6.COMP

    def rekey(frontier, dv_by_node):
        controller._install_vector(controller.u)
        out = BASE6._rekey_frontier(frontier, dv_by_node, DYNAMIC_STRATEGY)
        controller.note_rekey()
        return out

    def snapshot_search_state(
        frontier, dv_by_node, seen, rng, local_use, shared_use,
        tie, meta_before_current, improvement_marker_before_current,
        dv_final_since_improvement_before_current, current_entry, current_node,
        current_node_dv
    ):
        # The active popped node is put back into the checkpoint so rollback
        # truly resumes from the pre-child search state rather than silently
        # losing the boundary node that diagnosed failure.
        frontier_copy = list(frontier)
        frontier_copy.append(current_entry)
        heapq.heapify(frontier_copy)
        dv_copy = dict(dv_by_node)
        dv_copy[current_node] = current_node_dv
        return {
            "frontier": frontier_copy,
            "dv_by_node": dv_copy,
            "seen": set(seen),
            "rng_state": rng.getstate(),
            "local_use": dict(local_use),
            "shared_use": dict(shared_use),
            "tie": int(tie),
            "meta": deepcopy(meta_before_current),
            "improvement_marker": int(improvement_marker_before_current),
            "dv_final_since_improvement": int(dv_final_since_improvement_before_current),
        }

    def restore_search_state(snap, rng, local_use, shared_use):
        rng.setstate(snap["rng_state"])
        local_use.clear()
        local_use.update(snap["local_use"])
        shared_use.clear()
        shared_use.update(snap["shared_use"])
        return (
            list(snap["frontier"]),
            dict(snap["dv_by_node"]),
            set(snap["seen"]),
            int(snap["tie"]),
            deepcopy(snap["meta"]),
            int(snap["improvement_marker"]),
            int(snap["dv_final_since_improvement"]),
        )

    def prove(goal_tree, index, budget, max_depth, rank=None,
              say=print, progress=2000, max_open=6, profile=None,
              seed=0, shared_use=None, agent_name=None):
        if profile is None:
            profile = P8.Profile("deterministic", 0.0, 0.0, 0.0, 0.0,
                                 0.0, 48, 1.0)
        rng = random.Random(seed)
        local_use = defaultdict(int)
        if shared_use is None:
            shared_use = defaultdict(int)
        agent_name = agent_name or profile.name
        controller.begin_agent(agent_name)

        start = P8.Node([(goal_tree, None, 0)], {}, (), 0)
        start_h = COMP.settlement_distance_hat(start.goals, start.sub)
        controller.best_rhat = min(controller.best_rhat, float(start_h))
        frontier = [(start_h, start_h, start_h, 0.0, 0, 0.0, start)]
        dv_by_node = {start: ()}
        exp = tie = 0
        seen = set()
        t0 = time.perf_counter()
        announced = False
        meta = R3I4.R3Controller()
        total_imagined = 0
        imagined_previous_control = 0
        dv_rejects = 0
        dv_final_rejects = 0
        dv_final_since_improvement = 0
        improvement_marker = 0
        child_search_checkpoint = None

        BASE6.STRATEGY[DYNAMIC_STRATEGY] = controller.decode_vector()

        while frontier and exp < budget:
            meta_before_current = deepcopy(meta)
            improvement_marker_before_current = improvement_marker
            dv_final_since_improvement_before_current = dv_final_since_improvement
            current_entry = heapq.heappop(frontier)
            _fhat, _reachhat, _rhat, _neglegacy, _, g_cost, node = current_entry
            node_dv = dv_by_node.pop(node, ())
            exp += 1
            if not R3I4._dv_ok(node_dv, node.sub):
                dv_rejects += 1
                continue

            live_rhat = COMP.settlement_distance_hat(node.goals, node.sub)
            mode, stale, dup_rate = meta.observe(exp, live_rhat, False)

            if meta.last_improvement != improvement_marker:
                improvement_marker = meta.last_improvement
                dv_final_since_improvement = 0

            action = controller.sample(
                exp=exp,
                live_rhat=live_rhat,
                stale=stale,
                dup_rate=dup_rate,
                terminal_rejects=dv_final_since_improvement,
                frontier_size=len(frontier),
                imagined_total=total_imagined,
                imagined_previous=imagined_previous_control,
                remaining_budget=budget - exp,
            )
            if controller.last_control_exp == exp:
                imagined_previous_control = total_imagined

            if action == "START_CHILD":
                child_search_checkpoint = snapshot_search_state(
                    frontier, dv_by_node, seen, rng, local_use, shared_use,
                    tie, meta_before_current, improvement_marker_before_current,
                    dv_final_since_improvement_before_current, current_entry, node,
                    node_dv
                )
                frontier = rekey(frontier, dv_by_node)
                if say:
                    say("      [%s] DATA-MIND 2.3 CHILD: checkpointed full search state; "
                        "actual 11D knob vector inverted; second child move forbidden for %s expansions"
                        % (agent_name, f"{controller.child_trial_expansions:,}"))
            elif action == "ROLLBACK_CHILD":
                if child_search_checkpoint is None:
                    raise RuntimeError("child rollback requested without search checkpoint")
                (
                    frontier, dv_by_node, seen, tie, meta,
                    improvement_marker, dv_final_since_improvement,
                ) = restore_search_state(
                    child_search_checkpoint, rng, local_use, shared_use
                )
                controller.rollback_child(exp=exp)
                frontier = rekey(frontier, dv_by_node)
                child_search_checkpoint = None
                if say:
                    say("      [%s] DATA-MIND 2.3 CHILD FAILED: exact pre-child search state restored; "
                        "same inverse remembered; cooldown=%s expansions"
                        % (agent_name, f"{controller.child_cooldown_expansions:,}"))
            elif action == "ACCEPT_CHILD":
                child_search_checkpoint = None
                frontier = rekey(frontier, dv_by_node)
                if say:
                    say("      [%s] DATA-MIND 2.3 CHILD ACCEPTED: adult keeps the new basin; "
                        "child cooldown=%s expansions"
                        % (agent_name, f"{controller.child_cooldown_expansions:,}"))
            elif exp == controller.last_control_exp:
                # Adult updated physical knobs; re-key under the new vector.
                frontier = rekey(frontier, dv_by_node)

            sp = BASE6.STRATEGY[DYNAMIC_STRATEGY]

            if not announced and say:
                say("      [%s] DATA-MIND %s actual-knob control active: "
                    "11D adult local optimization%s; verifier unchanged"
                    % (
                        agent_name,
                        controller.version,
                        " + reversible child inverse trials" if controller.version == "2.3" else "",
                    ))
                announced = True

            if progress and say and exp % progress == 0:
                say(
                    "      [%s] %s expansions, %d open, r_hat=%.3f, R3=%s, "
                    "control=%s, stale=%d, dup=%.1f%%, imagined=%s, "
                    "dvfinal=%s, adult=%s, child=%s/%s/%s, D=%.3f, %.0fs"
                    % (
                        agent_name, f"{exp:,}", len(node.goals), live_rhat,
                        mode, controller.mode, stale, 100.0 * dup_rate,
                        f"{total_imagined:,}", f"{dv_final_rejects:,}",
                        f"{controller.adult_updates:,}", controller.child_trials,
                        controller.child_accepts, controller.child_rollbacks,
                        controller.last_dissatisfaction, time.perf_counter() - t0,
                    )
                )

            if not node.goals:
                if not BASE5._terminal_dv_ok(node_dv, node.sub):
                    dv_final_rejects += 1
                    dv_final_since_improvement += 1
                    if say and BASE5._notable_count(dv_final_rejects):
                        say("      [%s] terminal DV rejection #%s after grounding; continuing frontier"
                            % (agent_name, f"{dv_final_rejects:,}"))
                    continue

                root = None
                for parent, ix, st in node.trail:
                    if parent is None:
                        root = st
                    else:
                        parent.subs[ix] = st
                if say:
                    say("      [%s] terminal branch passed final-ground DV gate; "
                        "adult updates=%s, child trials=%s, rollbacks=%s"
                        % (
                            agent_name, f"{controller.adult_updates:,}",
                            controller.child_trials, controller.child_rollbacks,
                        ))
                controller.end_agent(
                    expansions=exp, imagined=total_imagined,
                    terminal_rejects=dv_final_rejects,
                )
                return (root, node.sub), exp

            if node.depth >= max_depth or len(node.goals) > max_open:
                continue

            gi = P8.pick_goal(node.goals, node.sub)
            gt, slot, hix = node.goals[gi]
            rest = node.goals[:gi] + node.goals[gi + 1:]
            gt = P8.apply_sub(gt, node.sub)

            key = (
                node.depth,
                " ".join(gt.tokens()),
                tuple(sorted(
                    " ".join(P8.apply_sub(g, node.sub).tokens())
                    for g, _, _ in rest
                )),
            )
            if key in seen:
                meta.observe(exp, live_rhat, True)
                continue
            seen.add(key)

            closers, openers = index.candidates(gt)
            legacy_c = COMP._legacy_scores(
                gt, closers, profile, rng, local_use, shared_use
            )
            legacy_o = COMP._legacy_scores(
                gt, openers, profile, rng, local_use, shared_use
            )
            chosen_openers = BASE6._select_openers_switch(
                openers, len(rest), legacy_o, profile, rng, DYNAMIC_STRATEGY
            )
            pick = [(legacy_c.get(item[0], 0.0), item) for item in closers]
            pick += [(legacy_o.get(item[0], 0.0), item) for item in chosen_openers]
            pick.sort(key=lambda pair: (
                COMP._pre_distance(len(rest), pair[1]), -pair[0], pair[1][0]
            ))

            ranked_opener_labels = [item[0] for _score, item in pick if item[2][2]]
            imagine_labels = set(ranked_opener_labels[:sp["imagine_top"]])

            for legacy_score, (lab, ct, data) in pick:
                m = {}
                c2 = P8.rename_apart(ct, m)
                s2 = P8.unify(c2, gt, node.sub)
                if s2 is None:
                    continue
                _dv, f_hyps, e_hyps, _concl = data
                fmap = {
                    var: m.get(var, P8.fresh(tc))
                    for _fh, tc, var in f_hyps
                }
                for _fh, tc, var in f_hyps:
                    m.setdefault(var, fmap[var])

                successor_dv = node_dv + R3I4._dv_obligations(data, m)
                if not R3I4._dv_ok(successor_dv, s2):
                    dv_rejects += 1
                    continue

                step = P8.Step(lab, fmap, data)
                newgoals = []
                ok = True
                for hj, (_ename, stat) in enumerate(e_hyps):
                    try:
                        ht = P8.G.parse(stat[1:], "wff", index.by_tc)
                    except (RecursionError, P8.MMError):
                        ht = None
                    if ht is None:
                        ok = False
                        break
                    newgoals.append((P8.rename_apart(ht, m), step, hj))
                if not ok:
                    continue

                successor_goals = newgoals + rest
                if len(successor_goals) > max_open:
                    continue
                successor = P8.Node(
                    successor_goals, s2,
                    node.trail + ((slot, hix, step),),
                    node.depth + 1,
                )
                dv_by_node[successor] = successor_dv
                new_g = g_cost + 1.0
                rhat = COMP.settlement_distance_hat(successor_goals, s2)
                reachhat = rhat

                if lab in imagine_labels and successor_goals:
                    best_future, solved4, best_d, nim = R3I4.reasoned_imagination4(
                        successor_goals, s2, index, max_open,
                        beam_width=sp["beam"], branch_cap=sp["branch_cap"]
                    )
                    total_imagined += nim
                    progress4 = max(0.0, rhat - best_future)
                    reachhat = (
                        rhat
                        - sp["progress_weight"] * progress4
                        - (sp["solve_bonus"] if solved4 else 0.0)
                        + 0.03 * best_d
                    )

                goal_metas = BASE6._goal_meta_count(successor_goals, s2)
                dv_metas = BASE6._dv_meta_count(successor_dv, s2)
                local_use[lab] += 1
                shared_use[lab] += 1
                tie += 1

                fhat = (
                    new_g + sp["rhat_weight"] * reachhat
                    + sp["goal_meta_weight"] * goal_metas
                    + sp["dv_meta_weight"] * dv_metas
                    - sp["diversity_bonus"] * BASE6._diversity_fraction(successor)
                )
                heapq.heappush(
                    frontier,
                    (fhat, reachhat, rhat, -legacy_score, tie, new_g, successor),
                )

        if say:
            say(
                "      [%s] search ended: adult updates=%s, child trials=%s, "
                "accepts=%s, rollbacks=%s, imagined states=%s"
                % (
                    agent_name, f"{controller.adult_updates:,}",
                    controller.child_trials, controller.child_accepts,
                    controller.child_rollbacks, f"{total_imagined:,}",
                )
            )
        controller.end_agent(
            expansions=exp, imagined=total_imagined,
            terminal_rejects=dv_final_rejects,
        )
        return None, exp

    return prove


def _selftest_controller(controller: ActualKnobController) -> None:
    original = dict(controller.u)
    inv = controller.inverse_vector(original)
    twice = controller.inverse_vector(inv)
    if any(not math.isclose(original[k], twice[k], abs_tol=1e-12) for k in KNOBS):
        raise SystemExit("11D group inverse involution self-test failed")
    if set(controller.decode_vector()) != set(KNOBS):
        raise SystemExit("decoded physical knob vector is incomplete")
    for key, value in controller.decode_vector().items():
        lo, hi = controller.bounds[key]
        if not (lo - 1e-12 <= float(value) <= hi + 1e-12):
            raise SystemExit(f"{key}: decoded knob outside frozen legal bounds")
    print("[DATA-MIND 2.x SELFTEST] 11D inverse involution, bounds, and decode: passed")


def write_summary(path: Path, controller: ActualKnobController, *, target: str, rc: int | None) -> None:
    data = controller.summary()
    data.update({
        "solver": f"DATA-MIND {controller.version}",
        "target": target,
        "search_returncode": rc,
        "shared_kernel": "Predator 8.007 R3/I4 DV-coherent search kernel",
        "candidate_is_proposal_only": True,
        "independent_verifier_required_for_bank": True,
        "controlled_difference": (
            "2.3 adds checkpointed reversible actual-11D group-inverse child excursions; "
            "2.2 is the identical adult controller without child authority"
        ),
    })
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", choices=["2.2", "2.3"], required=True)
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
    ap.add_argument("--control-interval", type=int, default=250)
    ap.add_argument("--adult-step", type=float, default=.025)
    ap.add_argument("--adult-failure-stale", type=int, default=6000)
    ap.add_argument("--child-trial-expansions", type=int, default=12000)
    ap.add_argument("--child-cooldown-expansions", type=int, default=12000)
    ap.add_argument("--out", required=True)
    ap.add_argument("--transactions", required=True)
    ap.add_argument("--summary", required=True)
    a = ap.parse_args()

    atp_root = Path(a.atp_root).resolve()
    kernel_path = atp_root / "predator 8" / "predator 8.007-R3I4-dvcoherent-imagination.py"
    if not kernel_path.exists():
        raise SystemExit(f"missing pinned kernel: {kernel_path}")

    sys.path.insert(0, str(atp_root))
    sys.path.insert(0, str(kernel_path.parent))
    kernel = load_module("data_mind_2x_kernel", kernel_path)
    BASE6 = kernel.BASE6
    P8 = kernel.P8

    log = TransactionLog(a.transactions)
    emit(
        log, EventType.SELF_REPORT_FILED, "self_description",
        architecture=f"DATA-MIND {a.version}",
        target=a.target,
        actual_11d_knob_control=True,
        adult_controller_same_in_2_2_and_2_3=True,
        child_inverse_enabled=a.version == "2.3",
        five_strategy_labels_advisory_only=True,
        eight_agents_advisory_only=True,
        verifier_external_and_sovereign=True,
        target_specific_tuning=False,
    )

    controller = ActualKnobController(
        version=a.version,
        base6=BASE6,
        log=log,
        control_interval=a.control_interval,
        adult_step=a.adult_step,
        adult_failure_stale=a.adult_failure_stale,
        child_trial_expansions=a.child_trial_expansions,
        child_cooldown_expansions=a.child_cooldown_expansions,
    )
    _selftest_controller(controller)
    P8.prove = make_prover(kernel, controller)

    summary_path = Path(a.summary).resolve()
    _RUNTIME.update(controller=controller, summary_path=summary_path, target=a.target)

    def on_term(_signum, _frame):
        write_summary(summary_path, controller, target=a.target, rc=124)
        raise SystemExit(124)

    signal.signal(signal.SIGTERM, on_term)

    emit(
        log, EventType.ACTION_PROPOSED, "search_start",
        version=a.version,
        budget=a.budget,
        max_depth=a.max_depth,
        agents=a.agents,
        creativity=a.creativity,
        seed=a.seed,
        opener_cap=a.opener_cap,
        max_open=a.max_open,
        actual_knob_vector=controller.decode_vector(),
        certificate_authority=False,
    )

    old_argv = sys.argv[:]
    sys.argv = [
        str(kernel_path), "prove", str(Path(a.setmm).resolve()),
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
        rc = int(kernel.main() or 0)
    finally:
        sys.argv = old_argv

    candidate = Path(a.out)
    if candidate.exists() and candidate.stat().st_size:
        emit(
            log, EventType.CERTIFICATE_SUBMITTED, "bank_proposal",
            target=a.target,
            candidate_path=str(candidate),
            certified_at_proposal_time=False,
            independent_verification_pending=True,
        )

    write_summary(summary_path, controller, target=a.target, rc=rc)
    print("DATA_MIND_2X_SUMMARY")
    print(summary_path.read_text(encoding="utf-8"), flush=True)
    if not log.verify():
        raise SystemExit("transaction log failed hash-chain verification")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
