#!/usr/bin/env python3
"""DATA-MIND 2.12 adaptive memory trading for the frozen GRP619 holdout.

2.12 keeps the DATA-MIND 2.11 verifier gate, durable breadcrumbs, frozen 171/9
training split, and exact held-out target. It changes the search controller:

* a 28-candidate portfolio explores 14 materially different E search profiles
  across the learned reordered presentation and the untouched original;
* Sentinel estimates process-group RSS slope and trades away from a trajectory
  before the hard 2.11 memory envelope when continued growth predicts failure;
* unused wall budget is automatically redistributed by the inherited 2.11
  scheduler to later portfolio members;
* failed trajectories are deposited into a federated BANK and written to a
  durable JSONL ledger with memory/search-efficiency telemetry.

The learner is not retrained and GRP619 remains unseen during education.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import signal
import sys
from typing import Any, Mapping, Sequence

from data_atp.federated_bank import FederatedBank, PropagationMode

import data_mind_2_11_tptp95_grp619 as dm211
import data_mind_2_11_durable_grp619 as dm211d

ARCH = "2.12"
_COMMON = ["--print-statistics", "--resources-info"]


def _profile(*args: str) -> list[str]:
    return [*_COMMON, *args]


# Four scheduler/filter modes plus heuristic/ordering variants and two explicit
# clause-set caps. With two presentations this yields 28 candidate searches.
PORTFOLIO: dict[str, list[str]] = {
    "default": _profile(),
    "sine_auto": _profile("--sine=Auto"),
    "auto_schedule": _profile("--auto-schedule=1"),
    "satauto_schedule": _profile("--satauto-schedule=1"),
    "weight_auto": _profile("--expert-heuristic=Weight", "--term-ordering=Auto"),
    "standardweight_auto": _profile("--expert-heuristic=StandardWeight", "--term-ordering=Auto"),
    "rweight_auto": _profile("--expert-heuristic=RWeight", "--term-ordering=Auto"),
    "fifo_auto": _profile("--expert-heuristic=FIFO", "--term-ordering=Auto"),
    "weight_kbo6": _profile("--expert-heuristic=Weight", "--term-ordering=KBO6"),
    "standardweight_kbo6": _profile("--expert-heuristic=StandardWeight", "--term-ordering=KBO6"),
    "rweight_kbo6": _profile("--expert-heuristic=RWeight", "--term-ordering=KBO6"),
    "weight_lpo4": _profile("--expert-heuristic=Weight", "--term-ordering=LPO4"),
    "default_clausecap_250k": _profile("--total-clause-set-limit=250000"),
    "sine_clausecap_250k": _profile("--sine=Auto", "--total-clause-set-limit=250000"),
}
PROFILE_ORDER = tuple(PORTFOLIO)

PROCESSED_RE = re.compile(r"(?mi)^\s*#?\s*Processed clauses\s*:\s*(\d+)")
GENERATED_RE = re.compile(r"(?mi)^\s*#?\s*Generated clauses\s*:\s*(\d+)")
_TRAJECTORY_BANK = FederatedBank(
    departments=("P", "QH", "COMPASS", "LEARNER", "SENTINEL", "VERIFIER")
)


def linear_slope(samples: Sequence[tuple[float, float]]) -> float | None:
    """Ordinary-least-squares slope in y-units per second."""
    if len(samples) < 2:
        return None
    xs = [float(x) for x, _ in samples]
    ys = [float(y) for _, y in samples]
    xbar = sum(xs) / len(xs)
    ybar = sum(ys) / len(ys)
    denom = sum((x - xbar) ** 2 for x in xs)
    if denom <= 0.0:
        return None
    return sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys)) / denom


def predictive_trade_reason(
    *,
    samples: Sequence[tuple[float, float]],
    current_rss_kib: int,
    mem_total_kib: int,
    hard_rss_fraction: float,
    min_rss_kib: int,
    min_slope_kib_per_second: float,
    forecast_seconds: float,
    min_samples: int = 3,
) -> dict[str, Any] | None:
    if len(samples) < min_samples or current_rss_kib < min_rss_kib or mem_total_kib <= 0:
        return None
    slope = linear_slope(samples)
    if slope is None or slope < min_slope_kib_per_second:
        return None
    hard_limit_kib = hard_rss_fraction * mem_total_kib
    seconds_to_hard = (hard_limit_kib - current_rss_kib) / slope
    if seconds_to_hard < 0:
        seconds_to_hard = 0.0
    if seconds_to_hard > forecast_seconds:
        return None
    return {
        "decision": "predictive_strategy_trade",
        "reasons": ["predicted_memory_envelope_collision"],
        "rss_kib": int(current_rss_kib),
        "mem_total_kib": int(mem_total_kib),
        "rss_fraction": float(current_rss_kib) / float(mem_total_kib),
        "hard_rss_fraction": float(hard_rss_fraction),
        "slope_kib_per_second": float(slope),
        "slope_mib_per_second": float(slope) / 1024.0,
        "predicted_seconds_to_hard_limit": float(seconds_to_hard),
        "forecast_seconds": float(forecast_seconds),
        "sample_count": len(samples),
    }


def search_efficiency(
    *, processed_clauses: int | None, generated_clauses: int | None,
    peak_rss_kib: int | None,
) -> dict[str, float | int | None | str | bool]:
    """A diagnostic search-progress-per-memory objective, not proof credit."""
    peak_mib = (float(peak_rss_kib) / 1024.0) if peak_rss_kib else None
    processed_per_mib = (
        float(processed_clauses) / peak_mib
        if processed_clauses is not None and peak_mib and peak_mib > 0.0 else None
    )
    generated_per_mib = (
        float(generated_clauses) / peak_mib
        if generated_clauses is not None and peak_mib and peak_mib > 0.0 else None
    )
    return {
        "objective_name": "search_progress_per_memory",
        "objective_is_proof_credit": False,
        "processed_clauses": processed_clauses,
        "generated_clauses": generated_clauses,
        "peak_rss_mib": peak_mib,
        "processed_clauses_per_peak_mib": processed_per_mib,
        "generated_clauses_per_peak_mib": generated_per_mib,
    }


def _read_status_rss_kib(pid: int) -> int | None:
    try:
        for line in Path(f"/proc/{pid}/status").read_text(
            encoding="utf-8", errors="replace"
        ).splitlines():
            if line.startswith("VmRSS:"):
                return int(line.split()[1])
    except (OSError, ValueError, IndexError):
        return None
    return None


def process_group_rss_kib(root_pid: int) -> int | None:
    """Sum Linux RSS for the E process group, including schedule children."""
    if os.name != "posix":
        return _read_status_rss_kib(root_pid)
    try:
        pgid = os.getpgid(root_pid)
    except (OSError, ProcessLookupError):
        return None
    total = 0
    found = False
    try:
        entries = list(Path("/proc").iterdir())
    except OSError:
        return _read_status_rss_kib(root_pid)
    for entry in entries:
        if not entry.name.isdigit():
            continue
        pid = int(entry.name)
        try:
            if os.getpgid(pid) != pgid:
                continue
        except (OSError, ProcessLookupError):
            continue
        rss = _read_status_rss_kib(pid)
        if rss is not None:
            total += rss
            found = True
    return total if found else _read_status_rss_kib(root_pid)


class AdaptiveBreadcrumbManager(dm211d.DurableBreadcrumbManager):
    """2.11 durability plus predictive memory-slope strategy trading."""

    def __init__(self, directory: str | Path, run_id: str) -> None:
        super().__init__(directory, run_id)
        self._min_rss_kib = int(
            float(os.environ.get("DM212_EARLY_MIN_RSS_GIB", "3.0")) * 1024 * 1024
        )
        self._min_slope_kib_s = (
            float(os.environ.get("DM212_EARLY_MIN_SLOPE_MIB_S", "24.0")) * 1024.0
        )
        self._forecast_seconds = float(
            os.environ.get("DM212_EARLY_FORECAST_SECONDS", "90")
        )
        self._window_seconds = float(
            os.environ.get("DM212_SLOPE_WINDOW_SECONDS", "30")
        )
        self._samples: dict[int, list[tuple[float, float]]] = {}
        self._telemetry: dict[int, dict[str, Any]] = {}

    def summary_for_pid(self, pid: int | None) -> dict[str, Any]:
        if not isinstance(pid, int):
            return {}
        return dict(self._telemetry.get(pid, {}))

    def _windowed(self, pid: int) -> list[tuple[float, float]]:
        samples = self._samples.get(pid, [])
        if not samples:
            return []
        latest = samples[-1][0]
        return [s for s in samples if latest - s[0] <= self._window_seconds]

    def _trigger(
        self, *, kind: str, pid: int, snapshot: Mapping[str, Any],
        metadata: Mapping[str, Any], reason: dict[str, Any],
    ) -> None:
        if dm211d._RESOURCE_STOP_REQUESTED:
            return
        dm211d._RESOURCE_STOP_REQUESTED = True
        dm211d._RESOURCE_STOP_REASON = dict(reason)

        already_paused = bool(metadata.get("process_paused"))
        paused_here = False
        if os.name == "posix" and not already_paused:
            try:
                os.killpg(pid, signal.SIGSTOP)
                paused_here = True
            except (OSError, ProcessLookupError):
                pass

        event_kind = (
            "ADAPTIVE_STRATEGY_TRADE"
            if reason.get("decision") == "predictive_strategy_trade"
            else "SENTINEL_RESOURCE_STOP"
        )
        emergency_snapshot = dict(snapshot)
        emergency_snapshot["phase"] = event_kind.lower()
        # E's internal clause database is not serializable. If the host dies
        # here, the truthful recovery boundary is the current attempt.
        emergency_snapshot["recovery_action"] = "restart_current_attempt"
        emergency_metadata = {
            "pid": pid,
            "process_paused": already_paused or paused_here,
            **reason,
        }
        self.record(
            event_kind, emergency_snapshot, metadata=emergency_metadata,
            checkpoint=True,
        )

        if os.name == "posix":
            try:
                os.killpg(pid, signal.SIGTERM)
            except (OSError, ProcessLookupError):
                pass
            if paused_here:
                try:
                    os.killpg(pid, signal.SIGCONT)
                except (OSError, ProcessLookupError):
                    pass

    def _sentinel_guard(
        self, kind: str, snapshot: Mapping[str, Any], metadata: Mapping[str, Any]
    ) -> None:
        if kind == "PRE_EXTERNAL_PROVER":
            dm211d._RESOURCE_STOP_REQUESTED = False
            dm211d._RESOURCE_STOP_REASON = None
            return
        if kind not in {"PROVER_HEARTBEAT", "CHECKPOINT_BARRIER"}:
            return
        if dm211d._RESOURCE_STOP_REQUESTED:
            return

        pid = metadata.get("pid")
        if not isinstance(pid, int) or pid <= 0:
            return
        active = snapshot.get("active_attempt")
        elapsed = None
        log_bytes = None
        if isinstance(active, Mapping):
            try:
                elapsed = float(active.get("elapsed_seconds"))
            except (TypeError, ValueError):
                elapsed = None
            try:
                log_bytes = int(active.get("log_bytes"))
            except (TypeError, ValueError):
                log_bytes = None
        if elapsed is None:
            return

        rss_kib = process_group_rss_kib(pid)
        if rss_kib is None:
            raw = metadata.get("rss_kib")
            rss_kib = int(raw) if isinstance(raw, int) else None
        if rss_kib is None:
            return

        samples = self._samples.setdefault(pid, [])
        samples.append((elapsed, float(rss_kib)))
        windowed = self._windowed(pid)
        slope = linear_slope(windowed)
        system = dm211d._system_memory_kib()
        mem_total = system.get("mem_total_kib")
        mem_available = system.get("mem_available_kib")

        telem = self._telemetry.setdefault(pid, {
            "sample_count": 0,
            "max_process_group_rss_kib": 0,
            "memory_slope_mib_per_second": None,
            "predicted_seconds_to_hard_limit": None,
            "adaptive_trade_triggered": False,
        })
        telem["sample_count"] = len(samples)
        telem["max_process_group_rss_kib"] = max(
            int(telem.get("max_process_group_rss_kib") or 0), int(rss_kib)
        )
        telem["memory_slope_mib_per_second"] = (
            float(slope) / 1024.0 if slope is not None else None
        )
        telem["last_log_bytes"] = log_bytes

        hard_reason = dm211d._resource_guard_reason(
            rss_kib=rss_kib,
            mem_total_kib=int(mem_total) if isinstance(mem_total, int) else None,
            mem_available_kib=int(mem_available) if isinstance(mem_available, int) else None,
            max_rss_fraction=self._max_rss_fraction,
            min_available_fraction=self._min_available_fraction,
        )
        if hard_reason is not None:
            hard_reason = {"decision": "hard_resource_stop", **hard_reason}
            telem["adaptive_trade_triggered"] = False
            telem["stop_reason"] = hard_reason
            self._trigger(
                kind=kind, pid=pid, snapshot=snapshot, metadata=metadata,
                reason=hard_reason,
            )
            return

        if not isinstance(mem_total, int) or mem_total <= 0:
            return
        predictive = predictive_trade_reason(
            samples=windowed,
            current_rss_kib=rss_kib,
            mem_total_kib=mem_total,
            hard_rss_fraction=self._max_rss_fraction,
            min_rss_kib=self._min_rss_kib,
            min_slope_kib_per_second=self._min_slope_kib_s,
            forecast_seconds=self._forecast_seconds,
        )
        if predictive is None:
            if slope and slope > 0:
                hard_limit = self._max_rss_fraction * mem_total
                telem["predicted_seconds_to_hard_limit"] = max(
                    0.0, (hard_limit - rss_kib) / slope
                )
            return
        telem["adaptive_trade_triggered"] = True
        telem["predicted_seconds_to_hard_limit"] = predictive[
            "predicted_seconds_to_hard_limit"
        ]
        telem["stop_reason"] = predictive
        self._trigger(
            kind=kind, pid=pid, snapshot=snapshot, metadata=metadata,
            reason=predictive,
        )


def _parse_int(regex: re.Pattern[str], text: str) -> int | None:
    match = regex.search(text)
    return int(match.group(1)) if match else None


def _problem_form(problem: Path) -> str:
    return "reordered" if "reordered" in problem.name else "original"


def adaptive_run_e_monitored(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Run one E attempt, annotate efficiency, and BANK a failed trajectory."""
    result = dm211d._guarded_run_e_monitored(*args, **kwargs)
    problem = Path(args[0])
    strategy = str(args[2])
    log_path = Path(kwargs["log_path"])
    breadcrumbs = kwargs.get("breadcrumbs")

    telemetry: dict[str, Any] = {}
    if isinstance(breadcrumbs, AdaptiveBreadcrumbManager):
        telemetry = breadcrumbs.summary_for_pid(result.get("pid"))
    result["adaptive_telemetry"] = telemetry

    reason = result.get("resource_guard_reason")
    if isinstance(reason, Mapping) and reason.get("decision") == "predictive_strategy_trade":
        result["sentinel_decision"] = "trade_strategy"
        result["adaptive_strategy_trade"] = True
    else:
        result["adaptive_strategy_trade"] = False

    try:
        text = log_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        text = ""
    processed = _parse_int(PROCESSED_RE, text)
    generated = _parse_int(GENERATED_RE, text)
    peak_rss = telemetry.get("max_process_group_rss_kib")
    if not isinstance(peak_rss, int) or peak_rss <= 0:
        guard = result.get("resource_guard_reason")
        peak_rss = guard.get("rss_kib") if isinstance(guard, Mapping) else None
    efficiency = search_efficiency(
        processed_clauses=processed,
        generated_clauses=generated,
        peak_rss_kib=peak_rss if isinstance(peak_rss, int) else None,
    )
    result["search_efficiency"] = efficiency

    # Smoke validates adapters/options only; it is not education. BANK only the
    # actual held-out examination trajectories.
    if log_path.name.startswith("e_") and not bool(result.get("verifier_accepted")):
        payload = {
            "architecture_version": ARCH,
            "target": dm211.TARGET,
            "target_seen_in_training": False,
            "problem_form": _problem_form(problem),
            "strategy": strategy,
            "strategy_flags": list(PORTFOLIO.get(strategy, [])),
            "outcome_class": result.get("outcome_class"),
            "sentinel_decision": result.get("sentinel_decision"),
            "elapsed_seconds": result.get("elapsed_seconds"),
            "allocated_seconds": result.get("allocated_seconds"),
            "szs_status": result.get("szs_status"),
            "resource_guard_reason": result.get("resource_guard_reason"),
            "adaptive_telemetry": telemetry,
            "search_efficiency": efficiency,
            "verifier_accepted": False,
        }
        deposits = _TRAJECTORY_BANK.propose(
            agent="LEARNER", kind="failure_trajectory", payload=payload,
            verify=lambda kind, value: (
                kind == "failure_trajectory"
                and isinstance(value, Mapping)
                and value.get("verifier_accepted") is False
                and value.get("target") == dm211.TARGET
            ),
            metadata={
                "architecture_version": ARCH,
                "target_seen_in_training": False,
                "purpose": "negative search-trajectory knowledge",
            },
            propagation=PropagationMode.CORE,
        )
        ids = [item.item_id for item in deposits]
        result["trajectory_bank_deposits"] = ids
        ledger = log_path.parent / "trajectory_bank.jsonl"
        with ledger.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(
                {"deposit_ids": ids, "payload": payload},
                sort_keys=True, default=str,
            ) + "\n")
    else:
        result["trajectory_bank_deposits"] = []
    return result


def adaptive_ordered_viable(
    smoke_result: dict[str, Any], problems: dict[str, Path]
) -> list[dict[str, str]]:
    healthy = {
        (str(item.get("problem_form")), str(item.get("strategy")))
        for item in smoke_result.get("viable_strategies", [])
        if item.get("problem_form") in problems and item.get("strategy") in PORTFOLIO
    }
    ordered: list[dict[str, str]] = []
    # Interleave learned-reordered and untouched-original so a bad presentation
    # geometry cannot monopolize the front of the total budget.
    for strategy in PROFILE_ORDER:
        for form in ("reordered", "original"):
            if (form, strategy) in healthy:
                ordered.append({"problem_form": form, "strategy": strategy})
    return ordered


def _augment_result_file(out_dir: Path, mode: str) -> None:
    path = out_dir / ("result.json" if mode == "examine" else "smoke_result.json")
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    runs = list(data.get("runs", []))
    deposits = [
        item for run in runs for item in run.get("trajectory_bank_deposits", [])
    ]
    trades = sum(bool(run.get("adaptive_strategy_trade")) for run in runs)
    data["architecture_version"] = ARCH
    data["adaptive_controller"] = {
        "portfolio_profiles": len(PORTFOLIO),
        "portfolio_candidate_capacity": len(PORTFOLIO) * 2,
        "strategy_profiles": list(PROFILE_ORDER),
        "memory_signal": "process-group RSS linear slope",
        "early_min_rss_gib": float(os.environ.get("DM212_EARLY_MIN_RSS_GIB", "3.0")),
        "early_min_slope_mib_per_second": float(
            os.environ.get("DM212_EARLY_MIN_SLOPE_MIB_S", "24.0")
        ),
        "forecast_seconds": float(os.environ.get("DM212_EARLY_FORECAST_SECONDS", "90")),
        "slope_window_seconds": float(os.environ.get("DM212_SLOPE_WINDOW_SECONDS", "30")),
        "hard_rss_fraction": float(
            os.environ.get("DM211_SENTINEL_MAX_RSS_FRACTION", "0.65")
        ),
        "budget_trade_semantics": (
            "actual time saved by an early stop remains in the inherited total "
            "budget and is redistributed over later viable candidates"
        ),
    }
    data["trajectory_bank_deposit_ids"] = deposits
    data["failure_trajectory_count"] = sum(
        1 for run in runs if run.get("trajectory_bank_deposits")
    )
    data["adaptive_strategy_trade_count"] = trades
    data["search_progress_objective"] = {
        "name": "search_progress_per_memory",
        "proof_credit": False,
        "primary_metric_when_available": "processed_clauses_per_peak_mib",
        "secondary_metric_when_available": "generated_clauses_per_peak_mib",
    }
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _arg_value(flag: str) -> str | None:
    try:
        index = sys.argv.index(flag)
    except ValueError:
        return None
    return sys.argv[index + 1] if index + 1 < len(sys.argv) else None


def configure() -> None:
    dm211.ARCH = ARCH
    dm211.STRATEGIES = PORTFOLIO
    dm211.SZS_RE = dm211d.ROBUST_SZS_RE
    dm211.BreadcrumbManager = AdaptiveBreadcrumbManager
    dm211._classify = dm211d._guarded_classify
    dm211._overall_status = dm211d._guarded_overall_status
    dm211.run_e_monitored = adaptive_run_e_monitored
    dm211._ordered_viable = adaptive_ordered_viable
    dm211d._ALWAYS_PUBLISH.add("ADAPTIVE_STRATEGY_TRADE")


def main() -> int:
    configure()
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    rc = int(dm211.main())
    out = _arg_value("--out")
    if out and mode in {"smoke", "examine"}:
        _augment_result_file(Path(out), mode)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
