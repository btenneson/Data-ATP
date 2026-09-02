import unittest

from data_atp import (
    DATA_MIND_ARCHITECTURE_VERSION,
    AgentProposal,
    AgentStepResult,
    FederatedBank,
    FutureProposal,
    PRICBankCoordinator,
    PropagationMode,
    SharedBank,
)


def accept_all(kind, payload):
    return True


def reject_all(kind, payload):
    return False


class FederatedBankTests(unittest.TestCase):
    def test_architecture_version_is_2_10(self):
        self.assertEqual(DATA_MIND_ARCHITECTURE_VERSION, "2.10")

    def test_core_is_logically_shared_without_physical_copy(self):
        bank = SharedBank()
        federation = FederatedBank(core=bank)
        federation.propose(
            agent="P1",
            kind="lemma",
            payload="L-core",
            verify=accept_all,
            propagation=PropagationMode.CORE,
        )
        self.assertEqual(len(federation.core_items()), 1)
        self.assertEqual(len(federation.local_items("P1")), 0)
        self.assertEqual(len(federation.local_items("R1")), 0)
        self.assertEqual([x.payload for x in federation.view_for("R1").items], ["L-core"])

    def test_local_storage_is_visible_to_source_and_coupled_neighbor_only(self):
        federation = FederatedBank(core=SharedBank())
        federation.propose(
            agent="P1",
            kind="lemma",
            payload="L-local",
            verify=accept_all,
            propagation=PropagationMode.LOCAL,
        )
        self.assertEqual([x.payload for x in federation.local_items("P1")], ["L-local"])
        self.assertIn("L-local", [x.payload for x in federation.view_for("P1").items])
        self.assertIn("L-local", [x.payload for x in federation.view_for("P2").items])
        self.assertNotIn("L-local", [x.payload for x in federation.view_for("R1").items])

    def test_coupled_mode_physically_copies_to_declared_neighbors(self):
        federation = FederatedBank(core=SharedBank())
        federation.propose(
            agent="PROFESSOR",
            kind="fact",
            payload="partial-credit-signal",
            verify=accept_all,
            propagation=PropagationMode.COUPLED,
        )
        self.assertIn("partial-credit-signal", [x.payload for x in federation.local_items("PROFESSOR")])
        self.assertIn("partial-credit-signal", [x.payload for x in federation.local_items("COMPASS")])
        self.assertIn("partial-credit-signal", [x.payload for x in federation.local_items("CHILD")])
        self.assertEqual(len(federation.core_items()), 0)

    def test_broadcast_materializes_to_all_nodes_and_core(self):
        federation = FederatedBank(core=SharedBank(), departments=("P1", "R1", "QH"), couplings={})
        federation.propose(
            agent="P1",
            kind="lemma",
            payload="L-all",
            verify=accept_all,
            propagation=PropagationMode.BROADCAST,
        )
        self.assertEqual([x.payload for x in federation.core_items()], ["L-all"])
        for department in federation.departments():
            self.assertEqual([x.payload for x in federation.local_items(department)], ["L-all"])

    def test_rejected_item_enters_no_bank(self):
        federation = FederatedBank(core=SharedBank())
        result = federation.propose(
            agent="P1",
            kind="lemma",
            payload="bad",
            verify=reject_all,
            propagation=PropagationMode.BROADCAST,
        )
        self.assertEqual(result, ())
        self.assertEqual(len(federation.core_items()), 0)
        self.assertTrue(all(len(federation.local_items(d)) == 0 for d in federation.departments()))

    def test_pric_coordinator_uses_federated_view_and_keeps_futurebank_separate(self):
        bank = SharedBank()
        coordinator = PRICBankCoordinator(bank=bank, verify=accept_all)
        observed = {}

        def p1_module(state, bank_view, future_view):
            observed["has_components"] = all(
                hasattr(bank_view, name)
                for name in ("core_items", "local_items", "coupled_items", "coupled_departments")
            )
            return AgentStepResult(
                output="p1",
                proposal=AgentProposal("lemma", "verified", propagation=PropagationMode.CORE),
                future_proposal=FutureProposal("lemma", "speculative"),
            )

        coordinator.step("P1", None, p1_module)
        self.assertTrue(observed["has_components"])
        self.assertEqual([x.payload for x in coordinator.shared_items()], ["verified"])
        self.assertEqual([x.payload for x in coordinator.future_items()], ["speculative"])
        self.assertNotIn("speculative", [x.payload for x in coordinator.federated_items("R1")])


if __name__ == "__main__":
    unittest.main()
