# NOTALD Tied-Ocean Implementation Qualification

Status: **PASSED**  
Scored benchmark status: **NOT STARTED**

This record documents the first non-scored implementation qualification run. It is deliberately
separate from the frozen scored benchmark and must not be cited as benchmark performance.

## GitHub Actions record

- Workflow: `NOTALD Ocean Qualification`
- Run ID: `31512994557`
- Head commit tested: `ddfef7a5464c03d25a28d780a23dd177b4b551f0`
- Result: `success`
- Artifact: `notald-ocean-qualification`
- Artifact SHA-256 digest: `472597129b9260b7fbb6c6d8f74e0a768bb0cb1564309ce56b426f484df851bd`

## Qualification-only sample

The qualification used five small horizons and three deterministic seeds per horizon:

- horizons: 10, 25, 75, 100, 250
- seeds: 101, 202, 303
- total generated qualification instances: 15

The temporary qualification geometry was:

- two distractor branches per backbone node
- distractor lengths 1 through 5
- optional re-entry probability 0.35

These geometry values are **not** the scored benchmark geometry and do not freeze it.

## Checks passed

All 15 generated instances passed an independent BFS audit with measured `d(s,t) = L` exactly.
Regenerating each `(L, seed)` pair produced an identical instance. For every instance, the
qualification runner also injected an artificial one-edge source-to-target shortcut; the independent
auditor correctly rejected the claimed horizon and measured distance 1.

The NOTALD settlement state machine also passed these required cases:

- no certificate, budget remaining -> `RUNNING`
- no certificate, budget exhausted -> `BOUNDED_UNKNOWN`
- verified Refuter certificate for `T_L` -> `REFUTED`
- verified Prover certificate for `NOT T_L` -> `AUDIT_FAILURE`
- verified certificates for both polarities -> `CRITICAL_AUDIT_FAILURE`

## Interpretation

This qualification validates the current generator/auditor plumbing and the wrong-polarity
settlement rules on small synthetic instances. It does **not** validate the eventual Ocean geometry,
professional ATP adapters, tied-learning protocol, shared lemma behavior, resource accounting, or
full NOTALD architecture. Those remain preconditions for the scored head-to-head campaign.
