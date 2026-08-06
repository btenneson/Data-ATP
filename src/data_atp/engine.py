"""Minimal accountable search execution loop."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .autonomy import (
    AccountableAutonomyController,
    ActionCandidate,
    AutonomyDecision,
    Decision,
    Directive,
    Evidence,
)
from .events import EventType, TransactionLog


@dataclass(frozen=True, slots=True)
class RunOutcome:
    decision: AutonomyDecision
    executed: bool
    verifier_accepted: bool | None
    remaining_budget: int


class AccountableSearchEngine:
    """Execute one bounded action while preserving verifier supremacy."""

    def __init__(self, log: TransactionLog, controller: AccountableAutonomyController) -> None:
        self.log = log
        self.controller = controller

    def run_action(
        self,
        directive: Directive,
        action: ActionCandidate,
        evidence: Evidence | None,
        remaining_budget: int,
        execute: Callable[[ActionCandidate], str | None],
        verify: Callable[[str], bool],
    ) -> RunOutcome:
        decision = self.controller.decide(directive, action, evidence, remaining_budget)
        executable = decision.decision in {Decision.FOLLOW_DIRECTIVE, Decision.OVERRIDE_SOFT_DIRECTIVE}
        if not executable:
            return RunOutcome(decision, False, None, remaining_budget)

        certificate = execute(action)
        new_budget = remaining_budget - action.estimated_cost
        self.log.append(EventType.ACTION_EXECUTED, {
            "action_id": action.action_id,
            "estimated_cost": action.estimated_cost,
            "remaining_budget": new_budget,
        })

        accepted: bool | None = None
        if certificate is not None:
            self.log.append(EventType.CERTIFICATE_SUBMITTED, {
                "action_id": action.action_id,
                "certificate": certificate,
            })
            accepted = bool(verify(certificate))
            self.log.append(
                EventType.VERIFIER_ACCEPTED if accepted else EventType.VERIFIER_REJECTED,
                {"action_id": action.action_id, "certificate": certificate},
            )

        if decision.override_used:
            self.log.append(EventType.SELF_REPORT_FILED, {
                "action_id": action.action_id,
                "directive_id": directive.directive_id,
                "outcome": "verified" if accepted else "not_verified",
                "remaining_budget": new_budget,
                "review_required": True,
            })

        return RunOutcome(decision, True, accepted, new_budget)
