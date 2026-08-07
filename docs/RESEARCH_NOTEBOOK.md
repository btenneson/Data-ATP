# Data-ATP Research Notebook

**Repository:** `btenneson/Data-ATP`  
**Status:** active private research notebook  
**Initialized:** 2026-08-07, approximately 01:30 Pacific Time  
**Project lead:** Brian Tenneson

This file is the chronological research record for executable Data-ATP work. It complements, but does not replace, the archived Phase 0 manuscripts or `docs/archive/PHASE0_ARCHITECTURE_SNAPSHOT.md`.

## Notebook rules

1. Preserve prior entries. Add corrections as new dated notes rather than silently rewriting experimental history.
2. Distinguish architecture, hypothesis, implementation, recorded experiment, verified result, and interpretation.
3. No theorem or reusable lemma is trusted merely because a search module, model, Counselor, Dreamer, or human expects it to be true. Formal acceptance requires the declared verifier.
4. Every substantive run should record, when available: date/time; run ID; exact Git commit; target theorem; formal database file and hash; verifier/version; model or training artifact and hash; training cutoff and leakage controls; seed; expansion/resource budget; exact command; environment notes; start/end time; wall time; expansions and other cost counters; outcome; certificate path/hash; logs; checkpoint/resume history; interruptions/faults; interpretation; and next action.
5. An operating-system reboot, power loss, manual stop, or similar external event is `INTERRUPTED`, not a mathematical failure.
6. Budget exhaustion without a verified proof is `BOUNDED_UNKNOWN`, not evidence of non-theoremhood.
7. A verifier, parser, checkpoint, protocol, or implementation defect is a fault/protocol result, not a mathematical result.
8. Counselor and Dreamer outputs remain advisory or speculative until they pass through the normal trusted proof path.

## Existing architectural baseline

The repository-level Phase 0 snapshot defines:

- Data001 — vision and non-sentient scope
- Data002 — formal computational model
- Data003 — transactions
- Data004 — expansions
- Data005 — Picard feedback loop
- Data006 — creativity engine
- Data007 — regulation engine
- Data008 — Counselor
- Data009 — memory and self-model
- Data010 — learning
- Data011 — verification and soundness
- Data012 — benchmarking
- Data013 — security and governance
- Data014 — Phase 0 roadmap

The immediate implementation principle is: reliable transactions, legal expansions, external verification, reproducible benchmarks, explicit budgets, audit logs, checkpointing, and human deactivation control come before claims of adaptive capability.

## GitHub Issues convention

The open GitHub Issues are treated as **research/work items**, not automatic bug reports.

- **#1 — Phase 0 architecture brief:** umbrella implementation checklist and master tracker.
- **#2 — Durable checkpoints and reboot-safe resumption:** high-priority infrastructure.
- **#3 — Expansion budgets and proof-step cost accounting:** formal resource accounting.
- **#4 — Verifier and proof-certificate pipeline:** trusted mathematical acceptance boundary.
- **#5 — Agent creativity profiles and shared verified-lemma memory:** diverse search with certified sharing only.
- **#6 — Counselor regulation subsystem:** non-authoritative search regulation and diagnosis.
- **#7 — Dreamer / candidate-world simulator:** sandboxed counterfactual search and replay.
- **#8 — Safety boundaries, private deployment, and deactivation controls:** operational governance.

These issues should remain open until their completion criteria are actually met. Commits and experiments may reference an issue number without implying that the issue is complete.

---

# Entry 0001 — Notebook initialization

**Date:** 2026-08-07  
**Local time:** approximately 01:30 Pacific Time  
**Classification:** research infrastructure / pre-experiment initialization

The Data-ATP research notebook was initialized before beginning the first executable Phase 0 drafting and benchmark work.

### Current experimental objective

Prepare a minimal runnable Data-ATP and use Metamath theorem `sgrpcl` as an early target, with the long-term question of whether Data-ATP can prove the same semigroup theorem used in the Predator experiments.

### Current status

- Phase 0 conceptual architecture exists.
- Repository-level editable architecture snapshot exists.
- GitHub Issues #1–#8 provide the implementation backlog.
- No Data-ATP result on `sgrpcl` is claimed at initialization.
- Before a meaningful `sgrpcl` run, the trusted proof path, verifier boundary, accounting, logs, and checkpoint behavior must be explicit enough that the result can be classified scientifically.

### Initial implementation priority

1. Minimal trusted proof path and transaction log.
2. External verifier/certificate pipeline.
3. Expansion/resource accounting.
4. Reboot-safe checkpointing before any long run.
5. Minimal search scheduler and agent interface.
6. Optional Counselor/Creativity instrumentation only after the core run is auditable.
7. Dreamer remains optional and must not be required for the first trusted proof experiment.

### Planned first benchmark

Target: `sgrpcl` in a frozen Metamath environment, using a declared budget and independent certificate verification. Any run must be classified as one of: `VERIFIED_PROOF`, `BOUNDED_UNKNOWN`, `INTERRUPTED`, `FRONTIER_COLLAPSE`, `FAULT`, or `PROTOCOL_FAILURE`, with no inference from finite silence to non-theoremhood.
