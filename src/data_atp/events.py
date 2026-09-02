"""Append-only, hash-chained transactions for Data-ATP."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Iterable


class EventType(StrEnum):
    PICARD_COMMAND_RECEIVED = "PicardCommandReceived"
    PICARD_COMMAND_REJECTED = "PicardCommandRejected"
    PICARD_STATE_CHANGED = "PicardStateChanged"
    PICARD_DIRECTIVE_ISSUED = "PicardDirectiveIssued"
    DIRECTIVE_RECEIVED = "DirectiveReceived"
    ACTION_PROPOSED = "ActionProposed"
    LEGALITY_CHECKED = "LegalityChecked"
    SENTINEL_ASSESSED = "SentinelAssessed"
    SENTINEL_BLOCKED = "SentinelBlocked"
    LOCAL_EVIDENCE_DETECTED = "LocalEvidenceDetected"
    STRATEGY_OVERRIDE_PROPOSED = "StrategyOverrideProposed"
    STRATEGY_OVERRIDE_EXECUTED = "StrategyOverrideExecuted"
    ACTION_REJECTED = "ActionRejected"
    ACTION_EXECUTED = "ActionExecuted"
    CERTIFICATE_SUBMITTED = "CertificateSubmitted"
    VERIFIER_ACCEPTED = "VerifierAccepted"
    VERIFIER_REJECTED = "VerifierRejected"
    SELF_REPORT_FILED = "SelfReportFiled"
    CHECKPOINT_SAVED = "CheckpointSaved"
    CHECKPOINT_RESTORED = "CheckpointRestored"
    CHECKPOINT_REJECTED = "CheckpointRejected"
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
    """Append-only SHA-256 hash chain, optionally persisted as JSONL.

    ``TransactionLog()`` remains an in-memory log for tests and small tools.
    Passing ``path`` makes each accepted append durable before it is exposed to
    callers. Existing JSONL logs are reloaded and verified on construction;
    malformed or hash-inconsistent logs fail closed.
    """

    def __init__(self, path: str | Path | None = None) -> None:
        self._items: list[Transaction] = []
        self._path = Path(path) if path is not None else None
        if self._path is not None:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            if self._path.exists() and self._path.stat().st_size:
                self._load_existing()

    @property
    def path(self) -> Path | None:
        return self._path

    @property
    def last_digest(self) -> str:
        return self._items[-1].digest if self._items else "GENESIS"

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
        encoded = json.dumps(record, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def append(self, event_type: EventType, payload: dict[str, Any]) -> Transaction:
        sequence = len(self._items) + 1
        timestamp_utc = datetime.now(timezone.utc).isoformat()
        previous_hash = self.last_digest
        digest = self._digest(sequence, event_type, payload, timestamp_utc, previous_hash)
        item = Transaction(sequence, event_type, payload, timestamp_utc, previous_hash, digest)
        if self._path is not None:
            record = asdict(item)
            record["event_type"] = str(item.event_type)
            line = json.dumps(record, sort_keys=True, default=str) + "\n"
            with self._path.open("a", encoding="utf-8") as handle:
                handle.write(line)
                handle.flush()
                os.fsync(handle.fileno())
        self._items.append(item)
        return item

    def items(self) -> tuple[Transaction, ...]:
        return tuple(self._items)

    def extend(self, events: Iterable[tuple[EventType, dict[str, Any]]]) -> None:
        for event_type, payload in events:
            self.append(event_type, payload)

    def _load_existing(self) -> None:
        assert self._path is not None
        previous_hash = "GENESIS"
        loaded: list[Transaction] = []
        with self._path.open("r", encoding="utf-8") as handle:
            for expected_sequence, line in enumerate(handle, start=1):
                raw = json.loads(line)
                event_type = EventType(raw["event_type"])
                payload = raw["payload"]
                timestamp_utc = raw["timestamp_utc"]
                sequence = int(raw["sequence"])
                if sequence != expected_sequence:
                    raise ValueError("transaction sequence mismatch")
                if raw["previous_hash"] != previous_hash:
                    raise ValueError("transaction previous-hash mismatch")
                digest = self._digest(sequence, event_type, payload, timestamp_utc, previous_hash)
                if digest != raw["digest"]:
                    raise ValueError("transaction digest mismatch")
                item = Transaction(sequence, event_type, payload, timestamp_utc, previous_hash, digest)
                loaded.append(item)
                previous_hash = digest
        self._items = loaded
