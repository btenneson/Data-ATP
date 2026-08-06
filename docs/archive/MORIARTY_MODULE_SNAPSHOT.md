# Moriarty module snapshot

Moriarty is an adversarial challenge generator for Data-ATP. Its purpose is productive opposition: find the next weakness after the previous weakness has been repaired, not keep Data weak.

## Core loop

1. Freeze prover, challenger, verifier, formal environment, budget, and seeds.
2. Moriarty proposes bounded candidate challenges.
3. Validate syntax, semantics, leakage, triviality, and governance.
4. Data attempts each accepted challenge under a frozen search budget.
5. The independent verifier checks every claimed certificate.
6. Preserve the complete transaction trace.
7. Train or revise candidate prover/challenger checkpoints.
8. Promote only after held-out tests and anti-forgetting gates.

## Challenge families

- barely provable conjectures near the competence frontier;
- representation-preserving attacks such as symbol renaming and hypothesis reordering;
- proof-state attacks exposing premature truncation, duplicate errors, oscillation, and deferred lemmas;
- counterexample or finite-countermodel tasks in an explicit model class;
- bounded resource attacks that reveal unfavorable expansion, memory, or preprocessing scaling;
- verifier-interface auditing, where any exploit is classified as a fault, never a proof.

## Counselor cooperation

Counselor identifies a trace pattern and asks a falsifiable diagnostic question. Moriarty converts the question into a controlled test. Data runs under a frozen protocol. Verifier and Benchmark Manager decide the outcome. Counselor interprets the result.

## Promotion gate

Reject a candidate update unless there is no verifier regression or benchmark leakage, the gain replicates, protected theorem families do not collapse beyond tolerance, resource use stays within the declared envelope, and all source/configuration/data/checkpoints are archived.

## Security boundary

Moriarty may not alter the verifier or governance, access sealed proofs, write to production without approval, obtain unrestricted network/OS access, hide traces, or declare itself successful. Use hard external CPU, memory, storage, and wall-clock limits; read-only formal libraries; append-only logs; recorded randomness; hashes; and reproducible shutdown/recovery.

## Staged roadmap

- M0: offline trace analyst;
- M1: safe meaning-preserving mutations;
- M2: barely-solvable curriculum;
- M3: frozen checkpoint self-play with historical opponents;
- M4: population of specialized challengers;
- M5: cross-system evaluation against other ATP versions.

Moriarty should be added only after minimal Data-ATP transactions and externally checked proofs are reliable.
