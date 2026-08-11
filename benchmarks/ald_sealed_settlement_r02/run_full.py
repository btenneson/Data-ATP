from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
WALL_SECONDS = 30
MEMORY_MIB = 4096


def run_checked(cmd, *, cwd=HERE, stdout=None) -> None:
    subprocess.run(cmd, check=True, cwd=cwd, stdout=stdout)


def memory_limiter():
    """Return a Linux pre-exec hook enforcing the frozen per-process memory cap."""
    if os.name != "posix":
        return None
    try:
        import resource
    except ImportError:
        return None

    limit = MEMORY_MIB * 1024 * 1024

    def _limit() -> None:
        resource.setrlimit(resource.RLIMIT_AS, (limit, limit))

    return _limit


def write_unknown(path: Path, reason: str) -> None:
    path.write_text(
        json.dumps({"claim": "UNKNOWN", "reason": reason, "agent": "scheduler"}, indent=2) + "\n",
        encoding="utf-8",
    )


def adversarial_guards(root: Path, ground_truth: dict) -> dict:
    sample = root / "public" / "instances" / ground_truth["instances"][0]["id"]
    guard_dir = root / "guards"
    guard_dir.mkdir(parents=True, exist_ok=True)

    tests = []

    bad_proof = guard_dir / "bad_proof.json"
    bad_proof.write_text(json.dumps({
        "claim": "PROVED",
        "certificate": {"literals": ["p(n999999)"], "axioms": ["u0"]},
    }), encoding="utf-8")
    bad_proof_audit = guard_dir / "bad_proof_audit.json"
    run_checked([sys.executable, "verifier.py", "--problem", str(sample), "--claim", str(bad_proof), "--out", str(bad_proof_audit)], stdout=subprocess.DEVNULL)
    result = json.loads(bad_proof_audit.read_text(encoding="utf-8"))
    tests.append({"test": "forged proof rejected", "pass": result["status"] == "AUDIT_FAILURE", "audit": result})

    fake_i = guard_dir / "fake_independence.json"
    fake_i.write_text(json.dumps({"claim": "INDEPENDENT", "model_C": {}, "model_not_C": {}}), encoding="utf-8")
    fake_i_audit = guard_dir / "fake_independence_audit.json"
    run_checked([sys.executable, "verifier.py", "--problem", str(sample), "--claim", str(fake_i), "--out", str(fake_i_audit)], stdout=subprocess.DEVNULL)
    result = json.loads(fake_i_audit.read_text(encoding="utf-8"))
    tests.append({"test": "fake independence rejected", "pass": result["status"] == "AUDIT_FAILURE", "audit": result})

    unknown = guard_dir / "unknown.json"
    write_unknown(unknown, "30-second budget expired")
    unknown_audit = guard_dir / "unknown_audit.json"
    run_checked([sys.executable, "verifier.py", "--problem", str(sample), "--claim", str(unknown), "--out", str(unknown_audit)], stdout=subprocess.DEVNULL)
    result = json.loads(unknown_audit.read_text(encoding="utf-8"))
    tests.append({
        "test": "timeout remains non-settlement",
        "pass": result["status"] == "BOUNDED_UNKNOWN" and result["logical_outcome"] is None,
        "audit": result,
    })

    return {"all_pass": all(t["pass"] for t in tests), "tests": tests}


def campaign(out: Path) -> dict:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    # The generator creates a public packet and a separate sealed ground-truth packet.
    # Solver subprocesses receive only the opaque public problem path.
    run_checked([sys.executable, "generator.py", "--out", str(out)], stdout=subprocess.DEVNULL)

    ground_truth = json.loads((out / "sealed" / "ground_truth.json").read_text(encoding="utf-8"))
    public_manifest = json.loads((out / "public" / "manifest.json").read_text(encoding="utf-8"))
    seal_sha256 = (out / "public" / "SEAL_SHA256.txt").read_text(encoding="utf-8").strip()

    if len(ground_truth["instances"]) != 135 or len(public_manifest["instances"]) != 135:
        raise RuntimeError("R02 full campaign must contain exactly 135 instances")

    claims = out / "claims"
    audits = out / "audits"
    claims.mkdir(parents=True, exist_ok=True)
    audits.mkdir(parents=True, exist_ok=True)

    rows = []
    limiter = memory_limiter()

    for index, entry in enumerate(ground_truth["instances"], start=1):
        instance_id = entry["id"]
        problem = out / "public" / "instances" / instance_id
        claim = claims / f"{instance_id}.json"
        audit = audits / f"{instance_id}.json"

        started = time.perf_counter()
        operational_status = "completed"
        returncode = 0
        try:
            proc = subprocess.run(
                [sys.executable, str(HERE / "reference_ald.py"), "--problem", str(problem), "--out", str(claim)],
                cwd=HERE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=WALL_SECONDS,
                preexec_fn=limiter,
            )
            returncode = proc.returncode
            if proc.returncode != 0 or not claim.exists():
                operational_status = "resource_or_process_failure"
                write_unknown(claim, f"solver exited with code {proc.returncode} without a verified certificate")
        except subprocess.TimeoutExpired:
            operational_status = "timeout"
            write_unknown(claim, f"{WALL_SECONDS}-second solver budget expired")

        solver_wall = time.perf_counter() - started

        verify_started = time.perf_counter()
        run_checked(
            [sys.executable, "verifier.py", "--problem", str(problem), "--claim", str(claim), "--out", str(audit)],
            stdout=subprocess.DEVNULL,
        )
        verifier_wall = time.perf_counter() - verify_started
        a = json.loads(audit.read_text(encoding="utf-8"))

        certified = a["status"] == "CERTIFIED"
        correct = certified and a["logical_outcome"] == entry["truth"]
        false_settlement = certified and a["logical_outcome"] != entry["truth"]

        row = {
            "index": index,
            "id": instance_id,
            "truth": entry["truth"],
            "horizon": entry["size_parameter"],
            "ocean_horizon": entry["ocean_horizon"],
            "audit_status": a["status"],
            "logical_outcome": a["logical_outcome"],
            "certified_correct": correct,
            "false_settlement": false_settlement,
            "operational_status": operational_status,
            "solver_returncode": returncode,
            "solver_wall_s": round(solver_wall, 6),
            "verifier_wall_s": round(verifier_wall, 6),
            "claim_bytes": claim.stat().st_size,
            "audit_bytes": audit.stat().st_size,
        }
        rows.append(row)
        print(json.dumps(row, sort_keys=True), flush=True)

    guards = adversarial_guards(out, ground_truth)

    status_counts = Counter(r["audit_status"] for r in rows)
    operational_counts = Counter(r["operational_status"] for r in rows)
    class_totals = Counter(r["truth"] for r in rows)
    class_certified = Counter(r["truth"] for r in rows if r["certified_correct"])
    class_unknown = Counter(r["truth"] for r in rows if r["audit_status"] == "BOUNDED_UNKNOWN")
    by_horizon = defaultdict(lambda: {"instances": 0, "certified_correct": 0, "unknown": 0, "audit_failure": 0})
    for r in rows:
        h = str(r["horizon"])
        by_horizon[h]["instances"] += 1
        by_horizon[h]["certified_correct"] += int(r["certified_correct"])
        by_horizon[h]["unknown"] += int(r["audit_status"] == "BOUNDED_UNKNOWN")
        by_horizon[h]["audit_failure"] += int(r["audit_status"] == "AUDIT_FAILURE")

    summary = {
        "benchmark": "ALD Sealed Conjecture-Settling R02",
        "track": "reference-cold-full-135",
        "instances": len(rows),
        "public_seal_sha256": seal_sha256,
        "resource_limits": {"wall_seconds_per_instance": WALL_SECONDS, "memory_mib_per_process": MEMORY_MIB},
        "certified_correct": sum(int(r["certified_correct"]) for r in rows),
        "false_settlements": sum(int(r["false_settlement"]) for r in rows),
        "audit_status_counts": dict(status_counts),
        "operational_status_counts": dict(operational_counts),
        "by_hidden_class": {
            k: {
                "instances": class_totals[k],
                "certified_correct": class_certified[k],
                "bounded_unknown": class_unknown[k],
            }
            for k in sorted(class_totals)
        },
        "by_horizon": dict(sorted(by_horizon.items(), key=lambda kv: int(kv[0]))),
        "adversarial_guards": guards,
        "all_135_certified_correct": len(rows) == 135 and all(r["certified_correct"] for r in rows),
        "campaign_valid": (
            len(rows) == 135
            and not any(r["false_settlement"] for r in rows)
            and guards["all_pass"]
        ),
        "rows": rows,
    }

    (out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "rows"}, indent=2, sort_keys=True))

    # A campaign can be scientifically valid while containing conservative UNKNOWNs.
    # It fails only for a false logical settlement, verifier-guard failure, or malformed campaign.
    if not summary["campaign_valid"]:
        raise SystemExit(1)
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "r02_full_135"))
    args = ap.parse_args()
    campaign(Path(args.out).resolve())


if __name__ == "__main__":
    main()
