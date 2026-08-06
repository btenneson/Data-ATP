# Data-ATP Phase 0 architecture snapshot

This editable snapshot preserves the current fourteen-part architecture represented in the archived Phase 0 PDFs. It is not a substitute for the archived page-faithful documents; it is the repository-level working specification.

## Data001 - Vision and non-sentient scope

Data-ATP is an experimental automated theorem-proving architecture. Names borrowed from Star Trek are engineering metaphors, not claims of consciousness. The target is a prover that records, explains, regulates, and improves its own search behavior while remaining externally verifiable.

## Data002 - Formal computational model

Model the system as a prover/challenger/verifier environment with frozen interfaces. Proof states, legal actions, budgets, randomness, formal libraries, and verifier versions must be explicit. Later Moriarty work extends the model from one adaptive prover to a prover-challenger-verifier system.

## Data003 - Transactions

Every meaningful action becomes an append-only transaction with provenance. The command-autonomy revision adds directive, evidence, override, and self-report transactions. Moriarty adds challenge and checkpoint events.

## Data004 - Expansions

An expansion is a controlled unit of proof-search work. Record legality, parent state, generated candidates, rank information, cost, provenance, and whether the expansion was productive, dead, duplicated, or deferred. Do not truncate on rough scores before legality is established.

## Data005 - Picard feedback loop

Picard is the governance and executive feedback interface. It can start, pause, redirect, or terminate experiments, change soft strategy under declared authority, and require review. The command-autonomy revision distinguishes Picard's hard boundaries from presumptive strategic orders.

## Data006 - Creativity engine

Creativity generates structured alternatives: unusual legal actions, lemma proposals, representation changes, counterfactual branches, and diverse proof routes. Creativity redistributes fixed compute; it does not create extra budget, certify legality, or declare proof success.

## Data007 - Regulation engine

Regulation allocates compute, preserves reserves, limits instability, controls exploration/exploitation, prevents runaway self-play, and enforces exception budgets. It tracks opponent strength, challenge volume, compute asymmetry, and historical sampling.

## Data008 - Counselor

Counselor interprets transaction histories and asks falsifiable diagnostic questions. It does not generate challenges or proofs by hidden authority. It studies patterns such as repeated deferral, representation sensitivity, override quality, or frontier collapse.

## Data009 - Memory and self-model

Store complete traces, checkpoints, weakness maps, competence maps, opponent lineages, challenge provenance, override history, budget use, and calibration. The self-model is descriptive and testable, not a claim of subjective awareness.

## Data010 - Learning

Learning updates ranking, premise selection, lemma prediction, resource allocation, and possibly representation. Promotion requires held-out gain, replication, anti-forgetting checks, complete provenance, and no verifier regression.

## Data011 - Verification and soundness

The verifier is outside the learned search policy and remains sovereign. Parser or wrapper exploitation is a fault discovery, never a proof. The exact certificate, formal environment, verifier version, command, hashes, stdout, stderr, and exit status should be preserved.

## Data012 - Benchmarking

Separate training/self-play curriculum, development tests, and sealed evaluation benchmarks. Use matched budgets, seeds, hardware, wall-clock and memory limits. Report proof rate, expansions, verifier time, proof quality, robustness, calibration, and fault rate.

## Data013 - Security and governance

Sandbox learned and adversarial modules. Restrict network and operating-system access, use read-only formal libraries when possible, preserve append-only logs and hashes, and prohibit modules from modifying governance or verification. Humans approve experiment classes, publication claims, and promotion.

## Data014 - Phase 0 roadmap

Begin with reliable transactions, legal expansions, external verification, and reproducible benchmarks. Add Creativity, Regulation, Counselor, Memory, and Learning incrementally. Add Moriarty only after the base prover is reliable. Treat the Dreamer as an optional bounded simulator mode that replays, recombines, compresses, and counterfactually extends traces while an always-awake core remains operational. Retain Dreamer only if matched-compute ablations show reproducible held-out verifier-confirmed gain.

## Cross-document propagation rule

No module is complete when its own chapter is written. Its consequences must be propagated through every affected interface, invariant, metric, benchmark, and governance rule.
