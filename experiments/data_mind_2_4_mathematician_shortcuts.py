#!/usr/bin/env python3
"""DATA-MIND 2.4 "The Mathematician": persistent shortcut-learning overlay.

Preserves DATA-MIND 2.3's proof kernel, verifier boundary, 11D logit-group
controller, inverse child revision, and checkpoint/rollback. Adds append-only
cross-run memory and P/R/I/C-Couple shortcut deliberation. The shortcut layer
may only bias legal search-control knobs; it cannot certify mathematics.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import importlib.util
import json
import math
from pathlib import Path
import sys
from typing import Any

from data_atp.mathematician_memory import AppendOnlyMemoryStore, ShortcutLearner

HERE = Path(__file__).resolve().parent
V2_PATH = HERE / "data_mind_2_2_2_3_actual_knob_controller_v2.py"
spec = importlib.util.spec_from_file_location("data_mind_2x_v2_for_24", V2_PATH)
if spec is None or spec.loader is None:
    raise SystemExit(f"cannot load {V2_PATH}")
V2 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = V2
spec.loader.exec_module(V2)

BASE = V2.BASE
EventType = V2.EventType
emit = V2.emit
KNOBS = V2.KNOBS
PARTNERS = {
    "P": ("P1", "P2"),
    "R": ("R1", "R2"),
    "I": ("I1", "I2"),
    "C": ("C1", "C2"),
}


@dataclass(frozen=True, slots=True)
class Config:
    problem_id: str
    run_id: str
    memory: Path
    shortcut_ledger: Path
    exposure_ledger: Path
    shortcut_step: float
    min_confidence: float
    top_k: int
    distant_probability: float
    shortcuts_enabled: bool
    ingest: tuple[tuple[str, Path], ...]


_CONFIG: Config | None = None


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str) + "\n")


def arg_value(argv: list[str], flag: str, default: str | None = None) -> str | None:
    try:
        i = argv.index(flag)
    except ValueError:
        return default
    return argv[i + 1] if i + 1 < len(argv) else default


def problem_id_for_target(target: str) -> str:
    low = target.lower()
    if low == "sgrpcl":
        return "DM-PB-0001"
    if "halo" in low:
        return "DM-PB-0002"
    return f"target:{target}"


def finite(x: Any) -> bool:
    return isinstance(x, (int, float)) and math.isfinite(float(x))


class MathematicianController(V2.ExactGroupActualKnobController):
    architecture_version = "2.4"

    def __init__(self, *args, **kwargs):
        if _CONFIG is None:
            raise RuntimeError("DATA-MIND 2.4 config missing")
        self.cfg = _CONFIG
        super().__init__(*args, **kwargs)
        self.memory_store = AppendOnlyMemoryStore(self.cfg.memory)
        for pid, path in self.cfg.ingest:
            self.memory_store.ingest_transaction_log(
                path,
                problem_id=pid,
                run_id=f"import:{path.stem}",
                source_label=str(path),
            )
        self.learner = ShortcutLearner(
            self.memory_store,
            knobs=KNOBS,
            seed=2301,
            distant_probability=self.cfg.distant_probability,
        )
        self.pending: dict[str, Any] | None = None
        self.shortcut_proposals = 0
        self.shortcut_applied = 0
        self.shortcut_successes = 0
        self.shortcut_failures = 0
        self.couple_messages = 0
        self.memory_store.append(
            problem_id=self.cfg.problem_id,
            run_id=self.cfg.run_id,
            kind="mathematician_run_start",
            action={
                "architecture_version": "2.4",
                "control_base_version": "2.3",
                "shortcuts_enabled": self.cfg.shortcuts_enabled,
            },
            tags=("run", "persistent-memory"),
            source="DATA-MIND 2.4",
        )

    def begin_agent(self, agent_name: str) -> None:
        self.pending = None
        super().begin_agent(agent_name)
        self.memory_store.append(
            problem_id=self.cfg.problem_id,
            run_id=self.cfg.run_id,
            kind="agent_start",
            source_agent=str(agent_name),
            state_signature={"mode": self.mode},
            action={"latent_vector": dict(self.u)},
            tags=("agent", "start"),
        )

    def state_signature(
        self,
        *,
        exp: int,
        live_rhat: float,
        stale: int,
        dup_rate: float,
        terminal_rejects: int,
        frontier_size: int,
        imagined_total: int,
        imagined_previous: int,
        remaining_budget: int,
    ) -> dict[str, Any]:
        return {
            "expansion": int(exp),
            "live_rhat": float(live_rhat),
            "stale": int(stale),
            "duplicate_rate": float(dup_rate),
            "terminal_rejects": int(terminal_rejects),
            "frontier_size": int(frontier_size),
            "imagined_delta": max(0, int(imagined_total) - int(imagined_previous)),
            "remaining_budget": int(remaining_budget),
            "quality": float(self.last_quality) if finite(self.last_quality) else None,
            "dissatisfaction": float(self.last_dissatisfaction),
            "mode": self.mode,
        }

    def settle_pending(self, *, exp: int) -> None:
        if self.pending is None:
            return
        p = self.pending
        quality_gain = (
            float(p["baseline_quality"]) - float(self.last_quality)
            if finite(p.get("baseline_quality")) and finite(self.last_quality)
            else 0.0
        )
        rhat_gain = (
            float(p["baseline_rhat"]) - float(self.best_rhat)
            if finite(p.get("baseline_rhat")) and finite(self.best_rhat)
            else 0.0
        )
        success = rhat_gain > 1e-12 or quality_gain > 0.005
        outcome = "success" if success else "failure"
        if success:
            self.shortcut_successes += 1
        else:
            self.shortcut_failures += 1
        metrics = {
            "proposal_id": p["proposal_id"],
            "applied_expansion": p["applied_expansion"],
            "evaluated_expansion": int(exp),
            "window_expansions": int(exp) - int(p["applied_expansion"]),
            "quality_gain": quality_gain,
            "rhat_gain": rhat_gain,
            "measured_gain": max(quality_gain, rhat_gain),
            "confidence": p["confidence"],
            "expected_gain": p["expected_gain"],
            "source_record_ids": p["source_record_ids"],
        }
        self.memory_store.append(
            problem_id=self.cfg.problem_id,
            run_id=self.cfg.run_id,
            kind="shortcut_outcome",
            outcome=outcome,
            source_agent=self.current_agent,
            shortcut_type="control",
            state_signature=p["state_signature"],
            action={"delta": p["delta"], "proposal_id": p["proposal_id"]},
            metrics=metrics,
            tags=("shortcut", outcome),
        )
        append_jsonl(
            self.cfg.shortcut_ledger,
            {
                "kind": "shortcut_outcome",
                "problem_id": self.cfg.problem_id,
                "run_id": self.cfg.run_id,
                "agent": self.current_agent,
                "outcome": outcome,
                "delta": p["delta"],
                **metrics,
            },
        )
        emit(
            self.log,
            EventType.SELF_REPORT_FILED,
            "shortcut_outcome",
            outcome=outcome,
            **metrics,
            verifier_authority=False,
        )
        self.pending = None

    def deliberate(self, *, exp: int, state: dict[str, Any]) -> None:
        proposal = self.learner.propose(
            problem_id=self.cfg.problem_id,
            state_signature=state,
            max_abs_delta=self.cfg.shortcut_step,
            top_k_per_couple=self.cfg.top_k,
        )
        self.shortcut_proposals += 1

        for cp in proposal.couples:
            self.couple_messages += 1
            emit(
                self.log,
                EventType.SELF_REPORT_FILED,
                "couple_shortcut_deliberation",
                couple=cp.couple,
                partners=PARTNERS[cp.couple],
                delta=cp.delta,
                confidence=cp.confidence,
                expected_gain=cp.expected_gain,
                source_record_ids=cp.source_record_ids,
                certified_math=False,
                may_verify=False,
            )
            self.memory_store.append(
                problem_id=self.cfg.problem_id,
                run_id=self.cfg.run_id,
                kind="couple_shortcut_deliberation",
                source_couple=cp.couple,
                shortcut_type="control",
                state_signature=state,
                action={"delta": cp.delta},
                metrics={
                    "confidence": cp.confidence,
                    "expected_gain": cp.expected_gain,
                    "source_record_ids": cp.source_record_ids,
                },
                tags=("shortcut", "couple", cp.couple, "pre-bank"),
            )

        emit(
            self.log,
            EventType.STRATEGY_OVERRIDE_PROPOSED,
            "persistent_shortcut_consensus",
            proposal_id=proposal.proposal_id,
            delta=proposal.delta,
            confidence=proposal.confidence,
            expected_gain=proposal.expected_gain,
            source_record_ids=proposal.source_record_ids,
            legal_control_only=True,
            verifier_authority=False,
        )
        self.memory_store.append(
            problem_id=self.cfg.problem_id,
            run_id=self.cfg.run_id,
            kind="shortcut_proposal",
            outcome="pending",
            source_agent=self.current_agent,
            shortcut_type="control",
            state_signature=state,
            action={"delta": proposal.delta, "proposal_id": proposal.proposal_id},
            metrics={
                "confidence": proposal.confidence,
                "expected_gain": proposal.expected_gain,
                "source_record_ids": proposal.source_record_ids,
            },
            tags=("shortcut", "proposal"),
        )

        active = any(abs(float(v)) > 1e-12 for v in proposal.delta.values())
        allowed = (
            self.cfg.shortcuts_enabled
            and active
            and proposal.confidence >= self.cfg.min_confidence
        )
        append_jsonl(
            self.cfg.shortcut_ledger,
            {
                "kind": "shortcut_proposal",
                "problem_id": self.cfg.problem_id,
                "run_id": self.cfg.run_id,
                "agent": self.current_agent,
                "proposal_id": proposal.proposal_id,
                "confidence": proposal.confidence,
                "expected_gain": proposal.expected_gain,
                "source_record_ids": proposal.source_record_ids,
                "delta": proposal.delta,
                "applied": allowed,
            },
        )
        if not allowed:
            return

        before = dict(self.u)
        for key, delta in proposal.delta.items():
            self._bounded_move(key, float(delta))
        self._install_vector(self.u)
        actual_delta = {k: float(self.u[k]) - float(before[k]) for k in KNOBS}
        self.shortcut_applied += 1
        emit(
            self.log,
            EventType.STRATEGY_OVERRIDE_EXECUTED,
            "persistent_shortcut_knob_bias",
            proposal_id=proposal.proposal_id,
            before_latent_vector=before,
            after_latent_vector=dict(self.u),
            actual_delta=actual_delta,
            confidence=proposal.confidence,
            expected_gain=proposal.expected_gain,
            source_record_ids=proposal.source_record_ids,
            certificate_authority=False,
            verifier_authority=False,
        )
        self.memory_store.append(
            problem_id=self.cfg.problem_id,
            run_id=self.cfg.run_id,
            kind="shortcut_applied",
            outcome="pending",
            source_agent=self.current_agent,
            shortcut_type="control",
            state_signature=state,
            action={
                "delta": actual_delta,
                "proposal_id": proposal.proposal_id,
                "before_latent_vector": before,
                "after_latent_vector": dict(self.u),
            },
            metrics={
                "confidence": proposal.confidence,
                "expected_gain": proposal.expected_gain,
                "source_record_ids": proposal.source_record_ids,
            },
            tags=("shortcut", "applied"),
        )
        self.pending = {
            "proposal_id": proposal.proposal_id,
            "applied_expansion": int(exp),
            "state_signature": state,
            "delta": actual_delta,
            "baseline_quality": float(self.last_quality) if finite(self.last_quality) else None,
            "baseline_rhat": float(self.best_rhat) if finite(self.best_rhat) else None,
            "confidence": proposal.confidence,
            "expected_gain": proposal.expected_gain,
            "source_record_ids": proposal.source_record_ids,
        }

    def sample(self, **kwargs) -> str:
        exp = int(kwargs["exp"])
        before_base = dict(self.u)
        action = super().sample(**kwargs)
        if self.last_control_exp != exp:
            return action

        state = self.state_signature(**kwargs)
        self.settle_pending(exp=exp)
        base_delta = {k: float(self.u[k]) - float(before_base[k]) for k in KNOBS}

        if action == "NONE":
            self.memory_store.append(
                problem_id=self.cfg.problem_id,
                run_id=self.cfg.run_id,
                kind="adult_control_observation",
                source_agent=self.current_agent,
                shortcut_type="control",
                state_signature=state,
                action={"latent_delta": base_delta},
                metrics={
                    "quality": float(self.last_quality) if finite(self.last_quality) else None,
                    "dissatisfaction": float(self.last_dissatisfaction),
                },
                tags=("control", "adult", "observation"),
            )
        else:
            # Child inverse/accept/rollback transitions are preserved, but are
            # not exposed to the shortcut learner as ordinary adult deltas.
            self.memory_store.append(
                problem_id=self.cfg.problem_id,
                run_id=self.cfg.run_id,
                kind="child_control_transition",
                source_agent=self.current_agent,
                shortcut_type=None,
                state_signature=state,
                action={"child_action": action},
                metrics={
                    "quality": float(self.last_quality) if finite(self.last_quality) else None,
                    "dissatisfaction": float(self.last_dissatisfaction),
                },
                tags=("control", "child", action.lower()),
            )

        # Never stack learned shortcut control on a child transition.
        if action == "NONE" and self.mode == "ADULT":
            self.deliberate(exp=exp, state=state)
        return action

    def end_agent(self, *, expansions: int, imagined: int, terminal_rejects: int) -> None:
        if self.pending is not None:
            p = self.pending
            self.memory_store.append(
                problem_id=self.cfg.problem_id,
                run_id=self.cfg.run_id,
                kind="shortcut_outcome",
                outcome="censored",
                source_agent=self.current_agent,
                shortcut_type="control",
                state_signature=p["state_signature"],
                action={"delta": p["delta"], "proposal_id": p["proposal_id"]},
                metrics={"reason": "agent-ended-before-next-control-sample"},
                tags=("shortcut", "censored"),
            )
            self.pending = None
        super().end_agent(
            expansions=expansions,
            imagined=imagined,
            terminal_rejects=terminal_rejects,
        )

    def summary(self) -> dict[str, Any]:
        data = super().summary()
        data.update(
            {
                "architecture_version": "2.4",
                "control_base_version": "2.3 exact-group controller",
                "persistent_append_only_memory": True,
                "successes_never_deleted": True,
                "failures_never_deleted": True,
                "shortcut_learning_enabled": self.cfg.shortcuts_enabled,
                "cross_problem_memory_allowed": True,
                "occasional_distant_retrieval": True,
                "p_r_i_c_couples_in_shortcut_deliberation": True,
                "child_transitions_separated_from_adult_shortcut_training": True,
                "shortcut_proposals": self.shortcut_proposals,
                "shortcut_applied": self.shortcut_applied,
                "shortcut_successes": self.shortcut_successes,
                "shortcut_failures": self.shortcut_failures,
                "couple_shortcut_messages": self.couple_messages,
                "memory_records": len(self.memory_store.records()),
                "memory_hash_chain_valid": self.memory_store.verify(),
                "verifier_sovereign": True,
                "shortcut_layer_search_control_only": True,
            }
        )
        return data


def parse_ingest(items: list[str], current_problem_id: str) -> tuple[tuple[str, Path], ...]:
    out: list[tuple[str, Path]] = []
    for item in items:
        if "::" in item:
            pid, path = item.split("::", 1)
            out.append((pid or current_problem_id, Path(path)))
        else:
            out.append((current_problem_id, Path(item)))
    return tuple(out)


def main() -> int:
    global _CONFIG
    custom = argparse.ArgumentParser(add_help=False)
    custom.add_argument("--version", choices=["2.4"], default="2.4")
    custom.add_argument("--problem-id")
    custom.add_argument("--run-id")
    custom.add_argument("--memory")
    custom.add_argument("--shortcut-ledger")
    custom.add_argument("--exposure-ledger")
    custom.add_argument("--shortcut-step", type=float, default=0.0125)
    custom.add_argument("--shortcut-min-confidence", type=float, default=0.08)
    custom.add_argument("--shortcut-top-k", type=int, default=8)
    custom.add_argument("--distant-probability", type=float, default=0.05)
    custom.add_argument("--disable-shortcuts", action="store_true")
    custom.add_argument("--ingest-transactions", action="append", default=[])
    ours, remaining = custom.parse_known_args(sys.argv[1:])

    target = arg_value(remaining, "--target", "sgrpcl") or "sgrpcl"
    problem_id = ours.problem_id or problem_id_for_target(target)
    run_id = ours.run_id or f"{problem_id}:{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    summary_raw = arg_value(remaining, "--summary")
    transactions_raw = arg_value(remaining, "--transactions")
    out_raw = arg_value(remaining, "--out")
    if not summary_raw or not transactions_raw or not out_raw:
        raise SystemExit("2.4 requires base --summary, --transactions, and --out")

    summary_path = Path(summary_raw).resolve()
    _CONFIG = Config(
        problem_id=problem_id,
        run_id=run_id,
        memory=Path(ours.memory).resolve() if ours.memory else summary_path.with_name("mathematician_memory.jsonl"),
        shortcut_ledger=Path(ours.shortcut_ledger).resolve() if ours.shortcut_ledger else summary_path.with_name("shortcut_runtime_ledger.jsonl"),
        exposure_ledger=Path(ours.exposure_ledger).resolve() if ours.exposure_ledger else summary_path.with_name("exposure_runtime_ledger.jsonl"),
        shortcut_step=max(0.0, min(0.05, float(ours.shortcut_step))),
        min_confidence=max(0.0, min(1.0, float(ours.shortcut_min_confidence))),
        top_k=max(1, int(ours.shortcut_top_k)),
        distant_probability=max(0.0, min(1.0, float(ours.distant_probability))),
        shortcuts_enabled=not ours.disable_shortcuts,
        ingest=parse_ingest(ours.ingest_transactions, problem_id),
    )

    append_jsonl(
        _CONFIG.exposure_ledger,
        {
            "kind": "run_start",
            "problem_id": problem_id,
            "run_id": run_id,
            "target": target,
            "architecture": "DATA-MIND 2.4 The Mathematician",
            "shortcuts_enabled": _CONFIG.shortcuts_enabled,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        },
    )

    BASE.ActualKnobController = MathematicianController
    original_argv = sys.argv[:]
    sys.argv = [original_argv[0], "--version", "2.3", *remaining]
    try:
        try:
            rc = int(BASE.main() or 0)
        except SystemExit as exc:
            rc = int(exc.code or 0)
    finally:
        sys.argv = original_argv

    store = AppendOnlyMemoryStore(_CONFIG.memory)
    imported = store.ingest_transaction_log(
        Path(transactions_raw).resolve(),
        problem_id=problem_id,
        run_id=f"{run_id}:transactions",
        source_label=str(Path(transactions_raw).resolve()),
    )
    candidate = Path(out_raw).resolve()
    candidate_present = candidate.exists() and candidate.stat().st_size > 0
    store.append(
        problem_id=problem_id,
        run_id=run_id,
        kind="mathematician_run_end",
        outcome="candidate-produced" if candidate_present else "search-ended",
        action={"search_returncode": rc, "candidate_present": candidate_present},
        metrics={"current_transactions_imported": imported},
        tags=("run", "end"),
    )
    append_jsonl(
        _CONFIG.exposure_ledger,
        {
            "kind": "run_end",
            "problem_id": problem_id,
            "run_id": run_id,
            "target": target,
            "search_returncode": rc,
            "candidate_present": candidate_present,
            "memory_records": len(store.records()),
            "memory_hash_chain_valid": store.verify(),
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        },
    )

    if summary_path.exists():
        data = json.loads(summary_path.read_text(encoding="utf-8"))
        data.update(
            {
                "solver": "DATA-MIND 2.4 The Mathematician",
                "architecture_version": "2.4",
                "control_base_version": "2.3",
                "problem_id": problem_id,
                "run_id": run_id,
                "persistent_memory_path": str(_CONFIG.memory),
                "shortcut_runtime_ledger": str(_CONFIG.shortcut_ledger),
                "exposure_runtime_ledger": str(_CONFIG.exposure_ledger),
                "memory_records_after_transaction_import": len(store.records()),
                "current_transactions_imported": imported,
                "memory_hash_chain_valid_after_import": store.verify(),
                "success_failure_history_append_only": True,
                "candidate_still_requires_independent_verification": True,
            }
        )
        summary_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    if not store.verify():
        raise SystemExit("DATA-MIND 2.4 memory hash-chain failure")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
