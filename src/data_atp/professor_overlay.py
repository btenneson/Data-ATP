"""Additive Professor -> Mathematician wiring.

This module is deliberately a mixin rather than a replacement controller.
A concrete DATA-MIND controller keeps all of its existing behavior and gains a
bounded Professor signal in the state signature that its learning/retrieval
machinery can consume.
"""
from __future__ import annotations

from typing import Any

from data_atp.professor import BoundedProfessor


class ProfessorStateMixin:
    """Mixin that augments, never replaces, an existing controller state."""

    professor: BoundedProfessor
    professor_grades: int

    def install_professor(self, professor: BoundedProfessor) -> None:
        self.professor = professor
        self.professor_grades = 0

    def state_signature(self, **kwargs) -> dict[str, Any]:
        # Cooperative super(): the Mathematician's complete state remains intact.
        state = dict(super().state_signature(**kwargs))
        signal = self.professor.grade(state)
        self.professor_grades += 1
        state.update(
            {
                "professor_credit": signal.credit,
                "professor_h": signal.objective_h,
                "professor_reward": signal.reward,
                "professor_penalty": signal.penalty,
                "professor_informative": signal.informative,
            }
        )
        return state

    def professor_summary(self) -> dict[str, Any]:
        return {
            "professor_present": True,
            "professor_additive_not_replacement": True,
            "professor_grades": int(self.professor_grades),
            "professor_certificate_authority": False,
            "professor_verifier_authority": False,
            "professor_knob_write_authority": False,
        }
