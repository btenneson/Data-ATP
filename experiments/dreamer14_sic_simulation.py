#!/usr/bin/env python3
"""Dreamer / Simulator 14 for DATA-MIND.

A bounded, clocked, quotient-capable, error-calibrated simulator of
counterfactual SIC trajectories. Dreamer is advisory only: it may forecast
and recommend, but it cannot mutate live controls, verify a proof, or commit
to the BANK.
"""
from __future__ import annotations

from collections import deque
import math


def _clip(x, lo, hi):
    return min(hi, max(lo, float(x)))


def _l2_delta(a, b, keys):
    return math.sqrt(sum((float(a[k]) - float(b[k])) ** 2 for k in keys))


class Dreamer14:
    """Bounded clocked simulator over a quotient of the live SIC state."""

    def __init__(self, *, knobs, latent_eps=1e-6, horizon=4, history=32,
                 initial_awareness=(5.0, 5.0)):
        self.knobs = tuple(knobs)
        self.latent_eps = float(latent_eps)
        self.horizon = max(1, int(horizon))
        self.control_awareness = float(initial_awareness[0])
        self.imagination_awareness = float(initial_awareness[1])
        self.initial_awareness = tuple(map(float, initial_awareness))
        self.real_history = deque(maxlen=max(8, int(history)))
        self.sensitivity = {k: 0.0 for k in self.knobs}
        self.model_error_ema = 0.10
        self.lipschitz_control = 1.0
        self.lipschitz_state = 1.0
        self.calibration_count = 0
        self.simulation_count = 0
        self.prediction_error_count = 0
        self.last_agent = None
        self.last_witness = None
        self.last_inverse_witness = None
        self.last_local_witness = None
        self._pending_predictions = deque(maxlen=24)

    def begin_episode(self, agent_name):
        self.last_agent = str(agent_name)

    @staticmethod
    def quotient_state(*, quality, live_rhat, stale, dup_rate,
                       terminal_rejects, frontier_size, imagined_total):
        return {
            "quality": float(quality),
            "rhat": float(live_rhat),
            "stale": math.log1p(max(0, int(stale)) / 1000.0),
            "dup": _clip(float(dup_rate), 0.0, 1.0),
            "dv_pressure": math.log1p(max(0, int(terminal_rejects))),
            "frontier_pressure": math.log1p(max(0, int(frontier_size))) / 20.0,
            "imagination_pressure": math.log1p(max(0, int(imagined_total))) / 30.0,
        }

    @staticmethod
    def _state_distance(a, b):
        keys = ("rhat", "stale", "dup", "dv_pressure",
                "frontier_pressure", "imagination_pressure")
        return math.sqrt(sum((float(a[k]) - float(b[k])) ** 2 for k in keys))

    def observe_real(self, *, exp, latent, quotient):
        rec = {
            "exp": int(exp),
            "latent": {k: float(latent[k]) for k in self.knobs},
            "quotient": {k: float(v) for k, v in quotient.items()},
        }
        if self.real_history:
            prev = self.real_history[-1]
            du = {k: rec["latent"][k] - prev["latent"][k] for k in self.knobs}
            n2 = sum(v * v for v in du.values())
            n = math.sqrt(n2)
            dq = rec["quotient"]["quality"] - prev["quotient"]["quality"]
            ds = self._state_distance(rec["quotient"], prev["quotient"])
            if n > 1e-12:
                self.lipschitz_control = _clip(
                    max(0.97 * self.lipschitz_control, abs(dq) / n), 0.01, 1e4
                )
                for k in self.knobs:
                    if abs(du[k]) > 1e-12:
                        p = dq * du[k] / (n2 + 1e-12)
                        self.sensitivity[k] = 0.85 * self.sensitivity[k] + 0.15 * p
            if ds > 1e-12:
                self.lipschitz_state = _clip(
                    max(0.97 * self.lipschitz_state, abs(dq) / ds), 0.01, 20.0
                )
            if self._pending_predictions:
                closest = min(
                    self._pending_predictions,
                    key=lambda p: _l2_delta(p["candidate"], rec["latent"], self.knobs),
                )
                if _l2_delta(closest["candidate"], rec["latent"], self.knobs) <= 0.08:
                    err = abs(float(closest["predicted_quality"]) - rec["quotient"]["quality"])
                    self.model_error_ema = 0.90 * self.model_error_ema + 0.10 * err
                    self.prediction_error_count += 1
            self.calibration_count += 1
            self._update_awareness()
        self.real_history.append(rec)

    def _update_awareness(self):
        experience = math.tanh(self.calibration_count / 20.0)
        reliability = math.exp(-min(5.0, self.model_error_ema))
        stability = math.exp(-max(0.0, self.lipschitz_state - 1.0) / 4.0)
        self.imagination_awareness = _clip(
            5.0 + 2.0 * experience + 1.5 * (reliability - 0.5)
            + 0.75 * (stability - 0.5), 0.0, 10.0
        )
        overhead_penalty = math.tanh(max(0.0, self.average_clock_overhead() - 4.0) / 4.0)
        self.control_awareness = _clip(
            5.0 + 1.5 * experience + 1.25 * (reliability - 0.5)
            - overhead_penalty, 0.0, 10.0
        )

    def average_clock_overhead(self):
        return 1.0 if not self.last_witness else float(
            self.last_witness.get("clock_overhead_ratio", 1.0)
        )

    def _temporal_trend(self):
        if len(self.real_history) < 4:
            return 0.0
        q = [float(r["quotient"]["quality"]) for r in list(self.real_history)[-4:]]
        return (q[-1] - q[0]) / max(1, len(q) - 1)

    def _clock_increment(self, candidate):
        ks = [k for k in ("imagine_top", "beam", "branch_cap") if k in candidate]
        load = sum(float(candidate[k]) for k in ks) / len(ks) if ks else 0.5
        return 1.0 + 2.0 * load

    def simulate(self, *, current, candidate, quotient, label):
        delta = {k: float(candidate[k]) - float(current[k]) for k in self.knobs}
        dist = math.sqrt(sum(v * v for v in delta.values()))
        effect = sum(self.sensitivity[k] * delta[k] for k in self.knobs)
        trend = self._temporal_trend()
        predicted = float(quotient["quality"])
        error = 0.0
        inc = self._clock_increment(candidate)
        clock = []
        for h in range(1, self.horizon + 1):
            damp = 1.0 / h
            predicted += effect * damp + trend * 0.35 * damp
            error = (
                min(self.lipschitz_state, 2.5) * error
                + self.model_error_ema
                + self.lipschitz_control * dist / self.horizon
            )
            clock.append(h * inc)
        score = predicted + error
        conf = _clip(math.exp(-min(20.0, error)) / (1.0 + dist), 0.0, 1.0)
        overhead = clock[-1] / self.horizon
        w = {
            "module": 14,
            "module_name": "Dreamer / Simulator",
            "simulation_kind": "bounded_clocked_counterfactual_SIC",
            "counterfactual_label": str(label),
            "candidate": {k: float(candidate[k]) for k in self.knobs},
            "horizon": self.horizon,
            "clock_map": clock,
            "clock_overhead_ratio": overhead,
            "quotient_state": dict(quotient),
            "encoding": "control-relevant quotient observables",
            "predicted_quality": predicted,
            "simulation_error_bound": error,
            "lipschitz_control": self.lipschitz_control,
            "lipschitz_state": self.lipschitz_state,
            "model_error_ema": self.model_error_ema,
            "risk_adjusted_score": score,
            "confidence": conf,
            "control_distance": dist,
            "awareness": {
                "c_D": self.control_awareness,
                "i_D": self.imagination_awareness,
                "initial": list(self.initial_awareness),
                "independent_of_other_modules": True,
            },
            "simulated_halt_is_not_real_halt": True,
            "may_change_live_knobs": False,
            "may_verify": False,
            "may_commit_bank": False,
            "meta_simulation_depth": 0,
        }
        self.simulation_count += 1
        self.last_witness = w
        self._pending_predictions.append({
            "candidate": dict(w["candidate"]),
            "predicted_quality": float(predicted),
        })
        return w

    def candidate_set(self, *, current, adult_step, include_inverse=True):
        out = [("current", dict(current))]
        d = max(0.001, min(float(adult_step), 0.10)) * 0.5
        for k in self.knobs:
            for sign, tag in ((-1.0, "minus"), (1.0, "plus")):
                v = dict(current)
                v[k] = _clip(
                    float(v[k]) + sign * d,
                    self.latent_eps,
                    1.0 - self.latent_eps,
                )
                out.append((f"local:{k}:{tag}", v))
        if include_inverse:
            out.append((
                "group_inverse",
                {k: 1.0 - float(current[k]) for k in self.knobs},
            ))
        return out

    def recommend(self, *, current, quotient, adult_step, include_inverse=True):
        ws = [
            self.simulate(current=current, candidate=c, quotient=quotient, label=l)
            for l, c in self.candidate_set(
                current=current,
                adult_step=adult_step,
                include_inverse=include_inverse,
            )
        ]
        cw = next(w for w in ws if w["counterfactual_label"] == "current")
        local = [w for w in ws if w["counterfactual_label"].startswith("local:")]
        lb = min(local, key=lambda w: w["risk_adjusted_score"]) if local else cw
        inv = next(
            (w for w in ws if w["counterfactual_label"] == "group_inverse"), None
        )
        self.last_local_witness = lb
        self.last_inverse_witness = inv
        return {
            "current": cw,
            "local_best": lb,
            "inverse": inv,
            "all_count": len(ws),
            "dreamer_has_advisory_authority_only": True,
        }

    def summary(self):
        return {
            "module": 14,
            "module_name": "Dreamer / Simulator",
            "architecture": "bounded clocked quotient-capable error-calibrated SIC simulator",
            "awareness_initial": list(self.initial_awareness),
            "awareness_current": {
                "c_D": self.control_awareness,
                "i_D": self.imagination_awareness,
            },
            "awareness_independent_of_other_modules": True,
            "simulation_count": self.simulation_count,
            "calibration_count": self.calibration_count,
            "prediction_error_count": self.prediction_error_count,
            "model_error_ema": self.model_error_ema,
            "lipschitz_control": self.lipschitz_control,
            "lipschitz_state": self.lipschitz_state,
            "horizon": self.horizon,
            "clocked_simulation": True,
            "quotient_simulation": True,
            "simulation_witnesses": True,
            "simulated_halt_is_not_real_halt": True,
            "may_change_live_knobs": False,
            "may_verify": False,
            "may_commit_bank": False,
            "last_local_witness": self.last_local_witness,
            "last_inverse_witness": self.last_inverse_witness,
        }
