"""Top-level NOTALD benchmark runner interlock.

This file deliberately does not launch solvers while the protocol is a freeze candidate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
DEFAULT_PROTOCOL = HERE / "protocol.json"


def load_protocol(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def unresolved_freeze_items(protocol: dict) -> list[str]:
    freeze = protocol.get("freeze", {})
    training = protocol.get("training_policy", {})
    unresolved: list[str] = []

    for name in protocol.get("required_before_run", []):
        if name in freeze:
            value = freeze[name]
        elif name in training:
            value = training[name]
        else:
            value = None
        if value is None:
            unresolved.append(name)
    return unresolved


def require_run_authorization(protocol: dict, cli_authorized: bool) -> None:
    unresolved = unresolved_freeze_items(protocol)
    if unresolved:
        joined = ", ".join(unresolved)
        raise SystemExit(f"REFUSING TO RUN: unresolved freeze items: {joined}")
    if protocol.get("run_authorized") is not True:
        raise SystemExit("REFUSING TO RUN: protocol.json has run_authorized=false")
    if protocol.get("scored_run_authorized") is not True:
        raise SystemExit("REFUSING TO RUN: protocol.json has scored_run_authorized=false")
    if not cli_authorized:
        raise SystemExit("REFUSING TO RUN: explicit --authorize-run flag was not supplied")


def main() -> None:
    parser = argparse.ArgumentParser(description="NOTALD Massive Tied-Ocean benchmark runner")
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument(
        "--authorize-run",
        action="store_true",
        help="Deliberate final interlock; protocol authorization is still required.",
    )
    args = parser.parse_args()

    protocol = load_protocol(args.protocol)
    require_run_authorization(protocol, args.authorize_run)

    # No solver launch code is connected in scaffold version 0.1.
    raise SystemExit(
        "Protocol gates passed, but scaffold 0.1 has no solver launch path. "
        "Create a new benchmark version when adapters and scoring are frozen."
    )


if __name__ == "__main__":
    main()
