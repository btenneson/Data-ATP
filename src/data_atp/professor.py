"""Bounded Professor grading for DATA-MIND.

The Professor is an additive advisory module.  It may know a hidden reference
solution through a caller-supplied progress oracle, but it may expose only a
bounded partial-credit signal.  It has no proof-certificate, verifier, BANK, or
knob-write authority.

This module intentionally does *not* replace DATA-MIND 2.4 The Mathematician.
The Mathematician remains responsible for learned shortcut/control proposals.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping
import math


ProgressOracle = Callable[[Mapping[str, Any]], tuple[float, float]]


@dataclass(frozen=True, slots=True)
class ProfessorSignal:
    """The only information the Professor may disclose to search control."""

    credit: float
    objective_h: float
    reward: float
    penalty: float
    informative: bool


class BoundedProfessor:
    """Reference-aware grader with a deliberately narrow information channel.

    The caller may supply ``progress_oracle`` that has access to hidden reference
    information.  The oracle returns ``(reward, penalty)`` in [0, 1]^2.  The
    hidden reference itself never crosses this interface.

    If no oracle is supplied the Professor is neutral and non-informative; this
    makes preservation/ablation tests possible without inventing fake grading.
    """

    def __init__(
        self,
        *,
        progress_oracle: ProgressOracle | None = None,
        penalty_weight: float = 1.0,
        enabled: bool = True,
    ) -> None:
        if not math.isfinite(float(penalty_weight)) or penalty_weight < 0:
            raise ValueError("penalty_weight must be finite and nonnegative")
        self._oracle = progress_oracle
        self.penalty_weight = float(penalty_weight)
        self.enabled = bool(enabled)

    @staticmethod
    def _unit(x: float) -> float:
        x = float(x)
        if not math.isfinite(x):
            raise ValueError("Professor reward/penalty must be finite")
        return min(1.0, max(0.0, x))

    def grade(self, state: Mapping[str, Any]) -> ProfessorSignal:
        if not self.enabled or self._oracle is None:
            return ProfessorSignal(
                credit=0.5,
                objective_h=0.5,
                reward=0.5,
                penalty=0.5,
                informative=False,
            )

        reward_raw, penalty_raw = self._oracle(state)
        reward = self._unit(reward_raw)
        penalty = self._unit(penalty_raw)
        lam = self.penalty_weight
        credit = (reward + lam * (1.0 - penalty)) / (1.0 + lam)
        credit = self._unit(credit)
        return ProfessorSignal(
            credit=credit,
            objective_h=1.0 - credit,
            reward=reward,
            penalty=penalty,
            informative=True,
        )
