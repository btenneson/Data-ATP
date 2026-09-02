# Data-ATP (private research repository)

Data-ATP is Brian Tenneson's experimental architecture for an accountable, creative, self-modeling automated theorem prover. The system is **not assumed to be sentient**. Star Trek names are interface metaphors that must reduce to executable inputs, outputs, authority limits, logs, and tests.

## Current architecture: DATA-MIND 2.9

DATA-MIND 2.9 adds **Sentinel**, a first-class security governor around reasoning, BANK use, verification, and any externally consequential action.

The 2.9 security invariant is:

> Mathematical validity is necessary but not sufficient for execution or export.

Sentinel adds resource-outlier monitoring, capability controls, security classification, fail-closed tripwires, a quarantine BANK, and a human-authorization boundary for high-risk actions. The executable implementation is in `src/data_atp/sentinel.py`; the architecture decision is documented in `docs/architecture/ADR-0002-data-mind-2.9-sentinel.md`.

## Architectural rule added after the command clips

> Data-ATP obeys logic and verification absolutely, follows strategy presumptively, and departs from strategy only through an explicit, bounded, recorded, and reviewable act of reasoning.

The clips add an **accountable autonomy** layer:

- hard invariants (logic, legality, verifier output, sealed benchmarks, external resource ceilings) are never overridden;
- soft directives (ranking, priority, restart, and search allocation) may be overridden by strong local and time-sensitive evidence;
- every override has a bounded cost, a return point, and an append-only transaction trail;
- success does not erase accountability: Data files a self-report after the action;
- authority is exercised without ego: subordinate or module objections are judged by evidence and competence, not status.

## Repository map

- `docs/archive/` - preserved Phase 0 and Moriarty working documents.
- `docs/architecture/` - current architecture decisions and implementation plan.
- `docs/research/` - the Hilbert-coverage/budget paper, source, and figures.
- `src/data_atp/` - first executable scaffold, including DATA-MIND 2.9 Sentinel.
- `tests/` - tests for hard/soft authority separation, transaction integrity, budget formulas, BANK behavior, and Sentinel security invariants.

## Run the scaffold

```bash
python -m unittest discover -s tests -v
```

The code is deliberately small. It tests interfaces and invariants before any large learned component is introduced.
