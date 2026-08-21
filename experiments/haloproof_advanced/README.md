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

The principal new formal work is now narrower:

1. define eventual-sign positivity/order near `0+`, preferably algebraically using the least-degree nonzero polynomial coefficients;
2. prove that this sign/order is independent of the chosen fraction representative;
3. identify the embedded polynomial variable as `t` and prove that it is a positive infinitesimal;
4. define the exact **two-sided** halo required by the benchmark (the native `<<<` relation may help but must not silently replace the benchmark definition);
5. prove `r |-> r t` is an injection from `RR` into the halo;
6. prove `H ~~ RR` from finite real coefficient data and derive the reverse cardinal inequality for the halo;
7. finish with `sbth`.

## Why the campaign begins with a development gate

HaloProof requires a reference proof before the blind benchmark is opened. That is not a hint to the blind ATP. It is a protocol check that the exact frozen target is actually derivable in the exact frozen environment.

At present, this directory therefore begins with an **environment/reference-proof gate** rather than pretending that a long proof search against an unfinished extension is a meaningful HaloProof run.

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

## Run the first local gate on Windows

From a PowerShell prompt in a checkout of this branch:

```powershell
cd .\experiments\haloproof_advanced
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\run_haloproof.ps1 `
  -ATPRoot "C:\path\to\ATP" `
  -SetMM "C:\path\to\frozen\set.mm"
```

The `ExecutionPolicy Bypass` applies only to that child PowerShell invocation; it does not permanently change the machine policy.

The first run verifies the local verifier, hashes the frozen inputs, and inventories the native `Poly1`, `Frac`, coefficient, ordered-field, infinitesimal, cardinality, and Schroeder-Bernstein machinery in the exact `set.mm` snapshot. It writes a timestamped run directory and `HALOPROOF_MANIFEST.json`.

Until the smaller HaloProof order/halo extension is supplied, the expected gate is:

`NEEDS_HALOPROOF_ORDER_HALO_EXTENSION`

That is a development status, **not** a mathematical outcome.

When a candidate extension exists, run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\run_haloproof.ps1 `
  -ATPRoot "C:\path\to\ATP" `
  -SetMM "C:\path\to\frozen\set.mm" `
  -Extension "C:\path\to\haloproof_order_halo.mm" `
  -TargetLabel "EXACT_TARGET_LABEL"
```

The runner concatenates the exact frozen database and extension in the run artifact directory, requires a zero-error grammar round trip, parses the target tree, records the exact target identity, and then stops at `REFERENCE_PROOF_REQUIRED`.

## Result semantics

Only four final scientific outcome classes are allowed:

- `VERIFIED_PROOF`
- `VERIFIED_REFUTATION`
- `BUDGET_EXHAUSTED_UNKNOWN`
- `PROTOCOL_FAILURE`

A timeout, empty frontier, crash, malformed certificate, or exhausted budget is never a refutation or independence result.
