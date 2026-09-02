"""Non-scored implementation qualification for the NOTALD Tied-Ocean benchmark.

This module is intentionally separate from the scored benchmark runner.  It exercises the
benchmark machinery on small deterministic Oceans so implementation defects can be found before
any scored instances are generated.  Qualification results MUST NOT be reported as benchmark
scores.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .auditor import audit_ocean, require_exact_horizon
from .generator import OceanGeometry, generate_ocean
from .notald_polarity import Evidence, Settlement, settle


QUALIFICATION_DEPTHS = (10, 25, 75, 100, 250)
QUALIFICATION_SEEDS = (101, 202, 303)
QUALIFICATION_GEOMETRY = OceanGeometry(
    distractors_per_backbone_node=2,
    distractor_min_length=1,
    distractor_max_length=5,
    parallel_detour_probability=0.35,
)


def _check_settlement_logic() -> dict[str, str]:
    cases = {
        "no_certificate": (Evidence(), Settlement.RUNNING),
        "budget_only": (Evidence(budget_exhausted=True), Settlement.BOUNDED_UNKNOWN),
        "refuter_wins": (Evidence(refuter_has_verified_T=True), Settlement.REFUTED),
        "prover_false_side": (Evidence(prover_has_verified_not_T=True), Settlement.AUDIT_FAILURE),
        "dual_certificates": (
            Evidence(prover_has_verified_not_T=True, refuter_has_verified_T=True),
            Settlement.CRITICAL_AUDIT_FAILURE,
        ),
    }
    observed: dict[str, str] = {}
    for name, (evidence, expected) in cases.items():
        actual = settle(evidence)
        if actual is not expected:
            raise AssertionError(f"settlement case {name}: expected {expected}, got {actual}")
        observed[name] = actual.value
    return observed


def run_qualification() -> dict:
    rows: list[dict] = []

    for L in QUALIFICATION_DEPTHS:
        for seed in QUALIFICATION_SEEDS:
            instance = generate_ocean(L=L, seed=seed, geometry=QUALIFICATION_GEOMETRY)
            repeated = generate_ocean(L=L, seed=seed, geometry=QUALIFICATION_GEOMETRY)
            if instance != repeated:
                raise AssertionError(f"generator is not deterministic for L={L}, seed={seed}")

            audit = require_exact_horizon(
                instance.edges,
                instance.source,
                instance.target,
                expected_L=L,
            )
            if len(audit.path) != L + 1:
                raise AssertionError(f"audited path has wrong node count for L={L}, seed={seed}")

            # Deliberately corrupt the graph with a one-edge source-to-target shortcut and ensure
            # the independent auditor detects the wrong horizon.
            tampered = audit_ocean(
                (*instance.edges, (instance.source, instance.target)),
                instance.source,
                instance.target,
                expected_L=L,
            )
            if tampered.distance_matches or tampered.shortest_distance != 1:
                raise AssertionError(f"auditor failed to detect injected shortcut for L={L}, seed={seed}")

            rows.append(
                {
                    "L": L,
                    "seed": seed,
                    "edge_count": len(instance.edges),
                    "shortest_distance": audit.shortest_distance,
                    "deterministic": True,
                    "tamper_detected": True,
                }
            )

    settlement = _check_settlement_logic()
    return {
        "qualification_not_scored": True,
        "purpose": "implementation qualification only; does not consume scored benchmark instances",
        "depths": list(QUALIFICATION_DEPTHS),
        "seeds": list(QUALIFICATION_SEEDS),
        "geometry": asdict(QUALIFICATION_GEOMETRY),
        "instances_checked": len(rows),
        "all_exact_horizons_verified": True,
        "determinism_verified": True,
        "shortcut_tamper_detection_verified": True,
        "settlement_logic": settlement,
        "instances": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run non-scored NOTALD Ocean qualification")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    result = run_qualification()
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
