"""Defensive resource Sentinel for DATA-MIND feature/signature computation.

The Sentinel is intentionally separate from theorem truth, BANK/FUTUREBANK, and
verification. It classifies resource behavior only. A theorem that is
quarantined here is a censored computation, not a negative theorem example.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable


_MAD_SCALE = 0.67448975


@dataclass(frozen=True)
class RobustBaseline:
    median_time_s: float
    mad_time_s: float
    median_rss_mb: float
    mad_rss_mb: float
    median_ram_growth_mb_s: float = 0.0
    mad_ram_growth_mb_s: float = 0.0


@dataclass(frozen=True)
class SentinelConfig:
    """Frozen Sentinel decision parameters.

    A joint anomaly is required for adaptive quarantine. Memory anomaly alone
    is deliberately insufficient so expensive-but-valid RAM outliers can pass.
    Hard ceilings are infrastructure protection and are reported distinctly.
    """

    time_z_threshold: float = 6.0
    rss_z_threshold: float = 6.0
    growth_z_threshold: float = 6.0
    min_joint_signals: int = 2
    hard_time_s: float | None = None
    hard_rss_mb: float | None = None


@dataclass(frozen=True)
class ResourceSample:
    elapsed_s: float
    peak_rss_mb: float
    ram_growth_mb_s: float = 0.0
    progress_rate: float | None = None


@dataclass(frozen=True)
class SentinelDecision:
    action: str  # "continue", "quarantine", "hard_stop"
    reason: str
    time_z: float
    rss_z: float
    growth_z: float
    anomaly_signals: int


def _robust_z(value: float, median: float, mad: float) -> float:
    if not all(isfinite(v) for v in (value, median, mad)):
        return 0.0
    if mad <= 0.0:
        return 0.0
    return _MAD_SCALE * (value - median) / mad


class Sentinel:
    """Frozen robust-resource policy for one evaluation run."""

    def __init__(self, baseline: RobustBaseline, config: SentinelConfig) -> None:
        self.baseline = baseline
        self.config = config

    def inspect(self, sample: ResourceSample) -> SentinelDecision:
        cfg = self.config

        if cfg.hard_time_s is not None and sample.elapsed_s >= cfg.hard_time_s:
            return SentinelDecision(
                "hard_stop", "hard_time_ceiling", 0.0, 0.0, 0.0, 0
            )
        if cfg.hard_rss_mb is not None and sample.peak_rss_mb >= cfg.hard_rss_mb:
            return SentinelDecision(
                "hard_stop", "hard_memory_ceiling", 0.0, 0.0, 0.0, 0
            )

        time_z = _robust_z(
            sample.elapsed_s, self.baseline.median_time_s, self.baseline.mad_time_s
        )
        rss_z = _robust_z(
            sample.peak_rss_mb, self.baseline.median_rss_mb, self.baseline.mad_rss_mb
        )
        growth_z = _robust_z(
            sample.ram_growth_mb_s,
            self.baseline.median_ram_growth_mb_s,
            self.baseline.mad_ram_growth_mb_s,
        )

        signals = sum(
            (
                time_z >= cfg.time_z_threshold,
                rss_z >= cfg.rss_z_threshold,
                growth_z >= cfg.growth_z_threshold,
            )
        )

        if signals >= cfg.min_joint_signals:
            return SentinelDecision(
                "quarantine",
                "joint_resource_anomaly",
                time_z,
                rss_z,
                growth_z,
                signals,
            )

        return SentinelDecision(
            "continue", "insufficient_joint_evidence", time_z, rss_z, growth_z, signals
        )


def median(values: Iterable[float]) -> float:
    xs = sorted(float(v) for v in values)
    if not xs:
        raise ValueError("median requires at least one value")
    n = len(xs)
    mid = n // 2
    return xs[mid] if n % 2 else (xs[mid - 1] + xs[mid]) / 2.0


def fit_robust_baseline(samples: Iterable[ResourceSample]) -> RobustBaseline:
    """Fit calibration-only robust statistics.

    Do not call this on the frozen 78-case evaluation labels/population when
    using the preregistered experiment.
    """

    rows = list(samples)
    if not rows:
        raise ValueError("at least one calibration sample is required")

    times = [r.elapsed_s for r in rows]
    rss = [r.peak_rss_mb for r in rows]
    growth = [r.ram_growth_mb_s for r in rows]

    mt = median(times)
    mr = median(rss)
    mg = median(growth)
    return RobustBaseline(
        median_time_s=mt,
        mad_time_s=median(abs(x - mt) for x in times),
        median_rss_mb=mr,
        mad_rss_mb=median(abs(x - mr) for x in rss),
        median_ram_growth_mb_s=mg,
        mad_ram_growth_mb_s=median(abs(x - mg) for x in growth),
    )
