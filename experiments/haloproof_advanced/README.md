# HaloProof Advanced Settlement Campaign

This experiment attacks the frozen HaloProof benchmark with the strongest *verified* techniques currently available in the project while preserving the original benchmark contract.

## Exact benchmark

The benchmark model is the rational-function field

`H = R(t)`

ordered by eventual sign near `0+`. The infinitesimal halo is

`I = { x in H : for every positive integer n, |x| < 1/n }`,

and the target is `I ~~ R` (equipollence), in the exact Metamath encoding chosen by the frozen extension.

This is deliberately **not** the separate ultrapower/nonprincipal-ultrafilter proposal in `ATP/hyperreal.mm`.

The known reference route is:

1. `R ~<_ I` using the injection `r |-> r t`;
2. `I ~<_ H` by inclusion;
3. `H ~~ R` by coding rational functions with finite real data;
4. `I ~<_ R` by composition;
5. `I ~~ R` by Schroeder-Bernstein.

## Native set.mm route

The frozen `set.mm` already contains most of the algebraic infrastructure needed for the benchmark. The preferred concrete construction is

`P = Poly1(RRfld)`

and

`H = Frac(P) = Frac(Poly1(RRfld))`.

The campaign reuses native machinery including `refld`, `fldidom`, `ply1idom`, `fracfld`, `fracf1`, `coe1`, `coe1f`, `coe1sfi`, `deg1nn0cl`, `deg1ldg`, the generic infinitesimal relation `<<<`, and `sbth` rather than reimplementing a rational-function field from scratch.

## Verified and candidate development lemmas

The bundled file `haloproof_order_halo.mm` contains the following no-new-axiom development lemmas:

- `hprefld`: `RRfld e. Field`;
- `hpridom`: `RRfld e. IDomn`;
- `hppolyidom`: `( Poly1 ` RRfld ) e. IDomn`;
- `hpfracfield`: `( Frac ` ( Poly1 ` RRfld ) ) e. Field`;
- `hpcoe1map`: coefficients of a concrete polynomial map `NN0` into the real-field carrier;
- `hpcoe1fsupp`: the coefficient vector has finite support relative to real zero;
- `hpcoe1nzex`: candidate theorem that a nonzero polynomial has at least one nonzero coefficient.

The first six have been independently accepted by the local project verifier on the frozen `set.mm`. `hpcoe1nzex` is the current candidate. It uses the native polynomial degree as a witness: `deg1nn0cl` places the degree in `NN0`, while `deg1ldg` proves the coefficient at that degree is nonzero.

The frozen snapshot used in the campaign has SHA-256

`1016D7EDB0508ABDE0FE240BB5243E588C5067F8CB10EE6E1CC5733FC05ACDB5`.

These are development lemmas only; they do **not** yet settle the HaloProof target.

The next mathematical steps are deliberately small:

1. independently verify `hpcoe1nzex`;
2. define the nonzero coefficient-index class and use well-ordering of `NN0` to obtain its least element;
3. define polynomial sign near `0+` from the coefficient at that least exponent;
4. prove multiplication compatibility;
5. lift the sign to `Frac(P)` and prove independence of representatives using `fracerl`;
6. prove the resulting relation is a strict total order compatible with the field operations;
7. identify the embedded polynomial variable as `t` and prove that it is a positive infinitesimal;
8. define the exact two-sided halo and prove the two cardinal bounds;
9. finish with `sbth`.

## Why the campaign has development gates

HaloProof requires a reference proof before the blind benchmark is opened. That is a protocol check that the exact frozen target is derivable in the exact frozen environment, not a hint supplied to the later blind ATP.

The gate requires an exact frozen `set.mm`, a conservative order/halo extension, an exact target label, a separately verified reference certificate, independent verifier agreement, and a nontrivial admissible theorem index excluding target leakage and direct restatements.

Only after those exist should the final proof be sealed away from the blind condition and the advanced search controller be launched.

## Search architecture after the gate

The intended final campaign combines legal-first candidate construction, subject-conditioned dense preparation, quotient/canonical proof-state representation where sound, settlement-compass premise/territory guidance, bounded learned intervention with a proof-covering fallback, diverse retrieval/creativity channels, a shared bank containing only verified lemmas, level-2-style reflective resource allocation, atomic checkpoints with deterministic replay, and fresh-process verification before any `VERIFIED_PROOF` result is accepted.

## Verify the current development milestone on Windows

```powershell
cd C:\Users\12096\GitHub\Data-ATP\experiments\haloproof_advanced
git pull

powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\run_haloproof.ps1 `
  -ATPRoot "C:\Users\12096\GitHub\ATP" `
  -SetMM "C:\google drive\Automated Theorem Proving\set.mm"
```

The runner checks all seven development labels against the frozen database. If successful, the expected gate is:

`NONZERO_COEFFICIENT_VERIFIED_NEEDS_LEAST_INDEX`

That means we have formally reached the point where a nonzero polynomial is known to have a nonzero coefficient; the next missing result is existence of the **least** such coefficient index.

If the candidate is malformed, the run stops at `PROTOCOL_FAILURE_DEVELOPMENT_VERIFY`. That is a failed candidate proof, not evidence against the HaloProof theorem.

A complete order/halo/target extension will later be supplied with `-Extension` and `-TargetLabel`; that route performs grammar/target checks and stops at `REFERENCE_PROOF_REQUIRED` before any blind run.

## Result semantics

Only four final scientific outcome classes are allowed:

- `VERIFIED_PROOF`
- `VERIFIED_REFUTATION`
- `BUDGET_EXHAUSTED_UNKNOWN`
- `PROTOCOL_FAILURE`

A timeout, empty frontier, crash, malformed certificate, or exhausted budget is never a refutation or independence result.
