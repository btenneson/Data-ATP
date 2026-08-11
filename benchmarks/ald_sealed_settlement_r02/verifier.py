from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict

from common import Literal, eval_literal, model_satisfies, parse_problem


def verify_path(problem, cert, target: Literal) -> tuple[bool, str]:
    lits = cert.get("literals")
    axioms = cert.get("axioms")
    if not isinstance(lits, list) or not isinstance(axioms, list) or not lits:
        return False, "path certificate requires literals and axioms"
    try:
        parsed = [Literal.parse(x) for x in lits]
    except Exception as e:
        return False, f"bad literal in certificate: {e}"
    unit_map = {name: lit for name, lit in problem.units}
    edge_map = {name: (a, b) for name, a, b in problem.edges}
    if len(axioms) != len(parsed):
        return False, "axiom list must name one unit axiom plus one axiom per edge"
    if axioms[0] not in unit_map or unit_map[axioms[0]] != parsed[0]:
        return False, "first literal is not justified by named unit axiom"
    for i in range(1, len(parsed)):
        name = axioms[i]
        if name not in edge_map or edge_map[name] != (parsed[i - 1], parsed[i]):
            return False, f"step {i} not justified by named input implication"
    if parsed[-1] != target:
        return False, "certificate ends at wrong target"
    return True, "verified input-axiom Ocean path"


def normalize_model(obj: object) -> Dict[int, bool]:
    if not isinstance(obj, dict):
        raise ValueError("model must be an object")
    out: Dict[int, bool] = {}
    for k, v in obj.items():
        ks = str(k)
        if ks.startswith("n"):
            ks = ks[1:]
        out[int(ks)] = bool(v)
    return out


def verify(problem_path: Path, claim_path: Path) -> dict:
    problem = parse_problem(problem_path)
    claim = json.loads(claim_path.read_text(encoding="utf-8"))
    kind = claim.get("claim")

    if kind == "PROVED":
        ok, detail = verify_path(problem, claim.get("certificate", {}), problem.goal)
        return {"accepted": ok, "logical_outcome": "PROVED" if ok else None,
                "status": "CERTIFIED" if ok else "AUDIT_FAILURE", "detail": detail}
    if kind == "REFUTED":
        ok, detail = verify_path(problem, claim.get("certificate", {}), problem.goal.complement())
        return {"accepted": ok, "logical_outcome": "REFUTED" if ok else None,
                "status": "CERTIFIED" if ok else "AUDIT_FAILURE", "detail": detail}
    if kind == "INDEPENDENT":
        try:
            mt = normalize_model(claim.get("model_C"))
            mf = normalize_model(claim.get("model_not_C"))
        except Exception as e:
            return {"accepted": False, "logical_outcome": None, "status": "AUDIT_FAILURE", "detail": str(e)}
        ok_t = model_satisfies(problem, mt) and eval_literal(problem.goal, mt)
        ok_f = model_satisfies(problem, mf) and not eval_literal(problem.goal, mf)
        ok = ok_t and ok_f
        return {
            "accepted": ok,
            "logical_outcome": "INDEPENDENT" if ok else None,
            "status": "CERTIFIED" if ok else "AUDIT_FAILURE",
            "detail": "two-model semantic independence certificate" if ok else "one or both models fail",
        }
    if kind == "UNKNOWN":
        return {"accepted": True, "logical_outcome": None, "status": "BOUNDED_UNKNOWN",
                "detail": claim.get("reason", "no verified certificate within budget")}
    return {"accepted": False, "logical_outcome": None, "status": "AUDIT_FAILURE", "detail": "unknown claim type"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--problem", required=True)
    ap.add_argument("--claim", required=True)
    ap.add_argument("--out")
    args = ap.parse_args()
    result = verify(Path(args.problem), Path(args.claim))
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
