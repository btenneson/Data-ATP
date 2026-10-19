# M* 0.8 — multi-calculus search bridge and fair settlement measurements

**Development date:** October 18, 2026 (user-local time).  
**Scope of authorization:** development and associated tests for general-purpose automated theorem proving and an exponential-to-linear performance objective; existing 0.7 inputs and release preserved.  
**Public article considered:** [Preorders and Fair Settlement Geometry](https://btenneson.github.io/pub/cs.LO_Logic_in_Computer_Science/preorders_and_fair_settlement_geometry_001/), Brian Tenneson, September 2026.

## Executive assessment

The M* 0.8 development bridge demonstrates shared verifier-gated scheduling over **three configured proof-system paths**:

* finite Horn derivations using explicit fact/rule certificates;
* propositional CNF with DPLL-style SAT models and resolution refutations for UNSAT;
* bounded Metamath axiom-instance search using the unchanged v0.7 local `mm_core.py` verifier and unmodified tiny demo database.

All accepted mathematical claims carry independently replayable certificates; a proof search result is never accepted merely because a solver says `UNSAT` or `PROVED`. All unknown cases remain `UNKNOWN`. The common scheduler has a periodically serviced universal finite-byte-string reserve; its eventual-coverage claim is conditional on *unbounded* service and time and does not imply practical completeness within a finite budget.

**Scientific status:** a multi-calculus executable ATP *prototype* has been demonstrated. A general-purpose competitive or complete-for-all-inputs implementation has not been established. The original M* 0.7 graph achievement is not a newly discovered M* 0.8 theorem.

## Verified local tests and evidence

* Core and adversarial unit tests: **18/18 pass** (`tests_08.log`). Tests include a single embedded differential suite of **320 seeded small CNF formulas**, cross-checked against exhaustive truth-table classifications.
* All four example problems, covering Horn PROVED, SAT, UNSAT, and Metamath PROVED, produced certificates, replayed by the independent-of-search `core.verify` module.
* Two receipt files were then replayed by the separate `verify_receipt.py` CLI process: Metamath PROVED and CNF UNSAT both accepted; matching frozen problem hashes were checked, and the Metamath frozen DB hash was also checked.
* The Metamath adapter reuses a byte-identical copy of the v0.7 `mm_core.py` kernel; **no third-party external proof checker was invoked**.
* Negative tests reject false Horn deductions, invalid SAT models, wrong resolution steps, incorrect Metamath goals, and malformed untrusted payloads.

## Predeclared exponential-versus-linear diagnostic

Frozen instance family: \(F_n = (x_1) \land \cdots \land (x_n)\) with \(n\) Boolean variables and \(n\) positive unit clauses. The baseline enumerates complete assignments in false-first lexicographic order, stopping at the first satisfying assignment (all true). It necessarily tests all \(2^n\) assignments, by construction. M* 0.8's ordinary unit propagation can discover the forced all-true assignment in \(\Theta(n)\) *unit-cost clause/literal steps*. Verifying the assignment and outputting \(n\) bits adds \(\Theta(n)\) in the same model.

The metered *implementation* additionally counts problem serialization and certificate bytes. With decimal variable identifiers, this is \(O(n\log n)\) byte work, so the v0.8 aggregate meter is **not** mathematically proved \(\Theta(n)\) in a bit-cost model. Observed data are saved in `benchmark_results_08.json` and illustrate expected growth. The experiment is a **restricted-family, baseline-relative** demonstration and **not** a speedup over a standard competent SAT solver: any standard solver using unit propagation resolves these instances in linear clause/literal operations as well.

| n | False-first assignments | M* measured aggregate development work |
|---:|---:|---:|
| 4 | 16 | 142 |
| 6 | 64 | 172 |
| 8 | 256 | 202 |
| 10 | 1,024 | 234 |
| 12 | 4,096 | 266 |
| 14 | 16,384 | 298 |
| 16 | 65,536 | 330 |

No general exponential-to-linear theorem, no unrestricted runtime upper bound, and no advantage over competent goal-aware comparators has been established. The two columns use different units and must **not** be called an equal-resource speed ratio.

## Article adoption: useful mathematical safeguards

The cited article supplies three distinct preorders. SIC and scheduled-AMLD clocked simulation preorders capture preserved *structure* but deliberately permit rescaling clock stages; they cannot yield speedup claims by themselves. Its fair settlement reduction preorder instead requires certified answer preservation and polynomial bounds on reduction cost, instance growth, certificate lifting, and two-sided Bellman settlement-cost distortion.

Most consequential for M* 0.8, the article distinguishes a best-path settlement value \(V(x)\) from executable cost \(C_{M^*,\pi}(x)\). Existence of a cheap route does not imply that a solver finds that route cheaply. This report counts guide work, reserve attempts, candidate bytes, and verifier work rather than substituting minimal proof length or simulated SIC stage number for actual operations. It does **not** compute Bellman-optimal values or prove Bellman competitiveness.

The article also defines errorless high-probability settlement relative to explicitly declared input distributions, with verified YES/NO settlements and UNKNOWN on budget exhaustion. M* 0.8 includes a small preliminary harness with interfaces `sample`, `solve`, `verify`, and a frozen resource meter. For each distribution/size/sample, it records reproducible seeds, encoded input size, work count, output class, settlement count, and certificate size. A 95% Wilson binomial confidence interval is included per row.

The sample families are random 3SAT and planted 3SAT with 4.2n clauses at n=4,6,8, each 12 independent seeded draws per size; results are in `distribution_results_08.json`. The high-probability limit \(\Pr[T(X_n)\le p(n)]\to1\) **cannot** be inferred from finite samples. This paper provides an experimental discipline, not a new SAT theorem for M*.

## Currently supported scientific-status updates

1. **General-purpose ATP:** changed from *not established* to **multi-calculus executable prototype demonstrated; general-purpose objective actively under development**. Full claim remains unestablished.
2. **Exponential-to-linear speedup:** changed from *not demonstrated* to **restricted-family exponential-versus-linear primitive-operation contrast demonstrated against a declared exhaustive baseline; broad or best-solver speedup not established**. Bit-complexity accounting precludes unqualified end-to-end linear cost.

## Next research gates

1. Expand Metamath from bounded axiom instantiation to target-independent structural proof discovery, preserving frozen-bank provenance, DV checks, and the v0.7 proof-completion baseline.
2. Add a second fully independent checker or maintained external proof verifier where feasible; compare checker outputs.
3. Introduce certified cutoffs, verified lemma reuse, and admissible search bounds without weakening the fair reserve.
4. Construct more demanding problem families, include standard target-aware comparators (unit propagation, resolution, modern SAT), and pre-register an identical end-to-end accounting method.
5. Attempt formal mathematical upper/lower bounds only after the cost metric and input family are precisely defined. Use hold-out distributions with more samples to investigate (not assume) high-probability performance.
6. For fair-reduction research, provide actual reduction and certificate-lifting code and establish quantitative Bellman distortion rather than merely citing the definition.

## Reproducibility

Python 3.12+; no third-party packages. Run `python -m unittest discover -s tests -v`, `python run_demo.py`, `python benchmark.py`, and `python high_probability_harness.py`; replay example receipts with `verify_receipt.py`. The 0.7 package remains a separate immutable predecessor artifact. No publication to the user's public website is implied or attempted.
