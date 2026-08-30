from data_atp.bank import SharedBank, select_by_kind


def test_rejected_candidate_never_enters_bank() -> None:
    bank = SharedBank()
    result = bank.deposit(
        "bad-certificate",
        deposited_by="P",
        verify=lambda _item: False,
        certificate_kind="proof",
    )
    assert result.accepted is False
    assert result.added is False
    assert len(bank) == 0


def test_verified_deposit_is_monotone_and_duplicate_is_idempotent() -> None:
    bank = SharedBank()
    before = set(bank.snapshot_ids())

    first = bank.deposit(
        "lemma-1",
        deposited_by="P",
        verify=lambda _item: True,
        certificate_kind="lemma",
    )
    after_first = set(bank.snapshot_ids())

    second = bank.deposit(
        "lemma-1",
        deposited_by="R",
        verify=lambda _item: True,
        certificate_kind="lemma",
    )
    after_second = set(bank.snapshot_ids())

    assert first.accepted and first.added
    assert before <= after_first <= after_second
    assert second.accepted and not second.added
    assert len(bank) == 1


def test_query_is_non_destructive() -> None:
    bank = SharedBank()
    bank.deposit("lemma-a", deposited_by="P", verify=lambda _item: True)
    bank.deposit("lemma-b", deposited_by="R", verify=lambda _item: True)

    before = bank.snapshot_ids()
    selected = bank.query("I", limit=1)
    after = bank.snapshot_ids()

    assert len(selected) == 1
    assert before == after
    assert len(bank) == 2


def test_cross_agent_reuse() -> None:
    bank = SharedBank()
    deposit = bank.deposit(
        "shared-lemma",
        deposited_by="P",
        verify=lambda _item: True,
        certificate_kind="lemma",
        metadata={"source": "P-turn"},
    )
    assert deposit.entry is not None

    selected_by_r = bank.query("R", selector=select_by_kind("lemma"))
    selected_by_i = bank.query("I", selector=select_by_kind("lemma"))
    selected_by_c = bank.query("C", selector=select_by_kind("lemma"))

    for selected in (selected_by_r, selected_by_i, selected_by_c):
        assert [entry.item for entry in selected] == ["shared-lemma"]

    assert bank.snapshot_ids() == (deposit.entry.entry_id,)


def test_selector_receives_agent_without_mutating_bank() -> None:
    bank = SharedBank()
    bank.deposit("p-only", deposited_by="P", verify=lambda _item: True)
    bank.deposit("r-only", deposited_by="R", verify=lambda _item: True)
    before = bank.snapshot_ids()

    def same_role(entry, state):
        return entry.deposited_by == state["agent"]

    p_view = bank.query("P", selector=same_role)
    r_view = bank.query("R", selector=same_role)

    assert [entry.item for entry in p_view] == ["p-only"]
    assert [entry.item for entry in r_view] == ["r-only"]
    assert bank.snapshot_ids() == before
