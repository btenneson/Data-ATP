#!/usr/bin/env python3
"""DATA-MIND 2.6 integrated semigroup controller.

Adds an above-creativity module controller to the existing 2.6-era Metamath
stack. The eleven R3/I4 knobs remain internal to Creativity. Module gains
scale module proposals, not verifier/BANK authority and not the meaning of the
creativity coordinates.

Tunable modules in this experiment:
  * creativity: the existing 11D adult local optimizer;
  * mathematician: persistent learned shortcut proposals;
  * qh: structural Quotient Hunter guidance from live goal shapes;
  * revision: sensitivity of the existing Child/inverse fallback trigger.

Hard/non-tunable structure:
  * Metamath proof rules and certificate validity;
  * external verifier sovereignty;
  * BANK admission gate and transaction/provenance logging.

Every tunable module begins at gain 1.0. Adaptive runs use one-at-a-time
positive probes and ternary {-1,0,+1} outcomes to retain, revert, or reverse a
module-gain move. Neutral-control runs keep all gains exactly 1.0.
"""
from __future__ import annotations

from collections import Counter, deque
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
import importlib.util
import json
import math
from pathlib import Path
import statistics
import sys
from typing import Any

HERE = Path(__file__).resolve().parent
DM24_PATH = HERE / "data_mind_2_4_mathematician_shortcuts.py"
spec = importlib.util.spec_from_file_location("data_mind_24_for_26_integrated", DM24_PATH)
if spec is None or spec.loader is None:
    raise SystemExit(f"cannot load {DM24_PATH}")
DM24 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = DM24
spec.loader.exec_module(DM24)

EventType = DM24.EventType
emit = DM24.emit
KNOBS = DM24.KNOBS
MODULES = ("creativity", "mathematician", "qh", "revision")


@dataclass(frozen=True, slots=True)
class IntegratedConfig:
    module_ledger: Path
    module_adaptation_enabled: bool = True
    module_probe_log_step: float = 0.12
    module_quality_epsilon: float = 0.01
    module_log_bound: float = 1.0
    module_probe_every: int = 1
    qh_min_samples: int = 18
    qh_min_abs_corr: float = 0.25
    qh_step: float = 0.006


_ICFG: IntegratedConfig | None = None
_LAST_CONTROLLER: "Integrated26Controller | None" = None


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(row, sort_keys=True, separators=(",", ":"), default=str) + "\n")


def finite(x: Any) -> bool:
    return isinstance(x, (int, float)) and math.isfinite(float(x))


def corr(xs: list[float], ys: list[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 3:
        return 0.0
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    vx = sum(x * x for x in dx)
    vy = sum(y * y for y in dy)
    if vx <= 1e-18 or vy <= 1e-18:
        return 0.0
    return sum(a * b for a, b in zip(dx, dy)) / math.sqrt(vx * vy)


class Integrated26Controller(DM24.MathematicianController):
    architecture_version = "2.6"

    def __init__(self, *args, **kwargs):
        global _LAST_CONTROLLER
        if _ICFG is None:
            raise RuntimeError("DATA-MIND 2.6 integrated config missing")
        self.icfg = _ICFG
        self.module_log_gain = {m: 0.0 for m in MODULES}
        self.module_context: str | None = None
        self.module_probe_pending: dict[str, Any] | None = None
        self.module_probe_index = 0
        self.module_control_samples = 0
        self.module_diagnostics: list[dict[str, Any]] = []
        self.module_score_counts = {m: {-1: 0, 0: 0, 1: 0} for m in MODULES}
        self.module_confidence_sum = {m: 0.0 for m in MODULES}

        self.structure_recent: deque[dict[str, float]] = deque(maxlen=256)
        self.structure_token_frequency: Counter[str] = Counter()
        self.structure_observations = 0
        self.qh_history: list[dict[str, Any]] = []
        self.qh_selected: dict[str, Any] | None = None
        self.qh_candidate_evaluations = 0
        self.qh_discovery_rounds = 0
        self.qh_activations = 0
        self.qh_top_candidates: list[dict[str, Any]] = []

        super().__init__(*args, **kwargs)
        self.base_adult_failure_stale = int(self.adult_failure_stale)
        self._install_structural_observer()
        _LAST_CONTROLLER = self

        row = {
            "kind": "module_controller_start",
            "architecture_version": "2.6",
            "modules": list(MODULES),
            "initial_gains": self.module_gains(),
            "adaptation_enabled": self.icfg.module_adaptation_enabled,
            "hard_unweighted": ["verifier", "certificate_validity", "bank_gate", "provenance"],
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }
        append_jsonl(self.icfg.module_ledger, row)
        emit(
            self.log,
            EventType.SELF_REPORT_FILED,
            "module_controller_start",
            architecture_version="2.6",
            modules=list(MODULES),
            initial_gains=self.module_gains(),
            adaptation_enabled=self.icfg.module_adaptation_enabled,
            creativity_knobs_are_internal=True,
            verifier_weighted=False,
            bank_gate_weighted=False,
        )

    # ----- module gains -----
    def module_gain(self, module: str) -> float:
        return math.exp(float(self.module_log_gain[module]))

    def module_gains(self) -> dict[str, float]:
        return {m: self.module_gain(m) for m in MODULES}

    def _set_module_log_gain(self, module: str, value: float) -> None:
        b = abs(float(self.icfg.module_log_bound))
        self.module_log_gain[module] = max(-b, min(b, float(value)))

    @contextmanager
    def _module(self, name: str):
        old = self.module_context
        self.module_context = name
        try:
            yield
        finally:
            self.module_context = old

    def _bounded_move(self, key: str, delta: float) -> None:
        # The knob remains a Creativity coordinate. Other modules can only
        # propose a legal change to it; the central brain controls proposal gain.
        gain = self.module_gain(self.module_context) if self.module_context in MODULES else 1.0
        return super()._bounded_move(key, float(delta) * gain)

    def _adult_update(self, **kwargs) -> None:
        with self._module("creativity"):
            return super()._adult_update(**kwargs)

    def deliberate(self, **kwargs) -> None:
        with self._module("mathematician"):
            return super().deliberate(**kwargs)

    def _adult_failure(self, stale: int) -> bool:
        # Revision gain changes trigger sensitivity only. The Child inverse is
        # still the same full group inverse.
        g = max(0.25, min(4.0, self.module_gain("revision")))
        effective = max(1000, int(round(self.base_adult_failure_stale / g)))
        old = self.adult_failure_stale
        self.adult_failure_stale = effective
        try:
            return super()._adult_failure(stale)
        finally:
            self.adult_failure_stale = old

    # ----- structural QH observer -----
    def _install_structural_observer(self) -> None:
        comp = self.base6.COMP
        p8 = self.base6.P8
        original = comp.settlement_distance_hat
        controller = self

        def observed(goals, sub):
            value = original(goals, sub)
            try:
                controller._observe_goal_structure(goals, sub, p8)
            except Exception as exc:
                emit(
                    controller.log,
                    EventType.SELF_REPORT_FILED,
                    "qh_structure_observer_error",
                    error=repr(exc),
                    verifier_authority=False,
                )
            return value

        comp.settlement_distance_hat = observed

    @staticmethod
    def _stable_token(tok: str) -> bool:
        if len(tok) > 24:
            return False
        return sum(ch.isdigit() for ch in tok) <= 2

    def _observe_goal_structure(self, goals, sub, p8) -> None:
        if not goals:
            return
        lengths: list[int] = []
        uniques: list[int] = []
        token_counts: Counter[str] = Counter()
        for g, _slot, _hix in list(goals)[:6]:
            toks = [str(t) for t in p8.apply_sub(g, sub).tokens()]
            lengths.append(len(toks))
            uniques.append(len(set(toks)))
            for tok in toks:
                if self._stable_token(tok):
                    token_counts[tok] += 1
        if not lengths:
            return
        total = max(1, sum(token_counts.values()))
        entropy = 0.0
        for n in token_counts.values():
            p = n / total
            entropy -= p * math.log(max(p, 1e-12))
        row: dict[str, float] = {
            "goal_count": float(len(goals)),
            "mean_goal_len": float(sum(lengths) / len(lengths)),
            "mean_unique_tokens": float(sum(uniques) / len(uniques)),
            "token_entropy": float(entropy),
            "max_token_multiplicity": float(max(token_counts.values(), default=0)),
        }
        for tok, n in token_counts.items():
            row[f"tok::{tok}"] = float(n)
            self.structure_token_frequency[tok] += n
        self.structure_recent.append(row)
        self.structure_observations += 1

    def _structure_snapshot(self) -> dict[str, float] | None:
        if not self.structure_recent:
            return None
        rows = list(self.structure_recent)[-32:]
        base_keys = (
            "goal_count",
            "mean_goal_len",
            "mean_unique_tokens",
            "token_entropy",
            "max_token_multiplicity",
        )
        snap = {
            k: sum(float(r.get(k, 0.0)) for r in rows) / len(rows)
            for k in base_keys
        }
        for tok, _n in self.structure_token_frequency.most_common(10):
            key = f"tok::{tok}"
            snap[key] = sum(float(r.get(key, 0.0)) for r in rows) / len(rows)
        return snap

    @staticmethod
    def _candidate_value(desc: dict[str, Any], row: dict[str, float]) -> float:
        x = float(row.get(str(desc["key"]), 0.0))
        if desc["kind"] == "raw":
            return x
        m = int(desc["modulus"])
        r = int(desc["residue"])
        return 1.0 if int(round(x)) % m == r else 0.0

    def _candidate_language(self) -> list[dict[str, Any]]:
        if not self.qh_history:
            return []
        keys = sorted({k for row in self.qh_history for k in row["structure"]})
        base = [k for k in keys if not k.startswith("tok::")]
        toks = [
            f"tok::{t}"
            for t, _ in self.structure_token_frequency.most_common(10)
            if f"tok::{t}" in keys
        ]
        out: list[dict[str, Any]] = []
        for k in base:
            out.append({"name": k, "kind": "raw", "key": k, "complexity": 1})
        for k in base + toks:
            for m in range(2, 7):
                for r in range(m):
                    out.append({
                        "name": f"{k} mod {m} == {r}",
                        "kind": "mod_eq",
                        "key": k,
                        "modulus": m,
                        "residue": r,
                        "complexity": 2,
                    })
        return out

    def _fit_structural_qh(self) -> dict[str, Any] | None:
        rows = [r for r in self.qh_history if finite(r.get("live_rhat"))]
        n = len(rows)
        if n < self.icfg.qh_min_samples:
            return None
        split = max(10, int(0.67 * n))
        if n - split < 5:
            return None
        train, valid = rows[:split], rows[split:]
        ytrain = [float(r["live_rhat"]) for r in train]
        yvalid = [float(r["live_rhat"]) for r in valid]
        fits = []
        self.qh_discovery_rounds += 1
        for desc in self._candidate_language():
            self.qh_candidate_evaluations += 1
            xt = [self._candidate_value(desc, r["structure"]) for r in train]
            xv = [self._candidate_value(desc, r["structure"]) for r in valid]
            ct, cv = corr(xt, ytrain), corr(xv, yvalid)
            if ct == 0.0 or cv == 0.0 or ct * cv <= 0.0:
                continue
            strength = min(abs(ct), abs(cv))
            score = strength - 0.01 * max(0, int(desc["complexity"]) - 1)
            fit = dict(desc)
            fit.update(
                score=score,
                train_corr=ct,
                validation_corr=cv,
                orientation=1 if ct > 0 else -1,
            )
            fits.append(fit)
        fits.sort(key=lambda f: (f["score"], -f["complexity"], f["name"]), reverse=True)
        self.qh_top_candidates = fits[:8]
        eligible = [
            f
            for f in fits
            if min(abs(f["train_corr"]), abs(f["validation_corr"]))
            >= self.icfg.qh_min_abs_corr
        ]
        return eligible[0] if eligible else None

    def _apply_qh_guidance(self, structure: dict[str, float]) -> None:
        best = self._fit_structural_qh()
        if best is not None:
            changed = self.qh_selected is None or self.qh_selected.get("name") != best.get("name")
            self.qh_selected = best
            if changed:
                emit(
                    self.log,
                    EventType.LOCAL_EVIDENCE_DETECTED,
                    "qh_structural_coordinate_selected",
                    agent="QH",
                    candidate=best,
                    candidate_language="live formula shape + generic modular residues",
                    target_proof_read=False,
                    theorem_authority=False,
                    verifier_authority=False,
                )
        if self.qh_selected is None:
            return

        desc = self.qh_selected
        current = self._candidate_value(desc, structure)
        history_vals = [
            self._candidate_value(desc, r["structure"])
            for r in self.qh_history[-40:]
        ]
        med = statistics.median(history_vals) if history_vals else current
        bad = ((current - med) * float(desc["orientation"])) > 0
        step = float(self.icfg.qh_step)
        if bad:
            proposal = {
                "explore_extra": +step,
                "diversity_bonus": +step,
                "goal_meta_weight": +0.75 * step,
                "rhat_weight": -0.50 * step,
                "imagine_top": -0.40 * step,
            }
            mode = "structural-escape"
        else:
            proposal = {
                "progress_weight": +0.65 * step,
                "solve_bonus": +0.55 * step,
                "rhat_weight": +0.50 * step,
                "explore_extra": -0.30 * step,
            }
            mode = "structural-exploit"

        before = dict(self.u)
        with self._module("qh"):
            for k, d in proposal.items():
                self._bounded_move(k, d)
        self._install_vector(self.u)
        delta = {k: float(self.u[k]) - float(before[k]) for k in KNOBS}
        if any(abs(v) > 1e-12 for v in delta.values()):
            self.qh_activations += 1
            emit(
                self.log,
                EventType.STRATEGY_OVERRIDE_EXECUTED,
                "qh_structural_guidance",
                agent="QH",
                mode=mode,
                candidate=desc,
                current_value=current,
                median_value=med,
                latent_delta=delta,
                module_gain=self.module_gain("qh"),
                search_control_only=True,
                verifier_authority=False,
            )

    # ----- ternary module diagnostics -----
    def _settle_module_probe(self, *, exp: int, live_rhat: float) -> None:
        p = self.module_probe_pending
        if p is None:
            return
        baseline_q = p.get("baseline_quality")
        quality_gain = (
            float(baseline_q) - float(self.last_quality)
            if finite(baseline_q) and finite(self.last_quality)
            else 0.0
        )
        baseline_r = p.get("baseline_rhat")
        rhat_gain = (
            float(baseline_r) - float(live_rhat)
            if finite(baseline_r) and finite(live_rhat)
            else 0.0
        )
        eps = float(self.icfg.module_quality_epsilon)
        if rhat_gain > 1e-12 or quality_gain > eps:
            score = 1
        elif quality_gain < -eps and rhat_gain <= 1e-12:
            score = -1
        else:
            score = 0
        confidence = min(
            1.0,
            abs(quality_gain) / max(4 * eps, 1e-9)
            + (0.5 if abs(rhat_gain) > 1e-12 else 0.0),
        )
        module = str(p["module"])
        baseline_u = float(p["baseline_log_gain"])
        probe = float(p["probe_step"])
        if score > 0:
            final_u = baseline_u + probe
        elif score < 0:
            final_u = baseline_u - probe * max(0.5, confidence)
        else:
            final_u = baseline_u
        self._set_module_log_gain(module, final_u)
        row = {
            "kind": "module_probe_outcome",
            "architecture_version": "2.6",
            "expansion": int(exp),
            "module": module,
            "ternary_score": score,
            "confidence": confidence,
            "quality_gain": quality_gain,
            "rhat_gain": rhat_gain,
            "baseline_gain": math.exp(baseline_u),
            "probed_gain": math.exp(baseline_u + probe),
            "final_gain": self.module_gain(module),
            "all_gains": self.module_gains(),
        }
        self.module_diagnostics.append(row)
        self.module_score_counts[module][score] += 1
        self.module_confidence_sum[module] += confidence
        append_jsonl(self.icfg.module_ledger, row)
        emit(
            self.log,
            EventType.LOCAL_EVIDENCE_DETECTED,
            "module_probe_outcome",
            **{k: v for k, v in row.items() if k != "kind"},
            claim_scope="local diagnostic evidence, not causal proof",
            verifier_authority=False,
        )
        self.module_probe_pending = None

    def _start_module_probe(self, *, exp: int, live_rhat: float) -> None:
        if not self.icfg.module_adaptation_enabled or self.module_probe_pending is not None:
            return
        if self.module_control_samples % max(1, int(self.icfg.module_probe_every)) != 0:
            return
        module = MODULES[self.module_probe_index % len(MODULES)]
        self.module_probe_index += 1
        baseline_u = float(self.module_log_gain[module])
        step = float(self.icfg.module_probe_log_step)
        self._set_module_log_gain(module, baseline_u + step)
        self.module_probe_pending = {
            "module": module,
            "baseline_log_gain": baseline_u,
            "probe_step": step,
            "baseline_quality": float(self.last_quality) if finite(self.last_quality) else None,
            "baseline_rhat": float(live_rhat) if finite(live_rhat) else None,
            "expansion": int(exp),
        }
        row = {
            "kind": "module_probe_started",
            "expansion": int(exp),
            "module": module,
            "baseline_gain": math.exp(baseline_u),
            "probed_gain": self.module_gain(module),
            "all_gains": self.module_gains(),
        }
        append_jsonl(self.icfg.module_ledger, row)
        emit(
            self.log,
            EventType.STRATEGY_OVERRIDE_PROPOSED,
            "module_probe_started",
            module=module,
            baseline_gain=row["baseline_gain"],
            probed_gain=row["probed_gain"],
            one_module_at_a_time=True,
            verifier_authority=False,
        )

    def sample(self, **kwargs) -> str:
        exp = int(kwargs["exp"])
        action = super().sample(**kwargs)
        if self.last_control_exp != exp:
            return action

        self.module_control_samples += 1
        live_rhat = float(kwargs["live_rhat"])
        structure = self._structure_snapshot()
        if structure is not None:
            self.qh_history.append(
                {"expansion": exp, "live_rhat": live_rhat, "structure": structure}
            )

        self._settle_module_probe(exp=exp, live_rhat=live_rhat)
        if action == "NONE" and self.mode == "ADULT" and structure is not None:
            self._apply_qh_guidance(structure)
            self._start_module_probe(exp=exp, live_rhat=live_rhat)
        return action

    def summary(self) -> dict[str, Any]:
        data = super().summary()
        data.update(
            {
                "architecture_version": "2.6",
                "solver": "DATA-MIND 2.6 integrated module controller + structural QH",
                "creativity_11d_knobs_internal_to_creativity": True,
                "module_level_controller_enabled": True,
                "module_adaptation_enabled": self.icfg.module_adaptation_enabled,
                "module_gain_parameterization": "g_i = exp(u_i); identity u_i=0 => g_i=1",
                "tunable_modules": list(MODULES),
                "final_module_gains": self.module_gains(),
                "module_control_samples": self.module_control_samples,
                "module_diagnostic_outcomes": len(self.module_diagnostics),
                "module_score_counts": self.module_score_counts,
                "module_confidence_sum": self.module_confidence_sum,
                "module_ledger": str(self.icfg.module_ledger),
                "verifier_module_gain": None,
                "bank_gate_module_gain": None,
                "correctness_spine_outside_optimizer": True,
                "structural_qh_enabled": True,
                "qh_structure_observations": self.structure_observations,
                "qh_control_observations": len(self.qh_history),
                "qh_candidate_evaluations": self.qh_candidate_evaluations,
                "qh_discovery_rounds": self.qh_discovery_rounds,
                "qh_selected_structural_coordinate": self.qh_selected,
                "qh_top_structural_candidates": self.qh_top_candidates,
                "qh_search_control_activations": self.qh_activations,
                "qh_candidate_language": "live formula-shape primitives and generic modular residue indicators",
                "qh_target_proof_read": False,
                "qh_theorem_authority": False,
                "revision_gain_changes_trigger_sensitivity_not_group_inverse_definition": True,
            }
        )
        return data


def arg_value(argv: list[str], flag: str, default: str | None = None) -> str | None:
    try:
        i = argv.index(flag)
    except ValueError:
        return default
    return argv[i + 1] if i + 1 < len(argv) else default


def main() -> int:
    global _ICFG
    import argparse

    custom = argparse.ArgumentParser(add_help=False)
    custom.add_argument("--module-ledger")
    custom.add_argument("--disable-module-adaptation", action="store_true")
    custom.add_argument("--module-probe-log-step", type=float, default=0.12)
    custom.add_argument("--module-quality-epsilon", type=float, default=0.01)
    custom.add_argument("--module-log-bound", type=float, default=1.0)
    custom.add_argument("--module-probe-every", type=int, default=1)
    custom.add_argument("--qh-min-samples", type=int, default=18)
    custom.add_argument("--qh-min-abs-corr", type=float, default=0.25)
    custom.add_argument("--qh-step", type=float, default=0.006)
    ours, remaining = custom.parse_known_args(sys.argv[1:])

    summary_raw = arg_value(remaining, "--summary")
    if not summary_raw:
        raise SystemExit("2.6 integrated adapter requires --summary")
    summary_path = Path(summary_raw).resolve()
    _ICFG = IntegratedConfig(
        module_ledger=(
            Path(ours.module_ledger).resolve()
            if ours.module_ledger
            else summary_path.with_name("module_diagnostics.jsonl")
        ),
        module_adaptation_enabled=not ours.disable_module_adaptation,
        module_probe_log_step=max(0.01, min(0.35, float(ours.module_probe_log_step))),
        module_quality_epsilon=max(1e-5, float(ours.module_quality_epsilon)),
        module_log_bound=max(0.1, min(2.0, float(ours.module_log_bound))),
        module_probe_every=max(1, int(ours.module_probe_every)),
        qh_min_samples=max(12, int(ours.qh_min_samples)),
        qh_min_abs_corr=max(0.05, min(0.95, float(ours.qh_min_abs_corr))),
        qh_step=max(0.001, min(0.02, float(ours.qh_step))),
    )

    DM24.MathematicianController = Integrated26Controller
    old = sys.argv[:]
    sys.argv = [old[0], *remaining]
    try:
        rc = int(DM24.main() or 0)
    finally:
        sys.argv = old

    if summary_path.exists():
        data = json.loads(summary_path.read_text(encoding="utf-8"))
        c = _LAST_CONTROLLER
        if c is not None:
            data.update(c.summary())
        data.update(
            {
                "architecture_version": "2.6",
                "solver": "DATA-MIND 2.6 integrated module controller + structural QH",
                "control_substrate": "2.4 Mathematician over exact-group 2.3 controller",
                "same_formal_calculus_as_control": True,
                "candidate_still_requires_independent_verification": True,
            }
        )
        summary_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
