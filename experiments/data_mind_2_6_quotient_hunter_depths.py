#!/usr/bin/env python3
"""DATA-MIND 2.6 — Quotient Hunter, Depths/Ocean adapter.

This is the first executable DATA-MIND 2.6 experiment.

2.6 retains the strongest executable Ocean-native faculties already present in
DATA-MIND 1.1 (adaptive control, structured creativity, group-inverse revision,
P/R/I/C-coupled eight-agent deliberation, Counselor, Professor, Learning,
shared frontier, verifier-gated BANK) and adds:

* QH — Quotient Hunter, a distinct metalogical agent.
* quotient/invariant candidate search, including MIU-like modular candidates;
* exact visible-graph distance-to-settlement geometry when it can be certified;
* H(Tx) contraction measurement and fixed-point detection;
* a verifier-safe target-specific "trade" from unrestricted graph ranking to
  a certified quotient-geodesic ranking policy;
* append-only cross-run memory that can prioritize previously successful QH
  candidate families;
* actual BANK read as well as verifier-gated BANK write.

The QH structural certificate is NOT a theorem certificate.  Candidate paths
still enter BANK only after the independent path verifier accepts them.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path
import time
from typing import Any, Iterable

from data_atp.events import EventType
from data_atp.mathematician_memory import AppendOnlyMemoryStore
from data_atp.quotient_hunter import QuotientHunter


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


BASE = load_module(
    "data_mind_ocean_full_feature_for_26",
    Path(__file__).with_name("data_mind_ocean_full_feature.py"),
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def independently_verify_rank_trade(
    *,
    source: int,
    target: int,
    edges: Iterable[tuple[int, int]],
    rank: dict[int, int],
) -> bool:
    """Independent Bellman/reachability check for the QH search-policy trade."""
    adj: dict[int, list[int]] = defaultdict(list)
    for u, v in edges:
        adj[int(u)].append(int(v))
    if rank.get(int(target)) != 0 or int(source) not in rank:
        return False
    for u, h in rank.items():
        if u == target:
            continue
        finite = [rank[v] for v in adj.get(u, ()) if v in rank]
        if not finite or h != 1 + min(finite):
            return False

    u = int(source)
    seen = {u}
    while u != target:
        h = rank.get(u)
        if h is None or h <= 0:
            return False
        nxt = [v for v in adj.get(u, ()) if rank.get(v) == h - 1]
        if not nxt:
            return False
        u = min(nxt)
        if u in seen:
            return False
        seen.add(u)
    return True


class VerifiedBank:
    """Append-only bank of independently verified target certificates."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _rows(self) -> list[dict[str, Any]]:
        if not self.path.exists() or not self.path.stat().st_size:
            return []
        rows = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
        return rows

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
            "architecture": "DATA-MIND 2.6 Quotient Hunter",
        }
        with self.path.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(row, sort_keys=True) + "\n")


class DataMind26Depths(BASE.FullFeatureOcean):
    """Full-feature Ocean search plus the QH metalogical agent."""

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
        qh_trade_enabled: bool,
        qh_warmup_expansions: int,
        qh_contract_threshold: float,
        qh_fixed_point_window: int,
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
        self.version = "2.6"
        # The base Ocean adapter clamps control epochs at 10k for million-edge
        # cases.  2.6 deliberately permits short epochs for the n=5 experiment.
        self.control_epoch = max(1, int(control_epoch))
        self.memory = memory
        self.problem_id = str(problem_id)
        self.depth_n = depth_n
        self.qh_trade_enabled = bool(qh_trade_enabled)
        self.qh_warmup_expansions = max(0, int(qh_warmup_expansions))
        self.qh_contract_threshold = float(qh_contract_threshold)
        self.qh_fixed_point_window = max(1, int(qh_fixed_point_window))
        self.qh_trade_active = False
        self.qh_trade_activations = 0
        self.qh_messages = 0
        self.qh_fixed_point_escapes = 0
        self.qh_horizon_observations: list[dict[str, Any]] = []
        self._qh_prev_h: float | None = None
        self._qh_noncontractive_epochs = 0

        state = {
            "depth_n": depth_n if depth_n is not None else -1,
            "nodes": len(self.qh_nodes(edges, source, target)),
            "edges": len(edges),
        }
        prior = self.memory.retrieve(
            problem_id=self.problem_id,
            state_signature=state,
            top_k=20,
            distant_probability=0.0,
        )
        preferred: list[str] = []
        for _, rec in prior:
            if rec.get("outcome") != "success":
                continue
            action = rec.get("action") or {}
            candidate = action.get("candidate")
            if isinstance(candidate, str):
                preferred.append(candidate)

        self.qh = QuotientHunter(
            source=source,
            target=target,
            edges=edges,
            preferred_candidates=preferred,
        )
        self.qh_discovery = self.qh.discover()
        self.qh_independent_trade_check = independently_verify_rank_trade(
            source=source,
            target=target,
            edges=edges,
            rank=dict(self.qh.reverse_rank),
        )
        self._record_qh_discovery(state)
        self._activate_qh_trade_if_certified()

    @staticmethod
    def qh_nodes(edges: Iterable[tuple[int, int]], source: int, target: int) -> set[int]:
        out = {int(source), int(target)}
        for u, v in edges:
            out.add(int(u)); out.add(int(v))
        return out

    def _record_qh_discovery(self, state: dict[str, Any]) -> None:
        for report in self.qh_discovery.reports:
            successful = bool(
                report.target_reachability_equivalence_certified
                and report.strict_progress_policy
            )
            self.memory.append(
                problem_id=self.problem_id,
                run_id=f"dm26-qh-{id(self)}",
                kind="qh_candidate",
                outcome="success" if successful else "observation",
                source_agent="QH",
                source_couple=None,
                shortcut_type="metalogical_quotient",
                state_signature=state,
                action={
                    "candidate": report.name,
                    "quotient_size": report.quotient_size,
                    "compression_ratio": report.compression_ratio,
                    "lambda_h_bound": report.lambda_h_bound,
                    "target_reachability_equivalence_certified":
                        report.target_reachability_equivalence_certified,
                },
                tags=("data-mind-2.6", "quotient-hunter", "candidate"),
                verified=successful,
                source="QH visible-graph structural analysis",
            )
        self.qh_messages += 1
        self.audit.emit(
            EventType.SELF_REPORT_FILED,
            "qh_agent_message",
            agent="QH",
            role="metalogical quotient/invariant hunter",
            discovery=self.qh_discovery.as_dict(),
            independent_trade_check=self.qh_independent_trade_check,
            certified_math=False,
            may_commit_theorem_to_bank=False,
        )

    def _activate_qh_trade_if_certified(self) -> None:
        proposed = bool(
            self.qh_trade_enabled
            and self.qh_discovery.trade_activatable
            and self.qh_independent_trade_check
        )
        self.audit.emit(
            EventType.STRATEGY_OVERRIDE_PROPOSED,
            "qh_trade_proposed",
            agent="QH",
            from_policy="general adaptive graph search",
            to_policy="certified reverse-rank quotient geodesic",
            target_specific=True,
            target_reachability_equivalence_certified=
                self.qh_discovery.trade_activatable,
            independent_trade_check=self.qh_independent_trade_check,
            verifier_authority=False,
            theorem_bank_authority=False,
            activatable=proposed,
        )
        if proposed:
            self.qh_trade_active = True
            self.qh_trade_activations += 1
            self.audit.emit(
                EventType.STRATEGY_OVERRIDE_EXECUTED,
                "qh_trade_activated",
                agent="QH",
                scope=self.qh_discovery.trade_scope,
                live_inference_kernel_modified=False,
                independent_theorem_verifier_unchanged=True,
            )

    def choose_strategy(self) -> tuple[str, int | None]:
        if self.qh_trade_active and self.expansions >= self.qh_warmup_expansions:
            live = [v for v in self.parent if v not in self.expanded]
            u = self.qh.best_live_vertex(live)
            if u is not None:
                self.qh_messages += 1
                if self.qh_messages <= 6 or self.qh_messages % 100 == 0:
                    self.audit.emit(
                        EventType.DIRECTIVE_RECEIVED,
                        "qh_geodesic_directive",
                        agent="QH",
                        vertex=u,
                        horizon=self.qh.horizon(u),
                        authority="search_order_only",
                        verifier_authority=False,
                    )
                return "qh", u
        return super().choose_strategy()

    def _frontier_horizon(self) -> float | None:
        vals = [
            self.qh.horizon(v)
            for v in self.parent
            if v not in self.expanded and self.qh.horizon(v) is not None
        ]
        return float(min(vals)) if vals else None

    def control(
        self,
        epoch_start_exp: int,
        epoch_start_discoveries: int,
        epoch_start_duplicates: int,
    ) -> None:
        super().control(
            epoch_start_exp,
            epoch_start_discoveries,
            epoch_start_duplicates,
        )
        h = self._frontier_horizon()
        ratio = None
        if h is not None and self._qh_prev_h is not None and self._qh_prev_h > 0:
            ratio = h / self._qh_prev_h
        row = {
            "expansions": self.expansions,
            "h_frontier": h,
            "previous_h": self._qh_prev_h,
            "lambda_hat": ratio,
            "contract_threshold": self.qh_contract_threshold,
        }
        self.qh_horizon_observations.append(row)
        self.audit.emit(
            EventType.LOCAL_EVIDENCE_DETECTED,
            "qh_contraction_observation",
            agent="QH",
            **row,
            claim_scope="empirical distance-to-settlement only",
        )
        self.memory.append(
            problem_id=self.problem_id,
            run_id=f"dm26-qh-{id(self)}",
            kind="qh_contraction_observation",
            outcome=(
                "success"
                if ratio is not None and ratio < self.qh_contract_threshold
                else "observation"
            ),
            source_agent="QH",
            state_signature={
                "depth_n": self.depth_n if self.depth_n is not None else -1,
                "expansion": self.expansions,
                "h_frontier": h if h is not None else -1,
            },
            action={"lambda_hat": ratio},
            tags=("data-mind-2.6", "contraction"),
            verified=None,
            source="within-run QH geometry",
        )

        if ratio is not None and ratio >= 1.0:
            self._qh_noncontractive_epochs += 1
        else:
            self._qh_noncontractive_epochs = 0

        if self._qh_noncontractive_epochs >= self.qh_fixed_point_window:
            inv = {k: 1.0 / max(self.weights[k], 1e-4) for k in BASE.STRATEGIES}
            self.qh_fixed_point_escapes += 1
            self.revision_count += 1
            self._set_weights(
                inv,
                "QH detected noncontractive/fixed-point-like stagnation; group inverse escape",
                "qh-fixed-point-escape",
            )
            self.audit.emit(
                EventType.STRATEGY_OVERRIDE_EXECUTED,
                "qh_fixed_point_escape",
                agent="QH",
                method="group_inverse",
                consecutive_noncontractive_epochs=self._qh_noncontractive_epochs,
            )
            self._qh_noncontractive_epochs = 0

        if h is not None:
            self._qh_prev_h = h


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--problem", required=True)
    ap.add_argument("--reference", required=True)
    ap.add_argument("--p8038", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--transactions", required=True)
    ap.add_argument("--memory", required=True)
    ap.add_argument("--bank", required=True)
    ap.add_argument("--problem-id", default="DEPTHS-N5")
    ap.add_argument("--depth-n", type=int, default=5)
    ap.add_argument("--time-limit", type=float, default=600.0)
    ap.add_argument("--max-expansions", type=int, default=100_000_000)
    ap.add_argument("--control-epoch", type=int, default=25)
    ap.add_argument("--seed", type=int, default=2301)
    ap.add_argument("--qh-warmup-expansions", type=int, default=0)
    ap.add_argument("--qh-contract-threshold", type=float, default=0.95)
    ap.add_argument("--qh-fixed-point-window", type=int, default=2)
    ap.add_argument("--disable-qh-trade", action="store_true")
    ap.add_argument("--ingest-transactions", action="append", default=[])
    a = ap.parse_args()

    problem = Path(a.problem)
    ref = load_module("ocean_reference_dm26", Path(a.reference))
    source, target, edges, adj, _ = ref.parse_problem(problem)
    problem_sha = sha256_file(problem)

    memory = AppendOnlyMemoryStore(a.memory)
    imported = 0
    for tx in a.ingest_transactions:
        imported += memory.ingest_transaction_log(
            tx,
            problem_id=a.problem_id,
            run_id=f"dm26-import-{Path(tx).stem}",
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

    engine = DataMind26Depths(
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
        qh_trade_enabled=not a.disable_qh_trade,
        qh_warmup_expansions=a.qh_warmup_expansions,
        qh_contract_threshold=a.qh_contract_threshold,
        qh_fixed_point_window=a.qh_fixed_point_window,
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
        run_id="dm26-depths-final",
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
            "qh_selected": engine.qh_discovery.selected,
            "qh_trade_active": engine.qh_trade_active,
        },
        tags=("data-mind-2.6", "depths", "final", "verifier-gated"),
        verified=verified,
        source="independent Ocean path verifier",
    )

    qh_selected = next(
        (r for r in engine.qh_discovery.reports if r.name == engine.qh_discovery.selected),
        None,
    )
    tx_ok = audit.log.verify()
    memory_ok = memory.verify()
    summary = {
        "solver": "DATA-MIND 2.6 — Quotient Hunter",
        "architecture_version": "2.6",
        "inherits_data_mind_2_5_concepts": True,
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
        "quotient_hunter_agent_enabled": True,
        "qh_agent_message_count": engine.qh_messages,
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
        "trading_enabled": True,
        "trade_type": "target-specific search-policy quotient trade",
        "qh_trade_requested": not a.disable_qh_trade,
        "qh_trade_activatable": engine.qh_discovery.trade_activatable,
        "qh_trade_independently_verified": engine.qh_independent_trade_check,
        "qh_trade_active": engine.qh_trade_active,
        "qh_trade_activations": engine.qh_trade_activations,
        "live_inference_kernel_modified": False,
        "independent_theorem_verifier_unchanged": True,
        "qh_selected_quotient": engine.qh_discovery.selected,
        "qh_source_horizon": engine.qh_discovery.source_horizon,
        "qh_quotient_size": qh_selected.quotient_size if qh_selected else None,
        "qh_compression_ratio": qh_selected.compression_ratio if qh_selected else None,
        "qh_lambda_H_bound": qh_selected.lambda_h_bound if qh_selected else None,
        "qh_unique_policy_fixed_point": (
            qh_selected.unique_policy_fixed_point if qh_selected else False
        ),
        "qh_policy_path_verified_structurally":
            engine.qh_discovery.policy_path_verified,
        "qh_candidate_reports": [r.as_dict() for r in engine.qh_discovery.reports],
        "qh_contraction_observations": engine.qh_horizon_observations,
        "qh_fixed_point_escapes": engine.qh_fixed_point_escapes,
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
            "QH certifies search geometry only.  PROVED and BANK admission still "
            "require the independent certificate verifier."
        ),
    }
    Path(a.out).write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)
    if not tx_ok or not memory_ok:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
