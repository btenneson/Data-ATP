# `sgrpcl` Hilbert-Style Pilot

**Plan version:** 0.1.0  
**Target:** Metamath `sgrpcl`  
**Hardware assumption:** Brian Tenneson's eight-core gaming laptop  
**Concurrency rule:** at most two substantial searches at once

## Target

Informally, `sgrpcl` states that the operation of a semigroup is closed on its base set:

```text
(G in Smgrp and X in Base(G) and Y in Base(G))
    -> (X .o. Y) in Base(G).
```

The final success condition is not textual similarity. It is a complete Metamath certificate accepted both in process and by the fresh external verifier.

## Why an adapter is required

The executable reference engine in this release performs forward consequence epochs over explicit `k`-ary rules. Predator 8.004 performs backward goal-directed search over unifiable Metamath assertions. A legitimate Hilbert pilot must therefore define the search coordinates inside Predator rather than merely rename its existing candidate order.

For a current open goal `g`, each legal assertion application contains discrete choices such as:

1. assertion/rule identity;
2. unifier or substitution identity;
3. ordered essential-hypothesis slots;
4. the selected next open hypothesis;
5. optional representation/agent profile.

The intrinsic action space is a coproduct over assertion schemas. Each assertion component has dimension equal to the number of independently enumerable choices needed to instantiate it. The dimension is not automatically just the number of essential hypotheses; substitution variables and side-condition choices must be included when they are not functionally determined by the goal.

## Version 0.1.0 pilot design

1. Freeze `set(3).mm`, target cutoff, model files, seed, expansion budget, depth, and verifier.
2. Preserve Predator 8.004 legal-first generation: rough retrieval, full unification, then legal applications only.
3. Give every legal application a stable integer address derived from its assertion label, substitution tuple, and ordered generated subgoals.
4. Partition legal applications by assertion schema: a coproduct, not one cross-rule product.
5. Within each component, quantize the independent integer coordinates to a power-of-two grid and compute a Hilbert distance.
6. Order legal candidates by a frozen combination of model score and Hilbert coverage priority.
7. Log both the ordinary rank and Hilbert address for every expansion.
8. Verify any candidate certificate twice.
9. Report `VERIFIED_PROOF`, `BOUNDED_UNKNOWN`, `FRONTIER_COLLAPSE`, or `SYSTEM_FAILURE` without reinterpretation.

## Honest baseline

Use the existing repaired Predator 8.004 search as the control. Do not overwrite its reports. The previously documented search uses:

```bat
py -u predator8_004_search.py "set(3).mm" ^
  --label sgrpcl ^
  --model "experiments\sgrpcl\dense\Predator_8.004_sgrpcl_dense_uniform.joblib" ^
  --budget 80000 ^
  --max-depth 10 ^
  --agents 4 ^
  --creativity 0.55 ^
  --seed 2301 ^
  --opener-cap 48 ^
  --max-open 6 ^
  --progress 2000 ^
  --out "experiments\sgrpcl\search\dense-uniform\sgrpcl_dense-uniform.mm" ^
  --report "experiments\sgrpcl\search\dense-uniform\search_report.json"
```

The Hilbert run must use separate paths, for example:

```text
experiments\sgrpcl\search\hilbert-v0.1.0\
```

## Laptop allocation

For an eight-core laptop with another search already running, begin the Hilbert pilot with four worker agents or fewer. Avoid launching the dense-uniform and dense-balanced Hilbert variants simultaneously with two other heavy jobs. Two substantial concurrent processes is the declared ceiling for the pilot.

## What must be implemented next

- a canonical serializer for a legal Metamath application;
- extraction of independently variable substitution coordinates;
- per-assertion coproduct component identifiers;
- Hilbert distance computation for variable-dimensional components;
- a fair scheduler that cannot permanently starve any legal component;
- checkpoint and resume support;
- paired control/Hilbert result reporting.

Until those items are implemented and tested, this document is an integration specification, not evidence that `sgrpcl` has been proved by Hilbert search.
