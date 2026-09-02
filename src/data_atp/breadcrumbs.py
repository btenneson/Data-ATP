"""DATA-MIND 2.11 durable breadcrumbs and resumable checkpoint barriers.

A breadcrumb is a small append-only transaction describing where a run is.
A checkpoint is the larger JSON snapshot needed to resume.  The transaction
log is already SHA-256 hash-chained; CheckpointManager separately hashes every
checkpoint and writes that checkpoint hash into the same transaction chain.
Together this provides tamper-evident ordering plus integrity-checked recovery.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .checkpoint import CheckpointManager, CheckpointManifest
from .events import EventType, TransactionLog


@dataclass(frozen=True, slots=True)
class BreadcrumbReceipt:
    kind: str
    transaction_sequence: int
    transaction_digest: str
    checkpoint: CheckpointManifest | None


class BreadcrumbManager:
    """Persist hash-chained breadcrumbs and optional full checkpoints.

    The caller owns the meaning of the snapshot.  For external provers whose
    internal search state cannot be serialized, the snapshot should identify
    the active attempt and explicitly declare the recovery action (normally
    restart_current_attempt).  This avoids pretending that a process heartbeat
    is a byte-for-byte prover checkpoint.
    """

    def __init__(self, directory: str | Path, run_id: str) -> None:
        if not run_id.strip():
            raise ValueError("run_id must be nonempty")
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.run_id = run_id
        self.log = TransactionLog(self.directory / "breadcrumbs.jsonl")
        self.checkpoints = CheckpointManager(
            self.directory / "checkpoints", run_id=run_id, log=self.log
        )

    def record(
        self,
        kind: str,
        snapshot: Mapping[str, Any],
        *,
        metadata: Mapping[str, Any] | None = None,
        checkpoint: bool = True,
    ) -> BreadcrumbReceipt:
        if not kind.strip():
            raise ValueError("breadcrumb kind must be nonempty")
        payload = {
            "run_id": self.run_id,
            "kind": kind,
            "architecture_version": str(snapshot.get("architecture_version", "")),
            "phase": str(snapshot.get("phase", "")),
            "attempt_index": snapshot.get("attempt_index"),
            "next_attempt_index": snapshot.get("next_attempt_index"),
            "recovery_action": snapshot.get("recovery_action"),
            "metadata": dict(metadata or {}),
        }
        tx = self.log.append(EventType.BREADCRUMB_RECORDED, payload)

        manifest = None
        if checkpoint:
            manifest = self.checkpoints.save(
                snapshot,
                metadata={
                    "breadcrumb_kind": kind,
                    "breadcrumb_transaction_sequence": tx.sequence,
                    "breadcrumb_transaction_digest": tx.digest,
                    **dict(metadata or {}),
                },
            )
        return BreadcrumbReceipt(
            kind=kind,
            transaction_sequence=tx.sequence,
            transaction_digest=tx.digest,
            checkpoint=manifest,
        )

    def restore_latest(self) -> dict[str, Any]:
        """Restore the latest integrity-checked checkpoint payload."""
        return self.checkpoints.restore()

    def verify(self) -> bool:
        """Verify the append-only transaction hash chain."""
        return self.log.verify()

    @property
    def chain_head(self) -> str:
        return self.log.last_digest
