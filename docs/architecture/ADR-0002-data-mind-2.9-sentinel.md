# ADR-0002: DATA-MIND 2.9 Sentinel Security Architecture

Status: Accepted

## Decision

DATA-MIND 2.9 introduces Sentinel as a first-class security governor surrounding the existing reasoning, BANK, verifier, and execution boundaries.

The architectural invariant is:

> Mathematical validity is necessary but not sufficient for execution or export.

An action may leave the internal reasoning environment only when both formal verification and security policy permit it. High-risk external actions additionally require explicit human authorization.

## Components

1. **Resource Sentinel** monitors abnormal runtime and memory use and converts resource outliers into risk rather than simply allowing an expensive strategy to continue unchecked.
2. **Capability Firewall** treats network access, external writes, code execution, and credential access as elevated capabilities. Capability combinations may trigger fail-closed tripwires.
3. **Security Governor** classifies actions as benign, dual-use, high-risk, or prohibited and returns one of five decisions: allow internal, allow export, quarantine, require human, or block.
4. **Quarantine BANK** is append-only and preserves high-risk or unverified discoveries without making them automatically consumable as operational actions.
5. **Human authorization boundary** is required for high-risk actions involving elevated capabilities or external targets.

## Acceptance rule

For ordinary internal reasoning, an action requires formal verification and Sentinel risk below the internal threshold.

For externally consequential or high-risk actions, authorization is conjunctive:

`formal_verified AND security_approved AND human_approved`

Tripwire combinations remain blocked even when human approval is asserted; changing those tripwires requires a policy change rather than an action-level override.

## Initial tripwires

The first implementation blocks combinations representing credentials plus network access, privilege escalation plus external writes, persistence plus stealth, and key recovery plus third-party targeting.

These rules are intentionally capability-oriented rather than keyword-oriented.

## Resource outliers

The initial defaults mark RAM use above 40% of the configured resource fraction and elapsed time above 120 seconds as resource-risk signals. These are policy defaults, not universal constants; experiment-specific policies may tune them while retaining the fail-closed decision path.

## BANK provenance

Existing verified BANK behavior remains append-only. Sentinel adds a separate quarantine store for discoveries that are mathematically or experimentally interesting but are not cleared for execution or export. Future integration should attach security classification, resource cost, generator identity, and external-data flags to ordinary BANK metadata.

## Non-goals

DATA-MIND 2.9 does not attempt to infer intent from prose alone, does not grant itself new external capabilities, and does not replace theorem verification with security scoring. Sentinel is a second gate, not a substitute verifier.

## Implementation

The executable reference implementation is `src/data_atp/sentinel.py`; unit invariants are in `tests/test_sentinel.py`.
