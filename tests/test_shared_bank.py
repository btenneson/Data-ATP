from data_atp.shared_bank import SharedBank


def test_all_pric_agents_and_couples_share_bank():
    bank = SharedBank()
    bank.deposit_verified(kind="fact", payload={"x": 1}, provenance="P1")

    for agent, partner in {
        "P1": "P2", "P2": "P1",
        "R1": "R2", "R2": "R1",
        "I1": "I2", "I2": "I1",
        "C1": "C2", "C2": "C1",
    }.items():
        view = bank.view_for(agent)
        assert view.partner == partner
        assert len(view.items) == 1
        assert view.items[0].payload == {"x": 1}


def test_axiom_to_rule_trade_keeps_original():
    bank = SharedBank(axiom_to_rules=lambda axiom: [{"premise": axiom, "conclusion": "B"}])
    added = bank.deposit_verified(kind="axiom", payload="A", provenance="P1")

    assert [item.kind for item in added] == ["axiom", "rule"]
    assert bank.items()[0].payload == "A"
    assert bank.items()[1].metadata["trade_direction"] == "axiom_to_rule"


def test_rule_to_axiom_trade_keeps_original():
    bank = SharedBank(rule_to_axioms=lambda rule: [{"axiomatized": rule}])
    added = bank.deposit_verified(kind="rule", payload={"from": "A", "to": "B"}, provenance="R1")

    assert [item.kind for item in added] == ["rule", "axiom"]
    assert bank.items()[0].kind == "rule"
    assert bank.items()[1].metadata["trade_direction"] == "rule_to_axiom"


def test_rejected_proposal_never_enters_bank():
    bank = SharedBank()
    added = bank.propose(
        agent="I1",
        kind="lemma",
        payload="candidate",
        verify=lambda kind, payload: False,
    )
    assert added == ()
    assert len(bank) == 0


def test_accepted_proposal_is_visible_to_partner():
    bank = SharedBank()
    bank.propose(
        agent="C1",
        kind="lemma",
        payload="L",
        verify=lambda kind, payload: True,
    )
    assert bank.view_for("C2").items[0].payload == "L"
