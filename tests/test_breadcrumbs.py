from pathlib import Path
import tempfile
import unittest

from data_atp import BreadcrumbManager, EventType


class BreadcrumbTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_breadcrumb_and_checkpoint_are_durable_and_chained(self):
        manager = BreadcrumbManager(self.root, "run-001")
        snapshot = {
            "architecture_version": "2.11",
            "phase": "pre_prover",
            "attempt_index": 0,
            "next_attempt_index": 0,
            "recovery_action": "restart_current_attempt",
        }
        receipt = manager.record("PRE_EXTERNAL_PROVER", snapshot, metadata={"target": "GRP619"})

        self.assertIsNotNone(receipt.checkpoint)
        self.assertTrue(Path(receipt.checkpoint.checkpoint_path).is_file())
        self.assertTrue(manager.verify())
        self.assertEqual(len(tuple(manager.log.events(EventType.BREADCRUMB_RECORDED))), 1)
        self.assertEqual(len(tuple(manager.log.events(EventType.CHECKPOINT_SAVED))), 1)

        restored = manager.restore_latest()
        self.assertEqual(restored["snapshot"], snapshot)
        self.assertEqual(
            restored["metadata"]["breadcrumb_transaction_digest"],
            receipt.transaction_digest,
        )
        self.assertTrue(manager.verify())

    def test_restart_continues_existing_chain_and_checkpoint_sequence(self):
        first = BreadcrumbManager(self.root, "run-001")
        r1 = first.record("START", {"architecture_version": "2.11", "phase": "start"})
        first_head = first.chain_head

        restarted = BreadcrumbManager(self.root, "run-001")
        self.assertEqual(restarted.chain_head, first_head)
        r2 = restarted.record("RESUME", {"architecture_version": "2.11", "phase": "resume"})

        self.assertGreater(r2.transaction_sequence, r1.transaction_sequence)
        self.assertEqual(r1.checkpoint.checkpoint_sequence, 0)
        self.assertEqual(r2.checkpoint.checkpoint_sequence, 1)
        self.assertTrue(restarted.verify())

    def test_heartbeat_can_be_small_without_full_checkpoint(self):
        manager = BreadcrumbManager(self.root, "run-001")
        receipt = manager.record(
            "PROVER_HEARTBEAT",
            {
                "architecture_version": "2.11",
                "phase": "external_prover_running",
                "attempt_index": 2,
                "next_attempt_index": 2,
                "recovery_action": "restart_current_attempt",
            },
            checkpoint=False,
        )
        self.assertIsNone(receipt.checkpoint)
        self.assertTrue(manager.verify())


if __name__ == "__main__":
    unittest.main()
