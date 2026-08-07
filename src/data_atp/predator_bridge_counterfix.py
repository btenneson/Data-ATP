"""Preserve Predator's hidden fresh-metavariable counter across Data-ATP resumes.

This is a narrow Phase 0.0.1 compatibility layer over ``predator_bridge``.
The frozen Predator bundle remains byte-for-byte untouched.  Predator 8.001
uses a module-global ``itertools.count`` to allocate metavariable names; a
faithful continuation must therefore checkpoint and restore that counter in
addition to the frontier, RNG, seen set, and expansion ledger.
"""

from __future__ import annotations

import itertools
from pathlib import Path
import subprocess
import sys
from typing import Any

from . import predator_bridge as base


COUNTERFIX_VERSION = "0.1"

_ORIGINAL_INIT = base.Continuation.__init__
_ORIGINAL_SAVE = base.Continuation.save
_ORIGINAL_FACTORY = base.make_resumable_prover


def _counter_args(engine: Any) -> list[int]:
    counter = getattr(engine, "_counter", None)
    if counter is None:
        raise base.BridgeError("external engine has no _counter to checkpoint")
    try:
        reduced = counter.__reduce__()
        args = list(reduced[1])
    except Exception as exc:  # pragma: no cover - defensive protocol failure
        raise base.BridgeError(f"cannot serialize external fresh counter: {exc}") from exc
    if not args or len(args) > 2 or not all(isinstance(x, int) for x in args):
        raise base.BridgeError(f"unexpected itertools.count state: {args!r}")
    return args


def _patched_init(
    self,
    run_root: Path,
    run_id: str,
    identity: dict[str, Any],
    budget: int,
    checkpoint_every: int,
    resume: bool,
    argv_without_resume: list[str],
) -> None:
    enriched = dict(identity)
    enriched["counterfix_version"] = COUNTERFIX_VERSION
    enriched["counterfix_sha256"] = base.sha256(Path(__file__).resolve())
    _ORIGINAL_INIT(
        self,
        run_root,
        run_id,
        enriched,
        budget,
        checkpoint_every,
        resume,
        argv_without_resume,
    )


def _patched_save(self, state: dict[str, Any], expansion: int, reason: str) -> None:
    engine = sys.modules.get(base.ENGINE_MODULE_NAME)
    if engine is None:
        raise base.BridgeError("external engine is not loaded; cannot checkpoint fresh counter")
    augmented = dict(state)
    augmented["engine_fresh_counter_args"] = _counter_args(engine)
    _ORIGINAL_SAVE(self, augmented, expansion, reason)


def _patched_factory(search_module, continuation):
    inner = _ORIGINAL_FACTORY(search_module, continuation)

    def prove_legal_first(engine, *args, **kwargs):
        state = continuation.restored_state
        if state is not None:
            counter_args = state.get("engine_fresh_counter_args")
            if counter_args is None:
                raise base.BridgeError(
                    "checkpoint predates fresh-counter capture; faithful resume refused"
                )
            if (
                not isinstance(counter_args, list)
                or not counter_args
                or len(counter_args) > 2
                or not all(isinstance(x, int) for x in counter_args)
            ):
                raise base.BridgeError("checkpoint contains malformed fresh-counter state")
            # Restore immediately before the resumed prover consumes its saved frontier.
            # This intentionally overrides any incidental counter movement during setup.
            engine._counter = itertools.count(*counter_args)
        return inner(engine, *args, **kwargs)

    return prove_legal_first


def _patched_resume_command(self) -> str:
    src = Path(__file__).resolve().parents[1]
    argv = [
        sys.executable,
        "-m",
        "data_atp.predator_bridge_counterfix",
        *self.argv_without_resume,
        "--resume",
    ]
    return (
        f"$env:PYTHONPATH = {base.ps_quote(str(src))}; & "
        + subprocess.list2cmdline(argv)
    )


# Install the narrow compatibility hooks before delegating to the audited bridge.
base.Continuation.__init__ = _patched_init
base.Continuation.save = _patched_save
base.Continuation.resume_command = _patched_resume_command
base.make_resumable_prover = _patched_factory


def main(argv: list[str] | None = None) -> int:
    return base.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
