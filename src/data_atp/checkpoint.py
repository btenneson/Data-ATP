"""Atomic, integrity-checked checkpoints for Data-ATP Phase 0."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Mapping

from .events import EventType, TransactionLog


CHECKPOINT_SCHEMA_VERSION = "0.1"


class CheckpointError(RuntimeError):
    """Raised when a checkpoint cannot be trusted or restored."""


@dataclass(frozen=True, slots=True)
class CheckpointManifest:
    run_id: str
    checkpoint_sequence: int
    checkpoint_path: str
    sha256_path: str
    sha256: str
    created_utc: str


class CheckpointManager:
    """Save and restore complete caller-supplied run snapshots atomically.

    The manager deliberately does not decide what the proof search state is.
    Callers must supply a complete JSON-serializable snapshot containing every
    item needed to resume (for example frontier, trusted state, budgets, seeds,
    transaction-log offset, and scheduler state).  This keeps the recovery
    mechanism independent of any particular search policy.
    """

    def __init__(self, directory: str | Path, run_id: str, log: TransactionLog) -> None:
        if not run_id.strip():
            raise ValueError("run_id must be nonempty")
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.run_id = run_id
        self.log = log
        self._next_sequence = self._discover_next_sequence()

    def _discover_next_sequence(self) -> int:
        maximum = -1
        for path in self.directory.glob("checkpoint-*.json"):
            try:
                maximum = max(maximum, int(path.stem.split("-")[-1]))
            except ValueError:
                continue
        return maximum + 1

    @staticmethod
    def _canonical_bytes(payload: Mapping[str, Any]) -> bytes:
        try:
            text = json.dumps(
                payload,
                sort_keys=True,
                indent=2,
                separators=(",", ": "),
                ensure_ascii=False,
            ) + "\n"
        except (TypeError, ValueError) as exc:
            raise CheckpointError(f"checkpoint snapshot is not JSON-serializable: {exc}") from exc
        return text.encode("utf-8")

    @staticmethod
    def _atomic_write(path: Path, data: bytes) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_name: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                dir=path.parent,
                prefix=f".{path.name}.",
                suffix=".tmp",
                delete=False,
            ) as handle:
                temp_name = handle.name
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, path)
        finally:
            if temp_name is not None and os.path.exists(temp_name):
                os.unlink(temp_name)

    def save(
        self,
        snapshot: Mapping[str, Any],
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> CheckpointManifest:
        sequence = self._next_sequence
        created_utc = datetime.now(timezone.utc).isoformat()
        payload = {
            "schema_version": CHECKPOINT_SCHEMA_VERSION,
            "run_id": self.run_id,
            "checkpoint_sequence": sequence,
            "created_utc": created_utc,
            "metadata": dict(metadata or {}),
            "snapshot": dict(snapshot),
        }
        raw = self._canonical_bytes(payload)
        digest = hashlib.sha256(raw).hexdigest().upper()

        checkpoint_path = self.directory / f"checkpoint-{sequence:06d}.json"
        sha_path = checkpoint_path.with_suffix(checkpoint_path.suffix + ".sha256")

        self._atomic_write(checkpoint_path, raw)
        self._atomic_write(sha_path, (digest + "\n").encode("ascii"))
        self._next_sequence += 1

        self.log.append(
            EventType.CHECKPOINT_SAVED,
            {
                "run_id": self.run_id,
                "checkpoint_sequence": sequence,
                "checkpoint_path": str(checkpoint_path),
                "sha256": digest,
            },
        )
        return CheckpointManifest(
            run_id=self.run_id,
            checkpoint_sequence=sequence,
            checkpoint_path=str(checkpoint_path),
            sha256_path=str(sha_path),
            sha256=digest,
            created_utc=created_utc,
        )

    def latest_path(self) -> Path:
        paths = sorted(self.directory.glob("checkpoint-*.json"))
        if not paths:
            raise CheckpointError("no checkpoint exists")
        return paths[-1]

    def restore(self, checkpoint_path: str | Path | None = None) -> dict[str, Any]:
        path = Path(checkpoint_path) if checkpoint_path is not None else self.latest_path()
        try:
            raw = path.read_bytes()
            sha_path = path.with_suffix(path.suffix + ".sha256")
            expected = sha_path.read_text(encoding="ascii").strip().upper()
            actual = hashlib.sha256(raw).hexdigest().upper()
            if not expected or expected != actual:
                raise CheckpointError("checkpoint SHA-256 verification failed")

            payload = json.loads(raw.decode("utf-8"))
            if payload.get("schema_version") != CHECKPOINT_SCHEMA_VERSION:
                raise CheckpointError("unsupported checkpoint schema version")
            if payload.get("run_id") != self.run_id:
                raise CheckpointError("checkpoint belongs to a different run")
            if not isinstance(payload.get("snapshot"), dict):
                raise CheckpointError("checkpoint snapshot is missing or malformed")
        except (OSError, UnicodeError, json.JSONDecodeError, CheckpointError) as exc:
            self.log.append(
                EventType.CHECKPOINT_REJECTED,
                {
                    "run_id": self.run_id,
                    "checkpoint_path": str(path),
                    "reason": str(exc),
                },
            )
            if isinstance(exc, CheckpointError):
                raise
            raise CheckpointError(f"checkpoint restore failed: {exc}") from exc

        self.log.append(
            EventType.CHECKPOINT_RESTORED,
            {
                "run_id": self.run_id,
                "checkpoint_sequence": payload["checkpoint_sequence"],
                "checkpoint_path": str(path),
                "sha256": actual,
            },
        )
        return payload
