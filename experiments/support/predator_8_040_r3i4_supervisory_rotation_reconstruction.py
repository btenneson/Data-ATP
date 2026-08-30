#!/usr/bin/env python3
"""Auditable reconstruction of the missing Predator 8.040 R3/I4 layer.

IMPORTANT PROVENANCE
--------------------
No historical file named ``predator 8.040-R3I4-supervisory-rotation.py`` is
present in the committed btenneson/ATP history used by this experiment.  This
module is therefore explicitly a reconstruction, not a claim to recover the
original bytes.

The reconstruction changes as little mathematical search code as possible:

* frozen base: Predator 8.009-R3I4-saturation-relay from ATP commit
  0e8110f6d4318c107454143b3cf43aa2cc500966;
* live strategy hook: Predator 8.006 ``_strategy_for`` exposed through the
  preserved 8.009 -> 8.008 -> 8.007 -> 8.006 import chain;
* the four preserved legal strategies remain byte-for-byte those of 8.006;
* one fifth legal strategy, ROTATED, is constructed only from extrema already
  present in the four-strategy 8.006 envelope, so no theorem-specific weights
  or new numerical magnitudes are introduced;
* when staleness reaches ``PREDATOR_840_ROTATE_STALE`` (default 5200), the
  supervisory policy selects ROTATED until genuine progress resets staleness.

ROTATED is the target-generic antipodal escape regime.  Coordinates associated
with imagination/exploitation/proximity confidence take the least aggressive
value already present in 8.006; coordinates associated with exploration,
diversity, breadth, and certificate caution take the greatest value already
present in 8.006.  This implements the intended bounded "try the opposite"
revision idea while staying inside the previously tested legal parameter
box.  Metamath rules, proof calculus, candidate emission, and independent
verification are untouched.
"""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "predator 8.009-R3I4-saturation-relay.py"
if not BASE_PATH.exists():
    raise SystemExit(f"missing frozen 8.009 base beside reconstruction: {BASE_PATH}")

spec = importlib.util.spec_from_file_location("predator8_r3i4_saturation_relay_for_840", BASE_PATH)
if spec is None or spec.loader is None:
    raise SystemExit("cannot load Predator 8.009-R3I4-saturation-relay")
BASE9 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = BASE9
spec.loader.exec_module(BASE9)

# Preserved import chain: 8.009 -> 8.008 -> 8.007 -> 8.006.
BASE8 = BASE9.BASE8
BASE7 = BASE8.BASE7
BASE6 = BASE7.BASE6
P8 = BASE9.P8

P8.VERSION = "8.040-R3I4-supervisory-rotation-RECONSTRUCTION"
_ORIGINAL_STRATEGY_FOR = BASE6._strategy_for

_REQUIRED = (
    "imagine_top", "beam", "branch_cap", "progress_weight", "solve_bonus",
    "explore_extra", "cap_factor", "goal_meta_weight", "dv_meta_weight",
    "rhat_weight", "diversity_bonus",
)
for _name in ("COMPASS", "CERTIFY", "DIVERSIFY", "LEAN"):
    if _name not in BASE6.STRATEGY:
        raise RuntimeError(f"frozen 8.006 strategy missing: {_name}")
    if set(BASE6.STRATEGY[_name]) != set(_REQUIRED):
        raise RuntimeError(f"unexpected frozen strategy schema for {_name}")

_values = {k: [BASE6.STRATEGY[s][k] for s in ("COMPASS", "CERTIFY", "DIVERSIFY", "LEAN")]
           for k in _REQUIRED}

# Antipodal escape direction, using only already-existing extrema.
ROTATED = {
    "imagine_top": min(_values["imagine_top"]),
    "beam": min(_values["beam"]),
    "branch_cap": max(_values["branch_cap"]),
    "progress_weight": min(_values["progress_weight"]),
    "solve_bonus": min(_values["solve_bonus"]),
    "explore_extra": max(_values["explore_extra"]),
    "cap_factor": max(_values["cap_factor"]),
    "goal_meta_weight": max(_values["goal_meta_weight"]),
    "dv_meta_weight": max(_values["dv_meta_weight"]),
    "rhat_weight": min(_values["rhat_weight"]),
    "diversity_bonus": max(_values["diversity_bonus"]),
}
BASE6.STRATEGY["ROTATED"] = ROTATED


def _rotate_stale_threshold() -> int:
    raw = os.environ.get("PREDATOR_840_ROTATE_STALE", "5200")
    try:
        value = int(raw)
    except ValueError as exc:
        raise RuntimeError("PREDATOR_840_ROTATE_STALE must be an integer") from exc
    return max(1, value)


def supervisory_strategy_for(stale: int, terminal_rejects_since_improvement: int) -> str:
    """Preserved 8.006 controller plus one bounded antipodal escape regime."""
    stale = int(stale)
    rejects = int(terminal_rejects_since_improvement)
    if stale >= _rotate_stale_threshold():
        return "ROTATED"
    return _ORIGINAL_STRATEGY_FOR(stale, rejects)


# DATA-MIND deliberately monkey-patches this exact module attribute.  Search
# functions defined in BASE6 resolve the name dynamically from BASE6 globals,
# so this is the smallest hook that changes legal search policy without touching
# proof rules or verification.
BASE6._strategy_for = supervisory_strategy_for


def reconstruction_selfcheck() -> dict:
    threshold = _rotate_stale_threshold()
    before = supervisory_strategy_for(max(0, threshold - 1), 0)
    at = supervisory_strategy_for(threshold, 0)
    return {
        "version": P8.VERSION,
        "base": str(BASE_PATH.name),
        "rotate_stale": threshold,
        "strategy_before_threshold": before,
        "strategy_at_threshold": at,
        "rotated": dict(ROTATED),
        "rotated_uses_only_existing_extrema": all(
            ROTATED[k] in _values[k] for k in _REQUIRED
        ),
    }


def main():
    return BASE9.main()


if __name__ == "__main__":
    raise SystemExit(main() or 0)
