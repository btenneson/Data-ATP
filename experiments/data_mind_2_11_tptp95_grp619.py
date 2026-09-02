#!/usr/bin/env python3
"""DATA-MIND 2.11 GRP619 prototype with checkpoint barriers and breadcrumbs.

2.11 preserves the frozen 2.10/2.7 learned policy and settlement logic.  The
change is operational: external prover calls are supervised by a state machine
that records PRE/heartbeat/POST breadcrumbs, periodically pauses the prover at
quiescent checkpoint barriers on POSIX, and distinguishes bounded unknown from
prover/adapter/infrastructure failure.

E itself does not expose a portable serialization of its live proof-search
state here.  Therefore recovery from a process/host loss is explicit and
truthful: restart_current_attempt from the last durable orchestration snapshot,
not pretend to resume E's internal clauses byte-for-byte.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time
from typing import Any

from data_atp.breadcrumbs import BreadcrumbManager
from data_atp.federated_bank import FederatedBank, PropagationMode

import data_mind_2_10_tptp95_grp619 as dm210

ARCH = "2.11"
TARGET = dm210.TARGET
ABSTRACT = dm210.ABSTRACT
STRATEGIES = dm210.STRATEGIES
SUCCESS = dm210.SUCCESS
SZS_RE = dm210.SZS_RE
PROOF_RE = dm210.PROOF_RE
RESOURCE_TEXT_RE = re.compile(
    r"(?i)(resource\s+limit|cpu\s+(?:time\s+)?limit|time\s+limit|out\s+of\s+memory|memory\s+limit)"
)
CRASH_TEXT_RE = re.compile(
    r"(?i)(segmentation fault|assertion[^\n]*failed|fatal signal|internal error)"
)
RESOURCE_SZS = {"ResourceOut", "Timeout"}


def _read_proc_memory(pid: int) -> dict[str, int | None]:
    """Best-effort Linux RSS/HWM sample for the external prover process."""
    result: dict[str, int | None] = {"rss_kib": None, "peak_rss_kib": None}
    path = Path(f"/proc/{pid}/status")
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("VmRSS:"):
                result["rss_kib"] = int(line.split()[1])
            elif line.startswith("VmHWM:"):
                result["peak_rss_kib"] = int(line.split()[1])
    except (OSError, ValueError, IndexError):
        pass
    return result


def _stop_group(proc: subprocess.Popen[Any]) -> bool:
    if os.name != "posix" or proc.poll() is not None:
        return False
    try:
        os.killpg(proc.pid, signal.SIGSTOP)
        return True
    except (OSError, ProcessLookupError):
        return False


def _continue_group(proc: subprocess.Popen[Any]) -> None:
    if os.name != "posix" or proc.poll() is not None:
        return
    try:
        os.killpg(proc.pid, signal.SIGCONT)
    except (OSError, ProcessLookupError):
        pass


def _terminate_group(proc: subprocess.Popen[Any]) -> None:
    if proc.poll() is not None:
        return
    try:
        if os.name == "posix":
            os.killpg(proc.pid, signal.SIGTERM)
        else:
            proc.terminate()
        proc.wait(timeout=5.0)
        return
    except (OSError, ProcessLookupError, subprocess.TimeoutExpired):
        pass
    try:
        if os.name == "posix":
            os.killpg(proc.pid, signal.SIGKILL)
        else:
            proc.kill()
    except (OSError, ProcessLookupError):
        pass
    try:
        proc.wait(timeout=5.0)
    except subprocess.TimeoutExpired:
        pass


def _snapshot(
    *,
    phase: str,
    attempt_index: int | None,
    next_attempt_index: int,
    runs: list[dict[str, Any]],
    spent_seconds: float,
    total_budget_seconds: int,
    candidate_keys: list[str],
    active_attempt: dict[str, Any] | None = None,
    recovery_action: str = "continue_from_next_attempt",
) -> dict[str, Any]:
    return {
        "architecture_version": ARCH,
        "target": TARGET,
        "phase": phase,
        "attempt_index": attempt_index,
        "next_attempt_index": next_attempt_index,
        "recovery_action": recovery_action,
        "spent_seconds": spent_seconds,
        "total_budget_seconds": total_budget_seconds,
        "candidate_keys": candidate_keys,
        "completed_runs": runs,
        "active_attempt": active_attempt,
    }


def _classify(
    *,
    output: str,
    returncode: int | None,
    wall_timed_out: bool,
    adapter_error: str | None,
    status: str | None,
    verifier_accepted: bool,
) -> str:
    if adapter_error is not None:
        return "ADAPTER_ERROR"
    if wall_timed_out:
        return "WALL_TIMEOUT"
    if verifier_accepted:
        return "SETTLED"
    if returncode is not None and returncode < 0:
        return "SIGNAL_TERMINATION"
    if CRASH_TEXT_RE.search(output):
        return "PROVER_CRASH"
    if status in RESOURCE_SZS or RESOURCE_TEXT_RE.search(output):
        return "RESOURCE_LIMIT"
    if returncode not in (None, 0, 1):
        return "PROVER_NONZERO_EXIT"
    return "PROVER_UNKNOWN"


def run_e_monitored(
    problem: Path,
    root: Path,
    strategy: str,
    seconds: int,
    *,
    log_path: Path,
    breadcrumbs: BreadcrumbManager,
    attempt_index: int,
    runs: list[dict[str, Any]],
    spent_before_attempt: float,
    total_budget_seconds: int,
    candidate_keys: list[str],
    heartbeat_seconds: float,
    checkpoint_seconds: float,
) -> dict[str, Any]:
    cmd = [
        "eprover", *STRATEGIES[strategy], "--tptp3-format", "--proof-object",
        f"--cpu-limit={max(1, int(seconds))}", str(problem),
    ]
    env = os.environ.copy()
    env["TPTP"] = str(root.resolve())
    started = time.perf_counter()
    active_base = {
        "strategy": strategy,
        "problem": str(problem),
        "command": cmd,
        "allocated_cpu_seconds": seconds,
        "log": log_path.name,
    }
    pre = _snapshot(
        phase="pre_external_prover",
        attempt_index=attempt_index,
        next_attempt_index=attempt_index,
        runs=runs,
        spent_seconds=spent_before_attempt,
        total_budget_seconds=total_budget_seconds,
        candidate_keys=candidate_keys,
        active_attempt=active_base,
        recovery_action="restart_current_attempt",
    )
    breadcrumbs.record(
        "PRE_EXTERNAL_PROVER",
        pre,
        metadata={"strategy": strategy, "problem": str(problem)},
        checkpoint=True,
    )

    log_path.parent.mkdir(parents=True, exist_ok=True)
    adapter_error: str | None = None
    wall_timed_out = False
    returncode: int | None = None
    pid: int | None = None
    next_heartbeat = max(1.0, heartbeat_seconds)
    next_checkpoint = max(next_heartbeat, checkpoint_seconds)
    wall_deadline = max(5.0, float(seconds) + 10.0)

    try:
        with log_path.open("w", encoding="utf-8", errors="replace") as handle:
            proc = subprocess.Popen(
                cmd,
                text=True,
                stdout=handle,
                stderr=subprocess.STDOUT,
                env=env,
                start_new_session=(os.name == "posix"),
            )
            pid = proc.pid
            launch_snapshot = _snapshot(
                phase="external_prover_running",
                attempt_index=attempt_index,
                next_attempt_index=attempt_index,
                runs=runs,
                spent_seconds=spent_before_attempt,
                total_budget_seconds=total_budget_seconds,
                candidate_keys=candidate_keys,
                active_attempt={**active_base, "pid": pid, "elapsed_seconds": 0.0},
                recovery_action="restart_current_attempt",
            )
            breadcrumbs.record(
                "POST_PROVER_LAUNCH",
                launch_snapshot,
                metadata={"pid": pid},
                checkpoint=False,
            )

            while proc.poll() is None:
                elapsed = time.perf_counter() - started
                if elapsed >= wall_deadline:
                    wall_timed_out = True
                    _terminate_group(proc)
                    break

                if elapsed >= next_heartbeat:
                    memory = _read_proc_memory(pid)
                    active = {
                        **active_base,
                        "pid": pid,
                        "elapsed_seconds": elapsed,
                        "log_bytes": log_path.stat().st_size if log_path.exists() else 0,
                        **memory,
                    }
                    snap = _snapshot(
                        phase="external_prover_running",
                        attempt_index=attempt_index,
                        next_attempt_index=attempt_index,
                        runs=runs,
                        spent_seconds=spent_before_attempt + elapsed,
                        total_budget_seconds=total_budget_seconds,
                        candidate_keys=candidate_keys,
                        active_attempt=active,
                        recovery_action="restart_current_attempt",
                    )
                    durable = elapsed >= next_checkpoint
                    paused = False
                    if durable:
                        paused = _stop_group(proc)
                    try:
                        breadcrumbs.record(
                            "CHECKPOINT_BARRIER" if durable else "PROVER_HEARTBEAT",
                            snap,
                            metadata={
                                "pid": pid,
                                "process_paused": paused,
                                "rss_kib": memory["rss_kib"],
                                "peak_rss_kib": memory["peak_rss_kib"],
                            },
                            checkpoint=durable,
                        )
                    finally:
                        if paused:
                            _continue_group(proc)
                    next_heartbeat += max(1.0, heartbeat_seconds)
                    if durable:
                        while next_checkpoint <= elapsed:
                            next_checkpoint += max(1.0, checkpoint_seconds)
                time.sleep(0.2)

            returncode = proc.poll()
            if returncode is None:
                returncode = proc.wait(timeout=2.0)
    except (OSError, subprocess.SubprocessError) as exc:
        adapter_error = f"{type(exc).__name__}: {exc}"

    elapsed = time.perf_counter() - started
    try:
        output = log_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        output = ""
        if adapter_error is None:
            adapter_error = f"log read failed: {exc}"
    match = SZS_RE.search(output)
    status = match.group(1) if match else None
    has_proof = bool(PROOF_RE.search(output))
    verifier_accepted = (
        status in SUCCESS and has_proof and returncode in (0, 1) and not wall_timed_out
    )
    outcome_class = _classify(
        output=output,
        returncode=returncode,
        wall_timed_out=wall_timed_out,
        adapter_error=adapter_error,
        status=status,
        verifier_accepted=verifier_accepted,
    )
    quarantined = outcome_class in {
        "ADAPTER_ERROR", "SIGNAL_TERMINATION", "PROVER_CRASH", "PROVER_NONZERO_EXIT"
    }
    result: dict[str, Any] = {
        "strategy": strategy,
        "command": cmd,
        "elapsed_seconds": elapsed,
        "allocated_seconds": seconds,
        "returncode": returncode,
        "wall_timed_out": wall_timed_out,
        "szs_status": status,
        "proof_marker_present": has_proof,
        "verifier_accepted": verifier_accepted,
        "outcome_class": outcome_class,
        "adapter_error": adapter_error,
        "sentinel_decision": "quarantine" if quarantined else "allow_internal",
        "abnormal_termination": quarantined,
        "log": log_path.name,
        "pid": pid,
    }
    post_runs = [*runs, result]
    post = _snapshot(
        phase="post_external_prover",
        attempt_index=attempt_index,
        next_attempt_index=attempt_index + 1,
        runs=post_runs,
        spent_seconds=spent_before_attempt + elapsed,
        total_budget_seconds=total_budget_seconds,
        candidate_keys=candidate_keys,
        active_attempt=None,
        recovery_action="continue_from_next_attempt",
    )
    breadcrumbs.record(
        "POST_EXTERNAL_PROVER",
        post,
        metadata={
            "outcome_class": outcome_class,
            "returncode": returncode,
            "wall_timed_out": wall_timed_out,
            "szs_status": status,
        },
        checkpoint=True,
    )
    return result


def _ordered_viable(smoke_result: dict[str, Any], problems: dict[str, Path]) -> list[dict[str, str]]:
    viable = [
        item for item in smoke_result.get("viable_strategies", [])
        if item.get("strategy") in STRATEGIES and item.get("problem_form") in problems
    ]
    viable.sort(key=lambda item: (item["problem_form"] != "reordered", item["strategy"]))
    return viable


def _overall_status(runs: list[dict[str, Any]], settled: bool) -> str:
    if settled:
        return "SETTLED"
    classes = {str(r.get("outcome_class")) for r in runs}
    if classes & {"RESOURCE_LIMIT", "WALL_TIMEOUT", "PROVER_UNKNOWN"}:
        return "BOUNDED_UNKNOWN"
    if classes & {"PROVER_NONZERO_EXIT", "PROVER_CRASH", "SIGNAL_TERMINATION"}:
        return "PROVER_FAILURE"
    return "INFRASTRUCTURE_FAILURE"


def smoke(args: argparse.Namespace) -> int:
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    policy, audit = dm210.validate_frozen_inputs(Path(args.policy), Path(args.manifest))
    problems, table = dm210.prepare_problem(Path(args.tptp_root), policy, out)
    run_id = args.run_id or f"dm211-smoke-{int(time.time())}"
    crumbs = BreadcrumbManager(out / "breadcrumbs", run_id)
    runs: list[dict[str, Any]] = []
    candidate_keys = [f"{pf}:{st}" for pf in problems for st in STRATEGIES]

    for index, key in enumerate(candidate_keys):
        problem_form, strategy = key.split(":", 1)
        log = out / f"smoke_{problem_form}_{strategy}.log"
        result = run_e_monitored(
            problems[problem_form], Path(args.tptp_root), strategy, args.seconds,
            log_path=log,
            breadcrumbs=crumbs,
            attempt_index=index,
            runs=runs,
            spent_before_attempt=sum(float(r["elapsed_seconds"]) for r in runs),
            total_budget_seconds=args.seconds * len(candidate_keys),
            candidate_keys=candidate_keys,
            heartbeat_seconds=args.heartbeat_seconds,
            checkpoint_seconds=args.checkpoint_seconds,
        )
        result["problem_form"] = problem_form
        runs.append(result)

    viable = [
        {"problem_form": r["problem_form"], "strategy": r["strategy"]}
        for r in runs
        if r["outcome_class"] not in {
            "ADAPTER_ERROR", "SIGNAL_TERMINATION", "PROVER_CRASH", "PROVER_NONZERO_EXIT"
        }
    ]
    result = {
        "status": "SMOKE_PASS" if viable else "SMOKE_FAIL",
        "architecture_version": ARCH,
        "target": TARGET,
        "run_id": run_id,
        "frozen_input_audit": audit,
        "objective_table": table,
        "viable_strategies": viable,
        "breadcrumb_chain_verified": crumbs.verify(),
        "breadcrumb_chain_head": crumbs.chain_head,
        "runs": runs,
    }
    (out / "smoke_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True), flush=True)
    return 0 if viable else 2


def examine(args: argparse.Namespace) -> int:
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    policy, audit = dm210.validate_frozen_inputs(Path(args.policy), Path(args.manifest))
    problems, table = dm210.prepare_problem(Path(args.tptp_root), policy, out)
    smoke_result = json.loads(Path(args.smoke_result).read_text(encoding="utf-8"))
    viable = _ordered_viable(smoke_result, problems)
    if not viable:
        raise RuntimeError("no Sentinel-approved strategy survived smoke test")

    candidate_keys = [f"{x['problem_form']}:{x['strategy']}" for x in viable]
    run_id = args.run_id or f"dm211-grp619-{int(time.time())}"
    crumbs = BreadcrumbManager(out / "breadcrumbs", run_id)
    runs: list[dict[str, Any]] = []
    next_attempt_index = 0
    spent_before = 0.0

    if args.resume:
        restored = crumbs.restore_latest()["snapshot"]
        if restored.get("architecture_version") != ARCH or restored.get("target") != TARGET:
            raise RuntimeError("latest checkpoint does not belong to this 2.11 target")
        if restored.get("candidate_keys") != candidate_keys:
            raise RuntimeError("candidate strategy ordering changed since checkpoint")
        runs = list(restored.get("completed_runs", []))
        next_attempt_index = int(restored.get("next_attempt_index", 0))
        spent_before = float(restored.get("spent_seconds", 0.0))
        crumbs.record(
            "RUN_RESUMED",
            _snapshot(
                phase="resumed",
                attempt_index=None,
                next_attempt_index=next_attempt_index,
                runs=runs,
                spent_seconds=spent_before,
                total_budget_seconds=args.total_seconds,
                candidate_keys=candidate_keys,
                recovery_action="continue_from_next_attempt",
            ),
            metadata={"restored_phase": restored.get("phase")},
            checkpoint=True,
        )
    else:
        crumbs.record(
            "RUN_STARTED",
            _snapshot(
                phase="started",
                attempt_index=None,
                next_attempt_index=0,
                runs=[],
                spent_seconds=0.0,
                total_budget_seconds=args.total_seconds,
                candidate_keys=candidate_keys,
                recovery_action="continue_from_next_attempt",
            ),
            metadata={"target": TARGET},
            checkpoint=True,
        )

    session_started = time.perf_counter()
    accepted: dict[str, Any] | None = None
    for index in range(next_attempt_index, len(viable)):
        candidate = viable[index]
        current_spent = spent_before + (time.perf_counter() - session_started)
        remaining = args.total_seconds - int(current_spent)
        if remaining <= 0:
            break
        slots = len(viable) - index
        seconds = remaining if slots == 1 else max(1, remaining // slots)
        problem_form = candidate["problem_form"]
        strategy = candidate["strategy"]
        result = run_e_monitored(
            problems[problem_form], Path(args.tptp_root), strategy, seconds,
            log_path=out / f"e_{problem_form}_{strategy}.log",
            breadcrumbs=crumbs,
            attempt_index=index,
            runs=runs,
            spent_before_attempt=current_spent,
            total_budget_seconds=args.total_seconds,
            candidate_keys=candidate_keys,
            heartbeat_seconds=args.heartbeat_seconds,
            checkpoint_seconds=args.checkpoint_seconds,
        )
        result["problem_form"] = problem_form
        runs.append(result)
        if result["verifier_accepted"]:
            accepted = result
            break

    bank = FederatedBank(departments=("P", "QH", "COMPASS", "LEARNER", "VERIFIER"))
    bank_items = ()
    if accepted:
        payload = {
            "target": TARGET,
            "szs_status": accepted["szs_status"],
            "proof_log": accepted["log"],
            "proof_sha256": dm210.sha256(out / accepted["log"]),
        }
        bank_items = bank.propose(
            agent="P", kind="certificate", payload=payload,
            verify=lambda kind, value: kind == "certificate" and bool(accepted["verifier_accepted"]),
            metadata={"target_seen_in_training": False, "architecture_version": ARCH},
            propagation=PropagationMode.CORE,
        )

    elapsed_total = spent_before + (time.perf_counter() - session_started)
    status = _overall_status(runs, bool(bank_items))
    final_snapshot = _snapshot(
        phase="finished",
        attempt_index=None,
        next_attempt_index=len(runs),
        runs=runs,
        spent_seconds=elapsed_total,
        total_budget_seconds=args.total_seconds,
        candidate_keys=candidate_keys,
        recovery_action="none",
    )
    crumbs.record(
        "RUN_FINISHED",
        final_snapshot,
        metadata={"status": status, "verifier_gate_passed": bool(bank_items)},
        checkpoint=True,
    )

    result = {
        "status": status,
        "architecture_version": ARCH,
        "prototype": True,
        "run_id": run_id,
        "target": TARGET,
        "target_seen_during_education": False,
        "same_abstract_problem_variants_seen_during_education": False,
        "training_count": 171,
        "holdout_count": 9,
        "total_budget_seconds": args.total_seconds,
        "elapsed_seconds": elapsed_total,
        "frozen_input_audit": audit,
        "objective_table": table,
        "sentinel_smoke_status": smoke_result.get("status"),
        "runs": runs,
        "verifier_gate_passed": bool(bank_items),
        "federated_bank_core_deposits": [item.item_id for item in bank_items],
        "certificate": bank_items[0].payload if bank_items else None,
        "breadcrumb_chain_verified": crumbs.verify(),
        "breadcrumb_chain_head": crumbs.chain_head,
        "recovery_semantics": "restart_current_attempt_if_latest_checkpoint_was_inside_external_E",
    }
    (out / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True), flush=True)
    # Mathematical non-settlement and prover failure are recorded outcomes.
    # Return nonzero only for a corrupted breadcrumb chain.
    return 0 if result["breadcrumb_chain_verified"] else 3


def _common(p: argparse.ArgumentParser) -> None:
    p.add_argument("--tptp-root", required=True)
    p.add_argument("--policy", required=True)
    p.add_argument("--manifest", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--run-id")
    p.add_argument("--heartbeat-seconds", type=float, default=15.0)
    p.add_argument("--checkpoint-seconds", type=float, default=60.0)


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="mode", required=True)
    p = sub.add_parser("smoke")
    _common(p)
    p.add_argument("--seconds", type=int, default=15)
    p.set_defaults(func=smoke)

    p = sub.add_parser("examine")
    _common(p)
    p.add_argument("--smoke-result", required=True)
    p.add_argument("--total-seconds", type=int, default=300)
    p.add_argument("--resume", action="store_true")
    p.set_defaults(func=examine)

    args = parser.parse_args()
    if args.heartbeat_seconds <= 0 or args.checkpoint_seconds <= 0:
        parser.error("heartbeat/checkpoint intervals must be positive")
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
