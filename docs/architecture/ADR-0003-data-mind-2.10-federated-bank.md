# ADR-0003: DATA-MIND 2.10 Federated BANK Architecture

Status: Accepted for integration testing

## Decision

DATA-MIND 2.10 changes BANK from a single shared-memory topology into a federation of department-specific BANK nodes around the existing verifier-gated shared core.

The architecture number changes from 2.9 to 2.10 because this changes how reasoning departments receive, retain, and propagate verified information.

No existing module is removed. The verifier remains sovereign, FUTUREBANK remains speculative, Sentinel remains the security/resource governor, and Quarantine remains separate from trusted BANK knowledge.

## Core invariant

A department may have its own local BANK and coupled neighboring BANKs, but mathematical truth status does not depend on location:

`verified before BANK deposit`

A speculative item belongs in FUTUREBANK until verifier acceptance. A quarantined item does not become trusted merely because it is preserved.

## Federation topology

Every registered department receives a read-only federated view composed of:

1. **CORE** — verifier-accepted mathematics logically visible to all departments;
2. **LOCAL** — items physically retained by the department's own BANK node;
3. **COUPLED** — items visible from explicitly coupled neighboring BANK nodes.

The initial topology registers P/R/I/C Couples plus named interfaces for QH, Professor, Proof Compass, Child, Presentation Manager, Learner, Sentinel, and Verifier. The coupling graph is configuration, not a theorem: experiments may alter it when the topology itself is the independent variable.

## Propagation modes

A verifier-accepted proposal declares one of four propagation modes:

- `local`: physically store in the source department's BANK node;
- `coupled`: store in the source node and physically copy to its declared coupled neighbors;
- `core`: place one trusted copy in the shared core, making it logically visible to all departments without needless duplication;
- `broadcast`: place it in the core and physically copy it to every registered local BANK.

`core` is the default because it preserves global reuse while minimizing copying overhead. `broadcast` exists for experiments that explicitly require all-copied BANKs.

## Department use

The federation does not make BANK a solver. Each department remains a separate reasoning process and receives a different local/coupled context around the common trusted core.

Examples of intended use:

- P/R/I/C reuse verified lemmas, rules, certificates, and traded presentations;
- QH can retain quotient/invariant results near the agents that consume them;
- Professor can couple evaluation-relevant verified facts to Compass/Child without forcing physical copies everywhere;
- Proof Compass can consume globally verified structure while receiving local/coupled geometry signals through its own adapter;
- Child can be coupled to departments whose verified results inform strategy revision;
- Presentation Manager can couple alternate verified presentations to QH/Compass;
- Learner can read a controlled federated slice rather than requiring every local store to be identical.

These named non-P/R/I/C interfaces are BANK-topology endpoints in 2.10; wiring their full reasoning implementations remains separate from the federation primitive itself.

## FUTUREBANK and Quarantine

FUTUREBANK remains a distinct append-only speculative store. Federation does not promote speculative material automatically. Promotion still requires the independent verifier.

Sentinel's Quarantine BANK remains separate from both verified BANK and FUTUREBANK. Resource/security isolation therefore does not contaminate mathematical truth status.

## Performance hypothesis

Federation adds small bookkeeping costs but permits two opposing performance strategies under one architecture:

- logical shared-core access avoids physical duplication;
- selective/local/coupled retention can reduce irrelevant scanning and isolate expensive or specialized flows.

The first planned 2.10 training rerun should preserve the frozen 95% cohort and learning objective. BANK topology and Sentinel containment must not silently remove `quartfull` or any other theorem from the cohort. A pathological transaction may be isolated from execution while its identity, provenance, and failure remain recorded.

## Implementation

- `src/data_atp/federated_bank.py`
- `src/data_atp/pric_bank.py`
- `tests/test_federated_bank.py`

The public architecture marker is `DATA_MIND_ARCHITECTURE_VERSION = "2.10"`.
