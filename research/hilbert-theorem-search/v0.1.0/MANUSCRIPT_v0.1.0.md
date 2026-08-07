# Hilbert Space Filling Curve-Style Theorem Search

**By ChatGPT, inspired by Brian Tenneson**  
**Version 0.1.0 — August 6, 2026**

## Abstract

This manuscript specifies and implements a budgeted theorem-discovery architecture in which finite approximants to Hilbert space-filling curves order candidate inference applications. For a finitary formal system, inference rules are separated into a coproduct of rule-specific premise spaces. A rule of arity `k` receives a `k`-dimensional Hilbert traversal; unrelated rules do not generate a wasteful Cartesian product of all argument positions. Brian Tenneson's explicit surjection from the positive natural numbers onto the rationals, together with his least-preimage section and positive pairing polynomial, supplies an explicit rational-address layer for points in `(Q ∩ [0,1])^n`. WFF/Godel line numbers remain the unique logical identities, while rational points act as geometric addresses. A conclusion becomes a theorem-point only after an independent verifier accepts its certificate. Complete frozen epochs compute one direct-consequence layer, and repeated complete epochs enumerate the deductive closure under the stated effective finitary hypotheses.

## 1. Formal system and rule-arity coproduct

Let

```text
F = (x, y, z),
z = {r_1, ..., r_m},
```

where `y` is the WFF domain and rule `r_i` has finite arity `k_i`.

For a frozen verified formula set `C`, the intrinsic inference-address space is

```text
A_F(C) = ⊔_(i=1)^m C^(k_i).
```

A point is a tagged tuple

```text
(i; a_1, ..., a_(k_i)),
```

and means exactly: apply `r_i` to that ordered premise tuple.

The optional orthogonal ambient dimension is

```text
K = Σ_i k_i.
```

Each `C^(k_i)` may be embedded into its own coordinate block of an ambient `K`-dimensional cube, but the actual search runs over the coproduct. Searching the entire product would combine premise selections for unrelated inference rules in the same cell, even though one proof step selects only one rule.

## 2. Explicit rational addresses from Tenneson's map

Tenneson's rational enumeration is

```text
r(n) = (-1)^n A002260(floor(n/2)) / A004736(floor(n/2)),
```

with `n >= 1`, where the two coordinate sequences enumerate positive pairs along triangular rows. His least-preimage section `s` satisfies

```text
r(s(q)) = q
```

for every rational `q`, and returns the least input attaining `q`.

The positive pairing polynomial is

```text
π(a,b) = ((a+b-1)(a+b-2))/2 + a.
```

Recursively define

```text
π_1(a_1) = a_1,
π_n(a_1,...,a_n) = π(a_1, π_(n-1)(a_2,...,a_n)).
```

This gives one positive natural-number line for every positive integer `n`-tuple.

To obtain rational coordinates in the unit interval, version 0.1.0 uses the rational transport

```text
u(1) = 1,
u(n) = |r(n-1)| / (1 + |r(n-1)|),  n > 1.
```

The map is onto `Q ∩ [0,1]`. Its section is explicit: for `0 <= q < 1`, invert the transport with

```text
t = q/(1-q)
```

and then use `s(t)+1`; reserve line 1 for `q=1`.

Consequently, one line `L` can be decoded into an integer tuple and then into a rational point

```text
R_n(L) ∈ (Q ∩ [0,1])^n.
```

A canonical right inverse is obtained by applying the unit-interval section coordinatewise and pairing the resulting positive integers.

## 3. WFF lines and theorem-points

Fix an effective one-to-one enumeration

```text
g ↦ φ_g
```

of all well-formed formulas of the formal language. The WFF/Godel line `g` is the formula's unique computational identity. A convenient injective coordinate is

```text
iota(g) = g/(g+1) ∈ Q ∩ [0,1).
```

Thus an ordered premise tuple with WFF lines `(g_1,...,g_k)` has the rational address

```text
(iota(g_1),...,iota(g_k)).
```

A rational address alone does not establish theoremhood. A theorem-point is a verified record

```text
Theta = (g, φ_g, certificate, verifier, provenance).
```

Only the verifier can admit `Theta` into trusted theorem storage.

## 4. Finite arbitrary-dimensional Hilbert traversal

At an epoch with `M = |C|` frozen verified formulas, let

```text
p = ceil(log_2 M),
N = 2^p.
```

For a rule of arity `k`, use a discrete Hilbert bijection

```text
H_(k,p): {0,...,N^k-1} -> {0,...,N-1}^k.
```

Each Hilbert distance gives one grid coordinate tuple. When every coordinate is below `M`, the cell decodes to one ordered premise tuple in `C^k`. Coordinates at least `M` are padding. Padding preserves an exact power-of-two Hilbert grid without duplicating valid premise tuples.

Therefore a completed traversal of the rule component attempts every ordered tuple in `C^k` exactly once.

Successive Hilbert cells are face-adjacent. In the proof-search interpretation:

- straight motion continues varying the same premise slot;
- a turn inside one component changes which premise slot varies;
- a coproduct turn changes the active inference rule.

These meanings are operational descriptions of coordinate-axis changes, not claims that geometry itself proves anything.

## 5. Frozen theorem-discovery epochs

Define the direct-consequence operator

```text
D_F(C) = C ∪ {r_i(a_1,...,a_(k_i)) :
              (a_1,...,a_(k_i)) ∈ C^(k_i)
              and the rule application is defined}.
```

An epoch freezes `C_e`, traverses every rule component, stages novel verified conclusions, and commits them only after the frozen sweep. If the epoch completes, then

```text
C_(e+1) = D_F(C_e).
```

Starting from hypotheses or axioms `C_0 = Gamma`, repeated completed epochs satisfy

```text
C_e = D_F^e(Gamma)
```

and, under the finitary effective assumptions,

```text
⋃_(e>=0) C_e = Con_F(Gamma).
```

The proof is induction on finite derivation length. Every theorem with a proof of length at most `e` belongs to `C_e`; conversely every committed formula is produced by a verified legal application from an earlier layer.

## 6. Budgets and interruption certificates

One expansion is one attempted rule application on one valid decoded premise tuple. For frozen set size `M`, a full epoch has

```text
E(M) = Σ_i M^(k_i)
```

valid candidate tuples. The padded address-visit count is

```text
A(M) = Σ_i N^(k_i),
N = 2^(ceil(log_2 M)).
```

The implementation separately records:

- Hilbert address visits;
- valid inference expansions;
- verifier calls;
- padding visits;
- verified novel conclusions;
- per-rule completion status.

An interrupted run reports exact finite work. It does not convert silence into falsehood or independence.

## 7. Training and post-training theorem discovery

A frozen trained policy may alter navigation by choosing rule-component order, Hilbert orientation, subcube priority, or budget allocation. It may not change rule legality, the proof verifier, sealed benchmark data, or declared resource ceilings.

The intended separation is

```text
training/policy -> where to look first,
symbolic engine -> what applications are legal,
verifier        -> what counts as a theorem.
```

For a run advertised as complete, the scheduling wrapper must preserve fairness: learned ranking may reorder cells but may not permanently discard them.

## 8. Executable reference implementation

The versioned package contains a 1,055-line Python implementation. It includes:

- Tenneson's `r` and `s` formulas;
- recursive positive tuple pairing and unpairing;
- rational unit-cube addressing;
- injective WFF coordinates;
- arbitrary-dimensional discrete Hilbert index/point conversion;
- rule, formal-system, certificate, database, and verifier interfaces;
- a deterministic fair scheduler;
- expansion, address, and verifier budgets;
- SHA-256 chained transaction logging;
- frozen theorem epochs;
- a unary/binary/ternary toy system;
- an exhaustive direct-consequence control.

The archival connector stored the source in six ordered segments. Run

```bash
python assemble_source.py
```

which checks SHA-256

```text
ae4f61c1dabcac69d25d0e3cd3c602a1e23196bbd6227c165f58251776151eab
```

before writing `hilbert_theorem_search.py`.

Then run

```bash
python hilbert_theorem_search.py
python -m unittest -v test_hilbert_theorem_search.py
```

The pre-upload test run passed all 12 regression tests.

## 9. Metamath semigroup pilot

The target `sgrpcl` states semigroup closure on the base set, informally:

```text
G is a semigroup, X ∈ Base(G), Y ∈ Base(G)
------------------------------------------------
X .o. Y ∈ Base(G).
```

The current executable is a forward consequence enumerator. Predator 8.004 is a backward unification prover. A legitimate Hilbert-style `sgrpcl` experiment therefore needs an adapter rather than a renamed candidate ranking.

For each current open goal, a legal Metamath assertion application must receive a stable address derived from independently variable choices such as assertion identity, substitution values, generated essential hypotheses, and selected open-goal position. Assertion schemas form coproduct components. Each component's dimension equals the number of independently enumerable choices needed for that application; it is not necessarily equal merely to the number of essential hypotheses.

The pilot must preserve the existing legal-first pipeline and external certificate verifier. Its report paths must be separate from previous Predator results. On an eight-core laptop with another substantial search running, the initial Hilbert pilot should use no more than four worker agents, with at most two heavy processes total.

No `sgrpcl` proof by Hilbert search is claimed in version 0.1.0. The package includes the precise integration specification needed for that next implementation step.

## 10. Coproduct refresher

For sets,

```text
A ⊔ B = ({0} × A) ∪ ({1} × B).
```

The tags make it a disjoint union even if `A` and `B` overlap. The universal-property interpretation is that a map out of `A ⊔ B` is exactly a pair of maps out of `A` and `B`.

The Cartesian product answers a different question:

```text
A × B = {(a,b) : a∈A and b∈B}.
```

A coproduct chooses one tagged component; a product chooses data from every factor simultaneously. They generally do not reduce to one another.

Simple cases include

```text
A ⊔ empty ≅ A,
A × {star} ≅ A.
```

Finite sets can have accidental equal cardinality, but equal size does not give a canonical or structure-preserving identification. In distributive settings,

```text
A × (B ⊔ C) ≅ (A × B) ⊔ (A × C),
```

which simplifies mixed constructions without turning coproducts into products.

The coproduct is appropriate here because one proof transaction selects one inference rule and supplies only that rule's arguments.

## 11. Research status

The architecture is implemented and testable on a finite formal system. The completeness statement for completed frozen epochs is a reformulation of exhaustive finitary consequence enumeration with a geometric ordering. The scientific novelty and practical value depend on whether Hilbert locality, rational addressing, coproduct separation, and trained scheduling improve verified theorem yield per expansion on real formal libraries. That question requires controlled comparisons against lexicographic, breadth-first, random, diversity-based, and learned baselines.
