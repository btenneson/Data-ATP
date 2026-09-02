"""DATA-MIND 2.10 federated verified-memory topology.

The federation preserves the existing verifier-gated, append-only SharedBank as
the common trusted core while giving departments distinct local bank nodes.
Verified items may remain local, propagate only to coupled departments, enter
the common core, or be physically copied to every registered department.

FUTUREBANK and Sentinel quarantine remain separate epistemic stores.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Iterable, Mapping

from .shared_bank import BankItem, BankKind, SharedBank, TradeFn


class PropagationMode(str, Enum):
    """How a verifier-accepted item propagates through the federation."""

    LOCAL = "local"
    COUPLED = "coupled"
    CORE = "core"
    BROADCAST = "broadcast"


@dataclass(frozen=True, slots=True)
class FederatedBankView:
    """Read-only bank view specialized to one department."""

    agent: str
    partner: str | None
    items: tuple[BankItem, ...]
    core_items: tuple[BankItem, ...]
    local_items: tuple[BankItem, ...]
    coupled_items: tuple[BankItem, ...]
    coupled_departments: tuple[str, ...]


DEFAULT_COUPLINGS: Mapping[str, tuple[str, ...]] = {
    "P1": ("P2", "QH", "COMPASS"),
    "P2": ("P1", "QH", "COMPASS"),
    "R1": ("R2", "QH", "COMPASS"),
    "R2": ("R1", "QH", "COMPASS"),
    "I1": ("I2", "COMPASS"),
    "I2": ("I1", "COMPASS"),
    "C1": ("C2", "PROFESSOR", "CHILD"),
    "C2": ("C1", "PROFESSOR", "CHILD"),
    "P": ("QH", "COMPASS"),
    "R": ("QH", "COMPASS"),
    "I": ("COMPASS",),
    "C": ("PROFESSOR", "CHILD"),
    "QH": ("P", "R", "PRESENTATION", "COMPASS"),
    "PROFESSOR": ("COMPASS", "CHILD"),
    "COMPASS": ("P", "R", "I", "C", "QH", "PROFESSOR", "CHILD", "PRESENTATION", "LEARNER"),
    "CHILD": ("PROFESSOR", "COMPASS", "PRESENTATION"),
    "PRESENTATION": ("QH", "COMPASS", "CHILD"),
    "LEARNER": ("COMPASS", "QH", "PROFESSOR"),
    "SENTINEL": (),
    "VERIFIER": (),
}


class FederatedBank:
    """Federation of verifier-gated BANK nodes around one shared trusted core.

    All departments can read the common core. Each department also has a local
    SharedBank. Coupling controls which local banks are additionally visible
    and where ``COUPLED`` deposits are copied.

    ``CORE`` is the conservative default: one verified copy enters the shared
    core and becomes logically visible to every department without unnecessary
    physical duplication. ``BROADCAST`` additionally copies the item into every
    registered local bank when an experiment explicitly wants all-copied BANKs.
    """

    def __init__(
        self,
        *,
        core: SharedBank | None = None,
        departments: Iterable[str] | None = None,
        couplings: Mapping[str, Iterable[str]] | None = None,
        axiom_to_rules: TradeFn | None = None,
        rule_to_axioms: TradeFn | None = None,
    ) -> None:
        self.core = core if core is not None else SharedBank(
            axiom_to_rules=axiom_to_rules,
            rule_to_axioms=rule_to_axioms,
        )
        requested = set(departments or DEFAULT_COUPLINGS.keys())
        supplied_couplings = couplings or DEFAULT_COUPLINGS
        for source, peers in supplied_couplings.items():
            requested.add(source)
            requested.update(peers)

        self._axiom_to_rules = axiom_to_rules
        self._rule_to_axioms = rule_to_axioms
        self._locals: dict[str, SharedBank] = {}
        self._couplings: dict[str, tuple[str, ...]] = {}

        for department in sorted(requested):
            self.register_department(department)
        for source, peers in supplied_couplings.items():
            self.set_couplings(source, peers)

    def register_department(self, department: str) -> None:
        if not department:
            raise ValueError("department name must be non-empty")
        if department not in self._locals:
            self._locals[department] = SharedBank(
                axiom_to_rules=self._axiom_to_rules,
                rule_to_axioms=self._rule_to_axioms,
            )
        self._couplings.setdefault(department, ())

    def departments(self) -> tuple[str, ...]:
        return tuple(sorted(self._locals))

    def set_couplings(self, department: str, peers: Iterable[str]) -> None:
        self.register_department(department)
        normalized: list[str] = []
        seen: set[str] = set()
        for peer in peers:
            if peer == department or peer in seen:
                continue
            self.register_department(peer)
            seen.add(peer)
            normalized.append(peer)
        self._couplings[department] = tuple(normalized)

    def coupled_departments(self, department: str) -> tuple[str, ...]:
        self.register_department(department)
        return self._couplings.get(department, ())

    def local_items(self, department: str) -> tuple[BankItem, ...]:
        self.register_department(department)
        return self._locals[department].items()

    def core_items(self) -> tuple[BankItem, ...]:
        return self.core.items()

    @staticmethod
    def _dedupe(*groups: Iterable[BankItem]) -> tuple[BankItem, ...]:
        out: list[BankItem] = []
        seen: set[str] = set()
        for group in groups:
            for item in group:
                if item.item_id in seen:
                    continue
                seen.add(item.item_id)
                out.append(item)
        return tuple(out)

    def view_for(self, department: str, partner: str | None = None) -> FederatedBankView:
        self.register_department(department)
        coupled = self.coupled_departments(department)
        core_items = self.core.items()
        local_items = self._locals[department].items()
        coupled_items = self._dedupe(*(self._locals[p].items() for p in coupled))
        items = self._dedupe(core_items, local_items, coupled_items)
        return FederatedBankView(
            agent=department,
            partner=partner,
            items=items,
            core_items=core_items,
            local_items=local_items,
            coupled_items=coupled_items,
            coupled_departments=coupled,
        )

    def propose(
        self,
        *,
        agent: str,
        kind: BankKind,
        payload: Any,
        verify: Callable[[BankKind, Any], bool],
        metadata: Mapping[str, Any] | None = None,
        propagation: PropagationMode = PropagationMode.CORE,
    ) -> tuple[BankItem, ...]:
        """Verify once, then propagate according to the declared topology."""
        self.register_department(agent)
        if not bool(verify(kind, payload)):
            return ()

        tagged_metadata = {
            **dict(metadata or {}),
            "federation_source": agent,
            "federation_propagation": propagation.value,
        }

        destinations: list[tuple[str, SharedBank]] = []
        if propagation is PropagationMode.LOCAL:
            destinations.append((agent, self._locals[agent]))
        elif propagation is PropagationMode.COUPLED:
            destinations.append((agent, self._locals[agent]))
            destinations.extend((peer, self._locals[peer]) for peer in self.coupled_departments(agent))
        elif propagation is PropagationMode.CORE:
            destinations.append(("CORE", self.core))
        elif propagation is PropagationMode.BROADCAST:
            destinations.append(("CORE", self.core))
            destinations.extend((department, self._locals[department]) for department in self.departments())
        else:
            raise ValueError(f"unsupported propagation mode: {propagation!r}")

        added: list[BankItem] = []
        seen_keys: set[tuple[str, str]] = set()
        for destination, bank in destinations:
            entries = bank.deposit_verified(
                kind=kind,
                payload=payload,
                provenance=agent,
                metadata={**tagged_metadata, "federation_destination": destination},
            )
            for item in entries:
                key = (destination, item.item_id)
                if key not in seen_keys:
                    seen_keys.add(key)
                    added.append(item)
        return tuple(added)

    def copy_core_to_local(self, department: str) -> tuple[BankItem, ...]:
        """Materialize verified core items into one local BANK node."""
        self.register_department(department)
        added: list[BankItem] = []
        for item in self.core.items():
            entries = self._locals[department].deposit_verified(
                kind=item.kind,
                payload=item.payload,
                provenance=item.provenance,
                metadata={**dict(item.metadata), "federation_copied_from_core": True},
            )
            added.extend(entries)
        return tuple(added)

    def copy_core_to_all(self) -> int:
        """Materialize the current core into every registered local BANK."""
        copied = 0
        for department in self.departments():
            copied += len(self.copy_core_to_local(department))
        return copied
