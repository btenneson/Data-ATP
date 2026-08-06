# Data-ATP implementation plan after the command-autonomy revision

## Phase A0 - executable invariants (implemented here)

1. Hash-chained append-only transaction log.
2. Hard/soft directive type system.
3. Legality-before-ranking rule.
4. Bounded exception policy with protected reserve.
5. Independent verifier callback.
6. Mandatory self-report after an override.
7. Hilbert-derived coverage formulas for physical and abstract budgets.

## Phase A1 - connect to a real prover

- Define a `ProofStateAdapter` for Predator/set.mm traces.
- Emit one transaction per legal expansion.
- Store candidate generation separately from legality filtering and final ranking.
- Treat the Metamath verifier as an external process; record command, version, hashes, exit code, stdout, and stderr.
- Preserve complete failed runs, not only successful proofs.

## Phase A2 - budget-balanced frontier coverage

- Freeze a proof-state feature vector and distance function.
- Partition the active feature region recursively.
- Allocate representative expansions across all coarse regions before deep refinement.
- Record `CoverageLevelCompleted` only when every eligible region met its declared sampling obligation.
- Compare the coverage schedule with best-first, breadth-first, random, and diversity-only baselines.

## Phase A3 - evidence-triggered exceptions

- Define transient evidence channels: sudden verifier-compatible lemma chain, rare unification bridge, frontier entropy collapse, or a local proof-state signature with calibrated success probability.
- Freeze thresholds before benchmark runs.
- Cap override count, per-override expansions, and total exception budget.
- Require an explicit return point and automatic return when the exception budget expires.

## Phase A4 - Counselor and self-model

- Aggregate override precision, recall, gain per expansion, false-alarm rate, and calibration.
- Ask falsifiable questions rather than generating proofs directly.
- Store competence maps by theorem family, representation, and budget.

## Phase A5 - Creativity, Dreamer, and Moriarty

- Creativity proposes alternate lemmas and routes under fixed total compute.
- Dreamer replays and recombines bounded traces offline or in a low-priority mode.
- Moriarty generates controlled challenges only after the base transaction/verifier path is reliable.
- Promotion requires held-out verifier-confirmed gain and anti-forgetting checks.

## First integration target

Use a small frozen theorem suite already verified in set.mm. Run the same legal action generator under:

1. no exceptions;
2. accountable exceptions;
3. accountable exceptions with budget-balanced feature coverage.

Report success, expansions, wall time, memory, proof length, transaction integrity, override count, and verifier faults.
