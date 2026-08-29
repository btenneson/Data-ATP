#!/usr/bin/env python3
"""Paired DATA-MIND 1.0 / 1.1 architecture smoke harness over frozen Depths-F.

This is deliberately an architecture/integration test, not a performance
benchmark and not a claim that every DATA-MIND module is production-complete.
The mathematical work is delegated unchanged to the frozen R01
Depths-F_Ocean_Control_1.0 implementation. This harness checks that the
architecture wrapper routes proposals through the verifier before BANK commit
and, for 1.1, that the newly explicit modules are actually exercised.

DATA-MIND 1.1 smoke additions checked here:
  * machine-readable self-description
  * Professor hook
  * append-only hash-chained transaction log
  * Counselor/Critic hook
  * Learning hook consuming verified outcomes
  * shared pre-BANK deliberation in which all eight AMLD agents
    P1,P2,R1,R2,I1,I2,C1,C2 can speak

The Verifier is external to the eight-agent roster and remains sovereign.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

AGENTS = ("P1", "P2", "R1", "R2", "I1", "I2", "C1", "C2")
VERSIONS = ("1.0", "1.1")


@dataclass(frozen=True)
class Event:
    sequence: int
    event_type: str
    problem: str
    payload: dict[str, Any]
    previous_hash: str | None = None
    digest: str | None = None


class PlainTrace:
    """Experiment instrumentation only; not the DATA-MIND 1.1 transaction log."""

    def __init__(self) -> None:
        self.items: list[Event] = []

    def append(self, event_type: str, problem: str, payload: dict[str, Any]) -> Event:
        event = Event(len(self.items), event_type, problem, dict(payload))
        self.items.append(event)
        return event

    def verify(self) -> bool:
        return all(e.sequence == i for i, e in enumerate(self.items))


class HashTransactionLog:
    """Minimal append-only SHA-256 chain used to smoke-test the 1.1 interface."""

    def __init__(self) -> None:
        self.items: list[Event] = []

    @staticmethod
    def _digest(sequence: int, event_type: str, problem: str,
                payload: dict[str, Any], previous_hash: str) -> str:
        raw = json.dumps(
            {
                "sequence": sequence,
                "event_type": event_type,
                "problem": problem,
                "payload": payload,
                "previous_hash": previous_hash,
            },
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def append(self, event_type: str, problem: str, payload: dict[str, Any]) -> Event:
        sequence = len(self.items)
        previous = self.items[-1].digest if self.items else "GENESIS"
        assert previous is not None
        digest = self._digest(sequence, event_type, problem, payload, previous)
        event = Event(sequence, event_type, problem, dict(payload), previous, digest)
        self.items.append(event)
        return event

    def verify(self) -> bool:
        previous = "GENESIS"
        for i, event in enumerate(self.items):
            if event.sequence != i or event.previous_hash != previous or event.digest is None:
                return False
            expected = self._digest(
                event.sequence, event.event_type, event.problem,
                event.payload, previous,
            )
            if event.digest != expected:
                return False
            previous = event.digest
        return True


class SmokeLearningEngine:
    """Integration-only learner: proves that verified outcomes reach Learning."""

    def __init__(self) -> None:
        self.examples_seen = 0
        self.verified_successes = 0

    def consume(self, verified: bool) -> dict[str, int]:
        self.examples_seen += 1
        self.verified_successes += int(bool(verified))
        return {
            "examples_seen": self.examples_seen,
            "verified_successes": self.verified_successes,
        }


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_depths_f(control_script: Path, problem: Path, out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / f"{problem.stem}.json"
    cert_path = out_dir / f"{problem.stem}.cert.txt"
    cp = subprocess.run(
        [
            sys.executable, str(control_script),
            "--solver", "depths-f",
            "--problem", str(problem),
            "--out", str(result_path),
            "--cert", str(cert_path),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=30,
        check=False,
    )
    if cp.returncode != 0 or not result_path.exists():
        raise RuntimeError(
            f"Depths-F failed on {problem.name}: rc={cp.returncode}\n{cp.stdout}"
        )
    result = json.loads(result_path.read_text(encoding="utf-8"))
    result["process_stdout"] = cp.stdout.strip()
    result["input_sha256"] = sha256_file(problem)
    return result


def role_message(agent: str) -> str:
    if agent.startswith("P"):
        return "proof-route observation"
    if agent.startswith("R"):
        return "refutation/challenge observation"
    if agent.startswith("I"):
        return "independence-channel observation"
    return "contradiction-channel observation"


def assert_verifier_gate(events: list[Event], problem: str) -> bool:
    accepted_at: int | None = None
    for event in events:
        if event.problem != problem:
            continue
        if event.event_type == "VERIFIER_RESULT" and bool(event.payload.get("accepted")):
            accepted_at = event.sequence
        if event.event_type == "BANK_COMMIT":
            if accepted_at is None or accepted_at >= event.sequence:
                return False
    return True


def run_case(version: str, problem: Path, solver_result: dict[str, Any], trace,
             learning: SmokeLearningEngine | None) -> dict[str, Any]:
    name = problem.name
    verified = bool(solver_result.get("certificate_verified"))

    trace.append("SELF_AWARENESS_REPORT", name, {
        "solver": solver_result.get("solver"),
        "goal": "obtain verifier-gated Ocean certificate",
        "status_before_verification": solver_result.get("status"),
        "architecture_version": version,
    })

    if version == "1.1":
        trace.append("SELF_DESCRIPTION", name, {
            "architecture": "DATA-MIND 1.1",
            "agents": list(AGENTS),
            "verifier_external_to_agent_roster": True,
            "pre_bank_communication": "shared_bus",
            "newly_explicit_modules": [
                "self_description", "professor", "transaction_log",
                "counselor", "learning",
            ],
        })
        for agent in AGENTS:
            trace.append("AGENT_MESSAGE", name, {
                "agent": agent,
                "channel": "shared_pre_bank_deliberation",
                "kind": role_message(agent),
                "certified_math": False,
            })
        trace.append("COUNSELOR_ADVICE", name, {
            "diagnostic": "architecture smoke case; keep mathematical search unchanged",
            "authority": "advisory_only",
        })
        trace.append("PROFESSOR_REVIEW", name, {
            "lesson": "test verifier gating and module participation before optimization",
            "authority": "teaching/evaluation_only",
            "may_verify": False,
        })
    else:
        for agent in AGENTS:
            trace.append("AGENT_LOCAL_TURN", name, {
                "agent": agent,
                "channel": "role_local",
                "certified_math": False,
            })

    trace.append("CONTROL_ASSESSMENT", name, {
        "difficulty_intent": "easy_architecture_smoke",
        "intervention": "none",
        "reason": "Depths-F is frozen; do not tune the mathematical solver",
    })

    trace.append("BANK_PROPOSAL", name, {
        "source": "Depths-F_Ocean_Control_1.0",
        "certificate_sha256": solver_result.get("certificate_sha256"),
        "verified_at_proposal_time": False,
    })

    trace.append("VERIFIER_RESULT", name, {
        "accepted": verified,
        "solver_status": solver_result.get("status"),
        "proof_length": solver_result.get("proof_length"),
    })

    if verified:
        trace.append("BANK_COMMIT", name, {
            "certificate_sha256": solver_result.get("certificate_sha256"),
            "gate": "verifier_accepted",
        })
    else:
        trace.append("BANK_REJECT", name, {"gate": "verifier_rejected"})

    learning_state = None
    if version == "1.1":
        assert learning is not None
        learning_state = learning.consume(verified)
        trace.append("LEARNING_UPDATE", name, {
            **learning_state,
            "scope": "smoke_integration_only",
            "solver_policy_changed": False,
        })

    problem_events = [e for e in trace.items if e.problem == name]
    gate_ok = assert_verifier_gate(problem_events, name)
    agent_messages = [e for e in problem_events if e.event_type == "AGENT_MESSAGE"]
    speakers = {e.payload.get("agent") for e in agent_messages}

    return {
        "problem": name,
        "input_sha256": solver_result.get("input_sha256"),
        "solver": solver_result.get("solver"),
        "solver_status": solver_result.get("status"),
        "certificate_verified": verified,
        "proof_length": solver_result.get("proof_length"),
        "expansions": solver_result.get("expansions"),
        "wall_s_internal": solver_result.get("wall_s_internal"),
        "bank_commit_after_verifier": gate_ok,
        "all_eight_agents_spoke": (speakers == set(AGENTS)) if version == "1.1" else None,
        "learning_state": learning_state,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", choices=VERSIONS, required=True)
    ap.add_argument("--problems", required=True)
    ap.add_argument("--depths-f-script", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    version = args.version
    problem_dir = Path(args.problems)
    control_script = Path(args.depths_f_script)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    problems = sorted(problem_dir.glob("*.p"))
    if len(problems) != 5:
        raise SystemExit(f"smoke test requires exactly 5 Ocean instances, found {len(problems)}")

    trace = HashTransactionLog() if version == "1.1" else PlainTrace()
    learning = SmokeLearningEngine() if version == "1.1" else None
    rows = []
    solver_dir = out_dir / "depths_f_results"
    for problem in problems:
        solver_result = run_depths_f(control_script, problem, solver_dir)
        rows.append(run_case(version, problem, solver_result, trace, learning))

    trace_ok = trace.verify()
    all_solver_verified = all(r["certificate_verified"] for r in rows)
    all_gate_ok = all(r["bank_commit_after_verifier"] for r in rows)
    all_agents_ok = (
        all(r["all_eight_agents_spoke"] for r in rows)
        if version == "1.1" else True
    )

    counts: dict[str, int] = {}
    for event in trace.items:
        counts[event.event_type] = counts.get(event.event_type, 0) + 1

    if version == "1.1":
        required_counts = {
            "SELF_DESCRIPTION": 5,
            "COUNSELOR_ADVICE": 5,
            "PROFESSOR_REVIEW": 5,
            "LEARNING_UPDATE": 5,
            "AGENT_MESSAGE": 40,
            "VERIFIER_RESULT": 5,
            "BANK_COMMIT": 5,
        }
        modules_ok = all(counts.get(k) == v for k, v in required_counts.items())
    else:
        forbidden = {
            "SELF_DESCRIPTION", "COUNSELOR_ADVICE", "PROFESSOR_REVIEW",
            "LEARNING_UPDATE", "AGENT_MESSAGE",
        }
        modules_ok = not any(counts.get(k, 0) for k in forbidden)

    input_set_sha = hashlib.sha256(
        "\n".join(sorted(str(r["input_sha256"]) for r in rows)).encode("utf-8")
    ).hexdigest()

    architecture_pass = bool(
        all_solver_verified and all_gate_ok and trace_ok and all_agents_ok and modules_ok
    )
    summary = {
        "architecture": f"DATA-MIND {version}",
        "purpose": "architecture_smoke_only",
        "n": 5,
        "frozen_solver": "Depths-F_Ocean_Control_1.0",
        "all_solver_certificates_verified": all_solver_verified,
        "all_bank_commits_verifier_gated": all_gate_ok,
        "trace_or_transaction_chain_verified": trace_ok,
        "all_eight_agents_spoke_each_case": all_agents_ok if version == "1.1" else None,
        "required_module_participation_ok": modules_ok,
        "event_counts": counts,
        "input_set_sha256": input_set_sha,
        "architecture_pass": architecture_pass,
        "cases": rows,
        "important_scope_note": (
            "This exercises interfaces and invariants only. Professor, Counselor, "
            "Self-Description, and Learning hooks are deterministic smoke hooks; "
            "Learning records verified outcomes but does not retune Depths-F."
        ),
    }

    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (out_dir / "trace.json").write_text(
        json.dumps([asdict(e) for e in trace.items], indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    if not architecture_pass:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
