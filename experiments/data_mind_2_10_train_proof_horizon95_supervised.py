#!/usr/bin/env python3
"""DATA-MIND 2.10 host for the frozen DATA-MIND 2.8 proof-horizon learner.

The learner itself is deliberately not changed.  This launcher is used with the
exact historical 2.8 trainer and 2.6 sanitizer downloaded from a pinned commit.
It intercepts predator_fast_parse.install(), lets it install the exact fast
parser, and only then places each grammar parse in a separate forked process.
The parent can therefore terminate a pathological parse even when the parser is
stuck below Python's ordinary signal/exception boundary.

A terminated parse is returned to the unchanged base learner as None.  The base
learner therefore counts it as a parse failure and still enforces its original
>=95% training parse-coverage validity guard.  No theorem is deleted from the
frozen cohort and no learning target, split, seed, or proof-horizon formula is
changed.
"""
from __future__ import annotations

import atexit
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import sys
import time
import traceback
from typing import Any

from data_atp import (
    ActionContext,
    ResourceSample,
    SecurityClass,
    SecurityGovernor,
    SentinelDecision,
    SentinelPolicy,
)


def _pop_float_option(argv: list[str], name: str, default: float) -> float:
    prefix = name + "="
    for i, arg in enumerate(list(argv)):
        if arg.startswith(prefix):
            value = float(arg[len(prefix):])
            del argv[i]
            return value
        if arg == name:
            if i + 1 >= len(argv):
                raise SystemExit(f"{name} requires a value")
            value = float(argv[i + 1])
            del argv[i:i + 2]
            return value
    return default


def _pop_flag(argv: list[str], name: str) -> bool:
    if name in argv:
        argv.remove(name)
        return True
    return False


def _peek_option(argv: list[str], name: str) -> str | None:
    prefix = name + "="
    for i, arg in enumerate(argv):
        if arg.startswith(prefix):
            return arg[len(prefix):]
        if arg == name and i + 1 < len(argv):
            return argv[i + 1]
    return None


PARSE_TIMEOUT_S = _pop_float_option(sys.argv, "--parse-timeout-s", 5.0)
MAX_RAM_FRACTION = _pop_float_option(sys.argv, "--sentinel-max-ram-fraction", 0.40)
POLL_S = _pop_float_option(sys.argv, "--supervision-poll-s", 0.010)
SELFTEST = _pop_flag(sys.argv, "--supervision-selftest")
OUT_OPTION = _peek_option(sys.argv, "--out")

if PARSE_TIMEOUT_S <= 0:
    raise SystemExit("--parse-timeout-s must be positive")
if not (0.0 < MAX_RAM_FRACTION <= 1.0):
    raise SystemExit("--sentinel-max-ram-fraction must be in (0,1]")
if POLL_S <= 0:
    raise SystemExit("--supervision-poll-s must be positive")
if "fork" not in mp.get_all_start_methods():
    raise SystemExit("DATA-MIND 2.10 proof-horizon supervision requires a POSIX fork runner")

_CTX = mp.get_context("fork")
# A single elapsed-time or RAM outlier must be enough to quarantine this
# particular training transaction.  ADR-0002 explicitly permits experiment-
# specific thresholds while retaining the fail-closed Sentinel decision path.
_SENTINEL = SecurityGovernor(
    policy=SentinelPolicy(
        internal_risk_threshold=0.25,
        max_ram_fraction=MAX_RAM_FRACTION,
        max_elapsed_seconds=max(1e-6, PARSE_TIMEOUT_S * 0.999),
    )
)

_STATS: dict[str, Any] = {
    "host_architecture_version": "2.10",
    "base_learner_architecture_version": "2.8",
    "calls": 0,
    "completed": 0,
    "parse_none": 0,
    "quarantined_runtime": 0,
    "quarantined_ram": 0,
    "child_errors": 0,
    "max_observed_elapsed_s": 0.0,
    "max_observed_ram_fraction": 0.0,
    "parse_timeout_s": PARSE_TIMEOUT_S,
    "sentinel_max_ram_fraction": MAX_RAM_FRACTION,
    "sentinel_internal_risk_threshold": 0.25,
    "process_isolation": "one forked child per grammar parse",
}


def _output_dir() -> Path | None:
    if not OUT_OPTION:
        return None
    return Path(OUT_OPTION)


def _write_jsonl(name: str, row: dict[str, Any]) -> None:
    out = _output_dir()
    if out is None:
        return
    out.mkdir(parents=True, exist_ok=True)
    with (out / name).open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


def _write_summary() -> None:
    out = _output_dir()
    if out is None:
        return
    try:
        out.mkdir(parents=True, exist_ok=True)
        (out / "supervision_summary.json").write_text(
            json.dumps(_STATS, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    except Exception as exc:
        print(f"[SUPERVISION-SUMMARY-ERROR] {type(exc).__name__}: {exc}", flush=True)


atexit.register(_write_summary)


def _pack_tree(tree):
    if tree is None:
        return None
    return (
        tree.label,
        tree.typecode,
        tree.var,
        tuple(_pack_tree(k) for k in tree.kids),
    )


def _unpack_tree(packed, grammar_module):
    if packed is None:
        return None
    label, typecode, var, kids = packed
    return grammar_module.Tree(
        label,
        typecode,
        [_unpack_tree(k, grammar_module) for k in kids],
        var,
    )


def _child_parse(parser, tokens, typecode, by_tc, send_conn) -> None:
    try:
        tree = parser(tokens, typecode, by_tc)
        send_conn.send(("ok", _pack_tree(tree)))
    except BaseException as exc:  # preserve unexpected parser errors for parent
        send_conn.send((
            "error",
            type(exc).__name__,
            str(exc),
            traceback.format_exc(limit=12),
        ))
    finally:
        try:
            send_conn.close()
        except Exception:
            pass


def _ram_fraction(pid: int) -> float:
    """Return child VmRSS/system MemTotal on Linux; zero if unavailable."""
    try:
        rss_kb = None
        for line in Path(f"/proc/{pid}/status").read_text().splitlines():
            if line.startswith("VmRSS:"):
                rss_kb = float(line.split()[1])
                break
        total_kb = None
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemTotal:"):
                total_kb = float(line.split()[1])
                break
        if rss_kb is None or not total_kb:
            return 0.0
        return max(0.0, min(1.0, rss_kb / total_kb))
    except Exception:
        return 0.0


def _stop_process(proc) -> None:
    if not proc.is_alive():
        proc.join(timeout=0.2)
        return
    proc.terminate()
    proc.join(timeout=1.0)
    if proc.is_alive():
        proc.kill()
        proc.join(timeout=1.0)


def _supervised_parse(parser, grammar_module, tokens, typecode, by_tc):
    _STATS["calls"] += 1
    call = int(_STATS["calls"])
    token_list = list(tokens)
    text = " ".join(token_list)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()

    recv_conn, send_conn = _CTX.Pipe(duplex=False)
    proc = _CTX.Process(
        target=_child_parse,
        args=(parser, token_list, typecode, by_tc, send_conn),
    )
    started = time.monotonic()
    proc.start()
    send_conn.close()
    max_ram = 0.0

    try:
        while True:
            if recv_conn.poll(POLL_S):
                message = recv_conn.recv()
                elapsed = time.monotonic() - started
                max_ram = max(max_ram, _ram_fraction(proc.pid or -1))
                _STATS["max_observed_elapsed_s"] = max(
                    float(_STATS["max_observed_elapsed_s"]), elapsed
                )
                _STATS["max_observed_ram_fraction"] = max(
                    float(_STATS["max_observed_ram_fraction"]), max_ram
                )
                proc.join(timeout=1.0)
                kind = message[0]
                if kind == "ok":
                    tree = _unpack_tree(message[1], grammar_module)
                    if tree is None:
                        _STATS["parse_none"] += 1
                    else:
                        _STATS["completed"] += 1
                    return tree
                _STATS["child_errors"] += 1
                _, exc_type, exc_text, tb = message
                raise RuntimeError(
                    f"isolated grammar parser raised {exc_type}: {exc_text}\n{tb}"
                )

            elapsed = time.monotonic() - started
            if proc.pid:
                max_ram = max(max_ram, _ram_fraction(proc.pid))
            runtime_outlier = elapsed > PARSE_TIMEOUT_S
            ram_outlier = max_ram > MAX_RAM_FRACTION
            if runtime_outlier or ram_outlier:
                sample = ResourceSample(
                    elapsed_seconds=elapsed,
                    ram_fraction=max_ram,
                )
                context = ActionContext(
                    action="proof_horizon_grammar_parse",
                    target_scope="internal",
                    security_class=SecurityClass.BENIGN,
                    requires_formal_verification=False,
                    metadata={
                        "call": call,
                        "token_count": len(token_list),
                        "token_sha256": digest,
                    },
                )
                assessment = _SENTINEL.assess(context, sample)
                # The hard process boundary is authoritative even if a future
                # policy were accidentally weakened.  Sentinel's assessment is
                # recorded as the policy explanation for the containment.
                _stop_process(proc)
                reason = "runtime" if runtime_outlier else "ram"
                if runtime_outlier:
                    _STATS["quarantined_runtime"] += 1
                else:
                    _STATS["quarantined_ram"] += 1
                _STATS["max_observed_elapsed_s"] = max(
                    float(_STATS["max_observed_elapsed_s"]), elapsed
                )
                _STATS["max_observed_ram_fraction"] = max(
                    float(_STATS["max_observed_ram_fraction"]), max_ram
                )
                row = {
                    "event": "SENTINEL_QUARANTINE",
                    "reason": reason,
                    "call": call,
                    "elapsed_s": elapsed,
                    "ram_fraction": max_ram,
                    "token_count": len(token_list),
                    "token_sha256": digest,
                    "preview": text[:180],
                    "sentinel_decision": assessment.decision.value,
                    "risk_score": assessment.risk_score,
                    "sentinel_reasons": list(assessment.reasons),
                }
                _write_jsonl("sentinel_quarantine.jsonl", row)
                print(
                    f"[SENTINEL-QUARANTINE] reason={reason} call={call} "
                    f"elapsed_s={elapsed:.3f} ram_fraction={max_ram:.6f} "
                    f"tokens={len(token_list)} sha256={digest} "
                    f"decision={assessment.decision.value}",
                    flush=True,
                )
                if assessment.decision not in {
                    SentinelDecision.QUARANTINE,
                    SentinelDecision.BLOCK,
                    SentinelDecision.REQUIRE_HUMAN,
                }:
                    print(
                        "[SUPERVISION-WARNING] hard boundary stopped a resource "
                        "outlier that Sentinel policy did not deny",
                        flush=True,
                    )
                return None

            if not proc.is_alive():
                # Give the pipe one last chance to deliver buffered output.
                if recv_conn.poll(0.05):
                    continue
                code = proc.exitcode
                _STATS["child_errors"] += 1
                raise RuntimeError(
                    f"isolated grammar parser exited without result; exitcode={code}"
                )
    finally:
        try:
            recv_conn.close()
        except Exception:
            pass
        if proc.is_alive():
            _stop_process(proc)


def _install_supervisor() -> tuple[Any, Any]:
    import setmm_grammar as G  # type: ignore
    import predator_fast_parse as PFP  # type: ignore

    original_install = PFP.install

    def supervised_install(grammar_module=None):
        gm = original_install(grammar_module)
        installed_parser = gm.parse

        def guarded(tokens, typecode, by_tc, memo=None, all_parses=False, cap=4):
            # The proof-horizon trainer calls the ordinary three-argument form.
            # Preserve the full signature if another caller supplies options.
            if memo is not None or all_parses or cap != 4:
                def configured_parser(ts, tc, btc):
                    return installed_parser(
                        ts, tc, btc, memo=memo, all_parses=all_parses, cap=cap
                    )
                parser = configured_parser
            else:
                parser = installed_parser
            return _supervised_parse(parser, gm, tokens, typecode, by_tc)

        guarded._dm210_supervised = True  # type: ignore[attr-defined]
        guarded._dm210_underlying_parser = installed_parser  # type: ignore[attr-defined]
        gm.parse = guarded
        return gm

    PFP.install = supervised_install
    return G, PFP


def _selftest_parser(tokens, typecode, by_tc):
    import setmm_grammar as G  # type: ignore
    if list(tokens) == ["HANG"]:
        time.sleep(max(0.20, PARSE_TIMEOUT_S * 4.0))
        return None
    return G.Tree(None, typecode, (), list(tokens)[0])


def _run_selftest() -> int:
    G, PFP = _install_supervisor()
    PFP.install(G)
    if not getattr(G.parse, "_dm210_supervised", False):
        raise RuntimeError("supervisor was overwritten by predator_fast_parse.install")
    ok = _supervised_parse(_selftest_parser, G, ["ph"], "wff", {})
    if ok is None or ok.var != "ph":
        raise RuntimeError("supervisor failed to return a normal parse tree")
    before = int(_STATS["quarantined_runtime"])
    bad = _supervised_parse(_selftest_parser, G, ["HANG"], "wff", {})
    after = int(_STATS["quarantined_runtime"])
    if bad is not None or after != before + 1:
        raise RuntimeError("supervisor failed to externally quarantine a hung parse")
    print("SUPERVISION_SELFTEST_OK", flush=True)
    _write_summary()
    return 0


def _write_host_manifest(base_rc: int) -> None:
    out = _output_dir()
    if out is None:
        return
    out.mkdir(parents=True, exist_ok=True)
    manifest = {
        "status": "TRAINING_COMPLETE" if base_rc == 0 and (out / "TRAINING_COMPLETE").exists() else "INCOMPLETE",
        "host_architecture_version": "2.10",
        "base_learner_architecture_version": "2.8",
        "base_learner_changed": False,
        "frozen_95pct_cohort_changed": False,
        "seed_changed": False,
        "learning_objective_changed": False,
        "validity_guard_changed": False,
        "validity_guard": "base trainer requires >=95% training parse coverage",
        "new_execution_boundary": "external per-grammar-parse fork process supervised by DATA-MIND 2.10 Sentinel",
        "process_isolation": True,
        "parse_timeout_s": PARSE_TIMEOUT_S,
        "sentinel_max_ram_fraction": MAX_RAM_FRACTION,
        "supervision_summary_file": "supervision_summary.json",
        "quarantine_file": "sentinel_quarantine.jsonl",
    }
    (out / "data_mind_2_10_training_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> int:
    if SELFTEST:
        return _run_selftest()

    _install_supervisor()
    # Import only after predator_fast_parse.install has been intercepted.  The
    # historical base trainer later calls PFP.install(G), which now installs the
    # fast parser first and wraps that exact installed parser second.
    import data_mind_2_8_train_proof_horizon95 as base

    print(
        f"[DATA-MIND-2.10] exact DATA-MIND 2.8 learner under external Sentinel "
        f"parse supervision: timeout={PARSE_TIMEOUT_S:.3f}s "
        f"max_ram_fraction={MAX_RAM_FRACTION:.3f}",
        flush=True,
    )
    rc = int(base.main())
    _write_summary()
    _write_host_manifest(rc)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
