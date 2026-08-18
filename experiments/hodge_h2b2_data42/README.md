# DATA 4.2 — H2B2 bundlewise Hodge-star experiment

Status: launch experiment, 2026-08-17.

## Target

This experiment treats H2B1 as frozen input and attacks the following deliberately restricted H2B2 gluing theorem.

Let `(U_i)` be a finite cover. On each chart there is a graded local Hodge-star operator `star_i`. On every overlap there is an invertible transition map `g_ij`. Assume:

1. cocycle compatibility for the transition maps;
2. H2B1/local Hodge-star laws on every chart;
3. overlap naturality `g_ij ∘ star_j = star_i ∘ g_ij`;
4. the local square law `star_i^2 = sigma * id`, where `sigma = (-1)^(k(n-k))` in the Riemannian convention being modeled.

The target is to construct a unique global bundle endomorphism `STAR` whose restriction to each chart is `star_i`, and to inherit the square law globally.

This is a **restricted bundlewise rung**, not the Hodge conjecture and not a claim that arbitrary local Hodge stars automatically glue. The overlap-naturality hypothesis is essential.

## DATA 4.2 policy under test

The runner implements the architecture as an auditable proof-plan search:

- **quotient representation:** proof states are canonicalized modulo commutation of independent bookkeeping moves and alpha-like renaming of chart labels;
- **quotient-density training:** a small retained family of solved gluing DAGs is used to estimate move success rates by canonical state features; the target instance itself is excluded from training;
- **compass:** learned move scores rank candidate successors;
- **bounded intervention:** compass guidance receives a fixed share of each search epoch;
- **conservative fallback:** complete breadth/dovetail enumeration receives a guaranteed share and cannot be disabled by the learned compass;
- **verification:** an independent checker validates the final proof-plan certificate from primitive inference rules.

## Success criterion

A run is successful only if the independent checker accepts a certificate deriving both:

- existence/uniqueness of the glued global operator; and
- the inherited global square law.

The audit artifact records expansions, canonical-state counts, quotient collisions, compass/fallback usage, learned scores, certificate, and verification result.

## Interpretation boundary

A successful run supports only the claim that DATA 4.2 can navigate and verify this formalized H2B2 gluing subproblem efficiently enough under the stated hypotheses. It does not settle the full Hodge conjecture, algebraicity of Hodge classes, or any later global/cohomological rung.
