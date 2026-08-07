# `sgrpcl` Hilbert Structural Pilot v0.1

## Scientific status

This is an experimental search-order modification of Predator 8.004. It does **not** claim a proof of `sgrpcl`. Success requires a complete Metamath certificate accepted by the existing in-process verifier and a fresh external verifier.

## Why the original rule-cube idea was adjusted

Inspection of the real Predator 8.004 search source showed that, for one selected open goal, the current unifier normally yields at most one legal instantiation per assertion label. Therefore a literal Hilbert component per assertion schema would usually be a singleton and would provide essentially no useful traversal geometry.

The first real pilot therefore places Hilbert geometry over the **set of already-legal opener applications** at a proof state. Formal legality remains entirely upstream of the geometry.

## Four structural coordinates

The Hilbert embedding uses four quantities already computed by Predator's learned-ranking feature pipeline:

1. candidate relative age;
2. goal/candidate node overlap;
3. log candidate size;
4. log total generated-child size.

For each open-goal candidate set, values on each axis are converted to stable ordinal grid coordinates. The resulting 4D integer points are mapped to a power-of-two discrete Hilbert grid. A deterministic seed- and goal-dependent rotation chooses the starting location.

## Density + Hilbert blend

Predator 8.004's existing trained dense model remains the density signal. The modified search first obtains the ordinary legal-candidate ranking, including the existing agent/profile scoring. It then blends rank percentiles:

```text
priority = (1 - h) * ordinary_rank_percentile
         + h       * hilbert_rank_percentile
```

where `h = --hilbert-mix`.

- `--hilbert-mix 0` is an exact software control: ordinary Predator ordering.
- `--hilbert-mix 0.25` is the frozen first hybrid pilot.
- `--hilbert-mix 1` is pure structural Hilbert ordering and is an ablation, not the recommended first run.

Closer applications are left unchanged. The Hilbert blend is applied only to legal openers, immediately before Predator's existing opener-cap/counterfactual selection.

## Preserved controls

The initial `sgrpcl` run should preserve the 8.004 dense-uniform protocol:

- target: `sgrpcl`;
- environment: the same frozen `set(3).mm`;
- model: `Predator_8.004_sgrpcl_dense_uniform.joblib`;
- expansion budget: 80,000;
- max depth: 10;
- agents: 4;
- creativity: 0.55;
- seed: 2301;
- opener cap: 48;
- max open goals: 6;
- progress interval: 2,000;
- independent external certificate verification.

Use separate result paths so the original 8.004 record is never overwritten.

## Recommended Windows command

From the Predator 8.004 comparison-bundle directory, after placing `predator8_hilbert_geometry.py` and `predator8_004_hilbert_search.py` beside the original scripts:

```bat
py -u predator8_004_hilbert_search.py "set(3).mm" ^
  --engine Predator_8.001_FROZEN.py ^
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
  --hilbert-mix 0.25 ^
  --out "experiments\sgrpcl\search\hilbert-v0.1\sgrpcl_hilbert_mix025.mm" ^
  --report "experiments\sgrpcl\search\hilbert-v0.1\search_report_mix025.json"
```

## Validation completed before packaging

- the modified search source compiles;
- command-line argument parsing succeeds;
- 4D Hilbert geometry is bijective on tested grids;
- consecutive tested Hilbert cells are face-adjacent;
- `hilbert_mix=0` reproduces the original candidate ordering exactly in the geometry layer;
- hybrid ranking is deterministic for a fixed seed and preserves the candidate set.

## Outcome discipline

Report only one of the existing experiment categories. In particular:

- `VERIFIED_PROOF` only after fresh external verification;
- budget exhaustion without a certificate is `BOUNDED_UNKNOWN`;
- an empty legal frontier is a frontier outcome, not a refutation;
- an implementation/environment failure is a fault.

The central scientific comparison is verified theorem yield and cost under the same budget, not whether the Hilbert code merely executes.
