"""Append-only, hash-chained transactions for Data-ATP."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import json
from typing import Any, Iterable


class EventType(StrEnum):
    PICARD_COMMAND_RECEIVED = "PicardCommandReceived"
    PICARD_COMMAND_REJECTED = "PicardCommandRejected"
    PICARD_STATE_CHANGED = "PicardStateChanged"
    PICARD_DIRECTIVE_ISSUED = "PicardDirectiveIssued"
    DIRECTIVE_RECEIVED = "DirectiveReceived"
    ACTION_PROPOSED = "ActionProposed"
    LEGALITY_CHECKED = "LegalityChecked"
    LOCAL_EVIDENCE_DETECTED = "LocalEvidenceDetected"
    STRATEGY_OVERRIDE_PROPOSED = "StrategyOverrideProposed"
    STRATEGY_OVERRIDE_EXECUTED = "StrategyOverrideExecuted"
    ACTION_REJECTED = "ActionRejected"
    ACTION_EXECUTED = "ActionExecuted"
    CERTIFICATE_SUBMITTED = "CertificateSubmitted"
    VERIFIER_ACCEPTED = "VerifierAccepted"
    VERIFIER_REJECTED = "VerifierRejected"
    SELF_REPORT_FILED = "SelfReportFiled"
    COVERAGE_LEVEL_STARTED = "CoverageLevelStarted"
    REGION_REPRESENTATIVE_EXPANDED = "RegionRepresentativeExpanded"
    COVERAGE_LEVEL_COMPLETED = "CoverageLevelCompleted"
    COVERAGE_GUARANTEE_RECORDED = "CoverageGuaranteeRecorded"


@dataclass(frozen=True, slots=True)
class Transaction:
    sequence: int
    event_type: EventType
    payload: dict[str, Any]
    timestamp_utc: str
    previous_hash: str
    digest: str


class TransactionLog:
    """In-memory append-only log with a deterministic SHA-256 hash chain."""

    def __init__(self) -> None:
        self._items: list[Transaction] = []

    @staticmethod
    def _digest(
        sequence: int,
        event_type: EventType,
        payload: dict[str, Any],
        timestamp_utc: str,
        previous_hash: str,
    ) -> str:
        record = {
            "sequence": sequence,
            "event_type": str(event_type),
            "payload": payload,
            "timestamp_utc": timestamp_utc,
            "previous_hash": previous_hash,
        }
        raw = json.dumps(record, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def append(self, event_type: EventType, payload: dict[str, Any]) -> Transaction:
        sequence = len(self._items)
        timestamp = datetime.now(timezone.utc).isoformat()
        previous_hash = self._items[-1].digest if self._items else "GENESIS"
        digest = self._digest(sequence, event_type, payload, timestamp, previous_hash)
        tx = Transaction(
            sequence=sequence,
            event_type=event_type,
            payload=dict(payload),
            timestamp_utc=timestamp,
            previous_hash=previous_hash,
            digest=digest,
        )
        self._items.append(tx)
        return tx

    def verify(self) -> bool:
        previous = "GENESIS"
        for expected_sequence, tx in enumerate(self._items):
            if tx.sequence != expected_sequence or tx.previous_hash != previous:
                return False
            expected = self._digest(
                tx.sequence,
                tx.event_type,
                tx.payload,
                tx.timestamp_utc,
                tx.previous_hash,
            )
            if expected != tx.digest:
                return False
            previous = tx.digest
        return True

    def events(self, event_type: EventType | None = None) -> Iterable[Transaction]:
        if event_type is None:
            return tuple(self._items)
        return tuple(tx for tx in self._items if tx.event_type == event_type)

    def to_json(self) -> str:
        return json.dumps([asdict(tx) for tx in self._items], indent=2, default=str)

    def __len__(self) -> int:
        return len(self._items)
