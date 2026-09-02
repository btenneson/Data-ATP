#!/usr/bin/env python3
"""DATA-MIND 2.10 held-out TPTP settlement prototype.

This runner consumes the already-frozen DATA-MIND 2.7 171/9 education policy.
It does not retrain, inspect another held-out problem, or expose GRP619 variants.
DATA-MIND 2.10 adds a fail-closed solver supervisor, certificate gate, and a
federated verified BANK deposit around the unchanged learned ranking policy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

from data_atp.federated_bank import FederatedBank, PropagationMode

import data_mind_2_7_tptp95_proof_density as dm27

ARCH = "2.10"
TARGET = "GRP619+1.p"
ABSTRACT = "GRP619"
STRATEGIES = {
    # Ubuntu's E 2.6 --auto path aborts in sat_solver_init on this problem.
    # These candidates deliberately avoid that broken SAT-backed schedule.
    "default": [],
    "sine_auto": ["--sine=Auto"],
}
SUCCESS = {"Theorem", "Unsatisfiable"}
SZS_RE = re.compile(r"(?mi)^#?\s*%?\s*SZS status\s+([A-Za-z]+)")
PROOF_RE = re.compile(r"(?mi)(SZS output start|CNFRefutation|fof\([^,]+,\s*plain)")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def validate_frozen_inputs(policy_path: Path, manifest_path: Path) -> tuple[dict, dict]:
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    checks = {
        "target": policy.get("target") == TARGET == manifest.get("target"),
        "seed": policy.get("seed") == manifest.get("seed") == 314159,
        "training_count": manifest.get("training_count") == 171,
        "holdout_count": manifest.get("holdout_count") == 9,
        "target_held_out": TARGET in manifest.get("holdout_files", []),
        "target_not_trained": TARGET not in manifest.get("training_files", []),
        "abstract_family_not_trained": not any(
            str(name).startswith(ABSTRACT) for name in manifest.get("training_files", [])
        ),
        "recorded_leakage_flags": (
            manifest.get("target_in_training") is False
            and manifest.get("same_abstract_problem_variants_in_training") is False
            and policy.get("learner_target_exposed_during_education") is False
            and policy.get("same_abstract_problem_proxy_exposed_during_education") is False
        ),
    }
    if not all(checks.values()):
        raise RuntimeError(f"frozen-input validation failed: {checks}")
    return policy, {"checks": checks, "policy_sha256": sha256(policy_path), "manifest_sha256": sha256(manifest_path)}


def run_e(problem: Path, root: Path, strategy: str, seconds: int) -> dict:
    cmd = [
        "eprover", *STRATEGIES[strategy], "--tptp3-format", "--proof-object",
        f"--cpu-limit={max(1, int(seconds))}", str(problem),
    ]
    env = os.environ.copy()
    env["TPTP"] = str(root.resolve())
    started = time.perf_counter()
    try:
        cp = subprocess.run(
            cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            env=env, timeout=max(5.0, seconds + 10.0), check=False,
        )
        output, returncode, timed_out = cp.stdout, cp.returncode, False
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        returncode, timed_out = 124, True
    elapsed = time.perf_counter() - started
    match = SZS_RE.search(output)
    status = match.group(1) if match else None
    has_proof = bool(PROOF_RE.search(output))
    verifier_accepted = status in SUCCESS and has_proof and returncode in (0, 1)
    abnormal = returncode < 0 or "Assertion" in output or "Segmentation fault" in output
    return {
        "strategy": strategy,
        "command": cmd,
        "elapsed_seconds": elapsed,
        "allocated_seconds": seconds,
        "returncode": returncode,
        "timed_out": timed_out,
        "szs_status": status,
        "proof_marker_present": has_proof,
        "verifier_accepted": verifier_accepted,
        "sentinel_decision": "quarantine" if abnormal else "allow_internal",
        "abnormal_termination": abnormal,
        "output": output,
    }


def prepare_problem(root: Path, policy: dict, out: Path) -> tuple[Path, list[dict]]:
    original = root / "Problems" / "GRP" / TARGET
    if not original.is_file():
        raise RuntimeError(f"held-out target missing: {original}")
    text = original.read_text(encoding="utf-8", errors="replace")
    problem = out / f"{TARGET}.dm210-reordered.p"
    problem.write_text(dm27.base.reorder_target(text, policy), encoding="utf-8")
    table = dm27.objective_table(text, policy)
    return problem, table


def smoke(args: argparse.Namespace) -> int:
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    policy, audit = validate_frozen_inputs(Path(args.policy), Path(args.manifest))
    problem, table = prepare_problem(Path(args.tptp_root), policy, out)
    runs = []
    for strategy in STRATEGIES:
        result = run_e(problem, Path(args.tptp_root), strategy, args.seconds)
        output = result.pop("output")
        (out / f"smoke_{strategy}.log").write_text(output, encoding="utf-8")
        runs.append(result)
    viable = [r["strategy"] for r in runs if not r["abnormal_termination"]]
    result = {
        "status": "SMOKE_PASS" if viable else "SMOKE_FAIL",
        "architecture_version": ARCH,
        "target": TARGET,
        "frozen_input_audit": audit,
        "objective_table": table,
        "viable_strategies": viable,
        "runs": runs,
    }
    (out / "smoke_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True), flush=True)
    return 0 if viable else 2


def examine(args: argparse.Namespace) -> int:
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    policy, audit = validate_frozen_inputs(Path(args.policy), Path(args.manifest))
    problem, table = prepare_problem(Path(args.tptp_root), policy, out)
    smoke_result = json.loads(Path(args.smoke_result).read_text(encoding="utf-8"))
    viable = [name for name in smoke_result.get("viable_strategies", []) if name in STRATEGIES]
    if not viable:
        raise RuntimeError("no Sentinel-approved strategy survived smoke test")

    # The frozen learner ties auto and auto_schedule on this target.  We retain
    # its reordered target and split budget equally over the safe E adapters.
    started = time.perf_counter()
    runs = []
    accepted = None
    for index, strategy in enumerate(viable):
        remaining = args.total_seconds - int(time.perf_counter() - started)
        if remaining <= 0:
            break
        slots = len(viable) - index
        seconds = remaining if slots == 1 else max(1, remaining // slots)
        result = run_e(problem, Path(args.tptp_root), strategy, seconds)
        output = result.pop("output")
        log = out / f"e_{strategy}.log"
        log.write_text(output, encoding="utf-8")
        result["log"] = log.name
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
            "proof_sha256": sha256(out / accepted["log"]),
        }
        bank_items = bank.propose(
            agent="P", kind="certificate", payload=payload,
            verify=lambda kind, value: kind == "certificate" and bool(accepted["verifier_accepted"]),
            metadata={"target_seen_in_training": False, "architecture_version": ARCH},
            propagation=PropagationMode.CORE,
        )

    result = {
        "status": "SETTLED" if bank_items else "UNSETTLED_WITHIN_BUDGET",
        "architecture_version": ARCH,
        "prototype": True,
        "target": TARGET,
        "target_seen_during_education": False,
        "same_abstract_problem_variants_seen_during_education": False,
        "training_count": 171,
        "holdout_count": 9,
        "total_budget_seconds": args.total_seconds,
        "elapsed_seconds": time.perf_counter() - started,
        "frozen_input_audit": audit,
        "objective_table": table,
        "sentinel_smoke_status": smoke_result.get("status"),
        "runs": runs,
        "verifier_gate_passed": bool(bank_items),
        "federated_bank_core_deposits": [item.item_id for item in bank_items],
        "certificate": bank_items[0].payload if bank_items else None,
    }
    (out / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True), flush=True)
    # Unsettled is an experimental outcome, not an infrastructure failure.
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="mode", required=True)
    for name in ("smoke", "examine"):
        p = sub.add_parser(name)
        p.add_argument("--tptp-root", required=True)
        p.add_argument("--policy", required=True)
        p.add_argument("--manifest", required=True)
        p.add_argument("--out", required=True)
        if name == "smoke":
            p.add_argument("--seconds", type=int, default=30)
            p.set_defaults(func=smoke)
        else:
            p.add_argument("--smoke-result", required=True)
            p.add_argument("--total-seconds", type=int, default=21600)
            p.set_defaults(func=examine)
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
