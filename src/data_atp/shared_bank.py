"""Shared monotone BANK for P/R/I/C agents and their Couples.

The BANK is append-only from the point of view of search modules: modules may
read any verified item and may propose deposits, but they never withdraw or
silently rewrite prior items.  When a verified axiom/rule is deposited, safe
trading callbacks may add an equivalent alternate presentation while retaining
the original presentation and provenance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json
from typing import Any, Callable, Iterable, Literal, Mapping

BankKind = Literal["axiom", "rule", "lemma", "certificate", "fact", "other"]
TradeFn = Callable[[Any], Iterable[Any]]


@dataclass(frozen=True, slots=True)
class BankItem:
    """One immutable BANK entry."""

    item_id: str
    kind: BankKind
    payload: Any
    provenance: str
    verified: bool = True
    traded_from: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class BankView:
    """Read-only view supplied to an agent and its Couple partner."""

    agent: str
    partner: str | None
    items: tuple[BankItem, ...]


class SharedBank:
    """Verifier-gated, append-only shared memory with bidirectional trading.

    Trading is deliberately callback-driven.  The BANK does not guess whether
    an arbitrary formal axiom/rule admits a sound trade; the formal-system
    adapter supplies the admissible conversions.  Originals are always kept.
    Generated traded forms are not recursively traded again, preventing loops.
    """

    COUPLES = {
        "P1": "P2", "P2": "P1",
        "R1": "R2", "R2": "R1",
        "I1": "I2", "I2": "I1",
        "C1": "C2", "C2": "C1",
        "P": None, "R": None, "I": None, "C": None,
    }

    def __init__(
        self,
        *,
        axiom_to_rules: TradeFn | None = None,
        rule_to_axioms: TradeFn | None = None,
    ) -> None:
        self._items: list[BankItem] = []
        self._ids: set[str] = set()
        self._axiom_to_rules = axiom_to_rules
        self._rule_to_axioms = rule_to_axioms

    @staticmethod
    def _stable_id(kind: BankKind, payload: Any, provenance: str, traded_from: str | None) -> str:
        body = json.dumps(
            {
                "kind": kind,
                "payload": payload,
                "provenance": provenance,
                "traded_from": traded_from,
            },
            sort_keys=True,
            separators=(",", ":"),
            default=repr,
        )
        return sha256(body.encode("utf-8")).hexdigest()

    def __len__(self) -> int:
        return len(self._items)

    def items(self) -> tuple[BankItem, ...]:
        return tuple(self._items)

    def view_for(self, agent: str) -> BankView:
        """Give every P/R/I/C agent the same verified BANK plus partner identity."""
        return BankView(agent=agent, partner=self.COUPLES.get(agent), items=self.items())

    def deposit_verified(
        self,
        *,
        kind: BankKind,
        payload: Any,
        provenance: str,
        metadata: Mapping[str, Any] | None = None,
    ) -> tuple[BankItem, ...]:
        """Deposit one verified item and all admissible one-step traded forms.

        Returns only entries newly appended by this call.  The original item is
        retained even when one or more traded equivalents are added.
        """
        added: list[BankItem] = []
        original = self._append(
            kind=kind,
            payload=payload,
            provenance=provenance,
            traded_from=None,
            metadata=metadata or {},
        )
        if original is not None:
            added.append(original)

        # Trade only the supplied original, never a generated form.  The formal
        # adapter decides whether a trade is admissible; returning () means no.
        if kind == "axiom" and self._axiom_to_rules is not None:
            for traded in self._axiom_to_rules(payload) or ():
                item = self._append(
                    kind="rule",
                    payload=traded,
                    provenance=f"trade({provenance})",
                    traded_from=original.item_id if original else None,
                    metadata={"trade_direction": "axiom_to_rule"},
                )
                if item is not None:
                    added.append(item)
        elif kind == "rule" and self._rule_to_axioms is not None:
            for traded in self._rule_to_axioms(payload) or ():
                item = self._append(
                    kind="axiom",
                    payload=traded,
                    provenance=f"trade({provenance})",
                    traded_from=original.item_id if original else None,
                    metadata={"trade_direction": "rule_to_axiom"},
                )
                if item is not None:
                    added.append(item)
        return tuple(added)

    def propose(
        self,
        *,
        agent: str,
        kind: BankKind,
        payload: Any,
        verify: Callable[[BankKind, Any], bool],
        metadata: Mapping[str, Any] | None = None,
    ) -> tuple[BankItem, ...]:
        """Let an agent/Couple propose an item; only verifier acceptance commits it."""
        if not bool(verify(kind, payload)):
            return ()
        return self.deposit_verified(
            kind=kind,
            payload=payload,
            provenance=agent,
            metadata=metadata,
        )

    def _append(
        self,
        *,
        kind: BankKind,
        payload: Any,
        provenance: str,
        traded_from: str | None,
        metadata: Mapping[str, Any],
    ) -> BankItem | None:
        item_id = self._stable_id(kind, payload, provenance, traded_from)
        if item_id in self._ids:
            return None
        item = BankItem(
            item_id=item_id,
            kind=kind,
            payload=payload,
            provenance=provenance,
            verified=True,
            traded_from=traded_from,
            metadata=dict(metadata),
        )
        self._ids.add(item_id)
        self._items.append(item)
        return item
