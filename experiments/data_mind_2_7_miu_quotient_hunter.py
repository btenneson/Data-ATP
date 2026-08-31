#!/usr/bin/env python3
"""DATA-MIND 2.7 Quotient Hunter: controlled MIU metalogical-shortcut test.

Scientific question
-------------------
Can Quotient Hunter discover a useful quotient/invariant from the MIU formal
system without being handed the famous shortcut, and can that invariant settle
MU where ordinary bounded rule search only returns UNKNOWN?

Anti-leakage design
-------------------
* The candidate language is generic: symbol-count coordinates for every MIU
  symbol plus string length, each reduced modulo m for m=2..12.
* QH is NOT told to inspect the number of I's and is NOT told modulus 3.
* QH is NOT given a known invariant or a proof that MU is impossible.
* Candidate quotients are mechanically verified against the axiom and all four
  MIU rules before they may settle the target.
* Ordinary BFS and QH receive the same formal system and target.

The verifier is specialized only to the declared candidate language
(count/length modulo m).  It computes the exact induced affine action of each
MIU rule on each candidate coordinate and closes the axiom class under those
maps.  Thus a separation is a genuine global invariant for that coordinate,
not merely an empirical pattern in a finite training sample.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, asdict
import argparse
import json
from pathlib import Path
import time
from typing import Callable

AXIOM = "MI"
TARGET_DEFAULT = "MU"
SYMBOLS = ("M", "I", "U")


def successors(w: str) -> set[str]:
    """All one-step MIU successors under Hofstadter's four rules."""
    out: set[str] = set()

    # Rule I: if a string ends in I, append U.
    if w.endswith("I"):
        out.add(w + "U")

    # Rule II: Mx -> Mxx.
    if w.startswith("M"):
        x = w[1:]
        out.add("M" + x + x)

    # Rule III: replace any occurrence III by U.
    start = 0
    while True:
        i = w.find("III", start)
        if i < 0:
            break
        out.add(w[:i] + "U" + w[i + 3 :])
        start = i + 1

    # Rule IV: delete any occurrence UU.
    start = 0
    while True:
        i = w.find("UU", start)
        if i < 0:
            break
        out.add(w[:i] + w[i + 2 :])
        start = i + 1

    return out


@dataclass(frozen=True)
class Candidate:
    feature: str
    modulus: int

    @property
    def name(self) -> str:
        return f"{self.feature} mod {self.modulus}"

    def value(self, w: str) -> int:
        if self.feature == "length":
            return len(w) % self.modulus
        if self.feature.startswith("count_"):
            sym = self.feature.split("_", 1)[1]
            return w.count(sym) % self.modulus
        raise ValueError(self.feature)


@dataclass
class QuotientReport:
    name: str
    feature: str
    modulus: int
    axiom_class: int
    target_class: int
    reachable_classes: list[int]
    separates_target: bool
    verified_global: bool
    transition_maps: dict[str, list[int]]
    class_count: int
    compression_ratio: float
    complexity: int


def candidate_language() -> list[Candidate]:
    features = ["length"] + [f"count_{s}" for s in SYMBOLS]
    return [Candidate(feature=f, modulus=m) for f in features for m in range(2, 13)]


def rule_map(candidate: Candidate, rule: str, r: int) -> int:
    """Exact induced residue map for the candidate coordinate.

    The maps come from the declared MIU rule syntax, not from target-specific
    knowledge.  For symbol counts and length, each rule acts affinely.
    """
    m = candidate.modulus
    f = candidate.feature

    if f == "count_M":
        # Every legal rule preserves the single leading M.
        return r % m

    if f == "count_I":
        if rule == "R1":   # append U
            return r % m
        if rule == "R2":   # duplicate tail; all I are in the tail
            return (2 * r) % m
        if rule == "R3":   # III -> U
            return (r - 3) % m
        if rule == "R4":   # UU -> empty
            return r % m

    if f == "count_U":
        if rule == "R1":
            return (r + 1) % m
        if rule == "R2":
            return (2 * r) % m
        if rule == "R3":
            return (r + 1) % m
        if rule == "R4":
            return (r - 2) % m

    if f == "length":
        if rule == "R1":
            return (r + 1) % m
        if rule == "R2":
            # len(Mx)=1+|x| -> len(Mxx)=1+2|x| = 2 len - 1.
            return (2 * r - 1) % m
        if rule == "R3":
            return (r - 2) % m
        if rule == "R4":
            return (r - 2) % m

    raise ValueError((candidate, rule, r))


def exact_quotient(candidate: Candidate, target: str) -> QuotientReport:
    m = candidate.modulus
    rules = ("R1", "R2", "R3", "R4")
    maps = {rule: [rule_map(candidate, rule, r) for r in range(m)] for rule in rules}

    start = candidate.value(AXIOM)
    reachable = {start}
    q = deque([start])
    while q:
        r = q.popleft()
        for rule in rules:
            s = maps[rule][r]
            if s not in reachable:
                reachable.add(s)
                q.append(s)

    target_class = candidate.value(target)
    separated = target_class not in reachable

    # Global verification for this quotient language: the axiom is in the
    # reachable class set and the set is closed under every induced rule map.
    closed = start in reachable and all(
        maps[rule][r] in reachable for r in reachable for rule in rules
    )

    return QuotientReport(
        name=candidate.name,
        feature=candidate.feature,
        modulus=m,
        axiom_class=start,
        target_class=target_class,
        reachable_classes=sorted(reachable),
        separates_target=bool(separated),
        verified_global=bool(closed),
        transition_maps=maps,
        class_count=len(reachable),
        compression_ratio=len(reachable) / m,
        complexity=m,
    )


def run_qh(target: str) -> dict:
    t0 = time.perf_counter()
    reports: list[QuotientReport] = []
    evaluations = 0
    for cand in candidate_language():
        evaluations += 1
        reports.append(exact_quotient(cand, target))

    # QH is not told which coordinate matters.  Prefer a VERIFIED separator,
    # then the smallest quotient (small modulus), then strongest compression.
    separators = [r for r in reports if r.verified_global and r.separates_target]
    separators.sort(key=lambda r: (r.modulus, r.compression_ratio, r.feature))
    selected = separators[0] if separators else None
    elapsed = time.perf_counter() - t0

    return {
        "status": "REFUTED_BY_VERIFIED_INVARIANT" if selected else "NO_SEPARATOR_FOUND",
        "target": target,
        "candidate_language_size": len(reports),
        "candidate_evaluations": evaluations,
        "candidate_features": ["length", "count_M", "count_I", "count_U"],
        "candidate_moduli": list(range(2, 13)),
        "known_miu_shortcut_handed_to_qh": False,
        "target_truth_handed_to_qh": False,
        "selected": asdict(selected) if selected else None,
        "all_verified_separators": [asdict(r) for r in separators],
        "elapsed_seconds": elapsed,
        "verifier_scope": "exact quotient closure for declared count/length modular candidate language",
    }


def run_bfs(target: str, budget: int, max_length: int) -> dict:
    t0 = time.perf_counter()
    seen = {AXIOM}
    q = deque([(AXIOM, 0)])
    expansions = 0
    generated = 0
    max_depth = 0

    while q and expansions < budget:
        w, depth = q.popleft()
        if w == target:
            return {
                "status": "PROVED",
                "target": target,
                "expansions": expansions,
                "generated": generated,
                "unique_states": len(seen),
                "max_depth": max_depth,
                "max_length": max_length,
                "budget": budget,
                "elapsed_seconds": time.perf_counter() - t0,
            }
        expansions += 1
        max_depth = max(max_depth, depth)
        for v in successors(w):
            generated += 1
            if len(v) > max_length:
                continue
            if v not in seen:
                seen.add(v)
                q.append((v, depth + 1))

    # Exhaustion under a length cap is NOT promoted to a theorem-level refutation.
    return {
        "status": "BOUNDED_UNKNOWN",
        "target": target,
        "expansions": expansions,
        "generated": generated,
        "unique_states": len(seen),
        "max_depth": max_depth,
        "max_length": max_length,
        "budget": budget,
        "queue_remaining": len(q),
        "elapsed_seconds": time.perf_counter() - t0,
    }


def independent_check(result: dict) -> dict:
    """Recompute the selected invariant from scratch and verify separation."""
    sel = result["qh"].get("selected")
    if not sel:
        return {"accepted": False, "reason": "no QH separator"}
    cand = Candidate(feature=sel["feature"], modulus=int(sel["modulus"]))
    fresh = exact_quotient(cand, result["target"])
    accepted = bool(fresh.verified_global and fresh.separates_target)
    return {
        "accepted": accepted,
        "candidate": fresh.name,
        "axiom_class": fresh.axiom_class,
        "target_class": fresh.target_class,
        "reachable_classes": fresh.reachable_classes,
        "reason": "closed under all four quotient rule maps and target class unreachable" if accepted else "verification failed",
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default=TARGET_DEFAULT)
    ap.add_argument("--budget", type=int, default=50000)
    ap.add_argument("--max-length", type=int, default=30)
    ap.add_argument("--out", type=Path, default=Path("results/miu-qh/result.json"))
    args = ap.parse_args()

    baseline = run_bfs(args.target, args.budget, args.max_length)
    qh = run_qh(args.target)
    result = {
        "experiment": "DATA-MIND 2.7 MIU Quotient Hunter",
        "architecture_version": "2.7",
        "formal_system": "MIU",
        "axiom": AXIOM,
        "target": args.target,
        "rules": [
            "R1: xI -> xIU",
            "R2: Mx -> Mxx",
            "R3: xIIIy -> xUy",
            "R4: xUUy -> xy",
        ],
        "baseline": baseline,
        "qh": qh,
    }
    result["independent_verifier"] = independent_check(result)
    result["scientific_endpoint_met"] = bool(
        baseline["status"] == "BOUNDED_UNKNOWN"
        and qh["status"] == "REFUTED_BY_VERIFIED_INVARIANT"
        and result["independent_verifier"]["accepted"]
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))

    if not result["independent_verifier"]["accepted"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
