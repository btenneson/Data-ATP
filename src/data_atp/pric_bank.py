"""P/R/I/C + Couples coordinator with first-class shared BANK access."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping

from .shared_bank import BankItem, BankView, SharedBank, BankKind

AgentStep = Callable[[Any, BankView], Any]
Verifier = Callable[[BankKind, Any], bool]


@dataclass(frozen=True, slots=True)
class AgentProposal:
    """Optional BANK proposal returned by an agent after consulting the BANK."""

    kind: BankKind
    payload: Any
    metadata: Mapping[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class AgentStepResult:
    """Result of one BANK-aware P/R/I/C step."""

    output: Any
    proposal: AgentProposal | None = None


class PRICBankCoordinator:
    """Run P/R/I/C agents and their Couples against one monotone BANK.

    Every module invocation receives a read-only ``BankView`` containing all
    currently verified BANK items and the identity of its Couple partner.  An
    agent may return a verifier-gated proposal.  If accepted, the proposal and
    every admissible traded presentation are appended before the next module
    runs, so later modules in the same round can use them immediately.
    """

    AGENTS = ("P1", "P2", "R1", "R2", "I1", "I2", "C1", "C2")

    def __init__(self, bank: SharedBank, verify: Verifier) -> None:
        self.bank = bank
        self.verify = verify

    def step(self, agent: str, state: Any, module: AgentStep) -> AgentStepResult:
        if agent not in self.AGENTS:
            raise ValueError(f"unknown P/R/I/C agent: {agent}")
        result = module(state, self.bank.view_for(agent))
        if not isinstance(result, AgentStepResult):
            result = AgentStepResult(output=result)
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

    def step_round(
        self,
        states: Mapping[str, Any],
        modules: Mapping[str, AgentStep],
    ) -> dict[str, AgentStepResult]:
        """Run one fair P/R/I/C Couple round with BANK refresh after every step."""
        out: dict[str, AgentStepResult] = {}
        for agent in self.AGENTS:
            if agent not in modules:
                continue
            out[agent] = self.step(agent, states.get(agent), modules[agent])
        return out

    def shared_items(self) -> tuple[BankItem, ...]:
        return self.bank.items()
