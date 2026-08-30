#!/usr/bin/env python3
"""DATA-MIND 2.2/2.3 readiness tightening.

This wrapper preserves the actual-search implementation in
``data_mind_2_2_2_3_actual_knob_controller.py`` while tightening three pieces
before the long experiment:

1. The eleven latent coordinates live strictly in (0,1) and use the logit
   product group.  Coordinatewise inverse is exactly u -> 1-u.  A small affine
   interior embedding maps the legal physical interval endpoints to epsilon and
   1-epsilon, so the decoded physical opposite is still exact.
2. Every adult update records latent before/after/delta as well as the executed
   (possibly rounded) physical knob vector.
3. A child excursion is accepted for quality only after sustained rolling
   improvement.  One lucky final quality sample is insufficient.  A genuine
   r_hat improvement remains independently sufficient.

Verifier sovereignty, Metamath rules, BANK gating, the shared adult controller,
and the 2.2-vs-2.3 controlled difference are unchanged.
"""
from __future__ import annotations

from collections import deque
import importlib.util
import math
from pathlib import Path
import sys
from typing import Any

HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "data_mind_2_2_2_3_actual_knob_controller.py"
spec = importlib.util.spec_from_file_location("data_mind_2x_base", BASE_PATH)
if spec is None or spec.loader is None:
    raise SystemExit(f"cannot load base controller: {BASE_PATH}")
BASE = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = BASE
spec.loader.exec_module(BASE)

KNOBS = BASE.KNOBS
INTEGER_KNOBS = BASE.INTEGER_KNOBS
EventType = BASE.EventType
emit = BASE.emit

LATENT_EPS = 1e-6
QUALITY_WINDOW = 4
QUALITY_MARGIN = 0.02
QUALITY_POINT_MARGIN = 0.01
QUALITY_REQUIRED_POINTS = 3


def _logit(x: float) -> float:
    return math.log(float(x) / (1.0 - float(x)))


def _logistic(x: float) -> float:
    if x >= 0.0:
        e = math.exp(-x)
        return 1.0 / (1.0 + e)
    e = math.exp(x)
    return e / (1.0 + e)


def logit_group_compose(a: float, b: float) -> float:
    """Group law on (0,1), with identity 1/2 and inverse 1-u."""
    a = float(a)
    b = float(b)
    if not (0.0 < a < 1.0 and 0.0 < b < 1.0):
        raise ValueError("logit group coordinates must be strictly inside (0,1)")
    return _logistic(_logit(a) + _logit(b))


class ExactGroupActualKnobController(BASE.ActualKnobController):
    """Actual 11D controller with exact latent group semantics."""

    def __init__(self, *args, **kwargs):
        self.latent_eps = LATENT_EPS
        self.child_quality_samples: deque[float] = deque(maxlen=8)
        self.child_checkpoint_quality_window_mean: float | None = None
        super().__init__(*args, **kwargs)

    def begin_agent(self, agent_name: str) -> None:
        super().begin_agent(agent_name)
        self.child_quality_samples.clear()
        self.child_checkpoint_quality_window_mean = None

    def _normalize_value(self, key: str, value: float) -> float:
        lo, hi = self.bounds[key]
        if math.isclose(lo, hi):
            return 0.5
        physical_u = min(1.0, max(0.0, (float(value) - lo) / (hi - lo)))
        return self.latent_eps + (1.0 - 2.0 * self.latent_eps) * physical_u

    def _decode_value(self, key: str, u: float):
        lo, hi = self.bounds[key]
        if math.isclose(lo, hi):
            x = lo
        else:
            latent = min(1.0 - self.latent_eps, max(self.latent_eps, float(u)))
            physical_u = (latent - self.latent_eps) / (1.0 - 2.0 * self.latent_eps)
            x = lo + min(1.0, max(0.0, physical_u)) * (hi - lo)
        if key in INTEGER_KNOBS:
            return max(1, int(round(x)))
        return float(x)

    def inverse_vector(self, uvec: dict[str, float] | None = None) -> dict[str, float]:
        src = self.u if uvec is None else uvec
        return {key: 1.0 - float(src[key]) for key in KNOBS}

    def _install_vector(self, uvec: dict[str, float]) -> None:
        cleaned: dict[str, float] = {}
        for key, value in uvec.items():
            lo, hi = self.bounds[key]
            if math.isclose(lo, hi):
                cleaned[key] = 0.5
            else:
                cleaned[key] = min(
                    1.0 - self.latent_eps,
                    max(self.latent_eps, float(value)),
                )
        self.u = cleaned
        self.base6.STRATEGY[BASE.DYNAMIC_STRATEGY] = self.decode_vector(self.u)

    def _bounded_move(self, key: str, delta: float) -> None:
        lo, hi = self.bounds[key]
        if math.isclose(lo, hi):
            self.u[key] = 0.5
            return
        d = max(-self.adult_step, min(self.adult_step, float(delta)))
        self.u[key] = min(
            1.0 - self.latent_eps,
            max(self.latent_eps, self.u[key] + d),
        )

    def _window_mean(self, values) -> float:
        seq = list(values)
        if not seq:
            return math.inf
        return sum(seq) / len(seq)

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
        """Adult update plus strict reversible child evaluation."""
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

        before_latent = dict(self.u)
        before_executed = self.decode_vector()
        self._adult_update(
            stale=stale,
            dup_rate=dup_rate,
            terminal_delta=terminal_delta,
            rhat_improved=rhat_improved,
        )
        after_latent = dict(self.u)
        after_executed = self.decode_vector()
        latent_delta = {
            key: float(after_latent[key]) - float(before_latent[key])
            for key in KNOBS
        }
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
            latent_before=before_latent,
            latent_after=after_latent,
            latent_delta=latent_delta,
            executed_before=before_executed,
            executed_after=after_executed,
            latent_group="logit_product_group",
            latent_group_identity=0.5,
            latent_domain=f"({self.latent_eps}, {1.0-self.latent_eps}) embedded in (0,1)",
            max_normalized_step=self.adult_step,
            actual_physical_knobs=True,
        )

        if self.version == "2.2":
            self.last_action = "adult_only"
            return "NONE"

        if self.mode == "CHILD_TRIAL":
            self.child_best_rhat = min(self.child_best_rhat, float(live_rhat))
            self.child_quality_samples.append(float(quality))
            assert self.child_start_exp is not None
            if exp - self.child_start_exp >= self.child_trial_expansions:
                baseline_rhat = (
                    self.child_checkpoint_best_rhat
                    if self.child_checkpoint_best_rhat is not None
                    else math.inf
                )
                baseline_window = (
                    self.child_checkpoint_quality_window_mean
                    if self.child_checkpoint_quality_window_mean is not None
                    else math.inf
                )
                recent = list(self.child_quality_samples)[-QUALITY_WINDOW:]
                child_window = self._window_mean(recent)
                good_points = sum(
                    q <= baseline_window - QUALITY_POINT_MARGIN for q in recent
                )
                sustained_quality = (
                    len(recent) == QUALITY_WINDOW
                    and child_window <= baseline_window - QUALITY_MARGIN
                    and good_points >= QUALITY_REQUIRED_POINTS
                )
                rhat_success = self.child_best_rhat < baseline_rhat - 1e-12
                improved = rhat_success or sustained_quality
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
                        acceptance_reason=(
                            "rhat_improvement" if rhat_success
                            else "sustained_quality_improvement"
                        ),
                        baseline_rhat=baseline_rhat,
                        child_best_rhat=self.child_best_rhat,
                        baseline_quality_window_mean=baseline_window,
                        child_quality_window_mean=child_window,
                        quality_window_points=len(recent),
                        quality_points_beating_margin=good_points,
                        ending_latent_vector=dict(self.u),
                        ending_executed_vector=self.decode_vector(),
                        cooldown_until_expansion=self.cooldown_until_exp,
                        verifier_authority=False,
                    )
                    return "ACCEPT_CHILD"
                self.last_action = "rollback_child"
                emit(
                    self.log,
                    EventType.SELF_REPORT_FILED,
                    "child_excursion_failed_evaluation",
                    expansion=int(exp),
                    baseline_rhat=baseline_rhat,
                    child_best_rhat=self.child_best_rhat,
                    baseline_quality_window_mean=baseline_window,
                    child_quality_window_mean=child_window,
                    quality_window_points=len(recent),
                    quality_points_beating_margin=good_points,
                    sustained_quality_improvement=False,
                    verifier_authority=False,
                )
                return "ROLLBACK_CHILD"
            self.last_action = "child_trial_adult_refinement"
            return "NONE"

        failure = self._adult_failure(stale)
        if exp >= self.cooldown_until_exp and not self.fresh_failure_required:
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
                baseline_recent = list(self.quality_history)[-QUALITY_WINDOW:]
                self.child_checkpoint_quality_window_mean = self._window_mean(baseline_recent)
                self.child_quality_samples.clear()
                self.child_start_exp = int(exp)
                self.child_best_rhat = math.inf
                self.mode = "CHILD_TRIAL"
                self.child_trials += 1
                self.fresh_failure_required = False
                checkpoint_latent = dict(self.u)
                self._install_vector(inverse)
                self.last_action = "start_child"
                emit(
                    self.log,
                    EventType.ACTION_EXECUTED,
                    "child_inverse_excursion_started",
                    expansion=int(exp),
                    checkpoint_latent_vector=checkpoint_latent,
                    inverse_latent_vector=dict(self.u),
                    checkpoint_executed_vector=self.decode_vector(checkpoint_latent),
                    inverse_executed_vector=self.decode_vector(self.u),
                    latent_group="logit_product_group",
                    inverse_rule="coordinatewise u -> 1-u",
                    baseline_quality_window_mean=self.child_checkpoint_quality_window_mean,
                    trial_expansions=self.child_trial_expansions,
                    child_reentry_forbidden_until_trial_complete=True,
                    verifier_authority=False,
                )
                return "START_CHILD"

        self.last_action = "adult_refinement"
        return "NONE"

    def rollback_child(self, *, exp: int) -> None:
        failed_latent = dict(self.u)
        checkpoint = dict(self.child_checkpoint_u or {})
        super().rollback_child(exp=exp)
        self.child_quality_samples.clear()
        emit(
            self.log,
            EventType.SELF_REPORT_FILED,
            "child_latent_rollback_audit",
            expansion=int(exp),
            failed_latent_vector=failed_latent,
            restored_latent_vector=dict(self.u),
            checkpoint_match=bool(checkpoint) and all(
                math.isclose(self.u[k], checkpoint[k], abs_tol=1e-12)
                for k in KNOBS
            ),
            restored_executed_vector=self.decode_vector(),
            verifier_authority=False,
        )

    def summary(self) -> dict[str, Any]:
        data = super().summary()
        data.update({
            "latent_group": "logit product group (0,1)^11",
            "latent_group_identity": 0.5,
            "latent_group_inverse": "coordinatewise u -> 1-u",
            "latent_epsilon_embedding": self.latent_eps,
            "latent_and_executed_vectors_logged": True,
            "child_quality_acceptance_window": QUALITY_WINDOW if self.version == "2.3" else None,
            "child_quality_acceptance_margin": QUALITY_MARGIN if self.version == "2.3" else None,
            "child_quality_required_points": QUALITY_REQUIRED_POINTS if self.version == "2.3" else None,
            "child_acceptance_requires_sustained_quality_or_rhat_improvement": self.version == "2.3",
        })
        return data


def exact_selftest(controller: ExactGroupActualKnobController) -> None:
    BASE._selftest_controller(controller)
    original = dict(controller.u)
    inv = controller.inverse_vector(original)
    twice = controller.inverse_vector(inv)
    for key in KNOBS:
        u = float(original[key])
        if not (0.0 < u < 1.0):
            raise SystemExit(f"{key}: latent coordinate is not in (0,1)")
        if not math.isclose(twice[key], u, abs_tol=1e-12):
            raise SystemExit(f"{key}: inverse is not an involution")
        composed = logit_group_compose(u, inv[key])
        if not math.isclose(composed, 0.5, abs_tol=1e-12):
            raise SystemExit(f"{key}: u * u^-1 != identity")
    # Interior embedding must preserve the exact decoded endpoints.
    for key in KNOBS:
        lo, hi = controller.bounds[key]
        if math.isclose(lo, hi):
            continue
        dlo = float(controller._decode_value(key, LATENT_EPS))
        dhi = float(controller._decode_value(key, 1.0 - LATENT_EPS))
        if key in INTEGER_KNOBS:
            if int(round(dlo)) != int(round(lo)) or int(round(dhi)) != int(round(hi)):
                raise SystemExit(f"{key}: latent embedding changed integer endpoints")
        else:
            if not math.isclose(dlo, lo, abs_tol=1e-12) or not math.isclose(dhi, hi, abs_tol=1e-12):
                raise SystemExit(f"{key}: latent embedding changed physical endpoints")
    print("[DATA-MIND 2.x V2 SELFTEST] exact logit-group inverse + endpoint decode: passed")


# Base.main resolves these globals when it runs.
BASE.ActualKnobController = ExactGroupActualKnobController
BASE._selftest_controller = exact_selftest


def main() -> int:
    return int(BASE.main() or 0)


if __name__ == "__main__":
    raise SystemExit(main())
