#!/usr/bin/env python3
"""DATA-MIND 2.7 Quotient Discovery overlay for Metamath search.

This is the transfer experiment for the semigroup theorem ``sgrpcl``.
Unlike Ocean, Metamath search does not expose an exact reverse target graph.
Quotient Hunter therefore receives no theorem-distance map and no target proof.

QH observes only ordinary search-state measurements already exposed to the
controller: staleness, duplicate pressure, frontier size, terminal rejects,
imagined-state volume, and remaining-budget fraction.  It synthesizes a bounded
language of scalar coordinates from those primitives, cross-validates them
against the existing live proof-horizon signal (live_rhat), and forms a finite
six-class quotient of observed search states.  A validated coordinate may bias
legal controller knobs by a small amount learned from prior successful search
transitions.  It has no theorem/certificate authority.

Scientific scope:
* this is empirical search geometry, not a formal quotient of ZFC;
* ``live_rhat`` is used only as an evaluator, not as a candidate coordinate;
* the theorem is PROVED only if the independent Metamath verifier accepts the
  emitted certificate;
* QH never reads the hidden proof of sgrpcl.
"""
from __future__ import annotations

from dataclasses import dataclass
import importlib.util
import json
import math
from pathlib import Path
import statistics
import sys
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
DM24_PATH = HERE / "data_mind_2_4_mathematician_shortcuts.py"
spec = importlib.util.spec_from_file_location("data_mind_24_for_27_semigroup", DM24_PATH)
if spec is None or spec.loader is None:
    raise SystemExit(f"cannot load {DM24_PATH}")
DM24 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = DM24
spec.loader.exec_module(DM24)

KNOBS = DM24.KNOBS
EventType = DM24.EventType
emit = DM24.emit


@dataclass(frozen=True, slots=True)
class CandidateSpec:
    name: str
    complexity: int
    fn: Callable[[dict[str, float]], float]


@dataclass(frozen=True, slots=True)
class CandidateFit:
    name: str
    score: float
    train_corr: float
    validation_corr: float
    orientation: int
    quotient_classes: int
    complexity: int
    empirical_lambda_median: float | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "score": self.score,
            "train_corr": self.train_corr,
            "validation_corr": self.validation_corr,
            "orientation": self.orientation,
            "quotient_classes": self.quotient_classes,
            "complexity": self.complexity,
            "empirical_lambda_median": self.empirical_lambda_median,
        }


def _finite(x: Any) -> bool:
    return isinstance(x, (int, float)) and math.isfinite(float(x))


def _corr(xs: list[float], ys: list[float]) -> float:
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


def _median(values: list[float]) -> float | None:
    vals = [float(x) for x in values if _finite(x)]
    return float(statistics.median(vals)) if vals else None


def _zstats(rows: list[dict[str, float]], keys: tuple[str, ...]) -> dict[str, tuple[float, float]]:
    out: dict[str, tuple[float, float]] = {}
    for key in keys:
        vals = [float(r[key]) for r in rows]
        mean = sum(vals) / max(1, len(vals))
        var = sum((x - mean) ** 2 for x in vals) / max(1, len(vals))
        out[key] = (mean, math.sqrt(var) if var > 1e-18 else 1.0)
    return out


def _standardize(row: dict[str, float], stats: dict[str, tuple[float, float]]) -> dict[str, float]:
    return {k: (float(row[k]) - stats[k][0]) / stats[k][1] for k in stats}


def _candidate_language() -> tuple[CandidateSpec, ...]:
    keys = (
        "log_stale",
        "duplicate_rate",
        "log_frontier",
        "log_terminal_rejects",
        "log_imagined_delta",
        "budget_fraction_used",
    )
    specs: list[CandidateSpec] = []
    for key in keys:
        specs.append(CandidateSpec(key, 1, lambda r, k=key: r[k]))

    for i, a in enumerate(keys):
        for b in keys[i + 1 :]:
            specs.extend(
                (
                    CandidateSpec(f"{a}+{b}", 2, lambda r, a=a, b=b: r[a] + r[b]),
                    CandidateSpec(f"{a}-{b}", 2, lambda r, a=a, b=b: r[a] - r[b]),
                    CandidateSpec(f"2*{a}+{b}", 3, lambda r, a=a, b=b: 2.0 * r[a] + r[b]),
                    CandidateSpec(f"{a}+2*{b}", 3, lambda r, a=a, b=b: r[a] + 2.0 * r[b]),
                    CandidateSpec(f"{a}*{b}", 3, lambda r, a=a, b=b: r[a] * r[b]),
                )
            )

    # Nonlinear one-coordinate shapes. They are generated from primitives; no
    # theorem-specific symbol or known sgrpcl proof feature occurs here.
    for key in keys:
        specs.append(CandidateSpec(f"abs({key})", 2, lambda r, k=key: abs(r[k])))
        specs.append(CandidateSpec(f"square({key})", 2, lambda r, k=key: r[k] * r[k]))
    return tuple(specs)


CANDIDATES = _candidate_language()
PRIMITIVE_KEYS = (
    "log_stale",
    "duplicate_rate",
    "log_frontier",
    "log_terminal_rejects",
    "log_imagined_delta",
    "budget_fraction_used",
)


class SemigroupQuotientDiscoveryController(DM24.MathematicianController):
    """DATA-MIND 2.7 controller with empirical quotient synthesis."""

    architecture_version = "2.7"
    qh_min_samples = 24
    qh_min_abs_corr = 0.35
    qh_classes = 6
    qh_step = 0.006

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.qh_history: list[dict[str, Any]] = []
        self.qh_experiences: list[dict[str, Any]] = []
        self.qh_pending_action: dict[str, Any] | None = None
        self.qh_selected: CandidateFit | None = None
        self.qh_selected_spec: CandidateSpec | None = None
        self.qh_activations = 0
        self.qh_discovery_rounds = 0
        self.qh_validated_rounds = 0
        self.qh_candidate_evaluations = 0
        self.qh_top_reports: list[dict[str, Any]] = []
        self.qh_last_quotient_class: int | None = None
        self.memory_store.append(
            problem_id=self.cfg.problem_id,
            run_id=self.cfg.run_id,
            kind="qh_run_start",
            source_agent="QH",
            action={
                "architecture_version": "2.7",
                "candidate_language_size": len(CANDIDATES),
                "candidate_primitives": list(PRIMITIVE_KEYS),
                "evaluator_only": "live_rhat",
                "exact_reverse_distance_handed_to_qh": False,
                "target_proof_read": False,
            },
            tags=("data-mind-2.7", "quotient-hunter", "semigroup"),
            verified=None,
            source="DATA-MIND 2.7 semigroup QH",
        )
        emit(
            self.log,
            EventType.SELF_REPORT_FILED,
            "qh_semigroup_capability",
            agent="QH",
            candidate_language_size=len(CANDIDATES),
            candidate_primitives=list(PRIMITIVE_KEYS),
            live_rhat_candidate_allowed=False,
            exact_reverse_distance_handed_to_qh=False,
            target_proof_read=False,
            claim_scope="empirical search geometry only",
            verifier_authority=False,
        )

    def _primitive_row(self, kwargs: dict[str, Any]) -> dict[str, float]:
        exp = max(0, int(kwargs["exp"]))
        remaining = max(0, int(kwargs["remaining_budget"]))
        total = max(1, exp + remaining)
        imagined_delta = max(0, int(kwargs["imagined_total"]) - int(kwargs["imagined_previous"]))
        return {
            "log_stale": math.log1p(max(0, int(kwargs["stale"]))),
            "duplicate_rate": max(0.0, min(1.0, float(kwargs["dup_rate"]))),
            "log_frontier": math.log1p(max(0, int(kwargs["frontier_size"]))),
            "log_terminal_rejects": math.log1p(max(0, int(kwargs["terminal_rejects"]))),
            "log_imagined_delta": math.log1p(imagined_delta),
            "budget_fraction_used": exp / total,
        }

    def _fit_candidates(self) -> tuple[CandidateFit | None, list[CandidateFit]]:
        rows = [r for r in self.qh_history if _finite(r.get("live_rhat"))]
        n = len(rows)
        if n < self.qh_min_samples:
            return None, []
        split = max(12, int(0.67 * n))
        if n - split < 6:
            return None, []
        train = rows[:split]
        valid = rows[split:]
        stats = _zstats([r["primitive"] for r in train], PRIMITIVE_KEYS)
        ztrain = [_standardize(r["primitive"], stats) for r in train]
        zvalid = [_standardize(r["primitive"], stats) for r in valid]
        ytrain = [float(r["live_rhat"]) for r in train]
        yvalid = [float(r["live_rhat"]) for r in valid]
        fits: list[CandidateFit] = []
        self.qh_discovery_rounds += 1

        for spec in CANDIDATES:
            self.qh_candidate_evaluations += 1
            xt = [float(spec.fn(r)) for r in ztrain]
            xv = [float(spec.fn(r)) for r in zvalid]
            ct = _corr(xt, ytrain)
            cv = _corr(xv, yvalid)
            if ct == 0.0 or cv == 0.0 or ct * cv <= 0.0:
                continue
            orientation = 1 if ct > 0 else -1
            strength = min(abs(ct), abs(cv))
            complexity_penalty = 0.015 * max(0, spec.complexity - 1)
            score = strength - complexity_penalty

            # Empirical contraction proxy on the whole observed trajectory.
            allz = [_standardize(r["primitive"], stats) for r in rows]
            vals = [orientation * float(spec.fn(z)) for z in allz]
            floor = min(vals)
            hs = [max(1e-9, v - floor) for v in vals]
            ratios = [
                hs[i] / hs[i - 1]
                for i in range(1, len(hs))
                if hs[i - 1] > 1e-7 and hs[i] <= hs[i - 1]
            ]
            lam = _median(ratios)
            fits.append(
                CandidateFit(
                    name=spec.name,
                    score=score,
                    train_corr=ct,
                    validation_corr=cv,
                    orientation=orientation,
                    quotient_classes=self.qh_classes,
                    complexity=spec.complexity,
                    empirical_lambda_median=lam,
                )
            )

        fits.sort(key=lambda f: (f.score, -f.complexity, f.name), reverse=True)
        eligible = [
            f for f in fits
            if min(abs(f.train_corr), abs(f.validation_corr)) >= self.qh_min_abs_corr
        ]
        best = eligible[0] if eligible else None
        if best is not None:
            self.qh_validated_rounds += 1
        return best, fits[:10]

    def _value_for_selected(self, primitive: dict[str, float]) -> tuple[float | None, int | None]:
        if self.qh_selected is None or self.qh_selected_spec is None or len(self.qh_history) < 12:
            return None, None
        rows = [r["primitive"] for r in self.qh_history]
        split = max(8, int(0.67 * len(rows)))
        stats = _zstats(rows[:split], PRIMITIVE_KEYS)
        z = _standardize(primitive, stats)
        value = self.qh_selected.orientation * float(self.qh_selected_spec.fn(z))

        observed = []
        for row in rows:
            zr = _standardize(row, stats)
            observed.append(self.qh_selected.orientation * float(self.qh_selected_spec.fn(zr)))
        ordered = sorted(observed)
        if len(ordered) < 2:
            return value, 0
        rank = sum(1 for x in ordered if x <= value) - 1
        rank = max(0, rank)
        qclass = min(self.qh_classes - 1, int(self.qh_classes * rank / max(1, len(ordered))))
        return value, qclass

    def _settle_qh_pending(self, *, current_rhat: float, current_qh: float | None) -> None:
        p = self.qh_pending_action
        if p is None:
            return
        same = p.get("candidate") == (self.qh_selected.name if self.qh_selected else None)
        rhat_gain = float(p["rhat"]) - float(current_rhat)
        qh_gain = 0.0
        if same and _finite(p.get("qh_value")) and _finite(current_qh):
            qh_gain = float(p["qh_value"]) - float(current_qh)
        weight = max(0.0, rhat_gain) + 0.10 * max(0.0, qh_gain)
        self.qh_experiences.append(
            {
                "candidate": p.get("candidate"),
                "latent_delta": dict(p["latent_delta"]),
                "rhat_gain": rhat_gain,
                "qh_gain": qh_gain,
                "weight": weight,
            }
        )
        self.qh_pending_action = None

    def _qh_bias(self) -> dict[str, float]:
        if self.qh_selected is None:
            return {k: 0.0 for k in KNOBS}
        usable = [
            e for e in self.qh_experiences
            if e.get("candidate") == self.qh_selected.name and float(e.get("weight", 0.0)) > 0.0
        ][-40:]
        if len(usable) < 3:
            return {k: 0.0 for k in KNOBS}
        out: dict[str, float] = {}
        for key in KNOBS:
            num = den = 0.0
            for e in usable:
                w = float(e["weight"])
                d = float(e["latent_delta"].get(key, 0.0))
                num += w * (1.0 if d > 1e-12 else (-1.0 if d < -1e-12 else 0.0))
                den += w
            strength = num / den if den > 0 else 0.0
            out[key] = self.qh_step * max(-1.0, min(1.0, strength))
        return out

    def sample(self, **kwargs) -> str:
        exp = int(kwargs["exp"])
        before = dict(self.u)
        action = super().sample(**kwargs)
        if self.last_control_exp != exp:
            return action

        primitive = self._primitive_row(kwargs)
        live_rhat = float(kwargs["live_rhat"])
        self.qh_history.append(
            {
                "expansion": exp,
                "agent": self.current_agent,
                "primitive": primitive,
                "live_rhat": live_rhat,
            }
        )

        best, top = self._fit_candidates()
        self.qh_top_reports = [x.as_dict() for x in top]
        if best is not None:
            spec_by_name = {s.name: s for s in CANDIDATES}
            changed = self.qh_selected is None or self.qh_selected.name != best.name
            self.qh_selected = best
            self.qh_selected_spec = spec_by_name[best.name]
            if changed:
                emit(
                    self.log,
                    EventType.LOCAL_EVIDENCE_DETECTED,
                    "qh_geometry_selected",
                    agent="QH",
                    selected=best.as_dict(),
                    candidates_generated=len(CANDIDATES),
                    candidates_evaluated_total=self.qh_candidate_evaluations,
                    evaluator="held-out live_rhat",
                    formal_theorem_claim=False,
                    verifier_authority=False,
                )
                self.memory_store.append(
                    problem_id=self.cfg.problem_id,
                    run_id=self.cfg.run_id,
                    kind="qh_geometry_selected",
                    source_agent="QH",
                    action=best.as_dict(),
                    tags=("data-mind-2.7", "qh", "empirical-geometry"),
                    verified=None,
                    source="cross-validated proof-search telemetry",
                )

        qh_value, qclass = self._value_for_selected(primitive)
        self.qh_last_quotient_class = qclass
        self._settle_qh_pending(current_rhat=live_rhat, current_qh=qh_value)

        # QH never stacks a new bias on a child/inverse transition.
        if action == "NONE" and self.mode == "ADULT" and self.qh_selected is not None:
            delta = self._qh_bias()
            active = any(abs(v) > 1e-12 for v in delta.values())
            emit(
                self.log,
                EventType.STRATEGY_OVERRIDE_PROPOSED,
                "qh_empirical_quotient_bias",
                agent="QH",
                candidate=self.qh_selected.as_dict(),
                quotient_class=qclass,
                qh_value=qh_value,
                latent_delta=delta,
                legal_search_control_only=True,
                verifier_authority=False,
            )
            if active:
                before_qh = dict(self.u)
                for key, d in delta.items():
                    self._bounded_move(key, float(d))
                self._install_vector(self.u)
                actual = {k: float(self.u[k]) - float(before_qh[k]) for k in KNOBS}
                self.qh_activations += 1
                emit(
                    self.log,
                    EventType.STRATEGY_OVERRIDE_EXECUTED,
                    "qh_empirical_quotient_bias",
                    agent="QH",
                    candidate=self.qh_selected.name,
                    quotient_class=qclass,
                    actual_latent_delta=actual,
                    certificate_authority=False,
                    verifier_authority=False,
                )

        total_delta = {k: float(self.u[k]) - float(before[k]) for k in KNOBS}
        self.qh_pending_action = {
            "candidate": self.qh_selected.name if self.qh_selected else None,
            "qh_value": qh_value,
            "rhat": live_rhat,
            "latent_delta": total_delta,
        }
        return action

    def summary(self) -> dict[str, Any]:
        data = super().summary()
        data.update(
            {
                "architecture_version": "2.7",
                "quotient_hunter_enabled": True,
                "quotient_discovery_mode": "empirical proof-search-state synthesis",
                "exact_reverse_distance_handed_to_qh": False,
                "target_proof_read_by_qh": False,
                "qh_candidate_primitives": list(PRIMITIVE_KEYS),
                "qh_candidate_language_size": len(CANDIDATES),
                "qh_candidate_evaluations": self.qh_candidate_evaluations,
                "qh_observations": len(self.qh_history),
                "qh_discovery_rounds": self.qh_discovery_rounds,
                "qh_validated_rounds": self.qh_validated_rounds,
                "qh_selected_geometry": self.qh_selected.as_dict() if self.qh_selected else None,
                "qh_top_candidate_reports": self.qh_top_reports,
                "qh_last_quotient_class": self.qh_last_quotient_class,
                "qh_search_control_activations": self.qh_activations,
                "qh_empirical_not_formal_geometry": True,
                "qh_theorem_authority": False,
                "independent_verifier_sovereign": True,
            }
        )
        return data


def main() -> int:
    DM24.MathematicianController = SemigroupQuotientDiscoveryController
    return int(DM24.main() or 0)


if __name__ == "__main__":
    raise SystemExit(main())
