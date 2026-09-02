"""P/R/I/C + Couples coordinator with DATA-MIND 2.10 federated BANK access."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping

from .federated_bank import FederatedBank, FederatedBankView, PropagationMode
from .future_bank import FutureBank, FutureBankView, FutureItem
from .shared_bank import BankItem, BankView, SharedBank, BankKind

BankReadView = BankView | FederatedBankView
AgentStep = Callable[[Any, BankReadView, FutureBankView], Any]
Verifier = Callable[[BankKind, Any], bool]


@dataclass(frozen=True, slots=True)
class AgentProposal:
    """Optional verifier-gated BANK proposal returned by an agent."""

    kind: BankKind
    payload: Any
    metadata: Mapping[str, Any] | None = None
    propagation: PropagationMode = PropagationMode.CORE


@dataclass(frozen=True, slots=True)
class FutureProposal:
    """Optional speculative FUTUREBANK proposal returned by an agent."""

    kind: BankKind
    payload: Any
    metadata: Mapping[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class AgentStepResult:
    """Result of one BANK/FUTUREBANK-aware P/R/I/C step."""

    output: Any
    proposal: AgentProposal | None = None
    future_proposal: FutureProposal | None = None


class PRICBankCoordinator:
    """Run P/R/I/C Couples against federated BANK and separate FUTUREBANK.

    The verifier-gated SharedBank remains the trusted common core. DATA-MIND
    2.10 adds department-local BANK nodes and configurable coupling around that
    core. Each P/R/I/C invocation receives a read-only federated view containing
    the shared core, its local node, and the local nodes of explicitly coupled
    departments. FUTUREBANK remains speculative and epistemically separate.
    """

    AGENTS = ("P1", "P2", "R1", "R2", "I1", "I2", "C1", "C2")

    def __init__(
        self,
        bank: SharedBank,
        verify: Verifier,
        future_bank: FutureBank | None = None,
        federation: FederatedBank | None = None,
    ) -> None:
        self.bank = bank
        self.federation = federation if federation is not None else FederatedBank(core=bank)
        if self.federation.core is not bank:
            raise ValueError("federation core must be the coordinator SharedBank")
        self.future_bank = future_bank if future_bank is not None else FutureBank()
        self.verify = verify

    def bank_view_for(self, department: str) -> FederatedBankView:
        """Return the 2.10 read-only federated BANK view for any department."""
        partner = SharedBank.COUPLES.get(department)
        return self.federation.view_for(department, partner=partner)

    def step(self, agent: str, state: Any, module: AgentStep) -> AgentStepResult:
        if agent not in self.AGENTS:
            raise ValueError(f"unknown P/R/I/C agent: {agent}")

        result = module(
            state,
            self.bank_view_for(agent),
            self.future_bank.view_for(agent),
        )
        if not isinstance(result, AgentStepResult):
            result = AgentStepResult(output=result)

        if result.future_proposal is not None:
            p = result.future_proposal
            self.future_bank.propose(
                agent=agent,
                kind=p.kind,
                payload=p.payload,
                metadata=p.metadata,
            )

        if result.proposal is not None:
            p = result.proposal
            self.federation.propose(
                agent=agent,
                kind=p.kind,
                payload=p.payload,
                verify=self.verify,
                metadata=p.metadata,
                propagation=p.propagation,
            )
        return result

    def promote_future(self, item_id: str, *, agent: str = "FUTUREBANK") -> tuple[BankItem, ...]:
        """Promote a speculative item into the verified shared core only."""
        return self.future_bank.promote(
            item_id=item_id,
            bank=self.bank,
            verify=self.verify,
            agent=agent,
        )

    def step_round(
        self,
        states: Mapping[str, Any],
        modules: Mapping[str, AgentStep],
    ) -> dict[str, AgentStepResult]:
        """Run one fair Couple round, refreshing both memories after every step."""
        out: dict[str, AgentStepResult] = {}
        for agent in self.AGENTS:
            if agent not in modules:
                continue
            out[agent] = self.step(agent, states.get(agent), modules[agent])
        return out

    def shared_items(self) -> tuple[BankItem, ...]:
        return self.bank.items()

    def federated_items(self, department: str) -> tuple[BankItem, ...]:
        return self.bank_view_for(department).items

    def future_items(self) -> tuple[FutureItem, ...]:
        return self.future_bank.items()
