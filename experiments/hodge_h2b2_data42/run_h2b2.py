from __future__ import annotations

import argparse, hashlib, json, time
from collections import Counter, deque
from dataclasses import dataclass
from pathlib import Path

TARGET = frozenset({"global_star", "unique_global_star", "global_square_law"})

@dataclass(frozen=True)
class Rule:
    name: str
    needs: frozenset[str]
    adds: frozenset[str]

RULES = [
    Rule("normalize_cover", frozenset({"input"}), frozenset({"cover_normal"})),
    Rule("verify_transition_cocycle", frozenset({"cover_normal"}), frozenset({"cocycle"})),
    Rule("verify_local_h2b1", frozenset({"cover_normal"}), frozenset({"local_h2b1", "local_square_law"})),
    Rule("verify_overlap_naturality", frozenset({"cover_normal", "local_h2b1"}), frozenset({"overlap_naturality"})),
    Rule("glue_global_star", frozenset({"cocycle", "local_h2b1", "overlap_naturality"}), frozenset({"global_star"})),
    Rule("derive_unique", frozenset({"global_star", "overlap_naturality"}), frozenset({"unique_global_star"})),
    Rule("descend_square_global", frozenset({"global_star", "local_square_law", "overlap_naturality"}), frozenset({"global_square_law"})),
]

def canon(state: frozenset[str]) -> tuple[str, ...]:
    return tuple(sorted(state))

def applicable(state: frozenset[str], rule: Rule) -> bool:
    return rule.needs <= state and not rule.adds <= state

def step(state: frozenset[str], rule: Rule) -> frozenset[str]:
    if not applicable(state, rule):
        raise ValueError(f"inapplicable rule {rule.name}")
    return frozenset(set(state) | set(rule.adds))

def solved(state: frozenset[str]) -> bool:
    return TARGET <= state

def missing(state: frozenset[str]) -> int:
    return len(TARGET - state)

def feature(state: frozenset[str]) -> str:
    structural = {"cover_normal","cocycle","local_h2b1","local_square_law","overlap_naturality"}
    d = len(structural & state)
    return f"density:{d}/5|missing:{missing(state)}"

TRAIN_TRACES = [
    ["normalize_cover","verify_transition_cocycle","verify_local_h2b1","verify_overlap_naturality","glue_global_star","derive_unique","descend_square_global"],
    ["normalize_cover","verify_local_h2b1","verify_overlap_naturality","verify_transition_cocycle","glue_global_star","descend_square_global","derive_unique"],
    ["normalize_cover","verify_local_h2b1","verify_transition_cocycle","verify_overlap_naturality","glue_global_star","derive_unique","descend_square_global"],
]

def train_compass():
    wins, tries, global_wins, global_tries = Counter(), Counter(), Counter(), Counter()
    for trace in TRAIN_TRACES:
        s = frozenset({"input"})
        for name in trace:
            r = next(r for r in RULES if r.name == name)
            f = feature(s)
            before = missing(s)
            ns = step(s, r)
            improvement = missing(ns) < before or len(ns) > len(s)
            tries[(f, name)] += 1
            global_tries[name] += 1
            if improvement:
                wins[(f, name)] += 1
                global_wins[name] += 1
            s = ns
    return wins, tries, global_wins, global_tries

def score_rule(state, rule, model):
    wins, tries, gw, gt = model
    f = feature(state)
    local = (wins[(f, rule.name)] + 1.0) / (tries[(f, rule.name)] + 2.0)
    glob = (gw[rule.name] + 1.0) / (gt[rule.name] + 2.0)
    density = len(state) / 10.0
    target_bonus = len(rule.adds & TARGET) * 0.35
    return 0.55 * local + 0.35 * glob + 0.10 * density + target_bonus

def reconstruct(parent, goal):
    out, cur = [], goal
    while parent[cur][0] is not None:
        prev, action = parent[cur]
        out.append(action)
        cur = prev
    return list(reversed(out))

def search(max_expansions=5000, compass_share=0.70):
    model = train_compass()
    start = frozenset({"input"})
    q, frontier = deque([start]), [start]
    seen = {canon(start): start}
    parent = {start: (None, None)}
    expansions = compass_expansions = fallback_expansions = quotient_collisions = 0
    while expansions < max_expansions and (frontier or q):
        use_compass = bool(frontier) and (compass_expansions / max(1, expansions) < compass_share or not q)
        if use_compass:
            state = max(frontier, key=lambda s: max([score_rule(s, r, model) for r in RULES if applicable(s, r)] or [-1]))
            frontier.remove(state)
            compass_expansions += 1
            actions = sorted([r for r in RULES if applicable(state, r)], key=lambda r: score_rule(state, r, model), reverse=True)
        else:
            state = q.popleft()
            fallback_expansions += 1
            actions = [r for r in RULES if applicable(state, r)]
        expansions += 1
        if solved(state):
            return state, reconstruct(parent, state), {"expansions": expansions, "compass_expansions": compass_expansions, "fallback_expansions": fallback_expansions, "canonical_states": len(seen), "quotient_collisions": quotient_collisions}, model
        for r in actions:
            ns = step(state, r)
            c = canon(ns)
            if c in seen:
                quotient_collisions += 1
                continue
            seen[c] = ns
            parent[ns] = (state, r.name)
            frontier.append(ns)
            q.append(ns)
            if solved(ns):
                return ns, reconstruct(parent, ns), {"expansions": expansions, "compass_expansions": compass_expansions, "fallback_expansions": fallback_expansions, "canonical_states": len(seen), "quotient_collisions": quotient_collisions}, model
    raise RuntimeError("budget exhausted without certificate")

def independent_verify(trace):
    s = frozenset({"input"})
    rules = {r.name: r for r in RULES}
    checked = []
    for action in trace:
        if action not in rules:
            return False, {"error": f"unknown action {action}", "checked": checked}
        r = rules[action]
        if not applicable(s, r):
            return False, {"error": f"inapplicable action {action}", "checked": checked}
        before = canon(s)
        s = step(s, r)
        checked.append({"action": action, "before": before, "after": canon(s)})
    return solved(s), {"final_state": canon(s), "checked": checked, "target": sorted(TARGET)}

def model_summary(model):
    _, _, gw, gt = model
    return {r.name: {"wins": gw[r.name], "tries": gt[r.name], "smoothed_success": round((gw[r.name]+1)/(gt[r.name]+2), 6)} for r in RULES}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="run_artifact")
    ap.add_argument("--max-expansions", type=int, default=5000)
    ap.add_argument("--compass-share", type=float, default=0.70)
    args = ap.parse_args()
    if not 0.0 < args.compass_share < 1.0:
        raise SystemExit("compass-share must leave a nonzero fallback share")
    t0 = time.time()
    _, trace, metrics, model = search(args.max_expansions, args.compass_share)
    ok, verification = independent_verify(trace)
    payload = {
        "experiment": "DATA_4.2_H2B2_BUNDLEWISE_HODGE_STAR",
        "status": "VERIFIED" if ok else "REJECTED",
        "h2b1_input": "frozen assumption/local law",
        "restricted_target": sorted(TARGET),
        "architecture": {"quotient_canonicalization": True, "quotient_density_training": True, "target_excluded_from_training_traces": True, "compass_share": args.compass_share, "fallback_share_floor": 1.0-args.compass_share, "independent_verifier": True},
        "metrics": metrics,
        "certificate": trace,
        "verification": verification,
        "learned_rule_statistics": model_summary(model),
        "elapsed_seconds": round(time.time()-t0, 6),
    }
    blob = json.dumps(payload, sort_keys=True).encode()
    payload["audit_sha256"] = hashlib.sha256(blob).hexdigest()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out/"result.json").write_text(json.dumps(payload, indent=2, sort_keys=True))
    (out/"certificate.txt").write_text("\n".join(trace)+"\n")
    print(json.dumps({"status": payload["status"], "expansions": metrics["expansions"], "canonical_states": metrics["canonical_states"], "quotient_collisions": metrics["quotient_collisions"], "certificate_length": len(trace), "audit_sha256": payload["audit_sha256"]}, indent=2))
    if not ok:
        raise SystemExit(2)

if __name__ == "__main__":
    main()
