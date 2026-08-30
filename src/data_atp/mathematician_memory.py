"""Append-only cross-run memory and shortcut retrieval for DATA-MIND.

Successes and failures are both first-class evidence.  The store has no delete
or overwrite operation: later experiments can append reweighting/superseding
records but never erase prior evidence.  This module advises search only; it
has no authority over proof verification or BANK admission.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import random
from typing import Any, Mapping, Sequence

COUPLES = ("P", "R", "I", "C")


def _json(x: Any) -> str:
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def _hash(x: Any) -> str:
    return hashlib.sha256(_json(x).encode("utf-8")).hexdigest()


def _couple(agent: Any) -> str | None:
    text = str(agent or "").upper()
    return text[0] if text and text[0] in COUPLES else None


def _outcome(event_type: str, kind: str, payload: Mapping[str, Any]) -> str:
    text = f"{event_type} {kind}".lower()
    if any(x in text for x in ("accepted", "proved", "progress", "success")):
        return "success"
    if any(x in text for x in ("rejected", "failed", "rollback", "stagnation", "timeout", "fault")):
        return "failure"
    if payload.get("evaluation") == "productive":
        return "success"
    if payload.get("evaluation") == "needs_revision":
        return "failure"
    return "observation"


def _numeric_similarity(a: Mapping[str, Any], b: Mapping[str, Any]) -> float:
    vals: list[float] = []
    for key in set(a) & set(b):
        av, bv = a[key], b[key]
        if isinstance(av, bool) or isinstance(bv, bool):
            continue
        if not isinstance(av, (int, float)) or not isinstance(bv, (int, float)):
            continue
        if not math.isfinite(float(av)) or not math.isfinite(float(bv)):
            continue
        scale = max(1.0, abs(float(av)), abs(float(bv)))
        vals.append(1.0 / (1.0 + abs(float(av) - float(bv)) / scale))
    return sum(vals) / len(vals) if vals else 0.0


@dataclass(frozen=True, slots=True)
class CoupleProposal:
    couple: str
    delta: dict[str, float]
    confidence: float
    expected_gain: float
    source_record_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ShortcutProposal:
    proposal_id: str
    delta: dict[str, float]
    confidence: float
    expected_gain: float
    couples: tuple[CoupleProposal, ...]
    source_record_ids: tuple[str, ...]


class AppendOnlyMemoryStore:
    """Hash-chained JSONL store.  Intentionally exposes no deletion API."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._records: list[dict[str, Any]] = []
        self._fingerprints: set[str] = set()
        if self.path.exists() and self.path.stat().st_size:
            self._load()

    def _load(self) -> None:
        previous = "GENESIS"
        for expected, line in enumerate(self.path.read_text(encoding="utf-8").splitlines()):
            if not line.strip():
                raise ValueError(f"blank memory line {expected + 1}")
            rec = json.loads(line)
            if int(rec["sequence"]) != expected or rec["previous_hash"] != previous:
                raise ValueError("memory chain sequence/previous_hash failure")
            body = dict(rec)
            digest = body.pop("digest")
            if _hash(body) != digest:
                raise ValueError("memory digest verification failed")
            self._records.append(rec)
            previous = digest
            fp = (rec.get("metrics") or {}).get("source_fingerprint")
            if fp:
                self._fingerprints.add(str(fp))

    @property
    def last_digest(self) -> str:
        return self._records[-1]["digest"] if self._records else "GENESIS"

    def append(
        self,
        *,
        problem_id: str,
        run_id: str,
        kind: str,
        outcome: str = "observation",
        source_agent: str | None = None,
        source_couple: str | None = None,
        shortcut_type: str | None = None,
        state_signature: Mapping[str, Any] | None = None,
        action: Mapping[str, Any] | None = None,
        metrics: Mapping[str, Any] | None = None,
        tags: Sequence[str] = (),
        verified: bool | None = None,
        source: str | None = None,
    ) -> dict[str, Any]:
        base = {
            "sequence": len(self._records),
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "problem_id": str(problem_id),
            "run_id": str(run_id),
            "kind": str(kind),
            "outcome": str(outcome),
            "source_agent": source_agent,
            "source_couple": source_couple,
            "shortcut_type": shortcut_type,
            "state_signature": dict(state_signature or {}),
            "action": dict(action or {}),
            "metrics": dict(metrics or {}),
            "tags": [str(x) for x in tags],
            "verified": verified,
            "source": source,
            "previous_hash": self.last_digest,
        }
        base["record_id"] = _hash({"path": str(self.path), **base})[:24]
        rec = dict(base)
        rec["digest"] = _hash(base)
        with self.path.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write(_json(rec) + "\n")
            fh.flush()
        self._records.append(rec)
        fp = rec["metrics"].get("source_fingerprint")
        if fp:
            self._fingerprints.add(str(fp))
        return dict(rec)

    def records(self) -> tuple[dict[str, Any], ...]:
        return tuple(dict(x) for x in self._records)

    def verify(self) -> bool:
        previous = "GENESIS"
        for expected, rec in enumerate(self._records):
            if rec["sequence"] != expected or rec["previous_hash"] != previous:
                return False
            body = dict(rec)
            digest = body.pop("digest")
            if _hash(body) != digest:
                return False
            previous = digest
        return True

    def ingest_transaction_log(
        self,
        path: str | Path,
        *,
        problem_id: str,
        run_id: str,
        source_label: str | None = None,
    ) -> int:
        path = Path(path)
        if not path.exists() or not path.stat().st_size:
            return 0
        added = 0
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            raw = json.loads(line)
            payload = dict(raw.get("payload") or {})
            fp = _hash({
                "path": str(path),
                "line": lineno,
                "digest": raw.get("digest"),
                "payload": payload,
            })
            if fp in self._fingerprints:
                continue
            event_type = str(raw.get("event_type") or "Unknown")
            kind = str(payload.get("kind") or event_type)
            lower = event_type.lower()
            verified = True if "verifieraccepted" in lower else False if "verifierrejected" in lower else None
            signature = {
                k: payload[k]
                for k in (
                    "stale", "duplicate_rate", "terminal_rejects",
                    "terminal_reject_delta", "dissatisfaction",
                    "quality", "expansion",
                )
                if k in payload and isinstance(payload[k], (int, float, bool))
            }
            self.append(
                problem_id=problem_id,
                run_id=run_id,
                kind=kind,
                outcome=_outcome(event_type, kind, payload),
                source_agent=str(payload["agent"]) if payload.get("agent") else None,
                source_couple=_couple(payload.get("agent")),
                shortcut_type="control" if any(x in kind.lower() for x in ("inverse", "knob", "strategy")) else None,
                state_signature=signature,
                action=payload,
                metrics={
                    "source_fingerprint": fp,
                    "imported_event_type": event_type,
                    "imported_sequence": raw.get("sequence"),
                },
                tags=("imported", event_type, kind),
                verified=verified,
                source=source_label or str(path),
            )
            added += 1
        return added

    def retrieve(
        self,
        *,
        problem_id: str,
        state_signature: Mapping[str, Any],
        couple: str | None = None,
        top_k: int = 10,
        distant_probability: float = 0.05,
        rng: random.Random | None = None,
    ) -> tuple[tuple[float, dict[str, Any]], ...]:
        rng = rng or random.Random(0)
        scored: list[tuple[float, dict[str, Any]]] = []
        for rec in self._records:
            score = 0.15
            if rec["problem_id"] == problem_id:
                score += 1.30
            score += 1.10 * _numeric_similarity(state_signature, rec.get("state_signature") or {})
            if couple and rec.get("source_couple") == couple:
                score += 0.35
            if rec.get("verified") is True:
                score += 0.12
            # Failures are deliberately NOT filtered or down-ranked.
            scored.append((score, rec))
        scored.sort(key=lambda x: (x[0], x[1]["sequence"]), reverse=True)
        chosen = scored[: max(0, int(top_k))]
        tail = scored[max(0, int(top_k)) :]
        if tail and distant_probability > 0 and rng.random() < distant_probability:
            chosen.append(tail[rng.randrange(len(tail))])
        return tuple((float(score), dict(rec)) for score, rec in chosen)


class ShortcutLearner:
    """Create bounded P/R/I/C-Couple control proposals from persistent memory."""

    def __init__(
        self,
        store: AppendOnlyMemoryStore,
        *,
        knobs: Sequence[str],
        seed: int = 2301,
        distant_probability: float = 0.05,
    ):
        self.store = store
        self.knobs = tuple(knobs)
        self.rng = random.Random(int(seed))
        self.distant_probability = max(0.0, min(1.0, float(distant_probability)))

    def _delta(self, rec: Mapping[str, Any]) -> dict[str, float]:
        action = rec.get("action") or {}
        raw = action.get("latent_delta") or action.get("delta")
        if isinstance(raw, Mapping):
            return {k: float(raw[k]) for k in self.knobs if isinstance(raw.get(k), (int, float))}
        before = action.get("checkpoint_latent_vector") or action.get("latent_before")
        after = action.get("inverse_latent_vector") or action.get("latent_after")
        if isinstance(before, Mapping) and isinstance(after, Mapping):
            return {
                k: float(after[k]) - float(before[k])
                for k in self.knobs
                if isinstance(before.get(k), (int, float)) and isinstance(after.get(k), (int, float))
            }
        return {}

    @staticmethod
    def _weight(rec: Mapping[str, Any], couple: str) -> float:
        outcome = str(rec.get("outcome") or "").lower()
        if couple == "P":
            return {"success": 1.0, "failure": -0.45}.get(outcome, 0.15)
        if couple == "R":
            return {"success": 0.45, "failure": -1.0}.get(outcome, -0.05)
        if couple == "I":
            return {"success": 0.70, "failure": -0.55}.get(outcome, 0.18)
        if rec.get("verified") is False:
            return -1.25
        if rec.get("verified") is True:
            return 1.0
        return {"success": 0.60, "failure": -0.75}.get(outcome, 0.05)

    def _couple(
        self,
        couple: str,
        *,
        problem_id: str,
        state_signature: Mapping[str, Any],
        top_k: int,
    ) -> CoupleProposal:
        memories = self.store.retrieve(
            problem_id=problem_id,
            state_signature=state_signature,
            couple=couple,
            top_k=top_k,
            distant_probability=min(1.0, self.distant_probability * (2.0 if couple == "I" else 1.0)),
            rng=self.rng,
        )
        totals = {k: 0.0 for k in self.knobs}
        norms = {k: 0.0 for k in self.knobs}
        source_ids: list[str] = []
        signed = absolute = 0.0
        for relevance, rec in memories:
            delta = self._delta(rec)
            if not delta:
                continue
            w = max(0.01, relevance) * self._weight(rec, couple)
            for k, value in delta.items():
                totals[k] += w * value
                norms[k] += abs(w)
            signed += w
            absolute += abs(w)
            source_ids.append(str(rec["record_id"]))
        out = {k: totals[k] / norms[k] if norms[k] else 0.0 for k in self.knobs}
        confidence = min(1.0, (len(source_ids) / max(1, top_k)) * (absolute / (1.0 + absolute)))
        gain = signed / absolute if absolute else 0.0
        return CoupleProposal(couple, out, confidence, gain, tuple(dict.fromkeys(source_ids)))

    def propose(
        self,
        *,
        problem_id: str,
        state_signature: Mapping[str, Any],
        max_abs_delta: float,
        top_k_per_couple: int = 8,
    ) -> ShortcutProposal:
        couples = tuple(
            self._couple(c, problem_id=problem_id, state_signature=state_signature, top_k=max(1, top_k_per_couple))
            for c in COUPLES
        )
        role_weight = {"P": 1.0, "R": 0.9, "I": 0.7, "C": 0.9}
        delta: dict[str, float] = {}
        limit = abs(float(max_abs_delta))
        for k in self.knobs:
            num = den = 0.0
            for p in couples:
                w = role_weight[p.couple] * max(0.05, p.confidence)
                num += w * p.delta.get(k, 0.0)
                den += w
            raw = num / den if den else 0.0
            delta[k] = max(-limit, min(limit, raw))
        confidence = sum(p.confidence for p in couples) / len(couples)
        expected = sum(p.expected_gain for p in couples) / len(couples)
        source_ids = tuple(dict.fromkeys(rid for p in couples for rid in p.source_record_ids))
        pid = _hash({
            "problem": problem_id,
            "state": dict(state_signature),
            "delta": delta,
            "sources": source_ids,
            "nonce": self.rng.random(),
        })[:24]
        return ShortcutProposal(pid, delta, confidence, expected, couples, source_ids)
