from data_atp import (
    AgentStepResult,
    FutureBank,
    FutureProposal,
    PRICBankCoordinator,
    SharedBank,
)


def test_futurebank_is_separate_from_verified_bank():
    bank = SharedBank()
    future = FutureBank()
    coord = PRICBankCoordinator(bank, lambda kind, payload: payload == "proved", future)

    def p1(state, bank_view, future_view):
        assert len(bank_view.items) == 0
        assert len(future_view.items) == 0
        return AgentStepResult(
            output=None,
            future_proposal=FutureProposal(kind="lemma", payload="maybe"),
        )

    coord.step("P1", None, p1)
    assert len(coord.future_items()) == 1
    assert len(coord.shared_items()) == 0


def test_futurebank_visible_to_partner_next_step():
    coord = PRICBankCoordinator(SharedBank(), lambda kind, payload: False)

    coord.step(
        "P1",
        None,
        lambda state, bank_view, future_view: AgentStepResult(
            output=None,
            future_proposal=FutureProposal(kind="lemma", payload="candidate"),
        ),
    )

    def p2(state, bank_view, future_view):
        assert future_view.partner == "P1"
        assert [item.payload for item in future_view.items] == ["candidate"]
        assert len(bank_view.items) == 0
        return AgentStepResult(output="seen")

    assert coord.step("P2", None, p2).output == "seen"


def test_futurebank_promotion_requires_verifier():
    bank = SharedBank()
    future = FutureBank()
    item = future.propose(agent="QH", kind="lemma", payload="candidate")
    assert item is not None

    rejected = future.promote(
        item_id=item.item_id,
        bank=bank,
        verify=lambda kind, payload: False,
    )
    assert rejected == ()
    assert len(bank) == 0
    assert len(future) == 1


def test_verified_future_can_be_promoted_without_removing_future_history():
    bank = SharedBank()
    future = FutureBank()
    item = future.propose(agent="Professor", kind="lemma", payload="proved")
    assert item is not None

    added = future.promote(
        item_id=item.item_id,
        bank=bank,
        verify=lambda kind, payload: payload == "proved",
    )
    assert len(added) == 1
    assert added[0].payload == "proved"
    assert len(bank) == 1
    assert len(future) == 1
