#!/usr/bin/env python3
"""Prepare and audit a local HaloProof development environment.

This script deliberately separates:
1. frozen-environment/reference-proof development, and
2. the later blind target search.

It never classifies a failed search as a refutation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
from datetime import datetime, timezone
from typing import Sequence


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest().upper()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(cmd: Sequence[str], cwd: Path, log_path: Path) -> dict:
    started = now()
    proc = subprocess.run(
        list(cmd),
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        errors="replace",
    )
    text = proc.stdout or ""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(
        "$ " + subprocess.list2cmdline(list(cmd)) + "\n\n" + text,
        encoding="utf-8",
    )
    return {
        "command": list(cmd),
        "returncode": proc.returncode,
        "started_utc": started,
        "finished_utc": now(),
        "log": str(log_path),
    }


def concat_files(base: Path, extension: Path, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("wb") as dst:
        for source in (base, extension):
            data = source.read_bytes()
            dst.write(data)
            if data and not data.endswith(b"\n"):
                dst.write(b"\n")


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description="Prepare/freeze HaloProof H=R(t) environment before blind search."
    )
    ap.add_argument("--atp-root", required=True, help="Local checkout of btenneson/ATP")
    ap.add_argument("--setmm", required=True, help="Exact frozen set.mm snapshot")
    ap.add_argument("--run-root", default="runs/haloproof_advanced")
    ap.add_argument(
        "--extension",
        help="HaloProof order/halo/target .mm extension built on native Poly1 and Frac machinery",
    )
    ap.add_argument("--target-label", help="Exact target label in the extension")
    ap.add_argument(
        "--launch",
        action="store_true",
        help="Reserved for the later blind run; refused until reference-proof gates exist",
    )
    return ap


# Inventory the exact native route first.  The benchmark does not require us
# to reimplement a rational-function field if the frozen set.mm already has
# Poly1/Frac and their supporting theorems.
INVENTORY = [
    ("schroeder_bernstein", ["search", "--prefix", "sbth"]),
    ("real_field", ["search", "--prefix", "refld"]),
    ("field_to_domain", ["search", "--prefix", "fldidom"]),
    ("poly1_domain", ["search", "--prefix", "ply1idom"]),
    ("poly1", ["search", "Poly1", "--logical-only", "--limit", "120"]),
    ("poly1_variable", ["search", "var1", "--logical-only", "--limit", "120"]),
    ("poly1_coefficients", ["search", "coe1", "--logical-only", "--limit", "160"]),
    ("fractions", ["search", "Frac", "--logical-only", "--limit", "160"]),
    ("fraction_prefix", ["search", "--prefix", "frac"]),
    ("infinitesimal", ["search", "<<<", "--logical-only", "--limit", "120"]),
    ("ordered_fields", ["search", "oField", "--logical-only", "--limit", "120"]),
    ("dominance", ["search", "~<_", "--logical-only", "--limit", "100"]),
    ("equinumerosity", ["search", "~~", "--logical-only", "--limit", "100"]),
    ("real_cardinality", ["search", "RR", "~~", "--logical-only", "--limit", "100"]),
    ("finite_functions", ["search", "Fin", "--logical-only", "--limit", "100"]),
    ("quotients", ["search", "/.", "--logical-only", "--limit", "100"]),
]


def write_manifest(run_root: Path, manifest: dict) -> None:
    (run_root / "HALOPROOF_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


def main(argv: list[str] | None = None) -> int:
    a = parser().parse_args(argv)
    atp = Path(a.atp_root).expanduser().resolve()
    setmm = Path(a.setmm).expanduser().resolve()
    run_root = Path(a.run_root).expanduser().resolve()
    logs = run_root / "logs"
    artifacts = run_root / "artifacts"
    logs.mkdir(parents=True, exist_ok=True)
    artifacts.mkdir(parents=True, exist_ok=True)

    metamath = atp / "metamath.py"
    grammar = atp / "setmm_grammar.py"
    required = [atp, setmm, metamath, grammar]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise SystemExit("required path missing:\n  " + "\n  ".join(missing))

    manifest = {
        "schema_version": "0.2",
        "campaign": "HaloProof Advanced Settlement Campaign",
        "benchmark_model": "H = R(t), eventual-sign order near 0+, I={x: forall n>0 |x|<1/n}",
        "native_route": {
            "real_field": "RRfld",
            "polynomial_ring": "Poly1 ` RRfld",
            "rational_function_field": "Frac ` ( Poly1 ` RRfld )",
            "distinguished_variable": "var1 ` RRfld",
            "reuse": [
                "refld",
                "fldidom",
                "ply1idom",
                "fracfld",
                "fracf1",
                "coe1",
                "<<<",
                "sbth",
            ],
        },
        "created_utc": now(),
        "host": {
            "platform": platform.platform(),
            "python": sys.version,
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "inputs": {
            "setmm": {"path": str(setmm), "sha256": sha256(setmm)},
            "metamath_py": {"path": str(metamath), "sha256": sha256(metamath)},
            "setmm_grammar_py": {"path": str(grammar), "sha256": sha256(grammar)},
        },
        "steps": [],
        "gate": "ENVIRONMENT_DEVELOPMENT",
        "mathematical_outcome": None,
    }

    selftest = run(
        [sys.executable, str(metamath), "selftest"],
        atp,
        logs / "00_metamath_selftest.txt",
    )
    manifest["steps"].append({"name": "verifier_selftest", **selftest})
    if selftest["returncode"] != 0:
        manifest["gate"] = "PROTOCOL_FAILURE"
        write_manifest(run_root, manifest)
        return 2

    for name, subargs in INVENTORY:
        cmd = [sys.executable, str(metamath), *subargs, "--file", str(setmm)]
        result = run(cmd, atp, logs / f"inventory_{name}.txt")
        manifest["steps"].append({"name": f"inventory_{name}", **result})

    extension = Path(a.extension).expanduser().resolve() if a.extension else None
    if extension is None:
        manifest["gate"] = "NEEDS_HALOPROOF_ORDER_HALO_EXTENSION"
        manifest["remaining_formal_obligations"] = [
            "Instantiate P = Poly1(RRfld) and H = Frac(P) using native set.mm machinery.",
            "Define eventual-sign positivity/order near 0+ algebraically from the least-degree nonzero polynomial coefficients.",
            "Prove the sign/order is independent of the chosen fraction representative.",
            "Identify the embedded variable t and prove it is positive and smaller than every positive real constant.",
            "Define the exact two-sided halo I = {x in H : forall positive n, |x| < 1/n}.",
            "Prove r |-> r*t injects RR into I.",
            "Prove H ~~ RR using finite real coefficient data, then I ~<_ RR.",
            "Apply Schroeder-Bernstein to obtain I ~~ RR.",
        ]
        manifest["next_action"] = (
            "Build the conservative eventual-sign order/halo/target extension on top of native "
            "Poly1(RRfld) and Frac(Poly1(RRfld)), then produce a separately verified reference "
            "proof before opening the blind target search."
        )
        write_manifest(run_root, manifest)
        print(f"HaloProof development inventory complete: {run_root}")
        print("Gate: NEEDS_HALOPROOF_ORDER_HALO_EXTENSION")
        return 3

    if not extension.exists():
        raise SystemExit(f"extension not found: {extension}")
    if not a.target_label:
        raise SystemExit("--target-label is required when --extension is supplied")

    environment = artifacts / "haloproof_frozen_environment.mm"
    concat_files(setmm, extension, environment)
    manifest["inputs"]["extension"] = {
        "path": str(extension),
        "sha256": sha256(extension),
    }
    manifest["inputs"]["environment"] = {
        "path": str(environment),
        "sha256": sha256(environment),
    }
    manifest["target_label"] = a.target_label

    roundtrip = run(
        [sys.executable, str(grammar), "roundtrip", str(environment)],
        atp,
        logs / "10_roundtrip.txt",
    )
    manifest["steps"].append({"name": "grammar_roundtrip", **roundtrip})
    if roundtrip["returncode"] != 0:
        manifest["gate"] = "PROTOCOL_FAILURE_GRAMMAR"
        write_manifest(run_root, manifest)
        return 4

    tree = run(
        [sys.executable, str(grammar), "tree", str(environment), a.target_label],
        atp,
        logs / "11_target_tree.txt",
    )
    manifest["steps"].append({"name": "target_parse_tree", **tree})
    if tree["returncode"] != 0:
        manifest["gate"] = "PROTOCOL_FAILURE_TARGET_PARSE"
        write_manifest(run_root, manifest)
        return 5

    show = run(
        [sys.executable, str(metamath), "show", str(environment), a.target_label],
        atp,
        logs / "12_target_show.txt",
    )
    manifest["steps"].append({"name": "target_identity", **show})
    if show["returncode"] != 0:
        manifest["gate"] = "PROTOCOL_FAILURE_TARGET_IDENTITY"
        write_manifest(run_root, manifest)
        return 6

    manifest["gate"] = "REFERENCE_PROOF_REQUIRED"
    manifest["next_action"] = (
        "Produce and independently verify a reference certificate for the exact target; "
        "seal it away from the later blind condition. Only then freeze the nontrivial index."
    )
    write_manifest(run_root, manifest)

    if not a.launch:
        print(f"HaloProof environment checks passed: {run_root}")
        print("Gate: REFERENCE_PROOF_REQUIRED")
        return 0

    raise SystemExit(
        "--launch refused: the HaloProof protocol requires a separately verified "
        "reference proof and frozen nontrivial index before the blind target run. "
        "Record those artifacts in a frozen environment release first."
    )


if __name__ == "__main__":
    raise SystemExit(main())
