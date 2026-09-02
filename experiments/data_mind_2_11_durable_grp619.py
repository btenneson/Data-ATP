#!/usr/bin/env python3
"""Durable and resource-defended DATA-MIND 2.11 GRP619 entrypoint.

This wrapper keeps the 2.11 settlement/search logic unchanged while adding two
operational guarantees around it:

1. Important checkpoints are copied to a run-specific Git state branch, so a
   GitHub-host shutdown cannot erase the latest recovery point.
2. Sentinel watches the external prover's RSS and host MemAvailable.  If the
   prover approaches an unsafe share of host memory, Sentinel first writes and
   remotely publishes an emergency checkpoint and only then terminates that
   prover attempt.  The result is a bounded resource outcome, not a false
   mathematical UNKNOWN and not an unexplained infrastructure crash.

E itself does not expose a portable serialization of its live search state in
this prototype.  Recovery from an in-E checkpoint therefore truthfully means
``restart_current_attempt`` rather than pretending to resume E's internal
clause database byte-for-byte.
"""
from __future__ import annotations

import os
from pathlib import Path
import re
import signal
import subprocess
import time
from typing import Any, Mapping

from data_atp.breadcrumbs import BreadcrumbManager as LocalBreadcrumbManager
from data_atp.events import EventType

import data_mind_2_11_tptp95_grp619 as dm211


_SAFE_BRANCH = re.compile(r"^[A-Za-z0-9._/-]+$")
ROBUST_SZS_RE = re.compile(
    r"(?mi)^\s*%*\s*SZS status\s+([A-Za-z][A-Za-z0-9_-]*)"
)
_ALWAYS_PUBLISH = {
    "RUN_STARTED",
    "RUN_RESUMED",
    "PRE_EXTERNAL_PROVER",
    "POST_EXTERNAL_PROVER",
    "SENTINEL_RESOURCE_STOP",
    "RUN_FINISHED",
}
_RESOURCE_STOP_REQUESTED = False
_RESOURCE_STOP_REASON: dict[str, Any] | None = None
_ORIGINAL_CLASSIFY = dm211._classify
_ORIGINAL_OVERALL_STATUS = dm211._overall_status
_ORIGINAL_RUN_E_MONITORED = dm211.run_e_monitored


def _system_memory_kib() -> dict[str, int | None]:
    result: dict[str, int | None] = {"mem_total_kib": None, "mem_available_kib": None}
    try:
        for line in Path("/proc/meminfo").read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("MemTotal:"):
                result["mem_total_kib"] = int(line.split()[1])
            elif line.startswith("MemAvailable:"):
                result["mem_available_kib"] = int(line.split()[1])
    except (OSError, ValueError, IndexError):
        pass
    return result


def _resource_guard_reason(
    *,
    rss_kib: int | None,
    mem_total_kib: int | None,
    mem_available_kib: int | None,
    max_rss_fraction: float,
    min_available_fraction: float,
) -> dict[str, Any] | None:
    if not mem_total_kib or mem_total_kib <= 0:
        return None
    rss_fraction = (float(rss_kib) / mem_total_kib) if rss_kib is not None else None
    available_fraction = (
        float(mem_available_kib) / mem_total_kib
        if mem_available_kib is not None
        else None
    )
    reasons: list[str] = []
    if rss_fraction is not None and rss_fraction >= max_rss_fraction:
        reasons.append("prover_rss_fraction")
    if available_fraction is not None and available_fraction <= min_available_fraction:
        reasons.append("host_mem_available_fraction")
    if not reasons:
        return None
    return {
        "reasons": reasons,
        "rss_kib": rss_kib,
        "mem_total_kib": mem_total_kib,
        "mem_available_kib": mem_available_kib,
        "rss_fraction": rss_fraction,
        "available_fraction": available_fraction,
        "max_rss_fraction": max_rss_fraction,
        "min_available_fraction": min_available_fraction,
    }


def _guarded_classify(**kwargs: Any) -> str:
    if _RESOURCE_STOP_REQUESTED:
        return "SENTINEL_RESOURCE_STOP"
    return _ORIGINAL_CLASSIFY(**kwargs)


def _guarded_overall_status(runs: list[dict[str, Any]], settled: bool) -> str:
    if settled:
        return "SETTLED"
    if any(run.get("outcome_class") == "SENTINEL_RESOURCE_STOP" for run in runs):
        # Sentinel deliberately exhausted a safe resource envelope.  That is a
        # truthful bounded non-settlement, not a prover or infrastructure fault.
        return "BOUNDED_UNKNOWN"
    return _ORIGINAL_OVERALL_STATUS(runs, settled)


def _guarded_run_e_monitored(*args: Any, **kwargs: Any) -> dict[str, Any]:
    result = _ORIGINAL_RUN_E_MONITORED(*args, **kwargs)
    if result.get("outcome_class") == "SENTINEL_RESOURCE_STOP":
        result["sentinel_decision"] = "resource_stop"
        result["resource_guard_triggered"] = True
        result["resource_guard_reason"] = dict(_RESOURCE_STOP_REASON or {})
        result["abnormal_termination"] = False
    return result


class DurableBreadcrumbManager(LocalBreadcrumbManager):
    """Breadcrumb manager with Git durability and a live memory Sentinel."""

    def __init__(self, directory: str | Path, run_id: str) -> None:
        super().__init__(directory, run_id)
        self._state_branch = os.environ.get("DM211_STATE_BRANCH", "").strip()
        self._remote_interval = max(
            1.0, float(os.environ.get("DM211_REMOTE_CHECKPOINT_SECONDS", "60"))
        )
        self._max_rss_fraction = float(
            os.environ.get("DM211_SENTINEL_MAX_RSS_FRACTION", "0.65")
        )
        self._min_available_fraction = float(
            os.environ.get("DM211_SENTINEL_MIN_AVAILABLE_FRACTION", "0.20")
        )
        if not 0.0 < self._max_rss_fraction < 1.0:
            raise ValueError("DM211_SENTINEL_MAX_RSS_FRACTION must be in (0,1)")
        if not 0.0 < self._min_available_fraction < 1.0:
            raise ValueError("DM211_SENTINEL_MIN_AVAILABLE_FRACTION must be in (0,1)")
        self._last_remote_publish = 0.0
        self._repo_root = self._discover_repo_root()
        if self._state_branch and not _SAFE_BRANCH.fullmatch(self._state_branch):
            raise ValueError("DM211_STATE_BRANCH contains unsupported characters")

    @staticmethod
    def _discover_repo_root() -> Path | None:
        try:
            cp = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            return Path(cp.stdout.strip()).resolve()
        except (OSError, subprocess.SubprocessError):
            return None

    def _relative_state_dir(self) -> Path:
        if self._repo_root is None:
            raise RuntimeError("Git repository root is unavailable")
        try:
            return self.directory.resolve().relative_to(self._repo_root)
        except ValueError as exc:
            raise RuntimeError("breadcrumb directory is outside the Git repository") from exc

    def _publish_remote(self, kind: str) -> None:
        if not self._state_branch:
            return
        if self._repo_root is None:
            raise RuntimeError("remote breadcrumb publication requested outside a Git repository")

        relative = self._relative_state_dir()
        env = os.environ.copy()
        commands = (
            ["git", "config", "user.name", "DATA-MIND 2.11 Breadcrumb Bot"],
            ["git", "config", "user.email", "data-mind-2.11@users.noreply.github.com"],
            ["git", "add", "-f", "--", str(relative)],
        )
        for cmd in commands:
            subprocess.run(cmd, cwd=self._repo_root, env=env, check=True)

        staged = subprocess.run(
            ["git", "diff", "--cached", "--quiet", "--", str(relative)],
            cwd=self._repo_root,
            env=env,
            check=False,
        )
        if staged.returncode == 0:
            return
        if staged.returncode != 1:
            raise RuntimeError(f"git staged-state check failed with rc={staged.returncode}")

        message = f"DATA-MIND 2.11 breadcrumb: {self.run_id} {kind}"
        subprocess.run(
            ["git", "commit", "-m", message, "--", str(relative)],
            cwd=self._repo_root,
            env=env,
            check=True,
        )
        subprocess.run(
            ["git", "push", "origin", f"HEAD:refs/heads/{self._state_branch}"],
            cwd=self._repo_root,
            env=env,
            check=True,
        )
        self._last_remote_publish = time.monotonic()

    def _publish_if_due(self, kind: str, checkpoint: bool, snapshot: Mapping[str, Any]) -> None:
        if not checkpoint or not self._state_branch:
            return
        now = time.monotonic()
        due = now - self._last_remote_publish >= self._remote_interval
        if kind not in _ALWAYS_PUBLISH and not due:
            return
        try:
            self._publish_remote(kind)
        except Exception as exc:
            # A local checkpoint remains valid even if its remote mirror fails.
            # Record degraded durability in the same tamper-evident chain.
            self.log.append(
                EventType.BREADCRUMB_RECORDED,
                {
                    "run_id": self.run_id,
                    "kind": "REMOTE_PUBLISH_FAILED",
                    "architecture_version": dm211.ARCH,
                    "phase": str(snapshot.get("phase", "")),
                    "recovery_action": snapshot.get("recovery_action"),
                    "error": f"{type(exc).__name__}: {exc}",
                },
            )

    def _sentinel_guard(
        self,
        kind: str,
        snapshot: Mapping[str, Any],
        metadata: Mapping[str, Any],
    ) -> None:
        global _RESOURCE_STOP_REQUESTED, _RESOURCE_STOP_REASON
        if kind == "PRE_EXTERNAL_PROVER":
            _RESOURCE_STOP_REQUESTED = False
            _RESOURCE_STOP_REASON = None
            return
        if kind not in {"PROVER_HEARTBEAT", "CHECKPOINT_BARRIER"}:
            return
        if _RESOURCE_STOP_REQUESTED:
            return

        pid = metadata.get("pid")
        rss_kib = metadata.get("rss_kib")
        if not isinstance(pid, int) or pid <= 0:
            return
        system = _system_memory_kib()
        reason = _resource_guard_reason(
            rss_kib=int(rss_kib) if isinstance(rss_kib, int) else None,
            mem_total_kib=system["mem_total_kib"],
            mem_available_kib=system["mem_available_kib"],
            max_rss_fraction=self._max_rss_fraction,
            min_available_fraction=self._min_available_fraction,
        )
        if reason is None:
            return

        _RESOURCE_STOP_REQUESTED = True
        _RESOURCE_STOP_REASON = reason
        already_paused = bool(metadata.get("process_paused"))
        paused_here = False
        if os.name == "posix" and not already_paused:
            try:
                os.killpg(pid, signal.SIGSTOP)
                paused_here = True
            except (OSError, ProcessLookupError):
                pass

        emergency_snapshot = dict(snapshot)
        emergency_snapshot["phase"] = "sentinel_resource_stop"
        emergency_snapshot["recovery_action"] = "continue_from_next_attempt"
        emergency_metadata = {
            "pid": pid,
            "process_paused": already_paused or paused_here,
            **reason,
        }
        # Recursive call is safe: SENTINEL_RESOURCE_STOP is not a guard-input
        # kind, and it is always remotely published before the process is told
        # to terminate.
        self.record(
            "SENTINEL_RESOURCE_STOP",
            emergency_snapshot,
            metadata=emergency_metadata,
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

    def record(
        self,
        kind: str,
        snapshot: Mapping[str, Any],
        *,
        metadata: Mapping[str, Any] | None = None,
        checkpoint: bool = True,
    ):
        md = dict(metadata or {})
        receipt = super().record(kind, snapshot, metadata=md, checkpoint=checkpoint)
        self._publish_if_due(kind, checkpoint, snapshot)
        self._sentinel_guard(kind, snapshot, md)
        return receipt


def main() -> int:
    # Upgrade the inherited 2.10 SZS parser: E emits lines such as
    # ``%% SZS status ResourceOut``.  The older expression accepted only one
    # leading percent sign and therefore recorded a real ResourceOut as null.
    dm211.SZS_RE = ROBUST_SZS_RE
    dm211.BreadcrumbManager = DurableBreadcrumbManager
    dm211._classify = _guarded_classify
    dm211._overall_status = _guarded_overall_status
    dm211.run_e_monitored = _guarded_run_e_monitored
    return int(dm211.main())


if __name__ == "__main__":
    raise SystemExit(main())
