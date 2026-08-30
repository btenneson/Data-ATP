#!/usr/bin/env python3
"""DATA-MIND sgrpcl full-feature v2: shared newest architecture, adaptive 1.1.

Both DATA-MIND 1.0 and 1.1 now exercise the same current architectural shell:

* eight-agent P1/P2/R1/R2/I1/I2/C1/C2 pre-BANK deliberation;
* group-valued revision coordinates and inverse fallback;
* Counselor and Professor diagnostics;
* self-awareness / dissatisfaction telemetry;
* verifier sovereignty and proposal-only BANK semantics;
* the same reconstructed Predator 8.040 R3/I4 supervisory-rotation base.

The controlled difference is policy authority:

* DATA-MIND 1.0 is advisory-only.  The eight agents, Counselor, Professor, and
  revision machinery run and are logged, but the frozen supervisory strategy
  remains authoritative and online utility learning is disabled.
* DATA-MIND 1.1 enables online strategy-utility learning and permits the same
  deliberative architecture to override the legal high-level search strategy.

Thus new architecture is not withheld from 1.0; 1.1 tests whether granting the
architecture adaptive control improves search while the verifier remains
unchanged.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "data_mind_sgrpcl_full_feature.py"

spec = importlib.util.spec_from_file_location("data_mind_sgrpcl_v1", BASE_PATH)
if spec is None or spec.loader is None:
    raise SystemExit(f"cannot load base DATA-MIND adapter: {BASE_PATH}")
BASE = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = BASE
spec.loader.exec_module(BASE)

AGENTS = BASE.AGENTS
STRATEGIES = BASE.STRATEGIES
emit = BASE.emit
EventType = BASE.EventType


class SharedArchitectureController(BASE.DataMindController):
    """Run newest common architecture in both arms; grant control only to 1.1."""

    def __init__(self, version: str, supervisory, p8038, log, rotate_stale: int):
        super().__init__(version, supervisory, p8038, log, rotate_stale)
        if self.eight is None:
            self._install_eight_agent_controller()

    def _maybe_learn(self, stale: int) -> None:
        if self.last_stale is None or self.last_choice is None:
            return
        if self.version == "1.0":
            if stale < self.last_stale:
                outcome = "progress"
            elif stale > self.last_stale:
                outcome = "stagnation"
            else:
                outcome = "flat"
            emit(
                self.log,
                EventType.SELF_REPORT_FILED,
                "learning_observation_advisory_only",
                previous_strategy=self.last_choice,
                observed=outcome,
                utility_update_applied=False,
                policy_authority=False,
                verifier_authority=False,
            )
            return
        super()._maybe_learn(stale)

    def _shared_advisory_deliberation(
        self,
        base: str,
        stale: int,
        terminal_rejects: int,
        metrics: dict[str, float],
    ) -> str:
        """Run the full eight-agent shell but never override 1.0's base policy."""
        assert self.eight is not None and self.agent_vectors is not None
        self.latest_dissatisfaction = metrics["dissatisfaction"]
        state = {
            "V": 1,
            "stale": stale,
            "terminal_rejects": terminal_rejects,
            "dissatisfaction": self.latest_dissatisfaction,
            "base_strategy": base,
        }
        self.trajectory = (self.trajectory + [state])[-8:]
        trajectories = {a: tuple(self.trajectory) for a in AGENTS}
        vectors = {a: dict(self.agent_vectors[a]) for a in AGENTS}
        next_vectors, decisions = self.eight.step_all(trajectories, vectors)
        self.agent_vectors = next_vectors

        for agent in AGENTS:
            vec = next_vectors[agent]
            top = max(STRATEGIES, key=lambda s: (vec[s], s))
            d = decisions[agent]
            emit(
                self.log,
                EventType.SELF_REPORT_FILED,
                "agent_message",
                agent=agent,
                channel="shared_pre_bank_deliberation",
                proposed_strategy=top,
                revision_mode=d["mode"],
                diagnostic=d["D(T)"],
                threshold=d["threshold"],
                certified_math=False,
                policy_authority=False,
            )
            self.agent_message_count += 1

        if terminal_rejects > 250:
            advice = "terminal rejection pressure high; preserve diversity and challenge current basin"
        elif stale >= self.rotate_stale:
            advice = "ordinary strategy family is stale; favor a genuine escape regime"
        elif self.latest_dissatisfaction > 0.45:
            advice = "progress is weakening; compare alternate legal search regimes"
        else:
            advice = "continue local refinement while progress evidence remains adequate"
        emit(
            self.log,
            EventType.SELF_REPORT_FILED,
            "counselor_advice",
            advice=advice,
            authority="advisory_only",
            may_verify=False,
            may_override_policy=False,
        )
        self.counselor_events += 1

        if self.last_choice is not None:
            prior = self.last_stale if self.last_stale is not None else stale
            grade = "productive" if stale < prior else "needs_revision"
            emit(
                self.log,
                EventType.SELF_REPORT_FILED,
                "professor_review",
                previous_strategy=self.last_choice,
                evaluation=grade,
                authority="teaching_evaluation_only",
                may_verify=False,
                may_override_policy=False,
            )
            self.professor_events += 1

        mean = {
            s: sum(next_vectors[a][s] for a in AGENTS) / len(AGENTS)
            for s in STRATEGIES
        }
        scores = {s: mean[s] + (0.24 if s == base else 0.0) for s in STRATEGIES}
        advisory_choice = max(STRATEGIES, key=lambda s: (scores[s], s))
        emit(
            self.log,
            EventType.STRATEGY_OVERRIDE_PROPOSED,
            "eight_agent_consensus_advisory_only",
            base_strategy=base,
            proposed_strategy=advisory_choice,
            scores=scores,
            dissatisfaction=self.latest_dissatisfaction,
            policy_authority=False,
            override_executed=False,
            verifier_authority=False,
        )
        return base

    def choose(self, stale: int, terminal_rejects: int) -> str:
        stale = int(stale)
        terminal_rejects = int(terminal_rejects)
        base = self.supervisory(stale, terminal_rejects)

        bucket = (stale // 500, terminal_rejects // 50)
        if self.last_bucket == bucket and self.last_choice is not None:
            return self.last_choice

        self._maybe_learn(stale)
        metrics = self._metrics(stale, terminal_rejects)
        emit(
            self.log,
            EventType.SELF_REPORT_FILED,
            "self_awareness",
            architecture=f"DATA-MIND {self.version}",
            stale=stale,
            terminal_rejects=terminal_rejects,
            base_strategy=base,
            metrics=metrics,
            verifier_sovereign=True,
            eight_agent_shell_active=True,
            policy_adaptation_enabled=(self.version == "1.1"),
        )

        if self.version == "1.1":
            choice = self._one_one_deliberate(base, stale, terminal_rejects, metrics)
        else:
            choice = self._shared_advisory_deliberation(base, stale, terminal_rejects, metrics)

        self.last_bucket = bucket
        self.last_stale = stale
        self.last_base = base
        self.last_choice = choice
        return choice


# Base main resolves this global at runtime.
BASE.DataMindController = SharedArchitectureController


def _arg_value(flag: str) -> str | None:
    try:
        i = sys.argv.index(flag)
    except ValueError:
        return None
    return sys.argv[i + 1] if i + 1 < len(sys.argv) else None


def main() -> int:
    rc = int(BASE.main() or 0)
    summary_path = _arg_value("--summary")
    version = _arg_value("--version")
    if summary_path and Path(summary_path).exists():
        p = Path(summary_path)
        data: dict[str, Any] = json.loads(p.read_text(encoding="utf-8"))
        data.update({
            "shared_newest_architecture_enabled": True,
            "eight_agent_deliberation_enabled": True,
            "counselor_professor_enabled": True,
            "group_inverse_revision_shell_enabled": True,
            "self_awareness_control_telemetry_enabled": True,
            "verifier_gated_bank_semantics": True,
            "policy_adaptation_enabled": version == "1.1",
            "online_strategy_utility_learning_enabled": version == "1.1",
            "policy_override_authority_enabled": version == "1.1",
            "data_mind_1_0_advisory_only": version == "1.0",
            "controlled_difference": "1.1 may learn and override legal high-level search policy; 1.0 may not",
        })
        p.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print("CORRECTED_SHARED_ARCHITECTURE_SUMMARY")
        print(json.dumps(data, indent=2), flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
