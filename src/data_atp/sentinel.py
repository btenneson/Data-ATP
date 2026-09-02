"""DATA-MIND 2.9 Sentinel security governor.

Sentinel is a fail-closed policy layer around reasoning and execution.  It does
not decide mathematical truth; it decides whether an otherwise valid action may
run, must remain internal, must be quarantined, requires human authorization,
or is blocked.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from time import time
from typing import FrozenSet, Mapping


class SecurityClass(str, Enum):
    BENIGN = "benign"
    DUAL_USE = "dual_use"
    HIGH_RISK = "high_risk"
    PROHIBITED = "prohibited"


class SentinelDecision(str, Enum):
    ALLOW_INTERNAL = "allow_internal"
    ALLOW_EXPORT = "allow_export"
    QUARANTINE = "quarantine"
    REQUIRE_HUMAN = "require_human"
    BLOCK = "block"


@dataclass(frozen=True, slots=True)
class ResourceSample:
    elapsed_seconds: float = 0.0
    ram_fraction: float = 0.0
    cpu_fraction: float = 0.0
    expansion_rate: float = 0.0


@dataclass(frozen=True, slots=True)
class ActionContext:
    action: str
    capabilities: FrozenSet[str] = frozenset()
    target_scope: str = "internal"
    security_class: SecurityClass = SecurityClass.BENIGN
    formal_verified: bool = False
    human_approved: bool = False
    metadata: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SecurityAssessment:
    decision: SentinelDecision
    risk_score: float
    reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SentinelPolicy:
    """Conservative defaults for DATA-MIND 2.9.

    Capability names are intentionally generic.  Adapters may use narrower
    names, but anything capable of changing or contacting an external system
    should map to ``external_write``, ``network``, or ``code_execution``.
    """

    internal_risk_threshold: float = 0.45
    export_risk_threshold: float = 0.25
    max_ram_fraction: float = 0.40
    max_elapsed_seconds: float = 120.0
    high_risk_capabilities: FrozenSet[str] = frozenset(
        {"network", "external_write", "code_execution", "credential_access"}
    )
    forbidden_pairs: tuple[FrozenSet[str], ...] = (
        frozenset({"credential_access", "network"}),
        frozenset({"privilege_escalation", "external_write"}),
        frozenset({"persistence", "stealth"}),
        frozenset({"key_recovery", "third_party_target"}),
    )


@dataclass(frozen=True, slots=True)
class QuarantineRecord:
    timestamp: float
    context: ActionContext
    assessment: SecurityAssessment


class QuarantineBank:
    """Append-only isolation store for high-risk discoveries."""

    def __init__(self) -> None:
        self._records: list[QuarantineRecord] = []

    def deposit(self, context: ActionContext, assessment: SecurityAssessment) -> QuarantineRecord:
        record = QuarantineRecord(time(), context, assessment)
        self._records.append(record)
        return record

    def records(self) -> tuple[QuarantineRecord, ...]:
        return tuple(self._records)


class SecurityGovernor:
    """Fail-closed security gate for DATA-MIND reasoning and tool actions."""

    _CLASS_RISK = {
        SecurityClass.BENIGN: 0.05,
        SecurityClass.DUAL_USE: 0.30,
        SecurityClass.HIGH_RISK: 0.70,
        SecurityClass.PROHIBITED: 1.00,
    }

    def __init__(self, policy: SentinelPolicy | None = None, quarantine: QuarantineBank | None = None) -> None:
        self.policy = policy or SentinelPolicy()
        self.quarantine = quarantine or QuarantineBank()

    def assess(self, context: ActionContext, resources: ResourceSample | None = None) -> SecurityAssessment:
        resources = resources or ResourceSample()
        reasons: list[str] = []
        caps = set(context.capabilities)

        if not context.formal_verified:
            reasons.append("formal verification missing")

        for pair in self.policy.forbidden_pairs:
            if pair.issubset(caps):
                assessment = SecurityAssessment(
                    SentinelDecision.BLOCK,
                    1.0,
                    tuple(reasons + [f"tripwire capability combination: {sorted(pair)}"]),
                )
                self.quarantine.deposit(context, assessment)
                return assessment

        if context.security_class is SecurityClass.PROHIBITED:
            assessment = SecurityAssessment(
                SentinelDecision.BLOCK,
                1.0,
                tuple(reasons + ["action classified prohibited"]),
            )
            self.quarantine.deposit(context, assessment)
            return assessment

        resource_risk = 0.0
        if resources.ram_fraction > self.policy.max_ram_fraction:
            resource_risk += 0.25
            reasons.append("RAM outlier")
        if resources.elapsed_seconds > self.policy.max_elapsed_seconds:
            resource_risk += 0.25
            reasons.append("runtime outlier")

        capability_risk = 0.20 if caps & self.policy.high_risk_capabilities else 0.0
        if capability_risk:
            reasons.append("elevated capability requested")

        external_risk = 0.20 if context.target_scope != "internal" else 0.0
        if external_risk:
            reasons.append("external target scope")

        risk = min(1.0, self._CLASS_RISK[context.security_class] + resource_risk + capability_risk + external_risk)

        if context.security_class is SecurityClass.HIGH_RISK or (
            external_risk and capability_risk
        ):
            if not context.human_approved:
                assessment = SecurityAssessment(
                    SentinelDecision.REQUIRE_HUMAN,
                    risk,
                    tuple(reasons + ["human authorization required"]),
                )
                self.quarantine.deposit(context, assessment)
                return assessment

        if risk > self.policy.internal_risk_threshold:
            assessment = SecurityAssessment(
                SentinelDecision.QUARANTINE,
                risk,
                tuple(reasons + ["risk exceeds internal threshold"]),
            )
            self.quarantine.deposit(context, assessment)
            return assessment

        if not context.formal_verified:
            return SecurityAssessment(
                SentinelDecision.QUARANTINE,
                risk,
                tuple(reasons),
            )

        if context.target_scope == "internal":
            return SecurityAssessment(SentinelDecision.ALLOW_INTERNAL, risk, tuple(reasons))

        if risk <= self.policy.export_risk_threshold:
            return SecurityAssessment(SentinelDecision.ALLOW_EXPORT, risk, tuple(reasons))

        assessment = SecurityAssessment(
            SentinelDecision.QUARANTINE,
            risk,
            tuple(reasons + ["export threshold exceeded"]),
        )
        self.quarantine.deposit(context, assessment)
        return assessment
