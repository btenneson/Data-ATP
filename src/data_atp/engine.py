"""Minimal accountable search execution loop."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Any

from .autonomy import (
    AccountableAutonomyController,
    ActionCandidate,
    AutonomyDecision,
    Decision,
    Directive,
    Evidence,
)
from .bank import BankEntry, Selector, SharedBank
from .events import EventType, TransactionLog
from .picard import PicardController


@dataclass(frozen=True, slots=True)
class RunOutcome:
    decision: AutonomyDecision
    executed: bool
    verifier_accepted: bool | None
    remaining_budget: int


class AccountableSearchEngine:
    """Execute bounded actions while preserving verifier and Picard supremacy.

    BANK support is additive. Existing ``run_action`` behavior is preserved.
    ``run_action_with_bank`` adds non-destructive BANK query/reuse and deposits
    only independently verified returned certificates.
    """

    def __init__(
        self,
        log: TransactionLog,
        controller: AccountableAutonomyController,
        picard: PicardController | None = None,
        bank: SharedBank | None = None,
    ) -> None:
        self.log = log
        self.controller = controller
        self.picard = picard
        self.bank = bank

    def query_bank(
        self,
        agent: str,
        *,
        state: Mapping[str, Any] | None = None,
        selector: Selector | None = None,
        limit: int | None = None,
    ) -> tuple[BankEntry, ...]:
        """Read a selected BANK view without changing BANK."""

        if self.bank is None:
            return ()
        before = self.bank.snapshot_ids()
        selected = self.bank.query(agent, state=state, selector=selector, limit=limit)
        after = self.bank.snapshot_ids()
        if before != after:
            raise RuntimeError("BANK query mutated BANK")
        self.log.append(
            EventType.BANK_QUERIED,
            {
                "agent": str(agent),
                "selected_entry_ids": [entry.entry_id for entry in selected],
                "bank_size": len(self.bank),
            },
        )
        return selected

    def _dispatch_allowed(self, action: ActionCandidate, remaining_budget: int) -> RunOutcome | None:
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
        return None

    def run_action(
        self,
        directive: Directive,
        action: ActionCandidate,
        evidence: Evidence | None,
        remaining_budget: int,
        execute: Callable[[ActionCandidate], str | None],
        verify: Callable[[str], bool],
    ) -> RunOutcome:
        blocked = self._dispatch_allowed(action, remaining_budget)
        if blocked is not None:
            return blocked

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

    def run_action_with_bank(
        self,
        directive: Directive,
        action: ActionCandidate,
        evidence: Evidence | None,
        remaining_budget: int,
        *,
        agent: str,
        execute: Callable[[ActionCandidate, tuple[BankEntry, ...]], str | None],
        verify: Callable[[str], bool],
        bank_state: Mapping[str, Any] | None = None,
        bank_selector: Selector | None = None,
        bank_limit: int | None = None,
        certificate_kind: str = "lemma",
    ) -> RunOutcome:
        """Execute an action with a non-destructive shared-BANK context.

        The agent receives selected verified BANK entries as read-only context.
        If execution returns a certificate, the same independent verifier used
        for settlement gates BANK admission. Rejected certificates never enter
        BANK. Existing ``run_action`` remains untouched for callers that do not
        opt into BANK reuse.
        """

        blocked = self._dispatch_allowed(action, remaining_budget)
        if blocked is not None:
            return blocked

        decision = self.controller.decide(directive, action, evidence, remaining_budget)
        executable = decision.decision in {Decision.FOLLOW_DIRECTIVE, Decision.OVERRIDE_SOFT_DIRECTIVE}
        if not executable:
            return RunOutcome(decision, False, None, remaining_budget)

        selected = self.query_bank(
            agent,
            state=bank_state,
            selector=bank_selector,
            limit=bank_limit,
        )
        certificate = execute(action, selected)
        new_budget = remaining_budget - action.estimated_cost
        self.log.append(
            EventType.ACTION_EXECUTED,
            {
                "action_id": action.action_id,
                "agent": str(agent),
                "bank_entry_ids_used": [entry.entry_id for entry in selected],
                "estimated_cost": action.estimated_cost,
                "remaining_budget": new_budget,
            },
        )

        accepted: bool | None = None
        if certificate is not None:
            self.log.append(
                EventType.CERTIFICATE_SUBMITTED,
                {"action_id": action.action_id, "certificate": certificate, "agent": str(agent)},
            )
            accepted = bool(verify(certificate))
            self.log.append(
                EventType.VERIFIER_ACCEPTED if accepted else EventType.VERIFIER_REJECTED,
                {"action_id": action.action_id, "certificate": certificate, "agent": str(agent)},
            )

            if self.bank is not None:
                result = self.bank.deposit(
                    certificate,
                    deposited_by=str(agent),
                    verify=lambda _candidate: bool(accepted),
                    certificate_kind=certificate_kind,
                    metadata={
                        "action_id": action.action_id,
                        "directive_id": directive.directive_id,
                    },
                )
                self.log.append(
                    EventType.BANK_DEPOSIT_ACCEPTED if result.accepted else EventType.BANK_DEPOSIT_REJECTED,
                    {
                        "action_id": action.action_id,
                        "agent": str(agent),
                        "accepted": result.accepted,
                        "added": result.added,
                        "entry_id": result.entry.entry_id if result.entry is not None else None,
                        "bank_size_before": result.size_before,
                        "bank_size_after": result.size_after,
                    },
                )

        if decision.override_used:
            self.log.append(
                EventType.SELF_REPORT_FILED,
                {
                    "action_id": action.action_id,
                    "directive_id": directive.directive_id,
                    "outcome": "verified" if accepted else "not_verified",
                    "remaining_budget": new_budget,
                    "review_required": True,
                },
            )

        return RunOutcome(decision, True, accepted, new_budget)
