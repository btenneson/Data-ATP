#!/usr/bin/env python3
"""Resilient launcher for DATA-MIND 2.8 learned proof-horizon training.

This wrapper deliberately leaves the frozen 95% cohort and the underlying
trainer unchanged.  It only guards individual grammar parses so one
pathological statement cannot consume the entire GitHub Actions budget.

A timed-out parse is returned as ``None`` to the original trainer, which
already counts parse failures and refuses to freeze a model unless training
parse coverage remains at least 95%.  Thus this engineering guard cannot
silently relax the trainer's existing validity threshold.
"""
from __future__ import annotations

import hashlib
import signal
import sys
import time


def _pop_float_option(argv: list[str], name: str, default: float) -> float:
    """Remove a wrapper-only numeric option before handing argv to base main."""
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


PARSE_TIMEOUT_S = _pop_float_option(sys.argv, "--parse-timeout-s", 5.0)
if PARSE_TIMEOUT_S <= 0:
    raise SystemExit("--parse-timeout-s must be positive")

# The workflow already places upstream_atp and upstream_atp/predator 8 on
# PYTHONPATH.  Import and patch the exact grammar module that the base trainer
# will subsequently import.
import setmm_grammar as G  # type: ignore

_ORIGINAL_PARSE = G.parse
_PARSE_CALL = 0


class _ParseDeadline(Exception):
    pass


def _deadline_handler(_signum, _frame):
    raise _ParseDeadline()


def _timed_parse(tokens, typecode, by_tc):
    global _PARSE_CALL
    _PARSE_CALL += 1
    call = _PARSE_CALL
    text = " ".join(tokens)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    started = time.monotonic()

    # GitHub's Ubuntu runner executes this in the main thread, where SIGALRM
    # provides a hard boundary even if the recursive parser stops making
    # progress.  Restore any prior handler after every theorem.
    prior_handler = signal.getsignal(signal.SIGALRM)
    signal.signal(signal.SIGALRM, _deadline_handler)
    signal.setitimer(signal.ITIMER_REAL, PARSE_TIMEOUT_S)
    try:
        return _ORIGINAL_PARSE(tokens, typecode, by_tc)
    except _ParseDeadline:
        elapsed = time.monotonic() - started
        preview = text[:180].replace("\n", " ")
        print(
            f"[PARSE-TIMEOUT] call={call} elapsed_s={elapsed:.3f} "
            f"type={typecode} tokens={len(tokens)} sha256={digest} "
            f"preview={preview!r}",
            flush=True,
        )
        return None
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0.0)
        signal.signal(signal.SIGALRM, prior_handler)


G.parse = _timed_parse

# Import only after patching G so the base trainer uses the guarded parser.
import data_mind_2_8_train_proof_horizon95 as base


if __name__ == "__main__":
    print(
        f"[RESILIENCE] per-grammar-parse timeout={PARSE_TIMEOUT_S:.3f}s; "
        "frozen cohort and base learner unchanged",
        flush=True,
    )
    raise SystemExit(base.main())
