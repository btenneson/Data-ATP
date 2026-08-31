"""Append-only, hash-chained transactions for Data-ATP."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import StrEnum
import copy
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

    Payloads are deep-copied at append time. This is necessary because control
    events often contain nested mutable dictionaries (for example live strategy
    weights). Without a deep snapshot, later controller mutations can change the
    in-memory payload after its digest was computed, causing a false hash-chain
    failure even though the persisted JSONL is intact.
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
        raw = json.dumps(record, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def _record_dict(tx: Transaction) -> dict[str, Any]:
        return {
            "sequence": tx.sequence,
            "event_type": str(tx.event_type),
            "payload": tx.payload,
            "timestamp_utc": tx.timestamp_utc,
            "previous_hash": tx.previous_hash,
            "digest": tx.digest,
        }

    def _load_existing(self) -> None:
        assert self._path is not None
        previous = "GENESIS"
        try:
            with self._path.open("r", encoding="utf-8") as handle:
                for expected_sequence, line in enumerate(handle):
                    if not line.strip():
                        raise ValueError(f"blank transaction-log line at {expected_sequence + 1}")
                    record = json.loads(line)
                    tx = Transaction(
                        sequence=int(record["sequence"]),
                        event_type=EventType(record["event_type"]),
                        payload=dict(record["payload"]),
                        timestamp_utc=str(record["timestamp_utc"]),
                        previous_hash=str(record["previous_hash"]),
                        digest=str(record["digest"]),
                    )
                    if tx.sequence != expected_sequence:
                        raise ValueError("transaction sequence is not contiguous")
                    if tx.previous_hash != previous:
                        raise ValueError("transaction previous_hash chain is broken")
                    expected_digest = self._digest(
                        tx.sequence,
                        tx.event_type,
                        tx.payload,
                        tx.timestamp_utc,
                        tx.previous_hash,
                    )
                    if tx.digest != expected_digest:
                        raise ValueError("transaction digest verification failed")
                    self._items.append(tx)
                    previous = tx.digest
        except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            self._items.clear()
            raise ValueError(f"cannot load trusted transaction log {self._path}: {exc}") from exc

    def _persist(self, tx: Transaction) -> None:
        if self._path is None:
            return
        line = json.dumps(
            self._record_dict(tx),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            default=str,
        ) + "\n"
        with self._path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())

    def append(self, event_type: EventType, payload: dict[str, Any]) -> Transaction:
        sequence = len(self._items)
        timestamp = datetime.now(timezone.utc).isoformat()
        previous_hash = self.last_digest
        frozen_payload = copy.deepcopy(payload)
        digest = self._digest(sequence, event_type, frozen_payload, timestamp, previous_hash)
        tx = Transaction(
            sequence=sequence,
            event_type=event_type,
            payload=frozen_payload,
            timestamp_utc=timestamp,
            previous_hash=previous_hash,
            digest=digest,
        )
        self._persist(tx)
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
