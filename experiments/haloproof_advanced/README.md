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

The campaign therefore reuses native machinery including `refld`, `fldidom`, `ply1idom`, `fracfld`, `fracf1`, `coe1`, the generic infinitesimal relation `<<<`, and `sbth` rather than reimplementing a rational-function field from scratch.

## Verified development foundation

The bundled file `haloproof_order_halo.mm` now contains the first four concrete HaloProof theorems, with no new axiom:

- `hprefld`: `RRfld e. Field`;
- `hpridom`: `RRfld e. IDomn`;
- `hppolyidom`: `( Poly1 ` RRfld ) e. IDomn`;
- `hpfracfield`: `( Frac ` ( Poly1 ` RRfld ) ) e. Field`.

These proofs have been stack-checked against the frozen `set(3).mm` snapshot with SHA-256

`1016D7EDB0508ABDE0FE240BB5243E588C5067F8CB10EE6E1CC5733FC05ACDB5`.

The local campaign runner independently re-verifies those four labels with the project `metamath.py` before advancing the gate. They are foundation lemmas only; they do **not** yet settle the HaloProof target.

The principal new formal work is now narrower:

1. define eventual-sign positivity/order near `0+`, preferably algebraically using the least-degree nonzero polynomial coefficients;
2. prove that this sign/order is independent of the chosen fraction representative, using the native fraction equivalence/cross-multiplication machinery such as `fracerl`;
3. prove the relation is a strict total order compatible with the field operations and package the benchmark structure as an ordered field;
4. identify the embedded polynomial variable as `t` and prove that it is a positive infinitesimal;
5. define the exact **two-sided** halo required by the benchmark (the native `<<<` relation may help but must not silently replace the benchmark definition);
6. prove `r |-> r t` is an injection from `RR` into the halo;
7. prove `H ~~ RR` from finite real coefficient data and derive the reverse cardinal inequality for the halo;
8. finish with `sbth`.

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

The runner verifies the local verifier, hashes the frozen inputs, inventories the native `Poly1`, `Frac`, coefficient, ordered-field, infinitesimal, cardinality, and Schroeder-Bernstein machinery, concatenates the bundled development extension, and verifies exactly the four foundation labels above.

If that succeeds, the expected gate is now:

`FOUNDATION_VERIFIED_NEEDS_EVENTUAL_SIGN_ORDER`

That means the concrete field foundation is formally verified and the next missing theorem family is the algebraic eventual-sign order. It is a development status, **not** a final mathematical outcome.

A complete order/halo/target extension will later be supplied with `-Extension` and `-TargetLabel`; that route performs grammar/target checks and stops at `REFERENCE_PROOF_REQUIRED` before any blind run.

## Result semantics

Only four final scientific outcome classes are allowed:

- `VERIFIED_PROOF`
- `VERIFIED_REFUTATION`
- `BUDGET_EXHAUSTED_UNKNOWN`
- `PROTOCOL_FAILURE`

A timeout, empty frontier, crash, malformed certificate, or exhausted budget is never a refutation or independence result.
