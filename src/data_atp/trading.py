from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite
from typing import Iterable


class TradeStatus(str, Enum):
    """Lifecycle state for a proposed rule-to-axiom trade."""

    PROPOSED = "proposed"
    VERIFIED = "verified"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class InferenceRule:
    """Presentation-level description of an inference rule.

    This is intentionally syntax-neutral.  DATA-MIND 2.5 does not alter the
    underlying Metamath proof kernel from this object alone.
    """

    name: str
    premises: tuple[str, ...]
    conclusion: str
    side_conditions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("rule name must be non-empty")
        if not self.conclusion.strip():
            raise ValueError("rule conclusion must be non-empty")


@dataclass(frozen=True, slots=True)
class RuleAxiomTrade:
    """A candidate image of an inference rule under a trading map tau.

    A trade is *activatable* only after a closure-equivalence certificate is
    attached.  A string certificate is provenance metadata here; it is not a
    substitute for the independent mathematical verifier.
    """

    rule_name: str
    traded_axiom: str
    status: TradeStatus = TradeStatus.PROPOSED
    closure_equivalence_certificate: str | None = None
    provenance: str = ""

    def __post_init__(self) -> None:
        if not self.rule_name.strip():
            raise ValueError("rule_name must be non-empty")
        if not self.traded_axiom.strip():
            raise ValueError("traded_axiom must be non-empty")

    @property
    def activatable(self) -> bool:
        return (
            self.status is TradeStatus.VERIFIED
            and bool(self.closure_equivalence_certificate)
        )


@dataclass(frozen=True, slots=True)
class FormalSystemPresentation:
    """A presentation of fixed mathematical content by axioms and rules."""

    name: str
    axioms: tuple[str, ...]
    rules: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class TradeApplication:
    original: FormalSystemPresentation
    derived: FormalSystemPresentation
    active_trades: tuple[RuleAxiomTrade, ...]
    inactive_trades: tuple[RuleAxiomTrade, ...]

    @property
    def complete_trade(self) -> bool:
        return bool(self.active_trades) and not self.derived.rules

    @property
    def rule_compliance_vacuous(self) -> bool:
        """True exactly at the no-inference-rule endpoint R = emptyset."""

        return not self.derived.rules


def apply_verified_trades(
    presentation: FormalSystemPresentation,
    trades: Iterable[RuleAxiomTrade],
    *,
    name: str | None = None,
) -> TradeApplication:
    """Create a new presentation without mutating or overwriting the original.

    Only VERIFIED trades with a closure-equivalence certificate are activated.
    Every untraded rule remains present.  Traded axioms are adjoined; existing
    axioms are preserved.
    """

    trades = tuple(trades)
    known_rules = set(presentation.rules)
    active: list[RuleAxiomTrade] = []
    inactive: list[RuleAxiomTrade] = []

    for trade in trades:
        if trade.rule_name not in known_rules:
            raise ValueError(f"trade refers to absent rule: {trade.rule_name}")
        (active if trade.activatable else inactive).append(trade)

    removed = {trade.rule_name for trade in active}
    new_rules = tuple(rule for rule in presentation.rules if rule not in removed)
    new_axioms = list(presentation.axioms)
    for trade in active:
        if trade.traded_axiom not in new_axioms:
            new_axioms.append(trade.traded_axiom)

    derived = FormalSystemPresentation(
        name=name or f"{presentation.name}+trade",
        axioms=tuple(new_axioms),
        rules=new_rules,
    )
    return TradeApplication(
        original=presentation,
        derived=derived,
        active_trades=tuple(active),
        inactive_trades=tuple(inactive),
    )


def finite_rule_axiom_candidate(rule: InferenceRule) -> RuleAxiomTrade:
    """Form the obvious implication-shaped *candidate* for a finite rule.

    This helper never certifies the trade.  Side-conditioned rules require a
    separate formal treatment and are rejected here rather than silently
    encoded unsafely.
    """

    if rule.side_conditions:
        raise ValueError("side-conditioned rules require an explicit trade")
    if not rule.premises:
        formula = rule.conclusion
    elif len(rule.premises) == 1:
        formula = f"({rule.premises[0]}) -> ({rule.conclusion})"
    else:
        antecedent = " & ".join(f"({p})" for p in rule.premises)
        formula = f"({antecedent}) -> ({rule.conclusion})"
    return RuleAxiomTrade(
        rule_name=rule.name,
        traded_axiom=formula,
        status=TradeStatus.PROPOSED,
        provenance="finite-rule implication candidate; equivalence unverified",
    )


def induction_trade_example() -> RuleAxiomTrade:
    """The abstract induction example discussed in the Trading Theorem work."""

    return RuleAxiomTrade(
        rule_name="induction",
        traded_axiom=(
            "(P(0) & forall n (P(n) -> P(n+1))) -> forall n P(n)"
        ),
        status=TradeStatus.PROPOSED,
        provenance="abstract induction rule-to-axiom example",
    )


@dataclass(frozen=True, slots=True)
class PresentationCost:
    """Measured proof-search cost for one certified-equivalent presentation."""

    presentation: str
    expansions: float = 0.0
    wall_seconds: float = 0.0
    verifier_work: float = 0.0
    peak_memory_mb: float = 0.0
    proof_length: float = 0.0
    equivalence_certified: bool = False

    def weighted_score(
        self,
        *,
        expansions: float = 1.0,
        wall_seconds: float = 1.0,
        verifier_work: float = 1.0,
        peak_memory_mb: float = 0.0,
        proof_length: float = 0.0,
    ) -> float:
        values = (
            self.expansions,
            self.wall_seconds,
            self.verifier_work,
            self.peak_memory_mb,
            self.proof_length,
        )
        if not all(isfinite(float(v)) and float(v) >= 0 for v in values):
            raise ValueError("presentation costs must be finite and non-negative")
        return (
            expansions * self.expansions
            + wall_seconds * self.wall_seconds
            + verifier_work * self.verifier_work
            + peak_memory_mb * self.peak_memory_mb
            + proof_length * self.proof_length
        )


def choose_least_cost(
    candidates: Iterable[PresentationCost],
    **weights: float,
) -> PresentationCost:
    """Solve the practical Trading Optimization Problem over certified views."""

    certified = tuple(c for c in candidates if c.equivalence_certified)
    if not certified:
        raise ValueError("no closure-equivalence-certified presentation supplied")
    return min(certified, key=lambda c: c.weighted_score(**weights))
