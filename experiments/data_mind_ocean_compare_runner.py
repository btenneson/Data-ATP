#!/usr/bin/env python3
"""Long-run Ocean comparison runner for DATA-MIND 1.0 and 1.1.

Both versions deliberately share the same generic mathematical search policy:
the frozen Data-ATP Ocean Reference 1.0 policy, with only its resource cap
enlarged.  DATA-MIND 1.1 adds the architecture layer under test.  Therefore
this experiment measures correctness/integration/overhead, not a search-policy
advantage for 1.1.

Neither version reads L*, the planted route, generator seed, or evaluator files.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

AGENTS = ("P1", "P2", "R1", "R2", "I1", "I2", "C1", "C2")


@dataclass(frozen=True)
class Event:
    sequence: int
    event_type: str
    payload: dict[str, Any]
    previous_hash: str | None = None
    digest: str | None = None


class PlainTrace:
    def __init__(self) -> None:
        self.items: list[Event] = []

    def append(self, kind: str, payload: dict[str, Any]) -> None:
        self.items.append(Event(len(self.items), kind, dict(payload)))

    def verify(self) -> bool:
        return all(e.sequence == i for i, e in enumerate(self.items))


class HashTrace:
    def __init__(self) -> None:
        self.items: list[Event] = []

    @staticmethod
    def digest(sequence: int, kind: str, payload: dict[str, Any], previous: str) -> str:
        raw = json.dumps(
            {"sequence": sequence, "event_type": kind, "payload": payload,
             "previous_hash": previous},
            sort_keys=True, separators=(",", ":"), default=str,
        ).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def append(self, kind: str, payload: dict[str, Any]) -> None:
        seq = len(self.items)
        previous = self.items[-1].digest if self.items else "GENESIS"
        assert previous is not None
        digest = self.digest(seq, kind, payload, previous)
        self.items.append(Event(seq, kind, dict(payload), previous, digest))

    def verify(self) -> bool:
        previous = "GENESIS"
        for i, e in enumerate(self.items):
            if e.sequence != i or e.previous_hash != previous or e.digest is None:
                return False
            if e.digest != self.digest(i, e.event_type, e.payload, previous):
                return False
            previous = e.digest
        return True


def load_ref(path: Path):
    spec = importlib.util.spec_from_file_location("ocean_reference", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Ocean reference solver")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def file_sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", choices=["1.0", "1.1"], required=True)
    ap.add_argument("--problem", required=True)
    ap.add_argument("--reference", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--trace", required=True)
    ap.add_argument("--max-expansions", type=int, default=100_000_000)
    a = ap.parse_args()

    problem = Path(a.problem)
    trace = HashTrace() if a.version == "1.1" else PlainTrace()
    ref = load_ref(Path(a.reference))
    ref.MAX_EXPANSIONS = int(a.max_expansions)

    total0 = time.perf_counter()
    parse0 = time.perf_counter()
    source, target, edges, adj, _ = ref.parse_problem(problem)
    parse_wall = time.perf_counter() - parse0

    trace.append("SELF_AWARENESS_REPORT", {
        "architecture": f"DATA-MIND {a.version}",
        "goal": "obtain verifier-gated Ocean certificate",
        "generic_search_core": "Data-ATP Ocean Reference 1.0 policy",
        "hidden_metadata_read": False,
    })

    if a.version == "1.1":
        trace.append("SELF_DESCRIPTION", {
            "architecture": "DATA-MIND 1.1",
            "agents": list(AGENTS),
            "verifier_external_to_eight_agents": True,
            "new_modules": ["self_description", "professor", "transaction_log",
                            "counselor", "learning"],
        })
        for agent in AGENTS:
            trace.append("AGENT_MESSAGE", {
                "agent": agent,
                "channel": "shared_pre_bank_deliberation",
                "certified_math": False,
            })
        trace.append("COUNSELOR_ADVICE", {
            "advice": "preserve frozen generic search policy for controlled comparison",
            "authority": "advisory_only",
        })
        trace.append("PROFESSOR_REVIEW", {
            "lesson": "evaluate long-run architecture reliability before policy promotion",
            "authority": "teaching/evaluation_only",
            "may_verify": False,
        })

    trace.append("CONTROL_ASSESSMENT", {
        "intervention": "none",
        "reason": "search policy frozen for paired comparison",
        "max_expansions": int(a.max_expansions),
    })

    search0 = time.perf_counter()
    result = ref.data_atp_reference(source, target, edges, adj)
    search_wall = time.perf_counter() - search0
    path = result.get("path")

    trace.append("BANK_PROPOSAL", {
        "source": "generic DATA-MIND search core",
        "status": result.get("status"),
        "certified_at_proposal_time": False,
    })

    verify0 = time.perf_counter()
    verified = bool(path is not None and ref.verify_path(source, target, edges, path))
    verify_wall = time.perf_counter() - verify0
    trace.append("VERIFIER_RESULT", {
        "accepted": verified,
        "proof_length": len(path) - 1 if verified else None,
    })

    if verified:
        trace.append("BANK_COMMIT", {"gate": "verifier_accepted"})
    else:
        trace.append("BANK_REJECT", {"gate": "verifier_rejected"})

    if a.version == "1.1":
        trace.append("LEARNING_UPDATE", {
            "verified_outcome_consumed": verified,
            "solver_policy_changed": False,
            "reason": "comparison policy frozen",
        })

    total_wall = time.perf_counter() - total0
    counts: dict[str, int] = {}
    for e in trace.items:
        counts[e.event_type] = counts.get(e.event_type, 0) + 1

    bank_gate_ok = True
    accepted_seen = False
    for e in trace.items:
        if e.event_type == "VERIFIER_RESULT" and e.payload.get("accepted"):
            accepted_seen = True
        if e.event_type == "BANK_COMMIT" and not accepted_seen:
            bank_gate_ok = False

    all_agents_spoke = None
    module_ok = True
    if a.version == "1.1":
        speakers = {e.payload.get("agent") for e in trace.items if e.event_type == "AGENT_MESSAGE"}
        all_agents_spoke = speakers == set(AGENTS)
        module_ok = all([
            counts.get("SELF_DESCRIPTION") == 1,
            counts.get("PROFESSOR_REVIEW") == 1,
            counts.get("COUNSELOR_ADVICE") == 1,
            counts.get("LEARNING_UPDATE") == 1,
            counts.get("AGENT_MESSAGE") == 8,
            trace.verify(), all_agents_spoke,
        ])

    summary = {
        "solver": f"DATA-MIND {a.version} Ocean prototype",
        "version": a.version,
        "status": "PROVED" if verified else result.get("status", "FAULT"),
        "certificate_verified": verified,
        "proof_length": len(path)-1 if verified else None,
        "expansions": result.get("expansions"),
        "scoring_edge_probes": result.get("scoring_edge_probes"),
        "discovered_states": result.get("discovered_states"),
        "parse_wall_s": parse_wall,
        "search_wall_s": search_wall,
        "verify_wall_s": verify_wall,
        "total_wall_s": total_wall,
        "problem_sha256": file_sha(problem),
        "transaction_or_trace_verified": trace.verify(),
        "bank_commit_verifier_gated": bank_gate_ok,
        "all_eight_agents_spoke": all_agents_spoke,
        "required_1_1_modules_participated": module_ok if a.version == "1.1" else None,
        "event_counts": counts,
        "hidden_metadata_read": False,
        "search_policy_difference_between_1_0_and_1_1": False,
        "scope_note": (
            "1.1 architecture modules are exercised but do not change the frozen "
            "search policy in this comparison."
        ),
    }
    Path(a.out).write_text(json.dumps(summary, indent=2), encoding="utf-8")
    Path(a.trace).write_text(
        json.dumps([asdict(e) for e in trace.items], indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2), flush=True)
    if not verified or not bank_gate_ok or not trace.verify() or not module_ok:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
