import unittest

from data_atp import (
    AuthorityLevel,
    EventType,
    PicardCommand,
    PicardController,
    RunControlState,
    TransactionLog,
)


class PicardTests(unittest.TestCase):
    def setUp(self):
        self.log = TransactionLog()
        self.picard = PicardController("run-sgrpcl-001", self.log)

    def test_start_pause_resume_and_graceful_stop(self):
        self.assertEqual(self.picard.state, RunControlState.CREATED)
        self.picard.command(PicardCommand.START, "begin bounded sgrpcl experiment")
        self.assertTrue(self.picard.status().may_dispatch_work)
        self.assertTrue(self.picard.status().may_commit_trusted_state)

        self.picard.command(PicardCommand.PAUSE, "operator requested inspection")
        self.assertEqual(self.picard.state, RunControlState.PAUSED)
        self.assertFalse(self.picard.status().may_dispatch_work)
        self.assertFalse(self.picard.status().may_commit_trusted_state)

        self.picard.command(PicardCommand.RESUME, "inspection complete")
        self.assertEqual(self.picard.state, RunControlState.RUNNING)

        self.picard.command(PicardCommand.GRACEFUL_STOP, "save checkpoint and stop")
        self.assertEqual(self.picard.state, RunControlState.QUIESCING)
        self.assertFalse(self.picard.status().may_dispatch_work)
        self.picard.complete_graceful_stop()
        self.assertEqual(self.picard.state, RunControlState.STOPPED)
        self.assertTrue(self.log.verify())

    def test_emergency_stop_is_terminal(self):
        self.picard.command(PicardCommand.START, "begin run")
        self.picard.command(PicardCommand.EMERGENCY_STOP, "operator kill switch")
        self.assertEqual(self.picard.state, RunControlState.EMERGENCY_STOP)
        self.assertFalse(self.picard.status().may_dispatch_work)
        self.assertFalse(self.picard.status().may_commit_trusted_state)
        with self.assertRaises(ValueError):
            self.picard.command(PicardCommand.RESUME, "attempt restart")
        self.assertEqual(
            len(tuple(self.log.events(EventType.PICARD_COMMAND_REJECTED))),
            1,
        )

    def test_directives_are_typed_logged_and_numbered(self):
        self.picard.command(PicardCommand.START, "begin run")
        soft = self.picard.issue_directive(
            "explore_lemma_branch",
            "temporary search preference",
        )
        hard = self.picard.issue_directive(
            "reject_unverified",
            "trusted state requires verifier approval",
            AuthorityLevel.HARD_INVARIANT,
        )
        self.assertEqual(soft.authority, AuthorityLevel.SOFT_DIRECTIVE)
        self.assertEqual(hard.authority, AuthorityLevel.HARD_INVARIANT)
        self.assertNotEqual(soft.directive_id, hard.directive_id)
        self.assertEqual(
            len(tuple(self.log.events(EventType.PICARD_DIRECTIVE_ISSUED))),
            2,
        )
        self.assertTrue(self.log.verify())

    def test_invalid_transition_is_rejected_and_logged(self):
        with self.assertRaises(ValueError):
            self.picard.command(PicardCommand.RESUME, "cannot resume before start")
        self.assertEqual(self.picard.state, RunControlState.CREATED)
        self.assertEqual(
            len(tuple(self.log.events(EventType.PICARD_COMMAND_REJECTED))),
            1,
        )
        self.assertTrue(self.log.verify())


if __name__ == "__main__":
    unittest.main()
