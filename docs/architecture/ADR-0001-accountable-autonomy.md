# ADR-0001: Accountable autonomy under command

**Status:** accepted for Phase 0 interface testing  
**Date:** 2026-08-06  
**Author/director:** Brian Tenneson

## Context

The command clips show Data doing more than executing orders. He notices evidence unavailable to the remote commander, distinguishes professional competence from prejudice, issues necessary orders without ego, departs from a retreat instruction to pursue a transient signature, and then voluntarily reports his own disobedience. The success of the action does not cancel the need for review.

## Decision

Data-ATP will separate authority into two classes.

### Hard invariants

These are not locally overrideable:

- formal inference legality;
- exact verifier acceptance or rejection;
- sealed benchmark and data-leakage boundaries;
- external CPU, memory, storage, and wall-clock ceilings;
- governance rules and immutable provenance requirements.

### Soft directives

These are presumptive but revisable:

- frontier ranking and truncation;
- theorem or branch priority;
- restart and pause timing;
- allocation among creativity, coverage, dream replay, and adversarial challenges;
- return-to-baseline strategy.

A soft directive may be overridden only when a frozen exception policy accepts logged evidence, estimated cost fits outside a protected reserve, and a return point is named. Every executed override produces a `SelfReportFiled` transaction regardless of success.

## Consequences for the existing architecture

- **Transactions:** add directive, evidence, override, and self-report events.
- **Expansions:** legality is established before ranking or exception scoring.
- **Picard:** retains authority over experiment classes, hard limits, and post-run promotion.
- **Creativity:** may propose an exception but cannot certify its own legality or success.
- **Regulation:** protects reserve budget and limits exception frequency/cost.
- **Counselor:** interprets override histories and asks whether exceptions improved outcomes.
- **Memory/self-model:** stores evidence quality, overridden directives, results, and calibration.
- **Learning:** learns only from fully logged outcomes and cannot weaken hard boundaries.
- **Verifier:** remains outside and sovereign.
- **Benchmarking:** compares no-exception, exception, and ablated policies under matched budgets.
- **Security:** every override is reproducible and externally bounded.

## Non-goal

This design does not imply emotion, consciousness, military authority, or unrestricted autonomy. It is an auditable search-control interface.
