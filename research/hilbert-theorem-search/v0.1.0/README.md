# Hilbert Space Filling Curve-Style Theorem Search

**Version:** 0.1.0  
**Date:** 2026-08-06  
**Authorship label:** *By ChatGPT, inspired by Brian Tenneson*  
**Repository:** private `btenneson/Data-ATP`

## Release status

Version 0.1.0 is the first executable reference release. It is a research prototype, not yet a Metamath/Lean production prover. The release contains a self-contained Python implementation, an independent toy verifier, a test suite, a manuscript source, and reproducible figure-generation code.

The test suite currently passes 12 tests covering Tenneson rational addressing, recursive tuple pairing, rational-cube round trips, arbitrary-dimensional Hilbert bijection and adjacency, frozen consequence epochs, budget interruption reports, certificate rejection, and finite closure discovery.

## Core construction

For a finitary formal system with rules `r_i` of arities `k_i`, the intrinsic inference-address space over a frozen verified formula set `C` is

```text
A_F(C) = coproduct_i C^(k_i).
```

An address is a tagged tuple

```text
(i; a_1, ..., a_(k_i)),
```

meaning: apply rule `r_i` to those ordered premises. Each rule component receives its own discrete Hilbert traversal. The optional orthogonal ambient dimension is

```text
K = sum_i k_i,
```

but the engine does not search the wasteful full product cube `[0,1]^K`.

A finite `k`-dimensional Hilbert order visits every grid address exactly once. Valid cells decode to ordered premise tuples; padding cells are reported but do not consume an inference expansion. Every accepted conclusion requires a proof certificate accepted by the verifier.

For a completed frozen epoch,

```text
C_(e+1) = D_F(C_e),
```

where `D_F` is the direct-consequence operator. Repeated complete epochs enumerate the deductive closure for the implemented finite-rule setting.

## Brian Tenneson's rational addressing layer

The code implements Tenneson's explicit surjection `r: N+ -> Q`, its least-preimage section `s`, and the positive pairing polynomial

```text
pi(a,b) = ((a+b-1)(a+b-2))/2 + a.
```

Recursive pairing assigns one natural-number line to an `n`-tuple. A rational transport then yields an explicit line-numbering of

```text
(Q intersect [0,1])^n.
```

WFF/Godel line numbers are kept as the unique logical identities. Rational points are addresses and geometric coordinates; theoremhood is created only by verification.

## Run the prototype

```bash
python hilbert_theorem_search.py
python -m unittest -v test_hilbert_theorem_search.py
```

No third-party Python package is required for the reference implementation.

## Contents

- `hilbert_theorem_search.py` — executable reference engine.
- `test_hilbert_theorem_search.py` — 12 regression tests.
- `MANUSCRIPT_v0.1.0.md` — mathematical and implementation source.
- `make_figures.py` — regenerates the four explanatory figures.
- `semigroup/SGRPCL_HILBERT_PILOT_v0.1.0.md` — integration plan for the Metamath `sgrpcl` target.
- `CHANGELOG.md` — release history.

## Semigroup target

The intended pilot target is Metamath theorem `sgrpcl`, informally:

```text
If G is a semigroup and X and Y are in Base(G), then X .o. Y is in Base(G).
```

The current release does **not** claim a Hilbert-generated `sgrpcl` certificate. Predator 8.004 is a backward unification prover, while the exact reference architecture in this release is a forward frozen-epoch consequence enumerator. The semigroup pilot document specifies the adapter and the controls needed to compare a Hilbert policy honestly against the existing legal-first Predator search.

## Short coproduct refresher

For sets, the coproduct of `A` and `B` is the tagged disjoint union

```text
A ⊔ B = ({0} x A) union ({1} x B).
```

The tags preserve which component an element came from, even when `A` and `B` overlap. For a family of rule spaces, the tag is the inference-rule identifier.

A coproduct and a Cartesian product generally represent different questions:

- `A ⊔ B`: choose **one component**, then choose an element from it.
- `A x B`: choose an element of `A` **and** an element of `B` simultaneously.

They do not ordinarily reduce to each other. Special set-theoretic coincidences can occur:

- `A ⊔ empty` is naturally isomorphic to `A`.
- `A x {star}` is naturally isomorphic to `A`.
- Finite sets can have accidental equal cardinalities, but that is not a canonical structural identification.
- In a distributive category, products distribute over coproducts: `A x (B ⊔ C) ≅ (A x B) ⊔ (A x C)`. This simplifies mixed expressions but does not identify coproduct with product.

For theorem search, the coproduct is the right object because one inference step selects one rule and supplies only that rule's arguments. A Cartesian product across all rules would pretend that every step supplies arguments to every inference rule simultaneously.
