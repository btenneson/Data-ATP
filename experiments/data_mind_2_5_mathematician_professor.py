#!/usr/bin/env python3
"""DATA-MIND 2.5 experimental additive Professor + Mathematician adapter.

This does not replace DATA-MIND 2.4.  It imports the exact 2.4 Mathematician,
adds bounded Professor grading to its state, and lets the Mathematician use the
Professor's all-minimization H signal for a tiny legal coordinate-descent bias.
The Professor never writes knobs, certifies mathematics, or bypasses the
verifier; the Mathematician remains the component that executes control moves.

The current Professor is a state-progress grader rather than an answer-key
oracle: it grades search health from already-visible runtime metrics.  That
keeps this first prcom A/B test leakage-free while exercising the intended
Professor -> Mathematician control channel.
"""
from __future__ import annotations

import argparse
import importlib.util
import math
from pathlib import Path
import sys
from typing import Any, Mapping

from data_atp.professor import BoundedProfessor
from data_atp.professor_overlay import ProfessorStateMixin

HERE = Path(__file__).resolve().parent
DM24_PATH = HERE / "data_mind_2_4_mathematician_shortcuts.py"
spec = importlib.util.spec_from_file_location("data_mind_24_for_25", DM24_PATH)
if spec is None or spec.loader is None:
    raise SystemExit(f"cannot load {DM24_PATH}")
DM24 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = DM24
spec.loader.exec_module(DM24)


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def progress_oracle(state: Mapping[str, Any]) -> tuple[float, float]:
    """Return bounded (reward, penalty) using only exposed search-state metrics."""
    rhat = state.get("live_rhat")
    quality = state.get("quality")
    stale = max(0.0, float(state.get("stale") or 0.0))
    dup = _clamp01(float(state.get("duplicate_rate") or 0.0))

    reward_terms: list[float] = []
    if isinstance(rhat, (int, float)) and math.isfinite(float(rhat)):
        reward_terms.append(1.0 / (1.0 + max(0.0, float(rhat))))
    if isinstance(quality, (int, float)) and math.isfinite(float(quality)):
        reward_terms.append(1.0 / (1.0 + max(0.0, float(quality))))
    reward = sum(reward_terms) / len(reward_terms) if reward_terms else 0.5

    stale_penalty = stale / (stale + 6000.0) if stale > 0 else 0.0
    penalty = _clamp01(0.60 * stale_penalty + 0.40 * dup)
    return _clamp01(reward), penalty


class ProfessorMathematicianController(ProfessorStateMixin, DM24.MathematicianController):
    """Exact 2.4 controller plus an additive Professor objective channel."""

    architecture_version = "2.5-professor-additive"

    def __init__(self, *args, professor_enabled: bool = True, professor_step: float = 0.00625, **kwargs):
        super().__init__(*args, **kwargs)
        self.install_professor(
            BoundedProfessor(
                progress_oracle=progress_oracle,
                penalty_weight=0.25,
                enabled=bool(professor_enabled),
            )
        )
        self.professor_enabled = bool(professor_enabled)
        self.professor_step = max(0.0, min(0.025, float(professor_step)))
        self._professor_last_state: dict[str, Any] | None = None
        self._professor_prev_h: float | None = None
        self._professor_knob_index = 0
        self._professor_direction = 1.0
        self.professor_optimizer_moves = 0
        self.professor_h_improvements = 0
        self.professor_h_nonimprovements = 0

    def state_signature(self, **kwargs) -> dict[str, Any]:
        state = dict(super().state_signature(**kwargs))
        self._professor_last_state = state
        return state

    def _professor_optimizer_move(self) -> None:
        """Mathematician executes a bounded coordinate move using Professor H."""
        state = self._professor_last_state or {}
        h = state.get("professor_h")
        if not self.professor_enabled or not isinstance(h, (int, float)) or not math.isfinite(float(h)):
            return
        if self.professor_step <= 0.0 or not DM24.KNOBS:
            return

        h = float(h)
        if self._professor_prev_h is not None:
            if h < self._professor_prev_h - 1e-12:
                self.professor_h_improvements += 1
            else:
                self.professor_h_nonimprovements += 1
                # Try the opposite local direction; after each miss rotate to
                # the next legal coordinate rather than replacing 2.4 policy.
                self._professor_direction *= -1.0
                self._professor_knob_index = (self._professor_knob_index + 1) % len(DM24.KNOBS)

        knob = DM24.KNOBS[self._professor_knob_index]
        before = dict(self.u)
        self._bounded_move(knob, self._professor_direction * self.professor_step)
        self._install_vector(self.u)
        actual = float(self.u[knob]) - float(before[knob])
        self.professor_optimizer_moves += 1

        DM24.emit(
            self.log,
            DM24.EventType.STRATEGY_OVERRIDE_EXECUTED,
            "professor_objective_coordinate_descent",
            professor_h=h,
            knob=knob,
            requested_delta=self._professor_direction * self.professor_step,
            actual_delta=actual,
            executor="Mathematician",
            professor_knob_write_authority=False,
            professor_verifier_authority=False,
            professor_certificate_authority=False,
            legal_control_only=True,
        )
        self.memory_store.append(
            problem_id=self.cfg.problem_id,
            run_id=self.cfg.run_id,
            kind="professor_guided_mathematician_move",
            outcome="observation",
            source_agent=self.current_agent,
            shortcut_type="control",
            state_signature=state,
            action={"delta": {knob: actual}, "executor": "Mathematician"},
            metrics={"professor_h": h},
            tags=("professor", "mathematician", "additive", "control"),
            source="DATA-MIND 2.5 Professor additive adapter",
        )
        self._professor_prev_h = h

    def sample(self, **kwargs) -> str:
        action = super().sample(**kwargs)
        exp = int(kwargs["exp"])
        # Preserve child inverse/accept/rollback behavior.  Professor guidance
        # is an adult-only additive move at an actual control sample.
        if (
            self.professor_enabled
            and self.last_control_exp == exp
            and action == "NONE"
            and self.mode == "ADULT"
        ):
            self._professor_optimizer_move()
        return action

    def summary(self) -> dict[str, Any]:
        data = dict(super().summary())
        data.update(self.professor_summary())
        data.update(
            {
                "architecture_version": "2.5-professor-additive",
                "mathematician_2_4_preserved": True,
                "professor_enabled": self.professor_enabled,
                "professor_objective": "minimize H=1-C",
                "professor_penalty_weight": 0.25,
                "professor_oracle_type": "leakage-free runtime-state progress grader",
                "professor_answer_key_used": False,
                "professor_optimizer_executor": "Mathematician",
                "professor_optimizer_step": self.professor_step,
                "professor_optimizer_moves": self.professor_optimizer_moves,
                "professor_h_improvements": self.professor_h_improvements,
                "professor_h_nonimprovements": self.professor_h_nonimprovements,
                "verifier_sovereign": True,
            }
        )
        return data


def main() -> int:
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--professor-step", type=float, default=0.00625)
    ap.add_argument("--disable-professor", action="store_true")
    ours, remaining = ap.parse_known_args(sys.argv[1:])

    base_cls = DM24.MathematicianController

    class ConfiguredProfessorMathematician(ProfessorMathematicianController):
        def __init__(self, *args, **kwargs):
            super().__init__(
                *args,
                professor_enabled=not ours.disable_professor,
                professor_step=ours.professor_step,
                **kwargs,
            )

    # Patch only the 2.4 module's controller hook for this process.  DM24.main
    # still performs all of its original configuration, memory, and BASE wiring.
    DM24.MathematicianController = ConfiguredProfessorMathematician
    original_argv = sys.argv[:]
    sys.argv = [original_argv[0], *remaining]
    try:
        return int(DM24.main() or 0)
    finally:
        sys.argv = original_argv
        DM24.MathematicianController = base_cls


if __name__ == "__main__":
    raise SystemExit(main())
