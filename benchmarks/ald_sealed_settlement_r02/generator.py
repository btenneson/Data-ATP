from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path
from typing import List, Tuple

from common import Literal, Problem, shortest_ocean_distance, write_json

HORIZONS = [10, 25, 75, 100, 250, 750, 1000, 2500, 7500, 10000, 25000, 75000, 100000, 250000, 750000]
CLASSES = ["PROVED", "REFUTED", "INDEPENDENT"]


def lit(rng: random.Random, var: int) -> Literal:
    return Literal(var, rng.choice([True, False]))


def render(problem: Problem) -> str:
    lines: List[str] = ["% ALD sealed settlement instance; no answer-bearing metadata"]
    for name, l in problem.units:
        lines.append(f"fof({name}, axiom, {l.tptp()}).")
    for name, a, b in problem.edges:
        lines.append(f"fof({name}, axiom, ({a.tptp()} => {b.tptp()})).")
    lines.append(f"fof(goal, conjecture, {problem.goal.tptp()}).")
    return "\n".join(lines) + "\n"


def build_instance(horizon: int, seed: int, truth: str) -> Tuple[Problem, dict]:
    rng = random.Random(seed)
    next_var = 1

    # Opaque signed-literal backbone. Each backbone variable is fresh, so the
    # designated Ocean modus-ponens distance is exactly the graph distance.
    backbone = [lit(rng, i) for i in range(next_var, next_var + horizon + 1)]
    next_var += horizon + 1
    units = [("u0", backbone[0])]
    edges: List[Tuple[str, Literal, Literal]] = []
    for i in range(horizon):
        edges.append((f"e{i:07d}", backbone[i], backbone[i + 1]))

    # Goal polarity is randomized independently of the settlement class.
    goal_var = next_var
    next_var += 1
    goal = lit(rng, goal_var)

    if truth == "PROVED":
        endpoint = goal
        edges[-1] = (edges[-1][0], edges[-1][1], endpoint)
        backbone[-1] = endpoint
    elif truth == "REFUTED":
        endpoint = goal.complement()
        edges[-1] = (edges[-1][0], edges[-1][1], endpoint)
        backbone[-1] = endpoint
    elif truth == "INDEPENDENT":
        # Keep the long anchored backbone as a size/depth distractor, while
        # placing the goal in an unanchored equivalence cycle. Both all-false
        # and all-true assignments on this free component satisfy the theory.
        free = [goal]
        for _ in range(3):
            free.append(lit(rng, next_var))
            next_var += 1
        for i in range(len(free)):
            a, b = free[i], free[(i + 1) % len(free)]
            edges.append((f"f{i:03d}", a, b))
            edges.append((f"fr{i:03d}", b, a))
    else:
        raise ValueError(truth)

    # Add dead spurs without creating a shorter path to the settlement literal.
    spur_count = max(3, min(50, horizon // 10 + 1))
    for j in range(spur_count):
        anchor_i = rng.randrange(0, max(1, horizon))
        a = backbone[anchor_i]
        s1 = lit(rng, next_var); next_var += 1
        s2 = lit(rng, next_var); next_var += 1
        edges.append((f"s{j:04d}a", a, s1))
        edges.append((f"s{j:04d}b", s1, s2))

    rng.shuffle(edges)
    problem = Problem(units=units, edges=edges, goal=goal)

    d_goal = shortest_ocean_distance(problem, goal)
    d_not_goal = shortest_ocean_distance(problem, goal.complement())
    if truth == "PROVED" and d_goal != horizon:
        raise AssertionError((truth, horizon, d_goal))
    if truth == "REFUTED" and d_not_goal != horizon:
        raise AssertionError((truth, horizon, d_not_goal))
    if truth == "INDEPENDENT" and (d_goal is not None or d_not_goal is not None):
        raise AssertionError((truth, d_goal, d_not_goal))

    meta = {
        "truth": truth,
        "ocean_horizon": horizon if truth in {"PROVED", "REFUTED"} else None,
        "size_parameter": horizon,
        "seed": seed,
        "goal": goal.tptp(),
        "distance_goal": d_goal,
        "distance_neg_goal": d_not_goal,
    }
    return problem, meta


def campaign(out: Path, smoke: bool = False) -> None:
    public = out / "public" / "instances"
    sealed = out / "sealed"
    public.mkdir(parents=True, exist_ok=True)
    sealed.mkdir(parents=True, exist_ok=True)

    horizons = [10, 25, 75] if smoke else HORIZONS
    manifest = {"version": "R02", "instances": []}
    public_manifest = {"version": "R02", "instances": []}

    serial = 0
    for horizon in horizons:
        for truth in CLASSES:
            for family in range(3):
                seed_material = f"R02|{horizon}|{truth}|{family}|sealed-v1"
                seed = int(hashlib.sha256(seed_material.encode()).hexdigest()[:16], 16)
                problem, meta = build_instance(horizon, seed, truth)
                text = render(problem)
                digest = hashlib.sha256(text.encode()).hexdigest()
                opaque = digest[:20] + ".p"
                (public / opaque).write_text(text, encoding="utf-8")
                manifest["instances"].append({"id": opaque, "sha256": digest, **meta})
                public_manifest["instances"].append({"id": opaque, "sha256": digest})
                serial += 1

    write_json(sealed / "ground_truth.json", manifest)
    write_json(out / "public" / "manifest.json", public_manifest)
    root = hashlib.sha256((out / "public" / "manifest.json").read_bytes()).hexdigest()
    (out / "public" / "SEAL_SHA256.txt").write_text(root + "\n", encoding="utf-8")
    print(json.dumps({"instances": serial, "seal_sha256": root, "out": str(out)}))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    campaign(Path(args.out), smoke=args.smoke)


if __name__ == "__main__":
    main()
