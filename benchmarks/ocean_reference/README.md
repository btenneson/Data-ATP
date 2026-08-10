# Ocean Six-Way Reference Benchmark

This directory freezes benchmark adapters used to compare six systems on the same sealed
`L*=4000` Ocean implication instances:

- Vampire
- E Prover
- SPASS
- Prover9
- Data-ATP Ocean Reference 1.0
- DATA 2.0.1 Ocean Reference 1.0

## Status of the two DATA entries

The two DATA entries are **frozen benchmark reference implementations**, not a claim that the
full research architectures are complete production ATP releases. This naming is deliberate.
The reference implementations convert the architectural commitments already documented in the
research program into executable policies that can be tested without silently substituting the
older dry stand-ins.

## Leakage barrier

Every solver receives the same sealed TPTP problem. Before execution the workflow:

1. generates the 20 deterministic Ocean instances using the pinned ATP repository generator;
2. removes all comments (the generator comment contains `L*`);
3. replaces informative filenames with opaque `problem_###.p` names;
4. deterministically reorders and renames implication axioms using only the visible shuffled node
   labels and a fixed hash salt;
5. keeps the seed, source filename, planted route, manifest, and externally verified `L*` outside
   every solver process.

The evaluator retains a private mapping only for scoring after each process has stopped.

## Data-ATP Ocean Reference 1.0

This is a deterministic multi-frontier policy with:

- bounded six-layer reconnaissance;
- a fixed 8:1:1 scheduler among reconnaissance, breadth resurvey, and branching resurvey;
- shared discovered landmarks and predecessor records;
- canonical one-dimensional locality tie-breaking.

The Ocean benchmark is unary implication search, so Hilbert geometry degenerates to one
dimension here. The reference therefore does **not** pretend that a higher-dimensional Hilbert
curve is doing work that the benchmark cannot support.

A logical expansion is one attempted visible implication edge. Reconnaissance edge inspections
are recorded separately as `scoring_edge_probes`; they are not hidden.

## DATA 2.0.1 Ocean Reference 1.0

The fast wing is a transparent bidirectional breadth-first search, an explicitly allowed
goal-directed/bidirectional policy in the DATA 2.0.1 architecture. It uses only the visible start,
implications, and target.

The separate Proof-Horizon wing is ordinary BFS on this finite, unit-cost graph. Its first
verified target is therefore a fewest-edge proof for this benchmark presentation. First landfall
and minimum-cost certification are reported on separate scoreboards.

## Verification and timing

The DATA adapters emit explicit node paths. A separate verifier checks that the path begins at
the start fact, ends at the conjecture, and that every consecutive pair is an input implication.
Only verified paths count as `PROVED`.

Every first-landfall solver receives the same 60-second per-instance wall-clock ceiling. The
DATA 2.0.1 Horizon certification phase is recorded separately and is never folded into its
first-landfall time.

The workflow retains raw professional ATP outputs, DATA path certificates, environment/version
information, the sealed problems, and summary tables as a 90-day GitHub Actions artifact.

## Frozen upstream benchmark source

The Ocean generator and professional ATP adapter are pinned to:

`btenneson/ATP@3f7d4a345dbada286e5b16b46b787408189ecbef`

Changing the reference policies, leakage barrier, solver versions, or upstream benchmark pin
requires a new benchmark version rather than silently overwriting this one.
