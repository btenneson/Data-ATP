# NOTALD Massive Tied-Ocean Benchmark

> **STATUS: IMPLEMENTATION SCAFFOLD ONLY — DO NOT RUN SCORED BENCHMARKS**

This directory implements the benchmark-and-architecture-validation protocol described in the approved **NOTALD Massive Tied-Ocean Benchmark Proposal**.

The benchmark deliberately gives NOTALD the wrong-polarity conjecture `C_L = not T_L`. The Prover role `P` searches for `not T_L`; the Refuter role `R` searches for `not C_L`, normalized to the native Ocean theorem `T_L`. For the frozen consistent Ocean family, the expected conclusive result is `REFUTED`/`REFUTABLE` through a verified certificate from `R`. Budget exhaustion remains `UNKNOWN` or `BOUNDED_UNKNOWN` and is never treated as a proof of non-theoremhood.

## Benchmark depths

The proposed native proof horizons are:

`10, 25, 75, 100, 250, 750, 1000, 2500, 7500, 10000, 25000, 75000, 100000, 250000, 750000`

Equivalently, `L = c * 10^n` for `c in {1, 2.5, 7.5}` and `n in {1,2,3,4,5}`.

## Principal professional ATP baselines

The principal professional quartet is frozen provisionally as:

- Vampire
- E
- iProver
- Prover9

SPASS may be retained as an optional legacy/unscored control for continuity with the earlier Ocean reference benchmark.

The full proposed comparison also includes Depths-F, Data-ATP, DATA 2.0.1, and NOTALD.

## Safety / run interlock

This scaffold is intentionally non-runnable as a scored benchmark. `protocol.json` contains `run_authorized: false` and unresolved freeze items. `run_benchmark.py` exits unless every required freeze field is resolved and a deliberate authorization flag is supplied.

No benchmark instances, training bundles, answer keys, or scored runs were generated while creating this scaffold.

## Directory roles

- `protocol.json` — machine-readable freeze state and system roster.
- `generator.py` — deterministic Ocean generator interface. It refuses to generate scored instances until Ocean geometry is frozen.
- `auditor.py` — independent shortest-path auditor for the generated directed graph.
- `notald_polarity.py` — explicit wrong-polarity role mapping and settlement checks.
- `run_benchmark.py` — top-level runner with hard authorization gates.
- `adapters/` — future wrappers for each ATP/ALD.
- `private_answer_keys/` — documentation only; actual answer keys must remain outside solver-visible inputs and should not be committed.

## Existing Ocean reference benchmark

The earlier `benchmarks/ocean_reference` benchmark is preserved unchanged. This NOTALD benchmark is a separate benchmark version and must not silently overwrite the earlier six-way Ocean reference work.

## Freeze items still required before execution

1. Ocean geometry / distractor specification.
2. Number of independent seeds per depth.
3. Exact software versions for Vampire, E, iProver, Prover9, and optional SPASS.
4. CPU, wall-clock, memory, and search-work budgets plus stopping rules.
5. Exact lower-resolution training artifact bundle.
6. Exact tied-predecessor exposure rule.
7. Double-negation normalization convention.
8. Certificate verifier and proof-counting convention.
9. Blinding / answer-key procedure.
10. Head-to-head scoring, tie, and UNKNOWN rules.

After these are frozen, the benchmark should be versioned and committed before the first scored run.