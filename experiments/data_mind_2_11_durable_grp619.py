#!/usr/bin/env python3
"""Durable DATA-MIND 2.11 GRP619 entrypoint.

This thin wrapper keeps the 2.11 proof/search runner unchanged while upgrading
its local checkpoint barriers into remotely durable breadcrumbs during GitHub
Actions runs.  Every important checkpoint, and periodic in-prover barriers,
may be committed to a run-specific Git state branch.  That branch is not a
workflow trigger, so publishing recovery state cannot recursively launch work.

The external E process is already SIGSTOP'ed by the core 2.11 runner while a
periodic checkpoint barrier is being written.  Because ``record`` returns only
after the local checkpoint and transaction-log records have been fsynced, the
remote publication below occurs while E remains paused.  The corresponding
SIGCONT is issued by the core runner only after this method returns.
"""
from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import time
from typing import Any, Mapping

from data_atp.breadcrumbs import BreadcrumbManager as LocalBreadcrumbManager

import data_mind_2_11_tptp95_grp619 as dm211


_SAFE_BRANCH = re.compile(r"^[A-Za-z0-9._/-]+$")
_ALWAYS_PUBLISH = {
    "RUN_STARTED",
    "RUN_RESUMED",
    "PRE_EXTERNAL_PROVER",
    "POST_EXTERNAL_PROVER",
    "RUN_FINISHED",
}


class DurableBreadcrumbManager(LocalBreadcrumbManager):
    """Breadcrumb manager with an optional Git-backed durability sink."""

    def __init__(self, directory: str | Path, run_id: str) -> None:
        super().__init__(directory, run_id)
        self._state_branch = os.environ.get("DM211_STATE_BRANCH", "").strip()
        self._remote_interval = max(
            1.0, float(os.environ.get("DM211_REMOTE_CHECKPOINT_SECONDS", "60"))
        )
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

    def record(
        self,
        kind: str,
        snapshot: Mapping[str, Any],
        *,
        metadata: Mapping[str, Any] | None = None,
        checkpoint: bool = True,
    ):
        receipt = super().record(kind, snapshot, metadata=metadata, checkpoint=checkpoint)
        if not checkpoint or not self._state_branch:
            return receipt

        now = time.monotonic()
        due = now - self._last_remote_publish >= self._remote_interval
        if kind in _ALWAYS_PUBLISH or due:
            try:
                self._publish_remote(kind)
            except Exception as exc:
                # Do not falsify the local checkpoint merely because its remote
                # copy failed.  Record the remote failure in the same local,
                # hash-chained log so the run can report degraded durability.
                self.log.append(
                    dm211.EventType.BREADCRUMB_RECORDED,
                    {
                        "run_id": self.run_id,
                        "kind": "REMOTE_PUBLISH_FAILED",
                        "architecture_version": dm211.ARCH,
                        "phase": str(snapshot.get("phase", "")),
                        "recovery_action": snapshot.get("recovery_action"),
                        "error": f"{type(exc).__name__}: {exc}",
                    },
                )
        return receipt


def main() -> int:
    # The core module resolves BreadcrumbManager at execution time, so replacing
    # this module-global name upgrades smoke/examine without duplicating the
    # settlement logic.
    dm211.BreadcrumbManager = DurableBreadcrumbManager
    return int(dm211.main())


if __name__ == "__main__":
    raise SystemExit(main())
