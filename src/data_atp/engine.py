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
from .picard import PicardController


@dataclass(frozen=True, slots=True)
class RunOutcome:
    decision: AutonomyDecision
    executed: bool
    verifier_accepted: bool | None
    remaining_budget: int


class AccountableSearchEngine:
    """Execute one bounded action while preserving verifier and Picard supremacy."""

    def __init__(
        self,
        log: TransactionLog,
        controller: AccountableAutonomyController,
        picard: PicardController | None = None,
    ) -> None:
        self.log = log
        self.controller = controller
        self.picard = picard

    def run_action(
        self,
        directive: Directive,
        action: ActionCandidate,
        evidence: Evidence | None,
        remaining_budget: int,
        execute: Callable[[ActionCandidate], str | None],
        verify: Callable[[str], bool],
    ) -> RunOutcome:
        if self.picard is not None and not self.picard.status().may_dispatch_work:
            reason = f"Picard blocks work dispatch while state={self.picard.state}."
            self.log.append(
                EventType.ACTION_REJECTED,
                {
                    "action_id": action.action_id,
                    "decision": Decision.REJECT_RUN_CONTROL,
                    "reason": reason,
                    "run_id": self.picard.run_id,
                    "run_state": self.picard.state,
                },
            )
            return RunOutcome(
                AutonomyDecision(Decision.REJECT_RUN_CONTROL, reason, False),
                False,
                None,
                remaining_budget,
            )

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
