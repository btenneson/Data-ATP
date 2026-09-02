"""Hard/soft authority separation and bounded strategy exceptions."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import FrozenSet, Mapping

from .events import EventType, TransactionLog
from .sentinel import SecurityClass


class AuthorityLevel(StrEnum):
    HARD_INVARIANT = "hard_invariant"
    SOFT_DIRECTIVE = "soft_directive"


class Decision(StrEnum):
    FOLLOW_DIRECTIVE = "follow_directive"
    OVERRIDE_SOFT_DIRECTIVE = "override_soft_directive"
    REJECT_RUN_CONTROL = "reject_run_control"
    REJECT_ILLEGAL = "reject_illegal"
    REJECT_HARD_CONFLICT = "reject_hard_conflict"
    REJECT_BUDGET = "reject_budget"
    REJECT_WEAK_EVIDENCE = "reject_weak_evidence"
    REJECT_SECURITY = "reject_security"


@dataclass(frozen=True, slots=True)
class Directive:
    directive_id: str
    authority: AuthorityLevel
    preferred_action: str
    rationale: str


@dataclass(frozen=True, slots=True)
class Evidence:
    evidence_id: str
    description: str
    strength: float
    expected_gain: float
    transient: bool = True

    def __post_init__(self) -> None:
        for name, value in (("strength", self.strength), ("expected_gain", self.expected_gain)):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must lie in [0, 1]")


@dataclass(frozen=True, slots=True)
class ActionCandidate:
    action_id: str
    name: str
    legal: bool
    estimated_cost: int
    return_point: str
    capabilities: FrozenSet[str] = frozenset()
    target_scope: str = "internal"
    security_class: SecurityClass = SecurityClass.BENIGN
    human_approved: bool = False
    security_metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.estimated_cost < 0:
            raise ValueError("estimated_cost must be nonnegative")


@dataclass(frozen=True, slots=True)
class ExceptionPolicy:
    minimum_evidence_strength: float = 0.80
    minimum_expected_gain: float = 0.60
    protected_reserve: int = 10
    require_transient_signal: bool = True


@dataclass(frozen=True, slots=True)
class AutonomyDecision:
    decision: Decision
    reason: str
    override_used: bool


class AccountableAutonomyController:
    """Decide whether a proposed search action may depart from a directive."""

    def __init__(self, log: TransactionLog, policy: ExceptionPolicy | None = None) -> None:
        self.log = log
        self.policy = policy or ExceptionPolicy()

    def decide(
        self,
        directive: Directive,
        action: ActionCandidate,
        evidence: Evidence | None,
        remaining_budget: int,
    ) -> AutonomyDecision:
        self.log.append(EventType.DIRECTIVE_RECEIVED, {
            "directive_id": directive.directive_id,
            "authority": directive.authority,
            "preferred_action": directive.preferred_action,
            "rationale": directive.rationale,
        })
        self.log.append(EventType.ACTION_PROPOSED, {
            "action_id": action.action_id,
            "name": action.name,
            "estimated_cost": action.estimated_cost,
            "return_point": action.return_point,
        })
        self.log.append(EventType.LEGALITY_CHECKED, {
            "action_id": action.action_id,
            "legal": action.legal,
        })

        if not action.legal:
            return self._reject(Decision.REJECT_ILLEGAL, action, "Action failed legality checking.")

        conflicts = action.name != directive.preferred_action
        if not conflicts:
            return AutonomyDecision(Decision.FOLLOW_DIRECTIVE, "Action follows the directive.", False)

        if directive.authority == AuthorityLevel.HARD_INVARIANT:
            return self._reject(
                Decision.REJECT_HARD_CONFLICT,
                action,
                "A hard invariant cannot be overridden by local evidence.",
            )

        usable = remaining_budget - self.policy.protected_reserve
        if action.estimated_cost > usable:
            return self._reject(
                Decision.REJECT_BUDGET,
                action,
                "The proposed exception would consume the protected reserve.",
            )

        if evidence is None:
            return self._reject(Decision.REJECT_WEAK_EVIDENCE, action, "No exception evidence was supplied.")

        self.log.append(EventType.LOCAL_EVIDENCE_DETECTED, {
            "evidence_id": evidence.evidence_id,
            "description": evidence.description,
            "strength": evidence.strength,
            "expected_gain": evidence.expected_gain,
            "transient": evidence.transient,
        })
        transient_ok = evidence.transient or not self.policy.require_transient_signal
        evidence_ok = (
            evidence.strength >= self.policy.minimum_evidence_strength
            and evidence.expected_gain >= self.policy.minimum_expected_gain
            and transient_ok
        )
        if not evidence_ok:
            return self._reject(
                Decision.REJECT_WEAK_EVIDENCE,
                action,
                "Evidence did not satisfy the frozen exception policy.",
            )

        self.log.append(EventType.STRATEGY_OVERRIDE_PROPOSED, {
            "directive_id": directive.directive_id,
            "action_id": action.action_id,
            "evidence_id": evidence.evidence_id,
            "bounded_cost": action.estimated_cost,
            "return_point": action.return_point,
        })
        self.log.append(EventType.STRATEGY_OVERRIDE_EXECUTED, {
            "directive_id": directive.directive_id,
            "action_id": action.action_id,
        })
        return AutonomyDecision(
            Decision.OVERRIDE_SOFT_DIRECTIVE,
            "Strong local transient evidence justified a bounded soft-policy exception.",
            True,
        )

    def _reject(self, decision: Decision, action: ActionCandidate, reason: str) -> AutonomyDecision:
        self.log.append(EventType.ACTION_REJECTED, {
            "action_id": action.action_id,
            "decision": decision,
            "reason": reason,
        })
        return AutonomyDecision(decision, reason, False)
