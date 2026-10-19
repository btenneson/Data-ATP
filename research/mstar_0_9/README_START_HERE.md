# M* 0.9 — Development automation starter (not a completed M* 0.9 prover)

This starter automates **testing and research evidence capture**, not theorem discovery or self-modifying upgrades. It includes a byte-verified frozen snapshot of M* 0.8, a separate editable development candidate, and a repeatable test/verification/benchmark/report pipeline.

## One step to begin

On Windows, unzip this package and double-click `AUTOPILOT_WINDOWS.cmd`. On Linux or macOS, use `sh AUTOPILOT_UNIX.sh`. Requires **Python 3.12+** and no third-party packages. The entire default run takes seconds on most ordinary computers.

Read `results/latest/AUTOPILOT_REPORT.md` afterwards. The machine-readable record is `results/latest/AUTOPILOT_RESULT.json`.

**Edit only `candidate_0_9/`.** The `frozen_0_8/` folder is protected by the included SHA256 manifest. The runner refuses to proceed if baseline source files change. It makes temporary working copies of each source tree so scripts cannot overwrite either tree during a run. Keep the original `Mstar_ATP_0_8_Multi_Calculus_Development.zip` archived separately.

## What is automated now

1. Verify frozen M* 0.8 file hashes before and after runs.
2. Run the v0.8 regression suite for the baseline and candidate, requiring at least 18 tests. Candidate additionally runs with Python `-O` to detect a subset of checks relying incorrectly on `assert`.
3. Generate Horn, SAT, UNSAT and limited Metamath proof results in isolated scratch folders.
4. Replay those certificates in **separate verifier CLI processes** (separate from search, but not unaffiliated external certification). For candidate outputs, the pipeline also runs the **unchanged frozen v0.8 checker**, so a candidate cannot silently weaken its own checker and pass the gate.
5. Re-run the restricted positive unit-CNF complexity diagnostic, preserving different costs rather than pretending all ratios are runtime speedups.
6. Re-run seeded finite SAT distribution tests, retaining `UNKNOWN` and honest confidence intervals.
7. Write machine-readable and readable pass/fail reports, including gate statements that cannot be upgraded automatically on mere test success.

Run a quick local check with `python autopilot.py --mode quick --output results/quick`. For a full pipeline, `python autopilot.py --mode full --output results/latest`.

To evaluate a different candidate working directory, run `python autopilot.py --candidate /path/to/Mstar_candidate --mode full --output results/candidate_name`.

## GitHub Actions (optional, user must connect/commit)

The repository `.github/workflows/mstar-09-autopilot.yml` file performs the same full pipeline on GitHub-hosted Ubuntu and Windows, for Python 3.12/3.13, when you **push changes or open a pull request**. In the public `btenneson/Data-ATP` repository, this package is located in `research/mstar_0_9/` and CI is in `.github/workflows/mstar-09-autopilot.yml`. The workflow runs from that directory; it does not modify any other ATP project. It does not deploy/publish, self-merge, overwrite branches, or request privileged tokens. No cloud automation has been enabled by this package alone.

For an even more automated research workflow: perform development changes on a new branch; let this pipeline run on every pull request; require human review for any status-changing scientific claims. Add externally maintained Metamath checkers and reliable comparison provers to the pipeline once configured and licensed appropriately. Never mark ``general-purpose ATP established`` or ``exponential-to-linear competitive speedup`` based solely on this starter.

## Immediate engineering backlog, recommended sequence

1. **Interruptible guide steps:** The current M* 0.8 guide can consume its entire work budget before reserve servicing. Replace long-running calls with one-step transitions that carry persistent state and have preemptible per-tick work limits; verify the invariant that reserve executes on an unbounded fair schedule.
2. **Logic breadth:** Implement first-order term data types, capture-avoiding substitution, occurs-check unification, ordered resolution/superposition and verified proof DAGs. Add nontrivial unseen test sets.
3. **Competitive benchmarks:** Use TPTP problem suites, strong reference provers, and a normalized cost model. For SAT, use competent DPLL/CDCL baselines; log preprocessing, hashing, verification, output bytes, memory, and actual work.
4. **Complexity theorem:** Pre-register one parametric family, input encoding, cost unit, and fair comparator, and prove matching asymptotic bounds. Memoization-vs-recalculation and bounded-treewidth SAT are promising *restricted* families, not universal breakthroughs.
5. **External proof checking:** Add at least one independently maintained checker for each certificate format where feasible; keep first-party search and checking separate even before external validation.

The September 2026 **Preorders and Fair Settlement Geometry** article is used as a guardrail: don't confuse minimum settlement cost, actual search cost, proof length, and simulated stage. Its Bellman competitiveness results are a research objective, **not** an implemented M* 0.9 theorem.

## Status

- v0.8: frozen baseline, originally 18 tests passing.
- v0.9 automation starter: **engineering pipeline** only, candidate initially identical to v0.8; no new theorem-proving capability claimed.
- General-purpose competitive ATP: **not established**.
- Competitive exponential-to-linear speedup: **not established**.
