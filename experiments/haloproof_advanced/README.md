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

The campaign therefore reuses native machinery including `refld`, `fldidom`, `ply1idom`, `fracfld`, `fracf1`, `coe1`, `coe1f`, `coe1sfi`, the generic infinitesimal relation `<<<`, and `sbth` rather than reimplementing a rational-function field from scratch.

## Verified and candidate development lemmas

The bundled file `haloproof_order_halo.mm` contains the following concrete HaloProof development lemmas, with no new axiom:

- `hprefld`: `RRfld e. Field`;
- `hpridom`: `RRfld e. IDomn`;
- `hppolyidom`: `( Poly1 ` RRfld ) e. IDomn`;
- `hpfracfield`: `( Frac ` ( Poly1 ` RRfld ) ) e. Field`;
- `hpcoe1map`: coefficients of a concrete polynomial map `NN0` into the real-field carrier;
- `hpcoe1fsupp`: the coefficient vector has finite support relative to real zero.

The first four have already been independently accepted by the local project verifier on the frozen `set.mm`. The last two are the current verifier candidates. They are promoted to verified status only if the next local campaign run accepts them on the same frozen snapshot.

The frozen snapshot used in the campaign has SHA-256

`1016D7EDB0508ABDE0FE240BB5243E588C5067F8CB10EE6E1CC5733FC05ACDB5`.

These are development lemmas only; they do **not** yet settle the HaloProof target.

The next mathematical steps are deliberately small:

1. prove that a nonzero polynomial has nonempty coefficient support;
2. use well-ordering of `NN0` to obtain a least nonzero exponent;
3. define the polynomial sign near `0+` as the sign of the coefficient at that least exponent;
4. prove multiplication compatibility;
5. lift the sign to `Frac(P)` and prove independence of representatives using `fracerl`;
6. prove the resulting relation is a strict total order compatible with the field operations;
7. identify the embedded polynomial variable as `t` and prove that it is a positive infinitesimal;
8. define the exact two-sided halo and prove the two cardinal bounds;
9. finish with `sbth`.

## Why the campaign has development gates

HaloProof requires a reference proof before the blind benchmark is opened. That is not a hint to the blind ATP. It is a protocol check that the exact frozen target is actually derivable in the exact frozen environment.

The gate requires:

- an exact frozen `set.mm` plus SHA-256;
- a conservative HaloProof eventual-sign order/halo/target extension plus SHA-256;
- a target label whose parse tree is valid;
- a separately verified reference certificate;
- independent verifier agreement;
- a nontrivial admissible theorem index excluding target leakage and direct restatements.

Only after those exist should the final proof be removed/sealed from the blind condition and the advanced search controller be launched.

## Search architecture after the gate

The intended final campaign combines:

- legal-first candidate construction from the repaired Predator line;
- subject-conditioned dense preparation;
- quotient/canonical proof-state representation where sound;
- settlement-compass guidance for relevant proof territory;
- bounded learned intervention with a guaranteed proof-covering fallback;
- diverse retrieval/creativity channels without allowing novelty to bypass verification;
- a shared bank containing only independently verified lemmas;
- a level-2-style reflective controller that may reallocate search effort from observed state but never decides theoremhood;
- atomic SHA-256 checkpoints, exact committed-expansion accounting, deterministic replay, and reboot recovery;
- fresh-process independent verification before any `VERIFIED_PROOF` result is accepted.

`campaign.json` is the machine-readable campaign specification.

## Verify the current development milestone on Windows

From the HaloProof directory, first update the branch:

```powershell
cd C:\Users\12096\GitHub\Data-ATP\experiments\haloproof_advanced
git pull
```

Then run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\run_haloproof.ps1 `
  -ATPRoot "C:\Users\12096\GitHub\ATP" `
  -SetMM "C:\google drive\Automated Theorem Proving\set.mm"
```

The `ExecutionPolicy Bypass` applies only to that child PowerShell invocation; it does not permanently change the machine policy.

The runner verifies the local verifier, hashes the frozen inputs, inventories the native machinery, concatenates the bundled development extension, and asks the project Metamath verifier to check all six labels listed above.

If that succeeds, the expected gate is:

`COEFFICIENT_SUPPORT_VERIFIED_NEEDS_NONEMPTY_SUPPORT`

That means the field foundation and the finite-support prerequisite for the least-nonzero-coefficient construction are formally verified. The next missing result is that a **nonzero** polynomial has **nonempty** support. It is a development status, not a final mathematical outcome.

If either candidate proof is malformed, the run instead stops at `PROTOCOL_FAILURE_DEVELOPMENT_VERIFY`; that is exactly why this gate exists. A failed candidate is corrected rather than counted as evidence about the HaloProof theorem.

A complete order/halo/target extension will later be supplied with `-Extension` and `-TargetLabel`; that route performs grammar/target checks and stops at `REFERENCE_PROOF_REQUIRED` before any blind run.

## Result semantics

Only four final scientific outcome classes are allowed:

- `VERIFIED_PROOF`
- `VERIFIED_REFUTATION`
- `BUDGET_EXHAUSTED_UNKNOWN`
- `PROTOCOL_FAILURE`

A timeout, empty frontier, crash, malformed certificate, or exhausted budget is never a refutation or independence result.
