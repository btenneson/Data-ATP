"""Picard: human-governed executive control for Data-ATP Phase 0.

Picard is not a prover and never certifies mathematics. It owns the run-control
state machine and issues typed directives that downstream search components may
follow or, for soft directives only, challenge through the accountable-autonomy
controller.

The control-plane analogy is an interrupt controller:
* PAUSE and GRACEFUL_STOP are cooperative interrupt requests handled at safe
  work boundaries;
* EMERGENCY_STOP is a non-maskable-style operator interrupt that terminates
  further search dispatch and trusted-state commits;
* soft strategy directives are scheduler guidance, not interrupt requests and
  not mathematical authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .autonomy import AuthorityLevel, Directive
from .events import EventType, TransactionLog


class RunControlState(StrEnum):
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    QUIESCING = "quiescing"
    STOPPED = "stopped"
    EMERGENCY_STOP = "emergency_stop"


class PicardCommand(StrEnum):
    START = "start"
    PAUSE = "pause"
    RESUME = "resume"
    GRACEFUL_STOP = "graceful_stop"
    EMERGENCY_STOP = "emergency_stop"


@dataclass(frozen=True, slots=True)
class PicardStatus:
    run_id: str
    state: RunControlState
    may_dispatch_work: bool
    may_commit_trusted_state: bool


class PicardController:
    """Authoritative human-governance interface for one Data-ATP run.

    Design rules:
    * emergency stop is terminal;
    * graceful stop first enters QUIESCING so a checkpoint manager can finish;
    * PAUSED and QUIESCING dispatch no new work and permit no trusted commits;
    * directives are logged and typed as hard invariants or soft strategy;
    * Picard never verifies a theorem or proof certificate.
    """

    def __init__(self, run_id: str, log: TransactionLog) -> None:
        if not run_id.strip():
            raise ValueError("run_id must be nonempty")
        self.run_id = run_id
        self.log = log
        self._state = RunControlState.CREATED
        self._directive_counter = 0

    @property
    def state(self) -> RunControlState:
        return self._state

    def status(self) -> PicardStatus:
        running = self._state == RunControlState.RUNNING
        return PicardStatus(
            run_id=self.run_id,
            state=self._state,
            may_dispatch_work=running,
            may_commit_trusted_state=running,
        )

    def command(self, command: PicardCommand, rationale: str) -> RunControlState:
        """Apply a human command and return the resulting run state."""
        if not rationale.strip():
            raise ValueError("Picard commands require a rationale")

        self.log.append(
            EventType.PICARD_COMMAND_RECEIVED,
            {
                "run_id": self.run_id,
                "command": command,
                "state_before": self._state,
                "rationale": rationale,
            },
        )

        target = self._transition_target(command)
        if target is None:
            self.log.append(
                EventType.PICARD_COMMAND_REJECTED,
                {
                    "run_id": self.run_id,
                    "command": command,
                    "state": self._state,
                    "rationale": rationale,
                },
            )
            raise ValueError(f"command {command} is invalid while state={self._state}")

        before = self._state
        self._state = target
        self.log.append(
            EventType.PICARD_STATE_CHANGED,
            {
                "run_id": self.run_id,
                "command": command,
                "state_before": before,
                "state_after": target,
                "rationale": rationale,
            },
        )
        return self._state

    def complete_graceful_stop(self, rationale: str = "checkpoint and shutdown complete") -> RunControlState:
        """Move QUIESCING to STOPPED after durable shutdown work completes."""
        if self._state != RunControlState.QUIESCING:
            raise ValueError("graceful stop can be completed only from QUIESCING")
        before = self._state
        self._state = RunControlState.STOPPED
        self.log.append(
            EventType.PICARD_STATE_CHANGED,
            {
                "run_id": self.run_id,
                "command": "complete_graceful_stop",
                "state_before": before,
                "state_after": self._state,
                "rationale": rationale,
            },
        )
        return self._state

    def issue_directive(
        self,
        preferred_action: str,
        rationale: str,
        authority: AuthorityLevel = AuthorityLevel.SOFT_DIRECTIVE,
    ) -> Directive:
        """Create a typed, auditable directive for the search layer."""
        if self._state not in {RunControlState.RUNNING, RunControlState.PAUSED}:
            raise ValueError("directives may be issued only to a running or paused run")
        if not preferred_action.strip() or not rationale.strip():
            raise ValueError("preferred_action and rationale must be nonempty")

        self._directive_counter += 1
        directive = Directive(
            directive_id=f"{self.run_id}:picard:{self._directive_counter:06d}",
            authority=authority,
            preferred_action=preferred_action,
            rationale=rationale,
        )
        self.log.append(
            EventType.PICARD_DIRECTIVE_ISSUED,
            {
                "run_id": self.run_id,
                "directive_id": directive.directive_id,
                "authority": directive.authority,
                "preferred_action": directive.preferred_action,
                "rationale": directive.rationale,
                "run_state": self._state,
            },
        )
        return directive

    def _transition_target(self, command: PicardCommand) -> RunControlState | None:
        if command == PicardCommand.EMERGENCY_STOP:
            if self._state in {RunControlState.STOPPED, RunControlState.EMERGENCY_STOP}:
                return None
            return RunControlState.EMERGENCY_STOP

        transitions: dict[tuple[RunControlState, PicardCommand], RunControlState] = {
            (RunControlState.CREATED, PicardCommand.START): RunControlState.RUNNING,
            (RunControlState.RUNNING, PicardCommand.PAUSE): RunControlState.PAUSED,
            (RunControlState.PAUSED, PicardCommand.RESUME): RunControlState.RUNNING,
            (RunControlState.RUNNING, PicardCommand.GRACEFUL_STOP): RunControlState.QUIESCING,
            (RunControlState.PAUSED, PicardCommand.GRACEFUL_STOP): RunControlState.QUIESCING,
            (RunControlState.CREATED, PicardCommand.GRACEFUL_STOP): RunControlState.QUIESCING,
        }
        return transitions.get((self._state, command))
