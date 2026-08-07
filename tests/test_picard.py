import unittest

from data_atp import (
    AccountableAutonomyController,
    AccountableSearchEngine,
    ActionCandidate,
    AuthorityLevel,
    Decision,
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

    def test_paused_picard_blocks_search_engine(self):
        self.picard.command(PicardCommand.START, "begin run")
        directive = self.picard.issue_directive("coverage", "normal search policy")
        self.picard.command(PicardCommand.PAUSE, "operator pause interrupt")

        controller = AccountableAutonomyController(self.log)
        engine = AccountableSearchEngine(self.log, controller, self.picard)
        action = ActionCandidate("A1", "coverage", True, 1, "coverage")
        outcome = engine.run_action(
            directive,
            action,
            evidence=None,
            remaining_budget=100,
            execute=lambda _: "certificate-should-not-run",
            verify=lambda _: True,
        )
        self.assertFalse(outcome.executed)
        self.assertEqual(outcome.decision.decision, Decision.REJECT_RUN_CONTROL)
        self.assertEqual(outcome.remaining_budget, 100)
        self.assertTrue(self.log.verify())

    def test_running_picard_allows_search_engine(self):
        self.picard.command(PicardCommand.START, "begin run")
        directive = self.picard.issue_directive("coverage", "normal search policy")

        controller = AccountableAutonomyController(self.log)
        engine = AccountableSearchEngine(self.log, controller, self.picard)
        action = ActionCandidate("A2", "coverage", True, 1, "coverage")
        outcome = engine.run_action(
            directive,
            action,
            evidence=None,
            remaining_budget=100,
            execute=lambda _: "verified-certificate",
            verify=lambda certificate: certificate == "verified-certificate",
        )
        self.assertTrue(outcome.executed)
        self.assertTrue(outcome.verifier_accepted)
        self.assertEqual(outcome.remaining_budget, 99)
        self.assertTrue(self.log.verify())


if __name__ == "__main__":
    unittest.main()
