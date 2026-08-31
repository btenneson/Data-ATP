#!/usr/bin/env python3
"""DATA-MIND 2.7 — Quotient Discovery, Depths/Ocean adapter.

2.7 retains the executable Ocean-native DATA-MIND faculties used by 2.6 and
changes the metalogical agent in one crucial way: Quotient Hunter is no longer
handed an exact reverse-distance quotient.  It generates and evaluates a small
language of candidate structural operators and must discover one that induces
a certified settlement geometry.

For the first Ocean experiment the candidate language contains fixed-point
shell operators, modular observables, and degree quotients.  The theorem BANK
remains verifier-sovereign: QH may alter search order only after an independent
structural check, and a theorem certificate enters BANK only after the
independent path verifier accepts it.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
from typing import Any, Iterable

from data_atp.events import EventType
from data_atp.mathematician_memory import AppendOnlyMemoryStore
from data_atp.quotient_discovery import (
    QuotientDiscoveryEngine,
    independently_verify_discovered_rank,
)


def safe_load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    # Python 3.12 dataclasses expect dynamically loaded modules to be visible
    # in sys.modules while class decorators execute.
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


BASE = safe_load_module(
    "data_mind_ocean_full_feature_for_27",
    Path(__file__).with_name("data_mind_ocean_full_feature.py"),
)
# The inherited eight-agent adapter dynamically loads Predator 8.038.  Replace
# its legacy loader with the Python-3.12-safe loader above.
BASE.load_module = safe_load_module


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


class VerifiedBank:
    """Append-only bank of independently verified theorem certificates."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _rows(self) -> list[dict[str, Any]]:
        if not self.path.exists() or not self.path.stat().st_size:
            return []
        return [
            json.loads(line)
            for line in self.path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def lookup(self, *, problem_sha256: str, verifier) -> tuple[list[int] | None, int]:
        checked = 0
        for row in reversed(self._rows()):
            if row.get("problem_sha256") != problem_sha256:
                continue
            path = row.get("path")
            if not isinstance(path, list) or not all(isinstance(x, int) for x in path):
                continue
            checked += 1
            if verifier(path):
                return list(path), checked
        return None, checked

    def append(
        self,
        *,
        problem_sha256: str,
        problem_id: str,
        path: list[int],
        proof_length: int,
        source: int,
        target: int,
    ) -> None:
        row = {
            "problem_sha256": problem_sha256,
            "problem_id": problem_id,
            "path": [int(x) for x in path],
            "proof_length": int(proof_length),
            "source": int(source),
            "target": int(target),
            "certificate_verified": True,
            "gate": "independent_path_verifier",
            "architecture": "DATA-MIND 2.7 Quotient Discovery",
        }
        with self.path.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(row, sort_keys=True) + "\n")


class DataMind27Depths(BASE.FullFeatureOcean):
    """Full-feature Ocean search with generalized Quotient Discovery."""

    def __init__(
        self,
        *,
        ref,
        source: int,
        target: int,
        edges: list[tuple[int, int]],
        adj: dict[int, list[int]],
        audit,
        time_limit_s: float,
        max_expansions: int,
        seed: int,
        p8038_path: Path,
        control_epoch: int,
        memory: AppendOnlyMemoryStore,
        problem_id: str,
        depth_n: int | None,
        qd_trade_enabled: bool,
        qd_warmup_expansions: int,
        qd_contract_threshold: float,
        qd_fixed_point_window: int,
    ) -> None:
        super().__init__(
            version="1.1",
            ref=ref,
            source=source,
            target=target,
            edges=edges,
            adj=adj,
            audit=audit,
            time_limit_s=time_limit_s,
            max_expansions=max_expansions,
            seed=seed,
            p8038_path=p8038_path,
            control_epoch=control_epoch,
        )
        self.version = "2.7"
        self.control_epoch = max(1, int(control_epoch))
        self.memory = memory
        self.problem_id = str(problem_id)
        self.depth_n = depth_n
        self.qd_trade_enabled = bool(qd_trade_enabled)
        self.qd_warmup_expansions = max(0, int(qd_warmup_expansions))
        self.qd_contract_threshold = float(qd_contract_threshold)
        self.qd_fixed_point_window = max(1, int(qd_fixed_point_window))
        self.qd_trade_active = False
        self.qd_trade_activations = 0
        self.qd_messages = 0
        self.qd_fixed_point_escapes = 0
        self.qd_horizon_observations: list[dict[str, Any]] = []
        self._qd_prev_h: float | None = None
        self._qd_noncontractive_epochs = 0

        state = {
            "depth_n": depth_n if depth_n is not None else -1,
            "nodes": len(self._nodes(edges, source, target)),
            "edges": len(edges),
        }
        prior = self.memory.retrieve(
            problem_id=self.problem_id,
            state_signature=state,
            top_k=24,
            distant_probability=0.0,
        )
        preferred: list[str] = []
        for _, rec in prior:
            if rec.get("outcome") != "success":
                continue
            action = rec.get("action") or {}
            op = action.get("operator")
            if isinstance(op, str):
                preferred.append(op)

        self.qd = QuotientDiscoveryEngine(
            source=source,
            target=target,
            edges=edges,
            preferred_operators=preferred,
        )
        self.qd_discovery = self.qd.discover()
        selected = self.qd_discovery.selected_operator
        labels = self.qd.labels_for(selected) if selected else {}
        self.qd_independent_trade_check = bool(
            selected
            and independently_verify_discovered_rank(
                source=source,
                target=target,
                edges=edges,
                labels=labels,
            )
        )
        self._record_discovery(state)
        self._activate_trade_if_certified()

    @staticmethod
    def _nodes(edges: Iterable[tuple[int, int]], source: int, target: int) -> set[int]:
        out = {int(source), int(target)}
        for u, v in edges:
            out.add(int(u)); out.add(int(v))
        return out

    def _record_discovery(self, state: dict[str, Any]) -> None:
        for report in self.qd_discovery.reports:
            success = bool(report.target_reachability_equivalence_certified)
            self.memory.append(
                problem_id=self.problem_id,
                run_id=f"dm27-qd-{id(self)}",
                kind="quotient_discovery_candidate",
                outcome="success" if success else "observation",
                source_agent="QH",
                shortcut_type="metalogical_operator_discovery",
                state_signature=state,
                action={
                    "operator": report.name,
                    "family": report.family,
                    "score": report.score,
                    "quotient_size": report.quotient_size,
                    "compression_ratio": report.compression_ratio,
                    "source_horizon": report.source_horizon,
                    "lambda_h_bound": report.lambda_h_bound,
                    "certified": report.target_reachability_equivalence_certified,
                },
                tags=("data-mind-2.7", "quotient-discovery", report.family),
                verified=success,
                source="QH candidate-language evaluation on visible rules",
            )
        self.qd_messages += 1
        self.audit.emit(
            EventType.SELF_REPORT_FILED,
            "quotient_discovery_report",
            agent="QH",
            role="metalogical quotient/operator discoverer",
            discovery=self.qd_discovery.as_dict(),
            independent_trade_check=self.qd_independent_trade_check,
            exact_reverse_distance_handed_to_qh=False,
            certified_math=False,
            theorem_bank_authority=False,
        )

    def _activate_trade_if_certified(self) -> None:
        activatable = bool(
            self.qd_trade_enabled
            and self.qd_discovery.trade_activatable
            and self.qd_independent_trade_check
        )
        self.audit.emit(
            EventType.STRATEGY_OVERRIDE_PROPOSED,
            "quotient_discovery_trade_proposed",
            agent="QH",
            selected_operator=self.qd_discovery.selected_operator,
            candidate_count=self.qd_discovery.generated_candidate_count,
            from_policy="general adaptive graph search",
            to_policy="discovered fixed-point quotient descent",
            target_reachability_equivalence_certified=self.qd_discovery.trade_activatable,
            independent_trade_check=self.qd_independent_trade_check,
            theorem_verifier_authority=False,
            activatable=activatable,
        )
        if activatable:
            self.qd_trade_active = True
            self.qd_trade_activations += 1
            self.audit.emit(
                EventType.STRATEGY_OVERRIDE_EXECUTED,
                "quotient_discovery_trade_activated",
                agent="QH",
                selected_operator=self.qd_discovery.selected_operator,
                live_inference_kernel_modified=False,
                independent_theorem_verifier_unchanged=True,
            )

    def choose_strategy(self) -> tuple[str, int | None]:
        op = self.qd_discovery.selected_operator
        if self.qd_trade_active and op and self.expansions >= self.qd_warmup_expansions:
            live = [v for v in self.parent if v not in self.expanded]
            u = self.qd.best_live_vertex(op, live)
            if u is not None:
                self.qd_messages += 1
                if self.qd_messages <= 8 or self.qd_messages % 100 == 0:
                    self.audit.emit(
                        EventType.DIRECTIVE_RECEIVED,
                        "quotient_discovery_directive",
                        agent="QH",
                        operator=op,
                        vertex=u,
                        horizon=self.qd.horizon(op, u),
                        authority="search_order_only",
                        verifier_authority=False,
                    )
                return "qd", u
        return super().choose_strategy()

    def _frontier_horizon(self) -> float | None:
        op = self.qd_discovery.selected_operator
        if not op:
            return None
        vals = [
            self.qd.horizon(op, v)
            for v in self.parent
            if v not in self.expanded and self.qd.horizon(op, v) is not None
        ]
        return float(min(vals)) if vals else None

    def control(
        self,
        epoch_start_exp: int,
        epoch_start_discoveries: int,
        epoch_start_duplicates: int,
    ) -> None:
        super().control(epoch_start_exp, epoch_start_discoveries, epoch_start_duplicates)
        h = self._frontier_horizon()
        ratio = None
        if h is not None and self._qd_prev_h is not None and self._qd_prev_h > 0:
            ratio = h / self._qd_prev_h
        row = {
            "expansions": self.expansions,
            "h_frontier": h,
            "previous_h": self._qd_prev_h,
            "lambda_hat": ratio,
            "contract_threshold": self.qd_contract_threshold,
            "operator": self.qd_discovery.selected_operator,
        }
        self.qd_horizon_observations.append(row)
        self.audit.emit(
            EventType.LOCAL_EVIDENCE_DETECTED,
            "quotient_discovery_contraction_observation",
            agent="QH",
            **row,
            claim_scope="empirical distance-to-settlement only",
        )
        self.memory.append(
            problem_id=self.problem_id,
            run_id=f"dm27-qd-{id(self)}",
            kind="quotient_discovery_contraction_observation",
            outcome=(
                "success"
                if ratio is not None and ratio < self.qd_contract_threshold
                else "observation"
            ),
            source_agent="QH",
            state_signature={
                "depth_n": self.depth_n if self.depth_n is not None else -1,
                "expansion": self.expansions,
                "h_frontier": h if h is not None else -1,
            },
            action={"lambda_hat": ratio, "operator": self.qd_discovery.selected_operator},
            tags=("data-mind-2.7", "contraction"),
            verified=None,
            source="within-run discovered geometry",
        )
        if ratio is not None and ratio >= 1.0:
            self._qd_noncontractive_epochs += 1
        else:
            self._qd_noncontractive_epochs = 0
        if self._qd_noncontractive_epochs >= self.qd_fixed_point_window:
            inv = {k: 1.0 / max(self.weights[k], 1e-4) for k in BASE.STRATEGIES}
            self.qd_fixed_point_escapes += 1
            self.revision_count += 1
            self._set_weights(
                inv,
                "QH discovered noncontractive/fixed-point-like stagnation; group inverse escape",
                "qd-fixed-point-escape",
            )
            self.audit.emit(
                EventType.STRATEGY_OVERRIDE_EXECUTED,
                "quotient_discovery_fixed_point_escape",
                agent="QH",
                method="group_inverse",
                consecutive_noncontractive_epochs=self._qd_noncontractive_epochs,
            )
            self._qd_noncontractive_epochs = 0
        if h is not None:
            self._qd_prev_h = h


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--problem", required=True)
    ap.add_argument("--reference", required=True)
    ap.add_argument("--p8038", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--transactions", required=True)
    ap.add_argument("--memory", required=True)
    ap.add_argument("--bank", required=True)
    ap.add_argument("--problem-id", default="DEPTHS-N6")
    ap.add_argument("--depth-n", type=int, default=6)
    ap.add_argument("--time-limit", type=float, default=600.0)
    ap.add_argument("--max-expansions", type=int, default=100_000_000)
    ap.add_argument("--control-epoch", type=int, default=2)
    ap.add_argument("--seed", type=int, default=2301)
    ap.add_argument("--qd-warmup-expansions", type=int, default=0)
    ap.add_argument("--qd-contract-threshold", type=float, default=0.95)
    ap.add_argument("--qd-fixed-point-window", type=int, default=2)
    ap.add_argument("--disable-qd-trade", action="store_true")
    ap.add_argument("--ingest-transactions", action="append", default=[])
    a = ap.parse_args()

    problem = Path(a.problem)
    ref = safe_load_module("ocean_reference_dm27", Path(a.reference))
    source, target, edges, adj, _ = ref.parse_problem(problem)
    problem_sha = sha256_file(problem)

    memory = AppendOnlyMemoryStore(a.memory)
    imported = 0
    for tx in a.ingest_transactions:
        imported += memory.ingest_transaction_log(
            tx,
            problem_id=a.problem_id,
            run_id=f"dm27-import-{Path(tx).stem}",
            source_label=f"prior transaction evidence: {tx}",
        )

    audit = BASE.Audit(Path(a.transactions))
    bank = VerifiedBank(a.bank)
    bank_path, bank_candidates_checked = bank.lookup(
        problem_sha256=problem_sha,
        verifier=lambda path: ref.verify_path(source, target, edges, path),
    )
    bank_hit = bank_path is not None
    if bank_hit:
        audit.emit(
            EventType.LOCAL_EVIDENCE_DETECTED,
            "bank_read",
            problem_sha256=problem_sha,
            reverified=True,
            proof_length=len(bank_path) - 1,
            candidates_checked=bank_candidates_checked,
        )

    engine = DataMind27Depths(
        ref=ref,
        source=source,
        target=target,
        edges=edges,
        adj=adj,
        audit=audit,
        time_limit_s=a.time_limit,
        max_expansions=a.max_expansions,
        seed=a.seed,
        p8038_path=Path(a.p8038),
        control_epoch=a.control_epoch,
        memory=memory,
        problem_id=a.problem_id,
        depth_n=a.depth_n,
        qd_trade_enabled=not a.disable_qd_trade,
        qd_warmup_expansions=a.qd_warmup_expansions,
        qd_contract_threshold=a.qd_contract_threshold,
        qd_fixed_point_window=a.qd_fixed_point_window,
    )

    search0 = time.perf_counter()
    if bank_hit:
        raw = {"status": "PROVED", "path": bank_path, "expansions": 0}
    else:
        raw = engine.search()
    search_wall = time.perf_counter() - search0
    path = raw.get("path")

    audit.emit(
        EventType.CERTIFICATE_SUBMITTED,
        "bank_proposal",
        status=raw.get("status"),
        expansions=raw.get("expansions"),
        from_existing_bank=bank_hit,
        certified_at_proposal_time=False,
    )
    verify0 = time.perf_counter()
    verified = bool(path is not None and ref.verify_path(source, target, edges, path))
    verify_wall = time.perf_counter() - verify0

    bank_commit_written = False
    if verified:
        audit.emit(
            EventType.VERIFIER_ACCEPTED,
            "verifier_result",
            accepted=True,
            proof_length=len(path) - 1,
            reverified_bank_hit=bank_hit,
        )
        if not bank_hit:
            bank.append(
                problem_sha256=problem_sha,
                problem_id=a.problem_id,
                path=list(path),
                proof_length=len(path) - 1,
                source=source,
                target=target,
            )
            bank_commit_written = True
        audit.emit(
            EventType.ACTION_EXECUTED,
            "bank_commit" if bank_commit_written else "bank_reuse",
            gate="independent_path_verifier",
        )
    else:
        audit.emit(
            EventType.VERIFIER_REJECTED,
            "verifier_result",
            accepted=False,
            status=raw.get("status"),
        )

    status = "PROVED" if verified else raw.get("status", "FAULT")
    memory.append(
        problem_id=a.problem_id,
        run_id="dm27-depths-final",
        kind="independent_verifier_result",
        outcome="success" if verified else "failure",
        source_agent="V",
        state_signature={
            "depth_n": a.depth_n,
            "expansions": int(raw.get("expansions") or 0),
        },
        action={
            "status": status,
            "proof_length": (len(path) - 1) if verified else None,
            "selected_operator": engine.qd_discovery.selected_operator,
            "qd_trade_active": engine.qd_trade_active,
        },
        tags=("data-mind-2.7", "depths", "final", "verifier-gated"),
        verified=verified,
        source="independent Ocean path verifier",
    )

    selected_report = next(
        (r for r in engine.qd_discovery.reports
         if r.name == engine.qd_discovery.selected_operator),
        None,
    )
    tx_ok = audit.log.verify()
    memory_ok = memory.verify()
    summary = {
        "solver": "DATA-MIND 2.7 — Quotient Discovery",
        "architecture_version": "2.7",
        "benchmark": "Depths/Ocean",
        "depth_n": a.depth_n,
        "problem_id": a.problem_id,
        "problem_sha256": problem_sha,
        "status": status,
        "certificate_verified": verified,
        "proof_length": (len(path) - 1) if verified else None,
        "expansions": raw.get("expansions"),
        "search_wall_s": search_wall,
        "verify_wall_s": verify_wall,
        "time_limit_s": a.time_limit,
        "all_eight_pric_agents_enabled": True,
        "quotient_hunter_enabled": True,
        "quotient_discovery_enabled": True,
        "exact_reverse_distance_handed_to_qh": False,
        "candidate_language": [
            "source/target x predecessor/successor least-fixed-point shells",
            "bounded degree signatures",
            "node-id modular observables mod 2..7",
        ],
        "generated_candidate_count": engine.qd_discovery.generated_candidate_count,
        "selected_operator": engine.qd_discovery.selected_operator,
        "selected_family": engine.qd_discovery.selected_family,
        "discovery_statement": engine.qd_discovery.discovery_statement,
        "source_horizon_discovered": engine.qd_discovery.source_horizon,
        "selected_quotient_size": selected_report.quotient_size if selected_report else None,
        "selected_compression_ratio": selected_report.compression_ratio if selected_report else None,
        "selected_lambda_H_bound": selected_report.lambda_h_bound if selected_report else None,
        "selected_unique_policy_fixed_point": (
            selected_report.unique_policy_fixed_point if selected_report else False
        ),
        "candidate_reports": [r.as_dict() for r in engine.qd_discovery.reports],
        "qd_trade_requested": not a.disable_qd_trade,
        "qd_trade_activatable": engine.qd_discovery.trade_activatable,
        "qd_trade_independently_verified": engine.qd_independent_trade_check,
        "qd_trade_active": engine.qd_trade_active,
        "qd_trade_activations": engine.qd_trade_activations,
        "qd_policy_path_verified_structurally": engine.qd_discovery.policy_path_verified,
        "live_inference_kernel_modified": False,
        "independent_theorem_verifier_unchanged": True,
        "qd_agent_message_count": engine.qd_messages,
        "qd_contraction_observations": engine.qd_horizon_observations,
        "qd_fixed_point_escapes": engine.qd_fixed_point_escapes,
        "professor_enabled": True,
        "counselor_enabled": True,
        "learning_enabled": True,
        "adaptive_control_enabled": True,
        "structured_creativity_enabled": True,
        "group_inverse_revision_enabled": True,
        "persistent_cross_run_memory_enabled": True,
        "prior_transactions_imported": imported,
        "memory_records": len(memory.records()),
        "memory_hash_chain_valid": memory_ok,
        "bank_read_enabled": True,
        "bank_hit": bank_hit,
        "bank_candidates_checked": bank_candidates_checked,
        "bank_write_verifier_gated": True,
        "bank_commit_written": bank_commit_written,
        "controller_switch_count": len(engine.controller_switches),
        "revision_count": engine.revision_count,
        "creativity_count": engine.creativity_count,
        "agent_message_count": engine.agent_messages,
        "professor_events": engine.professor_events,
        "counselor_events": engine.counselor_events,
        "learning_events": engine.learning_events,
        "transaction_log_verified": tx_ok,
        "hidden_metadata_read": False,
        "scope_note": (
            "2.7 discovers a useful operator from a bounded candidate language. "
            "It does not yet synthesize arbitrary mathematical invariants such as "
            "MIU's mod-3 invariant from unrestricted symbolic expressions."
        ),
    }
    Path(a.out).write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)
    if not tx_ok or not memory_ok:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
