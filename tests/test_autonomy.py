import unittest

from data_atp import (
    AccountableAutonomyController,
    AccountableSearchEngine,
    ActionCandidate,
    AuthorityLevel,
    Decision,
    Directive,
    Evidence,
    EventType,
    ExceptionPolicy,
    TransactionLog,
)


class AutonomyTests(unittest.TestCase):
    def setUp(self):
        self.log = TransactionLog()
        self.controller = AccountableAutonomyController(
            self.log,
            ExceptionPolicy(
                minimum_evidence_strength=0.8,
                minimum_expected_gain=0.6,
                protected_reserve=10,
            ),
        )

    def test_illegal_action_is_rejected_before_override(self):
        directive = Directive("D1", AuthorityLevel.SOFT_DIRECTIVE, "retreat", "scheduler")
        action = ActionCandidate("A1", "inspect_signal", False, 3, "resume-retreat")
        evidence = Evidence("E1", "transient local signature", 1.0, 1.0, True)
        result = self.controller.decide(directive, action, evidence, 100)
        self.assertEqual(result.decision, Decision.REJECT_ILLEGAL)
        self.assertEqual(len(tuple(self.log.events(EventType.LOCAL_EVIDENCE_DETECTED))), 0)

    def test_hard_invariant_cannot_be_overridden(self):
        directive = Directive("D2", AuthorityLevel.HARD_INVARIANT, "reject_illegal", "logic")
        action = ActionCandidate("A2", "accept_unverified", True, 1, "none")
        evidence = Evidence("E2", "high score", 1.0, 1.0, True)
        result = self.controller.decide(directive, action, evidence, 100)
        self.assertEqual(result.decision, Decision.REJECT_HARD_CONFLICT)

    def test_soft_directive_can_be_overridden_and_self_reported(self):
        directive = Directive("D3", AuthorityLevel.SOFT_DIRECTIVE, "return_to_coverage", "fleet policy")
        action = ActionCandidate("A3", "inspect_transient_lemma", True, 5, "coverage-level-2")
        evidence = Evidence("E3", "brief high-value lemma signature", 0.95, 0.85, True)
        engine = AccountableSearchEngine(self.log, self.controller)
        outcome = engine.run_action(
            directive,
            action,
            evidence,
            remaining_budget=50,
            execute=lambda _: "proof-certificate",
            verify=lambda certificate: certificate == "proof-certificate",
        )
        self.assertEqual(outcome.decision.decision, Decision.OVERRIDE_SOFT_DIRECTIVE)
        self.assertTrue(outcome.verifier_accepted)
        self.assertEqual(len(tuple(self.log.events(EventType.SELF_REPORT_FILED))), 1)
        self.assertTrue(self.log.verify())

    def test_protected_reserve_blocks_exception(self):
        directive = Directive("D4", AuthorityLevel.SOFT_DIRECTIVE, "coverage", "scheduler")
        action = ActionCandidate("A4", "local_branch", True, 6, "coverage")
        evidence = Evidence("E4", "signal", 0.99, 0.99, True)
        result = self.controller.decide(directive, action, evidence, remaining_budget=15)
        self.assertEqual(result.decision, Decision.REJECT_BUDGET)


if __name__ == "__main__":
    unittest.main()
