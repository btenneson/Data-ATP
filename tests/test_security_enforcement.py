import unittest

from data_atp import (
    AccountableAutonomyController,
    AccountableSearchEngine,
    ActionCandidate,
    AuthorityLevel,
    Decision,
    Directive,
    EventType,
    SecurityClass,
    SecurityFlag,
    SentinelDecision,
    TransactionLog,
)


class SentinelEnforcementTests(unittest.TestCase):
    def setUp(self):
        self.log = TransactionLog()
        self.controller = AccountableAutonomyController(self.log)
        self.engine = AccountableSearchEngine(self.log, self.controller)
        self.directive = Directive(
            "D-sec",
            AuthorityLevel.SOFT_DIRECTIVE,
            "search",
            "security enforcement test",
        )

    def test_benign_internal_search_executes(self):
        action = ActionCandidate("A-safe", "search", True, 3, "resume")
        outcome = self.engine.run_action(
            self.directive,
            action,
            evidence=None,
            remaining_budget=20,
            execute=lambda _: "certificate",
            verify=lambda c: c == "certificate",
        )
        self.assertTrue(outcome.executed)
        self.assertTrue(outcome.verifier_accepted)
        self.assertEqual(outcome.security_assessment.decision, SentinelDecision.ALLOW_INTERNAL)
        self.assertTrue(self.log.verify())

    def test_tripwire_blocks_before_execute_and_preserves_budget(self):
        executed = []
        action = ActionCandidate(
            "A-tripwire",
            "search",
            True,
            7,
            "resume",
            capabilities=frozenset({"credential_access", "network"}),
            target_scope="external",
            security_class=SecurityClass.HIGH_RISK,
        )
        outcome = self.engine.run_action(
            self.directive,
            action,
            evidence=None,
            remaining_budget=20,
            execute=lambda _: executed.append(True) or "should-not-run",
            verify=lambda _: True,
        )
        self.assertFalse(outcome.executed)
        self.assertEqual(outcome.decision.decision, Decision.REJECT_SECURITY)
        self.assertEqual(outcome.remaining_budget, 20)
        self.assertEqual(executed, [])
        self.assertEqual(outcome.security_assessment.decision, SentinelDecision.BLOCK)
        self.assertGreaterEqual(len(self.engine.sentinel.quarantine.records()), 1)

    def test_every_new_transaction_has_security_flag(self):
        self.log.append(EventType.ACTION_PROPOSED, {"action_id": "A1"})
        self.log.append(
            EventType.SENTINEL_ASSESSED,
            {"security_class": SecurityClass.DUAL_USE, "risk_score": 0.30},
        )
        self.log.append(
            EventType.SENTINEL_BLOCKED,
            {"security_class": SecurityClass.PROHIBITED, "decision": SentinelDecision.BLOCK},
        )
        flags = [tx.payload.get("_security_flag") for tx in self.log.events()]
        self.assertEqual(flags[0], SecurityFlag.BENIGN)
        self.assertEqual(flags[1], SecurityFlag.MALIGNANCY_LOW)
        self.assertEqual(flags[2], SecurityFlag.MALIGNANCY_CRITICAL)
        self.assertTrue(all(flag is not None for flag in flags))
        self.assertTrue(self.log.verify())


if __name__ == "__main__":
    unittest.main()
