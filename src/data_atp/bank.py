"""Monotone verifier-gated shared BANK for Data-ATP.

BANK is shared mathematical memory, not a consumable account. Agents may query
and use verified entries without removing them. The only state-changing
operation is a verifier-approved deposit.

The intended laws are::

    Q_i(B_t, s_t) <= B_t                 (non-destructive read/query)
    B_t <= B_{t+1}                       (monotonicity)
    B_{t+1} = B_t union {y} if V(y) else B_t

This module is additive. It does not replace the Professor, Mathematician,
Verifier, transaction log, or any search controller.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Callable, Iterable, Mapping, Sequence


Verifier = Callable[[Any], bool]
Selector = Callable[["BankEntry", Mapping[str, Any]], bool]


@dataclass(frozen=True, slots=True)
class BankEntry:
    """One verified, provenance-bearing BANK entry."""

    entry_id: str
    item: Any
    deposited_by: str
    certificate_kind: str
    metadata: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class BankDepositResult:
    """Result of attempting a verifier-gated deposit."""

    accepted: bool
    added: bool
    entry: BankEntry | None
    size_before: int
    size_after: int


class SharedBank:
    """Append-only verified commons with non-destructive agent queries.

    A query returns references to entries already in BANK and never mutates the
    store. A deposit invokes the supplied verifier first. Rejected candidates
    are never admitted.
    """

    def __init__(self, entries: Iterable[BankEntry] = ()) -> None:
        self._entries: list[BankEntry] = []
        self._by_id: dict[str, BankEntry] = {}
        for entry in entries:
            self._append_existing(entry)

    @staticmethod
    def _stable_id(item: Any, certificate_kind: str) -> str:
        payload = json.dumps(
            {"item": item, "certificate_kind": certificate_kind},
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _append_existing(self, entry: BankEntry) -> None:
        if entry.entry_id in self._by_id:
            return
        self._entries.append(entry)
        self._by_id[entry.entry_id] = entry

    def deposit(
        self,
        item: Any,
        *,
        deposited_by: str,
        verify: Verifier,
        certificate_kind: str = "lemma",
        metadata: Mapping[str, Any] | None = None,
    ) -> BankDepositResult:
        """Verify ``item`` and, only if accepted, add it to BANK.

        Duplicate accepted items are idempotent: they remain present but do not
        create a second BANK entry.
        """

        before = len(self._entries)
        if not bool(verify(item)):
            return BankDepositResult(False, False, None, before, before)

        entry_id = self._stable_id(item, certificate_kind)
        existing = self._by_id.get(entry_id)
        if existing is not None:
            return BankDepositResult(True, False, existing, before, before)

        entry = BankEntry(
            entry_id=entry_id,
            item=item,
            deposited_by=str(deposited_by),
            certificate_kind=str(certificate_kind),
            metadata=dict(metadata or {}),
        )
        self._entries.append(entry)
        self._by_id[entry_id] = entry
        return BankDepositResult(True, True, entry, before, len(self._entries))

    def query(
        self,
        agent: str,
        *,
        state: Mapping[str, Any] | None = None,
        selector: Selector | None = None,
        limit: int | None = None,
    ) -> tuple[BankEntry, ...]:
        """Return the subset of BANK selected for ``agent`` without mutation.

        ``agent`` is included in the query state so selectors may implement
        role-specific retrieval policies. With no selector, all entries are
        readable. ``limit`` truncates the selected view only; it never alters
        BANK.
        """

        if limit is not None and limit < 0:
            raise ValueError("limit must be non-negative or None")

        qstate = dict(state or {})
        qstate.setdefault("agent", str(agent))
        selected: list[BankEntry] = []
        for entry in self._entries:
            if selector is None or bool(selector(entry, qstate)):
                selected.append(entry)
                if limit is not None and len(selected) >= limit:
                    break
        return tuple(selected)

    def contains(self, entry_id: str) -> bool:
        return entry_id in self._by_id

    def entries(self) -> tuple[BankEntry, ...]:
        return tuple(self._entries)

    def items(self) -> tuple[Any, ...]:
        return tuple(entry.item for entry in self._entries)

    def __len__(self) -> int:
        return len(self._entries)

    def snapshot_ids(self) -> tuple[str, ...]:
        """Stable monotonicity witness for tests/audits."""

        return tuple(entry.entry_id for entry in self._entries)


def select_by_kind(*kinds: str) -> Selector:
    """Build a simple reusable BANK query policy by certificate kind."""

    allowed = frozenset(str(kind) for kind in kinds)

    def _selector(entry: BankEntry, _state: Mapping[str, Any]) -> bool:
        return entry.certificate_kind in allowed

    return _selector
