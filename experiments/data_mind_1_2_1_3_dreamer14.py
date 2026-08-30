#!/usr/bin/env python3
"""DATA-MIND 1.2 / 1.3 with explicit Dreamer / Simulator 14.

Public versions:
  1.2 = exact-group adult control + Dreamer 14, no radical child authority.
  1.3 = same adult control + same Dreamer 14 + reversible inverse child trials.

Internally these reuse the tested 2.2/2.3 control mechanics. The public
version mapping is recorded explicitly in the transaction log and summary.
"""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
V2_PATH = HERE / "data_mind_2_2_2_3_actual_knob_controller_v2.py"
DREAMER_PATH = HERE / "dreamer14_sic_simulation.py"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


V2 = _load("data_mind_2x_v2_for_1x", V2_PATH)
DREAMER_MOD = _load("data_mind_dreamer14", DREAMER_PATH)
BASE = V2.BASE
KNOBS = V2.KNOBS
EventType = V2.EventType
emit = V2.emit
ORIGINAL_EXACT_SELFTEST = V2.exact_selftest

PUBLIC_TO_INTERNAL = {"1.2": "2.2", "1.3": "2.3"}
INTERNAL_TO_PUBLIC = {v: k for k, v in PUBLIC_TO_INTERNAL.items()}


class DreamerIntegratedController(V2.ExactGroupActualKnobController):
    """Exact 11D control plus an independent advisory Dreamer 14."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.public_version = INTERNAL_TO_PUBLIC[self.version]
        self.dreamer = DREAMER_MOD.Dreamer14(
            knobs=KNOBS,
            latent_eps=self.latent_eps,
            horizon=4,
            initial_awareness=(5.0, 5.0),
        )
        self.dreamer_advice_count = 0
        self.dreamer_local_adoptions = 0
        self.dreamer_inverse_forecasts = 0
        emit(
            self.log,
            EventType.SELF_REPORT_FILED,
            "dreamer14_initialized",
            public_version=self.public_version,
            internal_control_version=self.version,
            module=14,
            module_name="Dreamer / Simulator",
            awareness_initial={"c_D": 5.0, "i_D": 5.0},
            awareness_independent_of_other_modules=True,
            simulation_theory=(
                "bounded clocked quotient-capable error-calibrated "
                "counterfactual SIC simulation"
            ),
            advisory_only=True,
            may_change_live_knobs=False,
            may_verify=False,
            may_commit_bank=False,
        )

    def begin_agent(self, agent_name):
        super().begin_agent(agent_name)
        self.dreamer.begin_episode(agent_name)

    def sample(self, *, exp, live_rhat, stale, dup_rate, terminal_rejects,
               frontier_size, imagined_total, imagined_previous,
               remaining_budget):
        # The controls active before this sample generated the current real state.
        real_latent = dict(self.u)
        action = super().sample(
            exp=exp,
            live_rhat=live_rhat,
            stale=stale,
            dup_rate=dup_rate,
            terminal_rejects=terminal_rejects,
            frontier_size=frontier_size,
            imagined_total=imagined_total,
            imagined_previous=imagined_previous,
            remaining_budget=remaining_budget,
        )
        if self.last_control_exp != int(exp):
            return action

        quotient = self.dreamer.quotient_state(
            quality=self.last_quality,
            live_rhat=live_rhat,
            stale=stale,
            dup_rate=dup_rate,
            terminal_rejects=terminal_rejects,
            frontier_size=frontier_size,
            imagined_total=imagined_total,
        )
        self.dreamer.observe_real(
            exp=exp,
            latent=real_latent,
            quotient=quotient,
        )

        # Preserve the exact inverse when a child trial has just started.
        baseline = (
            dict(self.child_checkpoint_u or real_latent)
            if action == "START_CHILD" else dict(self.u)
        )
        advice = self.dreamer.recommend(
            current=baseline,
            quotient=quotient,
            adult_step=self.adult_step,
            include_inverse=True,
        )
        self.dreamer_advice_count += 1
        if advice.get("inverse") is not None:
            self.dreamer_inverse_forecasts += 1

        local = advice["local_best"]
        current = advice["current"]
        local_improvement = (
            float(current["risk_adjusted_score"])
            - float(local["risk_adjusted_score"])
        )

        # Dreamer proposes. The Adult may adopt a small local proposal, never
        # an inverse proposal. Child authority remains confined to 1.3.
        adopted = False
        adoption_reason = "advisory_only_no_change"
        if (
            action == "NONE"
            and local["counterfactual_label"].startswith("local:")
            and float(local["confidence"]) >= 0.60
            and local_improvement >= 0.01
            and float(local["control_distance"]) <= self.adult_step + 1e-12
        ):
            self._install_vector(dict(local["candidate"]))
            self.dreamer_local_adoptions += 1
            adopted = True
            adoption_reason = "adult_accepted_high_confidence_local_dream"

        emit(
            self.log,
            EventType.SELF_REPORT_FILED,
            "dreamer14_clocked_simulation_advice",
            public_version=self.public_version,
            expansion=int(exp),
            awareness={
                "c_D": self.dreamer.control_awareness,
                "i_D": self.dreamer.imagination_awareness,
                "independent": True,
            },
            current_witness=current,
            local_best_witness=local,
            inverse_witness=advice.get("inverse"),
            adult_adopted_local_advice=adopted,
            adult_adoption_reason=adoption_reason,
            child_triggered_by_dreamer=False,
            verifier_authority=False,
            bank_authority=False,
        )
        return action

    def summary(self):
        data = super().summary()
        data.update({
            "version": self.public_version,
            "internal_control_version": self.version,
            "dreamer14_enabled": True,
            "dreamer14_identical_between_1_2_and_1_3": True,
            "dreamer14": self.dreamer.summary(),
            "dreamer_advice_count": self.dreamer_advice_count,
            "dreamer_local_adoptions_by_adult": self.dreamer_local_adoptions,
            "dreamer_inverse_forecasts": self.dreamer_inverse_forecasts,
            "controlled_difference": (
                "1.3 alone has reversible group-inverse child authority; "
                "1.2 and 1.3 share the same adult controller and Dreamer 14"
            ),
        })
        return data


def dreamer_selftest(controller):
    ORIGINAL_EXACT_SELFTEST(controller)
    if controller.dreamer.initial_awareness != (5.0, 5.0):
        raise SystemExit("Dreamer awareness did not initialize at (5,5)")
    if controller.dreamer.control_awareness != 5.0:
        raise SystemExit("Dreamer c_D did not initialize at 5")
    if controller.dreamer.imagination_awareness != 5.0:
        raise SystemExit("Dreamer i_D did not initialize at 5")
    q = controller.dreamer.quotient_state(
        quality=1.2,
        live_rhat=1.0,
        stale=1000,
        dup_rate=0.1,
        terminal_rejects=0,
        frontier_size=100,
        imagined_total=1000,
    )
    advice = controller.dreamer.recommend(
        current=dict(controller.u),
        quotient=q,
        adult_step=controller.adult_step,
        include_inverse=True,
    )
    inv = advice["inverse"]
    if inv is None or inv["counterfactual_label"] != "group_inverse":
        raise SystemExit("Dreamer failed to produce inverse SIC simulation")
    if not inv["clock_map"] or inv["simulation_error_bound"] < 0:
        raise SystemExit("Dreamer clock/error witness invalid")
    if inv["may_change_live_knobs"] or inv["may_verify"] or inv["may_commit_bank"]:
        raise SystemExit("Dreamer crossed authority firewall")
    print(
        "[DATA-MIND 1.2/1.3 SELFTEST] Dreamer 14 clocked SIC simulation, "
        "(5,5) awareness, and authority firewall: passed"
    )


BASE.ActualKnobController = DreamerIntegratedController
BASE._selftest_controller = dreamer_selftest


def main():
    old_argv = sys.argv[:]
    try:
        if "--version" not in sys.argv:
            raise SystemExit("--version must be 1.2 or 1.3")
        ix = sys.argv.index("--version") + 1
        if ix >= len(sys.argv) or sys.argv[ix] not in PUBLIC_TO_INTERNAL:
            raise SystemExit("--version must be 1.2 or 1.3")
        public = sys.argv[ix]
        sys.argv[ix] = PUBLIC_TO_INTERNAL[public]
        os.environ["DATA_MIND_PUBLIC_VERSION"] = public
        return int(BASE.main() or 0)
    finally:
        sys.argv = old_argv


if __name__ == "__main__":
    raise SystemExit(main())
