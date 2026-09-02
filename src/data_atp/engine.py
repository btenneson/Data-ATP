"""Minimal accountable search execution loop with DATA-MIND 2.9 Sentinel."""

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
from .sentinel import (
    ActionContext,
    ResourceSample,
    SecurityAssessment,
    SecurityGovernor,
    SentinelDecision,
)


@dataclass(frozen=True, slots=True)
class RunOutcome:
    decision: AutonomyDecision
    executed: bool
    verifier_accepted: bool | None
    remaining_budget: int
    security_assessment: SecurityAssessment | None = None


class AccountableSearchEngine:
    """Execute one bounded action under Picard, autonomy, verifier, and Sentinel."""

    def __init__(
        self,
        log: TransactionLog,
        controller: AccountableAutonomyController,
        picard: PicardController | None = None,
        sentinel: SecurityGovernor | None = None,
    ) -> None:
        self.log = log
        self.controller = controller
        self.picard = picard
        # DATA-MIND 2.9 is fail-closed by default: absence of an injected
        # governor creates the conservative default governor rather than
        # disabling security.
        self.sentinel = sentinel or SecurityGovernor()

    def run_action(
        self,
        directive: Directive,
        action: ActionCandidate,
        evidence: Evidence | None,
        remaining_budget: int,
        execute: Callable[[ActionCandidate], str | None],
        verify: Callable[[str], bool],
        resources: ResourceSample | None = None,
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

        # Preflight phase: an internal proof/search step is allowed to generate
        # an as-yet-unverified candidate. Formal verification is required later
        # before a certificate is accepted as truth or exported as such.
        context = ActionContext(
            action=action.name,
            capabilities=action.capabilities,
            target_scope=action.target_scope,
            security_class=action.security_class,
            formal_verified=False,
            requires_formal_verification=False,
            human_approved=action.human_approved,
            metadata={"action_id": action.action_id, **dict(action.security_metadata)},
        )
        assessment = self.sentinel.assess(context, resources)
        self.log.append(EventType.SENTINEL_ASSESSED, {
            "action_id": action.action_id,
            "decision": assessment.decision,
            "risk_score": assessment.risk_score,
            "reasons": assessment.reasons,
            "capabilities": sorted(action.capabilities),
            "target_scope": action.target_scope,
            "security_class": action.security_class,
        })

        allowed = assessment.decision in {
            SentinelDecision.ALLOW_INTERNAL,
            SentinelDecision.ALLOW_EXPORT,
        }
        if not allowed:
            reason = f"Sentinel denied execution: {assessment.decision.value}."
            security_decision = AutonomyDecision(Decision.REJECT_SECURITY, reason, False)
            self.log.append(EventType.SENTINEL_BLOCKED, {
                "action_id": action.action_id,
                "decision": assessment.decision,
                "risk_score": assessment.risk_score,
                "reasons": assessment.reasons,
            })
            self.log.append(EventType.ACTION_REJECTED, {
                "action_id": action.action_id,
                "decision": Decision.REJECT_SECURITY,
                "reason": reason,
            })
            return RunOutcome(
                security_decision,
                False,
                None,
                remaining_budget,
                assessment,
            )

        certificate = execute(action)
        new_budget = remaining_budget - action.estimated_cost
        self.log.append(EventType.ACTION_EXECUTED, {
            "action_id": action.action_id,
            "estimated_cost": action.estimated_cost,
            "remaining_budget": new_budget,
            "sentinel_risk_score": assessment.risk_score,
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

        return RunOutcome(decision, True, accepted, new_budget, assessment)
