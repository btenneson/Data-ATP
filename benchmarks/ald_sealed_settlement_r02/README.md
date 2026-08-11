# ALD Sealed Conjecture-Settling R02

## Purpose

R02 is an end-to-end conjecture-settling experiment, not merely a theorem-proving race. It is designed to demonstrate that a system can run **P** (prove the conjecture), **R** (prove its negation), and **I** (certify independence) against hidden targets while an independent verifier refuses every unsupported logical conclusion.

The only logically settling outcomes are:

- `PROVED`: a verifier checks an input-axiom proof of `C`;
- `REFUTED`: a verifier checks an input-axiom proof of `not C`;
- `INDEPENDENT`: a verifier checks two models of the same theory, one with `C` true and one with `C` false.

`UNKNOWN` means only that no verified settlement certificate was produced inside the budget. It is **never** evidence of independence.

## Why this is the next experiment after R01

R01 established a sealed Ocean harness with long exact proof horizons, external ATP adapters, independent path checking, and conservative bounded-unknown semantics. R02 adds the missing third logical branch: a positive, independently checkable certificate for independence.

The experiment deliberately separates four concepts that are often conflated:

1. semantic truth;
2. proof search;
3. certificate checking;
4. failure to settle inside a finite resource budget.

A solver may search however it likes. The benchmark trusts only the certificate.

## Formal problem family

Each public problem is a small propositional fragment written in TPTP-like FOF syntax:

- one or more signed literal axioms;
- signed-literal implication axioms;
- one signed-literal conjecture `C`.

For the designated Ocean modus-ponens calculus, an implication path is a proof. The generator uses fresh backbone variables and verifies the shortest path independently before sealing the ground truth.

### Theorem family: `F+(n)`

The hidden theory contains a shortest implication path of exactly `n` Ocean inferences from the asserted start literal to `C`.

Therefore `C` is outside proof horizon `n-1` but inside proof horizon `n`.

### Refutation family: `F-(n)`

The same construction instead places the exact `n`-step backbone at `not C`. P cannot settle the target through the backbone; R can settle it with a verified `n`-step certificate.

Goal polarity is randomized independently of the hidden class so a syntactic minus sign does not reveal which role is supposed to win.

### Independence family: `I(n)`

The long anchored Ocean backbone remains as a size/depth distractor, but the conjecture lives in an unanchored implication component whose truth value can be toggled while preserving all axioms. `n` is therefore a size/obfuscation parameter here, not a claimed minimum independence-proof depth.

Independence is not inferred from failed search. The I-agent must return two explicit complete valuations:

- `M+ |= T and C`;
- `M- |= T and not C`.

The independent verifier evaluates every input axiom in both models.

## The unconscious diver and exact proof horizon

For the theorem/refutation families, `F(n)` has minimum **Ocean** proof length exactly `n`. Nothing in the benchmark claims that every possible classical proof notation has minimum length `n`; the lower bound is with respect to the frozen Ocean inference calculus.

This is the “unconscious diver” picture: the theorem sits at depth `n`. It cannot be reached by any Ocean proof of depth `n-1`, yet a depth-aware search policy such as Depths-F can descend directly and find the `n`-step certificate quickly in wall-clock time. “Quickly found” and “short proof” are different quantities.

## Sealing and leakage barrier

`generator.py` emits two physically separable products:

- `public/`: opaque problem files, a hash-only manifest, and `SEAL_SHA256.txt`;
- `sealed/ground_truth.json`: hidden semantic class, generator seed, goal, and independently measured Ocean distances.

The runner must receive only the public side. The sealed directory must remain outside every solver/Professor/agent process until scoring is complete.

A production campaign should additionally commit or timestamp the public seal hash before execution and should run solver containers with no filesystem route to the sealed manifest.

## Agents

The benchmark API is role-neutral:

- **P** searches `T |- C`;
- **R** searches `T |- not C`;
- **I** searches for a two-model independence certificate;
- a **Professor/scheduler** may allocate compute, train search policy, and curate a shared lemma bank, but it receives no hidden class, planted route, seed, or sealed manifest.

Every shared lemma admitted to the bank must itself have a verifier-accepted certificate. A Professor may suggest; it may not certify its own suggestion.

`reference_ald.py` provides a transparent baseline: P and R use graph search in the Ocean calculus, while I uses a 2-SAT model search and returns both models. It is a benchmark reference implementation, not a claim that the full Data-ATP Professor architecture is complete.

## Conservative settlement state machine

For each instance:

1. accept `PROVED` only after the proof certificate verifies;
2. accept `REFUTED` only after the refutation certificate verifies;
3. accept `INDEPENDENT` only after both model certificates verify;
4. otherwise report `UNKNOWN`, `AUDIT_FAILURE`, timeout, or resource exhaustion as a **non-settlement**.

If two incompatible logical certificates ever verify for the same consistent sealed problem, the campaign halts and reports a harness/formalization fault rather than choosing a winner.

## Campaign matrix

The frozen intended horizons are:

`10, 25, 75, 100, 250, 750, 1,000, 2,500, 7,500, 10,000, 25,000, 75,000, 100,000, 250,000, 750,000`.

For each horizon there are three hidden semantic classes and three seed families, for 135 held-out instances in a full campaign. The nominal resource envelope is 30 seconds and 4,096 MiB per process.

`UNKNOWN` is not a fourth hidden semantic class. It is the correct operational response whenever the system has not earned one of the three settlement certificates.

## Training comparison

Run two scoreboards:

- **cold**: no sibling certificates;
- **trained**: every learning system receives the same lower-horizon sibling examples and independently verified certificates, while held-out test seeds remain sealed.

The run record must state whether training was actually consumed. This prevents a nominally “trained” benchmark from silently becoming another reference-algorithm test.

A professional ATP can be reported both in its ordinary cold configuration and, if desired, in a second lemma-pack condition where the same verified learned lemmas are supplied as additional premises. Those are distinct tracks and should never be merged into one score.

## Primary metrics

Report at least:

- verified settlement rate by hidden class;
- false-settlement count (target: zero);
- audit-failure count;
- `UNKNOWN` / resource-out count;
- maximum exact Ocean horizon settled by P and R;
- independence-certificate rate;
- certificate length/size;
- wall time to first verified settlement;
- training lift on held-out seeds;
- P/R/I contribution to successful settlements.

## Smoke test

From this directory:

```bash
python run_smoke.py
```

The smoke suite generates 27 sealed instances at size/depth parameters 10, 25, and 75, runs the transparent reference ALD, independently verifies every returned certificate, and fails if any accepted logical outcome disagrees with the sealed ground truth.

## Files

- `campaign.json` — frozen campaign dimensions and semantics.
- `common.py` — parser, literal semantics, model evaluator, and Ocean BFS certificate helper.
- `generator.py` — public/sealed campaign generator.
- `reference_ald.py` — transparent P/R/I baseline.
- `verifier.py` — independent certificate checker.
- `run_smoke.py` — end-to-end smoke test.

## Interpretation boundary

Passing R02 would establish that the conjecture-settling machinery works end-to-end under a deliberately controlled formal family: hidden outcomes, exact long Ocean proof horizons, independent checking, positive independence certificates, and conservative `UNKNOWN` semantics.

It would **not** establish a general algorithm for mathematical independence, nor would it imply that Hodge, ZFC independence questions, or arbitrary first-order theories are decidable. The purpose is to validate the machinery before asking it to operate in genuinely difficult mathematics.
