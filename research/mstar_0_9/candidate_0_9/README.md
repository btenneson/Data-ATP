# M* 0.8 — multi-calculus verifier-gated development bridge

Research prototype based on and **separate from** the frozen M* 0.7 package. The original 0.7 release is not modified or copied into this distribution. It can be reproduced using the original archive `Mstar_ATP_0_7_Both_Half_Proof_Development_Windows.zip`.

Three proof-system adapters share the **same goal-independent scheduler and fair byte-code reserve**:

1. Horn implication derivations with independently checked rule applications.
2. CNF satisfiability using verified models, or resolution UNSAT certificates (never an unverified UNSAT).
3. Metamath axiom-instance demonstration against the unmodified 0.7 local kernel (bounded and incomplete). This reuses the unmodified local Metamath proof-checking implementation and a tiny demo input.

**Known boundary:** This implementation handles only its explicitly supported finite calculi and a bounded Metamath axiom-instantiation tactic. It is not established to be a practical full general-purpose ATP, and does not inherit proof-completion prowess for arbitrary Metamath goals from v0.7. The fair reserve is mathematically universal over the finite byte strings and therefore eventually offers every finite UTF8 JSON proof certificate, but finite budgets can be useless and UNKNOWN is always permissible.

## Runs

Python 3.12+; no third-party dependencies. Run from the folder containing this README:

```sh
python -m unittest discover -s tests -v
python run_demo.py
python verify_receipt.py examples/unsat_problem.json examples/unsat_result.json
python verify_receipt.py examples/metamath_problem.json examples/metamath_result.json --database legacy_mm/demo0_base.mm
python benchmark.py
python high_probability_harness.py
```

Run result schema includes SHA256 of the exact JSON problem, ticks, reserve ticks, total development work units (including input/certificate bytes, search operations, and verification operations), accepted certificate, and wall time. Work units are an explicitly artificial aggregate meter; do not identify them with CPU instructions or a full universal machine cost.

## Speedup benchmark

The frozen demonstration family is positive unit CNF with n variables and clauses `(x1) ... (xn)`. False-first assignment enumeration requires `2^n` candidates before reaching all-true; DPLL unit propagation resolves the same instance in O(n) clause/literal operations, as does every normal unit-propagating SAT solver. JSON input bytes grow like O(n log n) because decimal variable indices grow; all byte operations are measured separately in the development meter. No competitive state-of-the-art claim. No speedup over standard goal-aware unit propagation.

## Preorders and Fair Settlement Geometry integration

The September 2026 paper is used as a **research contract**, not as an implemented Bellman oracle. It motivates distinguishing optimal settlement value V from *actual* search cost C and tracking verification and certificate output costs. The proposed fair-settlement reductions and high-probability distribution protocols remain unimplemented in this prototype. No Bellman competitiveness or high-probability polynomial SAT theorem is asserted.

Source: https://btenneson.github.io/pub/cs.LO_Logic_in_Computer_Science/preorders_and_fair_settlement_geometry_001/

## Research status boundaries

- The first local test suite contains both positive functionality tests and adversarial rejection cases. The differential tests compare 320 small SAT CNFs to exhaustive truth tables. There has been **no unaffiliated external checker run**.
- The positive unit-CNF speedup is a simple algorithmic contrast on one specially declared family, **not** an exponential-to-linear advance over competent goal-directed ATP/SAT solvers. Byte-encoding costs are explicitly not linear in n.
- The cost meter is an explicit workload proxy, not a fully standardized time-complexity unit. Certificate output bytes, input JSON byte lengths, guide work, reserve checks and verification work are charged in the shared aggregate.
- The September 2026 fair-settlement article is useful for experimental design, but its Bellman values, fair reductions and high-probability limits have not been mechanized or established for M*.
- M* 0.7's graph proof is deliberately not claimed as a new 0.8 proof discovery.
