"""First-class FUTUREBANK for speculative DATA-MIND search.

FUTUREBANK is deliberately separate from the verified BANK.  It stores
unverified possibilities worth preserving: candidate lemmas, branches,
repairs, counterfactuals, conjectural trades, and strategy ideas.  Modules may
read and add speculative items, but no FUTUREBANK item becomes trusted BANK
knowledge until it passes the independent verifier.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json
from typing import Any, Mapping

from .shared_bank import BankKind, SharedBank


@dataclass(frozen=True, slots=True)
class FutureItem:
    """One immutable speculative FUTUREBANK entry."""

    item_id: str
    kind: BankKind
    payload: Any
    provenance: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class FutureBankView:
    """Read-only speculative-memory view supplied to a DATA-MIND agent."""

    agent: str
    partner: str | None
    items: tuple[FutureItem, ...]


class FutureBank:
    """Append-only speculative memory, epistemically separate from BANK."""

    COUPLES = SharedBank.COUPLES

    def __init__(self) -> None:
        self._items: list[FutureItem] = []
        self._ids: set[str] = set()

    @staticmethod
    def _stable_id(kind: BankKind, payload: Any, provenance: str) -> str:
        body = json.dumps(
            {"kind": kind, "payload": payload, "provenance": provenance},
            sort_keys=True,
            separators=(",", ":"),
            default=repr,
        )
        return sha256(body.encode("utf-8")).hexdigest()

    def __len__(self) -> int:
        return len(self._items)

    def items(self) -> tuple[FutureItem, ...]:
        return tuple(self._items)

    def view_for(self, agent: str) -> FutureBankView:
        return FutureBankView(
            agent=agent,
            partner=self.COUPLES.get(agent),
            items=self.items(),
        )

    def propose(
        self,
        *,
        agent: str,
        kind: BankKind,
        payload: Any,
        metadata: Mapping[str, Any] | None = None,
    ) -> FutureItem | None:
        """Preserve an unverified possibility without contaminating BANK."""
        item_id = self._stable_id(kind, payload, agent)
        if item_id in self._ids:
            return None
        item = FutureItem(
            item_id=item_id,
            kind=kind,
            payload=payload,
            provenance=agent,
            metadata=dict(metadata or {}),
        )
        self._ids.add(item_id)
        self._items.append(item)
        return item

    def promote(
        self,
        *,
        item_id: str,
        bank: SharedBank,
        verify,
        agent: str = "FUTUREBANK",
    ):
        """Verify one speculative item and, only if accepted, deposit it in BANK.

        The FUTUREBANK item remains as provenance/history; promotion never
        deletes or merges the two stores.  BANK handles any admissible verified
        axiom/rule trading after promotion.
        """
        item = next((x for x in self._items if x.item_id == item_id), None)
        if item is None:
            raise KeyError(item_id)
        return bank.propose(
            agent=agent,
            kind=item.kind,
            payload=item.payload,
            verify=verify,
            metadata={**dict(item.metadata), "futurebank_source": item.item_id},
        )
