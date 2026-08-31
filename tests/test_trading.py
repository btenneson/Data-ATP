from __future__ import annotations

import pytest

from data_atp.trading import (
    FormalSystemPresentation,
    InferenceRule,
    PresentationCost,
    RuleAxiomTrade,
    TradeStatus,
    apply_verified_trades,
    choose_least_cost,
    finite_rule_axiom_candidate,
)


def test_proposed_trade_does_not_change_presentation() -> None:
    base = FormalSystemPresentation(
        name="base",
        axioms=("A",),
        rules=("induction", "modus_ponens"),
    )
    proposal = RuleAxiomTrade(
        rule_name="induction",
        traded_axiom="IND_AXIOM",
        status=TradeStatus.PROPOSED,
    )
    result = apply_verified_trades(base, (proposal,))
    assert result.original == base
    assert result.derived.axioms == base.axioms
    assert result.derived.rules == base.rules
    assert result.active_trades == ()
    assert result.inactive_trades == (proposal,)


def test_verified_trade_adjoins_axiom_and_preserves_other_rules() -> None:
    base = FormalSystemPresentation(
        name="base",
        axioms=("A",),
        rules=("induction", "modus_ponens"),
    )
    verified = RuleAxiomTrade(
        rule_name="induction",
        traded_axiom="IND_AXIOM",
        status=TradeStatus.VERIFIED,
        closure_equivalence_certificate="certificate:induction-trade-v1",
    )
    result = apply_verified_trades(base, (verified,), name="traded")
    assert result.original == base
    assert result.derived.name == "traded"
    assert result.derived.axioms == ("A", "IND_AXIOM")
    assert result.derived.rules == ("modus_ponens",)
    assert not result.rule_compliance_vacuous


def test_complete_verified_trade_has_empty_rule_set() -> None:
    base = FormalSystemPresentation(
        name="base",
        axioms=("A",),
        rules=("r1", "r2"),
    )
    trades = (
        RuleAxiomTrade(
            rule_name="r1",
            traded_axiom="AX1",
            status=TradeStatus.VERIFIED,
            closure_equivalence_certificate="c1",
        ),
        RuleAxiomTrade(
            rule_name="r2",
            traded_axiom="AX2",
            status=TradeStatus.VERIFIED,
            closure_equivalence_certificate="c2",
        ),
    )
    result = apply_verified_trades(base, trades)
    assert result.derived.rules == ()
    assert result.complete_trade
    assert result.rule_compliance_vacuous


def test_finite_rule_conversion_is_only_a_candidate() -> None:
    rule = InferenceRule(
        name="r",
        premises=("A", "A -> B"),
        conclusion="B",
    )
    trade = finite_rule_axiom_candidate(rule)
    assert trade.status is TradeStatus.PROPOSED
    assert not trade.activatable
    assert "A -> B" in trade.traded_axiom


def test_side_conditions_are_not_silently_encoded() -> None:
    rule = InferenceRule(
        name="generalization",
        premises=("P(x)",),
        conclusion="forall x P(x)",
        side_conditions=("x not free in assumptions",),
    )
    with pytest.raises(ValueError):
        finite_rule_axiom_candidate(rule)


def test_optimization_ignores_uncertified_presentation() -> None:
    candidates = (
        PresentationCost(
            presentation="original",
            expansions=100,
            wall_seconds=20,
            verifier_work=2,
            equivalence_certified=True,
        ),
        PresentationCost(
            presentation="fast-but-unverified",
            expansions=1,
            wall_seconds=1,
            verifier_work=1,
            equivalence_certified=False,
        ),
        PresentationCost(
            presentation="verified-trade",
            expansions=50,
            wall_seconds=10,
            verifier_work=2,
            equivalence_certified=True,
        ),
    )
    best = choose_least_cost(candidates)
    assert best.presentation == "verified-trade"
