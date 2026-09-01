#!/usr/bin/env python3
"""Read-only postmortem of the initial sgrpcl candidate ranking.

This diagnostic does not alter candidate scores, candidate selection, proof rules,
or verifier behavior. It wraps the frozen-education scorer only to report where
known proof references appear in the ordinary candidate ordering after the
experiment has already completed.
"""
from __future__ import annotations

import atexit
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ADAPTER = HERE / "data_mind_2_6_educated_ranker_adapter.py"
spec = importlib.util.spec_from_file_location("dm26_edu_diag", ADAPTER)
if spec is None or spec.loader is None:
    raise SystemExit(f"cannot load {ADAPTER}")
EDU = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = EDU
spec.loader.exec_module(EDU)

OUT = Path("results/sgrpcl-ranking-diagnostic.json")
records: list[dict] = []
seen: set[tuple[str, str]] = set()
ORIG = EDU.FrozenEducationRanker.score_candidates
WANTED = {"syl3an1", "mgmcl", "sgrpmgm"}


def pre_distance0(item) -> float:
    _lab, _ct, data = item
    e_hyps = data[2]
    token_burden = sum(max(0, len(stat) - 1) for _name, stat in e_hyps)
    return len(e_hyps) + 0.002 * min(250, token_burden)


def wrapped(self, goal_tree, items, legacy):
    out = ORIG(self, goal_tree, items, legacy)
    goal = " ".join(self._tokens(goal_tree))
    by_label = {str(item[0]): item for item in items}
    ordered = sorted(items, key=lambda item: (pre_distance0(item), -out.get(str(item[0]), 0.0), str(item[0])))
    positions = {str(item[0]): i + 1 for i, item in enumerate(ordered)}

    for lab in sorted(WANTED & set(by_label)):
        key = (goal, lab)
        if key in seen:
            continue
        seen.add(key)
        item = by_label[lab]
        learned = self.learned_score(goal_tree, item)
        pre = pre_distance0(item)
        row = {
            "goal": goal,
            "label": lab,
            "candidate_pool_size": len(items),
            "essential_hypotheses": len(item[2][2]),
            "pre_distance_rest0": pre,
            "legacy_score_before_education": float(legacy.get(lab, 0.0)),
            "learned_score": None if learned is None else float(learned),
            "combined_score": float(out.get(lab, 0.0)),
            "lexicographic_rank_within_this_pool": positions[lab],
            "candidates_with_strictly_lower_pre_distance": sum(pre_distance0(x) < pre for x in items),
            "candidates_with_equal_pre_distance": sum(abs(pre_distance0(x) - pre) < 1e-12 for x in items),
            "diagnostic_only": True,
        }
        records.append(row)
        print("POSTMORTEM_RANK " + json.dumps(row, sort_keys=True), flush=True)
    return out


EDU.FrozenEducationRanker.score_candidates = wrapped


def save() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"records": records, "diagnostic_only": True}, indent=2) + "\n", encoding="utf-8")


atexit.register(save)

if __name__ == "__main__":
    raise SystemExit(EDU.main())
