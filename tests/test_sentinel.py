import unittest

from data_atp import (
    ActionContext,
    ResourceSample,
    SecurityClass,
    SecurityGovernor,
    SentinelDecision,
)


class SentinelTests(unittest.TestCase):
    def test_verified_benign_internal_action_is_allowed(self) -> None:
        governor = SecurityGovernor()
        assessment = governor.assess(
            ActionContext(
                action="verify theorem",
                formal_verified=True,
                security_class=SecurityClass.BENIGN,
            )
        )
        self.assertEqual(assessment.decision, SentinelDecision.ALLOW_INTERNAL)

    def test_unverified_result_is_quarantined(self) -> None:
        governor = SecurityGovernor()
        assessment = governor.assess(ActionContext(action="new conjecture"))
        self.assertEqual(assessment.decision, SentinelDecision.QUARANTINE)
        self.assertEqual(len(governor.quarantine.records()), 1)

    def test_resource_outliers_quarantine(self) -> None:
        governor = SecurityGovernor()
        assessment = governor.assess(
            ActionContext(action="large signature", formal_verified=True),
            ResourceSample(elapsed_seconds=121.0, ram_fraction=0.41),
        )
        self.assertEqual(assessment.decision, SentinelDecision.QUARANTINE)
        self.assertIn("RAM outlier", assessment.reasons)
        self.assertIn("runtime outlier", assessment.reasons)

    def test_external_elevated_capability_requires_human(self) -> None:
        governor = SecurityGovernor()
        assessment = governor.assess(
            ActionContext(
                action="controlled external integration",
                capabilities=frozenset({"network"}),
                target_scope="external",
                security_class=SecurityClass.DUAL_USE,
                formal_verified=True,
            )
        )
        self.assertEqual(assessment.decision, SentinelDecision.REQUIRE_HUMAN)

    def test_tripwire_pair_is_blocked_fail_closed(self) -> None:
        governor = SecurityGovernor()
        assessment = governor.assess(
            ActionContext(
                action="unsafe combination",
                capabilities=frozenset({"credential_access", "network"}),
                target_scope="external",
                security_class=SecurityClass.HIGH_RISK,
                formal_verified=True,
                human_approved=True,
            )
        )
        self.assertEqual(assessment.decision, SentinelDecision.BLOCK)
        self.assertEqual(len(governor.quarantine.records()), 1)


if __name__ == "__main__":
    unittest.main()
