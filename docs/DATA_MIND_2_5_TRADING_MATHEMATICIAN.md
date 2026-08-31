# DATA-MIND 2.5 — The Trading Mathematician

DATA-MIND 2.5 is an **additive** extension of DATA-MIND 2.4. Nothing in the 2.4 architecture is overwritten. The 2.4 proof kernel, verifier boundary, 11-dimensional control system, inverse child revision, rollback/checkpoint behavior, append-only Mathematician memory, and P/R/I/C Couple deliberation remain intact.

The architecture change is a new **presentation-trading layer** motivated by the Trading Theorem work.

## Formal idea

Write a presentation of a formal system schematically as

```text
F = (symbols/WFF machinery, axioms A, inference rules R).
```

For a selected set of rules `R_t ⊆ R`, a trading map `tau` proposes corresponding axiom or axiom-schema images `tau(R_t)`. The derived presentation is

```text
F^tau = (same symbols/WFF machinery,
         A ∪ tau(R_t),
         R \ R_t).
```

A trade is valid only when the appropriate consequence closure is preserved:

```text
Cn(F) = Cn(F^tau).
```

The new axioms are therefore not arbitrary preloaded consequences. They are specifically the proposed or verified images of the rules being traded.

## Trading Theorem — architecture form

**Trading Theorem.** If a rule-to-axiom trading map `tau` is certified to preserve consequence closure, selected inference rules may be redistributed into traded axioms while deductive content is invariant. Existing axioms and all untraded rules are preserved.

This separates two things that need not be invariant together:

1. **theoremhood / consequence closure**, and
2. **proof presentation / reason for theoremhood**.

A statement obtained by induction in one presentation may be obtained axiomatically in a traded presentation, even though the two presentations have the same consequence closure.

## Complete-trade endpoint

If every inference rule is validly traded, then the derived presentation can have

```text
R^tau = emptyset.
```

At that endpoint, inference-rule compliance is vacuous because there are no inference rules to apply. The deductive work has been absorbed into axiomatic status.

This endpoint is conceptually important but is not assumed to be the computationally best presentation.

## Practical kernel-trade form

For ATP work, a more useful trade often leaves a small residual kernel. For example, an induction rule may be represented by an induction axiom/schema while a simple universal inference mechanism remains. Thus 2.5 distinguishes:

- **complete trade:** no residual inference rules;
- **kernel trade:** selected expensive/specialized rules are traded while a residual rule kernel remains.

## Trading Optimization Problem

Consequence-equivalent presentations can have radically different search costs. DATA-MIND 2.5 therefore registers a second problem:

```text
minimize C(F') over certified F' such that Cn(F') = Cn(F).
```

`C` may combine:

- expansions;
- wall-clock time;
- verifier work;
- peak memory;
- proof length.

This turns the Trading Theorem into an ATP search question: not merely *can* the mathematics be presented another way, but *which certified-equivalent presentation is cheapest for this prover on this problem?*

## Induction example

Abstractly, the rule

```text
P(0),  forall n (P(n) -> P(n+1))
---------------------------------- induction
             forall n P(n)
```

suggests the traded axiom/schema candidate

```text
(P(0) & forall n (P(n) -> P(n+1))) -> forall n P(n).
```

In 2.5 this is deliberately recorded as a **candidate**, not automatically certified. The general implication-shaped transformation is not sound as an automatic equivalence theorem for arbitrary formalisms, especially when side conditions, binding conditions, infinitary rules, or special proof conventions are present.

## Safety and verifier sovereignty

2.5 does not alter the live Metamath calculus merely because a trade has been proposed.

A trade has lifecycle state:

```text
PROPOSED -> VERIFIED
         -> REJECTED
```

Only a trade marked `VERIFIED` and carrying closure-equivalence provenance is considered activatable at the presentation layer. Even then, the initial 2.5 implementation does **not** inject an arbitrary new axiom into the Metamath proof kernel. A proof adapter must turn the traded object into verifier-checkable mathematics before BANK admission.

Therefore:

```text
presentation trading controls what representation to try;
Metamath verification still controls what is true.
```

## No-overwrite invariant

The implementation enforces the rule requested for this architecture:

```text
old axioms are preserved;
untraded rules are preserved;
2.4 source and behavior remain available;
a trade creates a derived presentation rather than mutating the original.
```

If `R_t` is the set of activated trades, then

```text
A' = A ∪ tau(R_t)
R' = R \ R_t.
```

Nothing else is silently deleted.

## DATA-MIND 2.5 runtime role

The initial 2.5 runner inherits DATA-MIND 2.4 and adds:

- registration of the Trading Theorem;
- registration of the complete-trade corollary;
- registration of the Trading Optimization Problem;
- an append-only trading runtime ledger;
- optional JSON trade specifications;
- explicit proposed/verified/rejected trade status;
- persistent Mathematician memory records for presentation trades;
- summary fields showing that the proof kernel remains unchanged.

The built-in induction trade is an unverified example. Additional trades can be supplied through `--trade-spec`.

## Example trade specification

```json
{
  "trades": [
    {
      "rule_name": "induction",
      "traded_axiom": "INDUCTION_AXIOM_SCHEMA",
      "status": "proposed",
      "provenance": "Trading Theorem notebook"
    }
  ]
}
```

A `verified` entry should additionally identify the closure-equivalence certificate or formal result that justifies treating it as an equivalent presentation. That metadata does not itself override independent proof verification.

## Versioning reason

This is numbered **2.5**, rather than a documentation-only revision to 2.4, because the architecture has changed: DATA-MIND now represents, remembers, and can optimize over alternative axiom/rule presentations. The 2.4 architecture remains frozen as its predecessor.
