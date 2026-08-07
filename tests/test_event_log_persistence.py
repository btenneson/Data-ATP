from pathlib import Path
import tempfile
import unittest

from data_atp import EventType, TransactionLog


class PersistentTransactionLogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "events.jsonl"

    def test_persist_and_reload_verified_chain(self):
        log = TransactionLog(self.path)
        first = log.append(EventType.ACTION_PROPOSED, {"action_id": "A1"})
        second = log.append(EventType.ACTION_EXECUTED, {"action_id": "A1"})
        self.assertTrue(self.path.exists())
        self.assertEqual(len(log), 2)
        self.assertEqual(log.last_digest, second.digest)

        reloaded = TransactionLog(self.path)
        self.assertEqual(len(reloaded), 2)
        self.assertEqual(reloaded.last_digest, second.digest)
        self.assertEqual(tuple(reloaded.events())[0].digest, first.digest)
        self.assertTrue(reloaded.verify())

    def test_tampered_persistent_log_fails_closed(self):
        log = TransactionLog(self.path)
        log.append(EventType.ACTION_PROPOSED, {"action_id": "A1"})
        text = self.path.read_text(encoding="utf-8")
        self.path.write_text(text.replace("A1", "A9"), encoding="utf-8")

        with self.assertRaises(ValueError):
            TransactionLog(self.path)

    def test_in_memory_api_still_works(self):
        log = TransactionLog()
        log.append(EventType.ACTION_PROPOSED, {"action_id": "A1"})
        self.assertEqual(len(log), 1)
        self.assertTrue(log.verify())
        self.assertIsNone(log.path)


if __name__ == "__main__":
    unittest.main()
