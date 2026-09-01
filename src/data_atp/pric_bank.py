"""P/R/I/C + Couples coordinator with first-class BANK and FUTUREBANK access."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping

from .future_bank import FutureBank, FutureBankView, FutureItem
from .shared_bank import BankItem, BankView, SharedBank, BankKind

AgentStep = Callable[[Any, BankView, FutureBankView], Any]
Verifier = Callable[[BankKind, Any], bool]


@dataclass(frozen=True, slots=True)
class AgentProposal:
    """Optional verified-BANK proposal returned by an agent."""

    kind: BankKind
    payload: Any
    metadata: Mapping[str, Any] | None = None


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
    """Run P/R/I/C Couples against two strictly separate shared memories.

    BANK contains only verifier-accepted mathematics. FUTUREBANK contains
    speculative possibilities and is never treated as verified knowledge.
    Every module invocation receives read-only views of both stores. Verified
    BANK deposits and speculative FUTUREBANK deposits become visible before the
    next module runs.
    """

    AGENTS = ("P1", "P2", "R1", "R2", "I1", "I2", "C1", "C2")

    def __init__(
        self,
        bank: SharedBank,
        verify: Verifier,
        future_bank: FutureBank | None = None,
    ) -> None:
        self.bank = bank
        self.future_bank = future_bank if future_bank is not None else FutureBank()
        self.verify = verify

    def step(self, agent: str, state: Any, module: AgentStep) -> AgentStepResult:
        if agent not in self.AGENTS:
            raise ValueError(f"unknown P/R/I/C agent: {agent}")

        result = module(
            state,
            self.bank.view_for(agent),
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
            self.bank.propose(
                agent=agent,
                kind=p.kind,
                payload=p.payload,
                verify=self.verify,
                metadata=p.metadata,
            )
        return result

    def promote_future(self, item_id: str, *, agent: str = "FUTUREBANK") -> tuple[BankItem, ...]:
        """Attempt verifier-gated promotion from FUTUREBANK into BANK."""
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

    def future_items(self) -> tuple[FutureItem, ...]:
        return self.future_bank.items()
