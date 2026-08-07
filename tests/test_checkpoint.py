import json
from pathlib import Path
import tempfile
import unittest

from data_atp import CheckpointError, CheckpointManager, EventType, TransactionLog


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.log = TransactionLog()
        self.manager = CheckpointManager(self.directory, "run-sgrpcl-001", self.log)

    def test_atomic_save_and_restore(self):
        snapshot = {
            "frontier": ["goal-1", "goal-2"],
            "expansions": 17,
            "remaining_budget": 79983,
            "seed": 2301,
        }
        manifest = self.manager.save(snapshot, metadata={"target": "sgrpcl"})

        self.assertTrue(Path(manifest.checkpoint_path).exists())
        self.assertTrue(Path(manifest.sha256_path).exists())
        restored = self.manager.restore(manifest.checkpoint_path)
        self.assertEqual(restored["snapshot"], snapshot)
        self.assertEqual(restored["metadata"]["target"], "sgrpcl")
        self.assertEqual(len(tuple(self.log.events(EventType.CHECKPOINT_SAVED))), 1)
        self.assertEqual(len(tuple(self.log.events(EventType.CHECKPOINT_RESTORED))), 1)
        self.assertTrue(self.log.verify())

    def test_tampered_checkpoint_is_rejected(self):
        manifest = self.manager.save({"expansions": 3})
        path = Path(manifest.checkpoint_path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["snapshot"]["expansions"] = 999999
        path.write_text(json.dumps(payload), encoding="utf-8")

        with self.assertRaises(CheckpointError):
            self.manager.restore(path)
        self.assertEqual(len(tuple(self.log.events(EventType.CHECKPOINT_REJECTED))), 1)
        self.assertTrue(self.log.verify())

    def test_checkpoint_from_other_run_is_rejected(self):
        manifest = self.manager.save({"expansions": 3})
        other_log = TransactionLog()
        other = CheckpointManager(self.directory, "different-run", other_log)

        with self.assertRaises(CheckpointError):
            other.restore(manifest.checkpoint_path)
        self.assertEqual(len(tuple(other_log.events(EventType.CHECKPOINT_REJECTED))), 1)

    def test_sequence_continues_after_manager_restart(self):
        first = self.manager.save({"expansions": 1})
        restarted = CheckpointManager(self.directory, "run-sgrpcl-001", TransactionLog())
        second = restarted.save({"expansions": 2})
        self.assertEqual(first.checkpoint_sequence, 0)
        self.assertEqual(second.checkpoint_sequence, 1)


if __name__ == "__main__":
    unittest.main()
